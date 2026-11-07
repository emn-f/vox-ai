"""
Testes unitários para o pipeline de ingestão com IA e revisão Human-in-the-Loop.
Issues: #255, #285, #97
"""

import json
import os
import tempfile
from unittest.mock import MagicMock
import pytest

from scripts.pipeline_ingestao_ia import (
    estruturar_conteudo_com_ia,
    extrair_texto_de_arquivo,
    listar_conteudos_pendentes,
    promover_item_para_knowledge_base,
    revisar_conteudo,
    salvar_em_staging,
)


@pytest.mark.unit
def test_extrair_texto_de_arquivo():
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
        tmp.write("Conteúdo informativo sobre direitos LGBTQIA+.")
        tmp_path = tmp.name

    try:
        texto = extrair_texto_de_arquivo(tmp_path)
        assert texto == "Conteúdo informativo sobre direitos LGBTQIA+."
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@pytest.mark.unit
def test_estruturar_conteudo_com_ia_fallback():
    # Sem cliente Gemini fornecido, deve cair no fallback seguro e estruturado
    itens = estruturar_conteudo_com_ia(
        texto_fonte="Decisão histórica do STF sobre retificação de prenome e gênero.",
        fonte_referencia="STF ADI 4275",
        cliente_gemini=None,
    )
    assert len(itens) == 1
    item = itens[0]
    assert "pergunta_usuario" in item
    assert "resposta_vox" in item
    assert item["fonte_original"] == "STF ADI 4275"
    assert "tags" in item


@pytest.mark.unit
def test_estruturar_conteudo_com_ia_mock_gemini():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps([
        {
            "pergunta_usuario": "Como retificar o prenome no cartório?",
            "resposta_vox": "Pelo Provimento 73/CNJ e decisão do STF, não é necessária cirurgia.",
            "topico": "Retificação de Registro",
            "eixo_tematico": "Direitos e Cidadania",
            "tags": ["cartorio", "nome", "stf"],
            "data_referencia": "2026-11-07",
        }
    ])
    mock_client.models.generate_content.return_value = mock_resp

    itens = estruturar_conteudo_com_ia(
        texto_fonte="Texto qualquer de entrada",
        fonte_referencia="https://cnj.jus.br/provimento-73",
        cliente_gemini=mock_client,
    )

    assert len(itens) == 1
    item = itens[0]
    assert item["topico"] == "Retificação de Registro"
    assert item["fonte_original"] == "https://cnj.jus.br/provimento-73"
    assert "cartorio" in item["tags"]


@pytest.mark.unit
def test_salvar_em_staging_com_mock_supabase():
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value.execute.return_value.data = [{"id": 101, "status": "PENDING_REVIEW"}]

    itens = [
        {
            "pergunta_usuario": "Qual é a lei do nome social?",
            "resposta_vox": "O Decreto 8.727/2016 rege o nome social na administração pública federal.",
            "tags": ["nome social", "decreto"],
            "fonte_original": "Decreto 8727",
        }
    ]

    resultado = salvar_em_staging(itens, supabase_client=mock_supabase)
    assert len(resultado) == 1
    assert resultado[0]["status"] == "PENDING_REVIEW"
    mock_supabase.table.assert_called_with("conteudo_pendente")
    args, _ = mock_table.insert.call_args
    assert args[0][0]["status"] == "PENDING_REVIEW"
    assert args[0][0]["pergunta_usuario"] == "Qual é a lei do nome social?"


@pytest.mark.unit
def test_listar_conteudos_pendentes_mock():
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_query = MagicMock()
    mock_table.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.execute.return_value.data = [
        {"id": 1, "pergunta_usuario": "Dúvida 1", "status": "PENDING_REVIEW"},
        {"id": 2, "pergunta_usuario": "Dúvida 2", "status": "PENDING_REVIEW"},
    ]

    pendentes = listar_conteudos_pendentes(supabase_client=mock_supabase)
    assert len(pendentes) == 2
    mock_table.select.assert_called_with("*")
    mock_query.eq.assert_called_with("status", "PENDING_REVIEW")


@pytest.mark.unit
def test_revisar_conteudo_aprovacao_e_rejeicao():
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_query = MagicMock()
    mock_table.update.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.execute.return_value.data = [{"id": 42, "status": "APPROVED", "revisado_por": "curador_1"}]

    # Caso aprovado
    res_appr = revisar_conteudo(
        item_id=42,
        decisao="APPROVED",
        notas="Informação checada",
        revisor="curador_1",
        supabase_client=mock_supabase,
    )
    assert res_appr["status"] == "APPROVED"
    assert res_appr["revisado_por"] == "curador_1"

    # Caso status inválido
    with pytest.raises(ValueError, match="A decisão deve ser 'APPROVED' ou 'REJECTED'"):
        revisar_conteudo(item_id=42, decisao="INVALID_STATUS")


@pytest.mark.unit
def test_promover_item_para_knowledge_base():
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value.execute.return_value.data = [{"kb_id": "vox-kb-1234", "ativo": True}]

    mock_gemini = MagicMock()
    mock_embed = MagicMock()
    mock_embed.embeddings = [MagicMock(values=[0.05] * 1536)]
    mock_gemini.models.embed_content.return_value = mock_embed

    # Item aprovado com id existente no staging
    item_aprovado = {
        "id": 10,
        "pergunta_usuario": "Quais os direitos no SUS?",
        "resposta_vox": "O processo transexualizador é garantido por portaria ministerial.",
        "tags": ["sus", "saude"],
        "fonte_original": "Portaria 2803/2013",
        "status": "APPROVED",
        "revisado_por": "auditor_clinico",
    }

    kb_item = promover_item_para_knowledge_base(
        item_staging=item_aprovado,
        topico="Saúde Trans no SUS",
        eixo_tematico="Saúde",
        supabase_client=mock_supabase,
        gemini_client=mock_gemini,
    )

    assert kb_item["kb_id"] == "vox-kb-1234"
    # Verifica inserção na knowledge_base e atualização no staging
    mock_supabase.table.assert_any_call("knowledge_base")
    mock_supabase.table.assert_any_call("conteudo_pendente")
    mock_table.update.assert_called()

    # Item não aprovado deve gerar erro
    item_pendente = dict(item_aprovado, status="PENDING_REVIEW")
    with pytest.raises(ValueError, match="Apenas itens com status 'APPROVED'"):
        promover_item_para_knowledge_base(item_pendente)


@pytest.mark.unit
def test_promover_item_preserva_topico_e_eixo_de_staging():
    mock_db = MagicMock()
    mock_db.table.return_value.insert.return_value.execute.return_value.data = [
        {"kb_id": "vox-kb-5555", "topico": "Terapia Hormonal Trans", "eixo_tematico": "Saúde Integral"}
    ]
    mock_gemini = MagicMock()
    mock_gemini.models.embed_content.return_value.embeddings = [MagicMock(values=[0.1] * 1536)]

    item_aprovado = {
        "id": 11,
        "pergunta_usuario": "Qual é a dosagem de hormônio?",
        "resposta_vox": "Acompanhamento médico contínuo é necessário.",
        "topico": "Terapia Hormonal Trans",
        "eixo_tematico": "Saúde Integral",
        "status": "APPROVED",
    }
    # Sem passar topico nem eixo na chamada, deve herdar do item_staging
    promovido = promover_item_para_knowledge_base(
        item_aprovado,
        supabase_client=mock_db,
        gemini_client=mock_gemini,
    )
    assert promovido["topico"] == "Terapia Hormonal Trans"
    assert promovido["eixo_tematico"] == "Saúde Integral"
    # Verifica que o insert enviou os campos preservados
    args, _ = mock_db.table.return_value.insert.call_args
    assert args[0]["topico"] == "Terapia Hormonal Trans"
    assert args[0]["eixo_tematico"] == "Saúde Integral"


@pytest.mark.unit
def test_estruturar_conteudo_com_ia_markdown_fences():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    # Simula resposta envolvida em ```json ... ```
    mock_resp.text = """```json
[
  {
    "pergunta_usuario": "Dúvida teste?",
    "resposta_vox": "Resposta teste com markdown.",
    "topico": "Geral",
    "eixo_tematico": "Geral",
    "tags": ["teste"]
  }
]
```"""
    mock_client.models.generate_content.return_value = mock_resp

    itens = estruturar_conteudo_com_ia("Texto", "Fonte", cliente_gemini=mock_client)
    assert len(itens) == 1
    assert itens[0]["pergunta_usuario"] == "Dúvida teste?"


@pytest.mark.unit
def test_estruturar_conteudo_com_ia_objeto_unico():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    # Simula resposta retornando um objeto único em vez de lista
    mock_resp.text = json.dumps({
        "pergunta_usuario": "Dúvida em objeto único?",
        "resposta_vox": "Resposta válida.",
        "topico": "Geral",
        "eixo_tematico": "Geral",
        "tags": ["unico"]
    })
    mock_client.models.generate_content.return_value = mock_resp

    itens = estruturar_conteudo_com_ia("Texto", "Fonte", cliente_gemini=mock_client)
    assert isinstance(itens, list)
    assert len(itens) == 1
    assert itens[0]["pergunta_usuario"] == "Dúvida em objeto único?"


@pytest.mark.unit
def test_estruturar_conteudo_com_ia_preambulo_conversacional():
    mock_client = MagicMock()
    mock_resp = MagicMock()
    # Simula modelo retornando preâmbulo e postâmbulo fora do bloco json
    mock_resp.text = (
        "Olá, aqui está o JSON estruturado para o Vox AI:\n\n"
        "```json\n"
        '[{"pergunta_usuario": "Como funciona o nome social?", "resposta_vox": "Garantido por decreto."}]\n'
        "```\n\n"
        "Qualquer dúvida estou à disposição!"
    )
    mock_client.models.generate_content.return_value = mock_resp

    itens = estruturar_conteudo_com_ia("Texto sobre nome social", "Decreto", cliente_gemini=mock_client)
    assert len(itens) == 1
    assert itens[0]["pergunta_usuario"] == "Como funciona o nome social?"
    assert itens[0]["resposta_vox"] == "Garantido por decreto."


@pytest.mark.unit
def test_estruturar_conteudo_texto_vazio():
    assert estruturar_conteudo_com_ia("", "Fonte") == []
    assert estruturar_conteudo_com_ia("   \n\t  ", "Fonte") == []


@pytest.mark.unit
def test_extrair_texto_de_arquivo_inexistente_e_vazio():
    with pytest.raises(FileNotFoundError, match="Arquivo não encontrado"):
        extrair_texto_de_arquivo("/tmp/arquivo_totalmente_inexistente_vox_xyz.txt")

    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
        tmp.write("   \n\t")
        tmp_vazio = tmp.name

    try:
        with pytest.raises(ValueError, match="está vazio"):
            extrair_texto_de_arquivo(tmp_vazio)
    finally:
        if os.path.exists(tmp_vazio):
            os.remove(tmp_vazio)


@pytest.mark.unit
def test_salvar_em_staging_lista_vazia():
    mock_db = MagicMock()
    resultado = salvar_em_staging([], supabase_client=mock_db)
    assert resultado == []
    # Não deve tentar executar insert([]) no Supabase
    assert not mock_db.table.called


@pytest.mark.unit
def test_revisar_conteudo_item_inexistente_no_banco():
    mock_db = MagicMock()
    mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []

    with pytest.raises(ValueError, match="Item com ID 99999 não encontrado"):
        revisar_conteudo(99999, "APPROVED", supabase_client=mock_db)

