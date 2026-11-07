"""
Testes unitários para o módulo de auditoria, limpeza e diagnóstico da KB.
Issues: #285, #306, #307, #308, #331
"""

import json
import os
import tempfile
import numpy as np
import pandas as pd
import pytest

from scripts.audit_kb import (
    AuditoriaFlashcard,
    buscar_vizinhos_similares,
    calcular_similaridade_cosseno,
    carregar_dados_kb,
    converter_para_vetor_numpy,
    detectar_anomalias,
    diagnosticar_distribuicao_tematica,
    diagnosticar_evolucao_temporal,
    diagnosticar_frequencia_tags,
    gerar_grafico_barras_ascii,
    limpar_base_conhecimento,
)


@pytest.mark.unit
def test_carregar_dados_kb_mock():
    mock_data = [
        {"kb_id": "item-1", "topico": "T1", "eixo_tematico": "E1", "descricao": "Desc 1"},
        {"kb_id": "item-2", "topico": "T2", "eixo_tematico": "E2", "descricao": "Desc 2"},
    ]
    df = carregar_dados_kb(dados_mock=mock_data)
    assert len(df) == 2
    assert "kb_id" in df.columns
    assert df.iloc[0]["kb_id"] == "item-1"


@pytest.mark.unit
def test_detectar_anomalias_identifica_placeholders_e_faltas():
    dados = [
        {
            "kb_id": "vox-kb-0000",
            "topico": "N/A",
            "eixo_tematico": "N/A",
            "descricao": "Texto curto",
            "tags": [],
            "embedding": None,
        },
        {
            "kb_id": "vox-kb-0001",
            "topico": "Direito",
            "eixo_tematico": "Cidadania",
            "descricao": "Descrição suficientemente longa para passar no filtro de tamanho mínimo.",
            "tags": ["direito", "stf"],
            "embedding": [0.1] * 10,
        },
    ]
    df = pd.DataFrame(dados)
    anomalias = detectar_anomalias(df, limite_caracteres_descricao=20)

    assert len(anomalias) == 1
    assert anomalias.iloc[0]["kb_id"] == "vox-kb-0000"
    motivos = anomalias.iloc[0]["motivos_anomalia"]
    assert "topico_invalido_ou_placeholder" in motivos
    assert "eixo_invalido_ou_placeholder" in motivos
    assert "descricao_muito_curta_ou_vazia" in motivos
    assert "tags_ausentes" in motivos
    assert "embedding_nulo" in motivos


@pytest.mark.unit
def test_limpar_base_conhecimento():
    dados = [
        {
            "kb_id": "vox-kb-0000",
            "topico": "N/A",
            "eixo_tematico": "N/A",
            "descricao": "Texto válido de descrição para o registro da base",
            "referencias": "N/A",
            "tags": "{tag1, tag2}",
        },
        {
            "kb_id": "vox-kb-0001",
            "topico": "Saúde",
            "eixo_tematico": "SUS",
            "descricao": "",  # Vazia, deve ser removida
            "referencias": "Portaria",
            "tags": "['saude', 'sus']",
        },
    ]
    df = pd.DataFrame(dados)
    df_limpo = limpar_base_conhecimento(df, substituir_na=True, remover_sem_descricao=True)

    assert len(df_limpo) == 1
    assert df_limpo.iloc[0]["kb_id"] == "vox-kb-0000"
    assert df_limpo.iloc[0]["topico"] == "Tópico Geral"
    assert df_limpo.iloc[0]["eixo_tematico"] == "Geral"
    assert df_limpo.iloc[0]["referencias"] == "Não especificada"
    assert df_limpo.iloc[0]["tags"] == ["tag1", "tag2"]


@pytest.mark.unit
def test_converter_para_vetor_numpy():
    # Caso 1: Lista nativa
    v1 = converter_para_vetor_numpy([0.1, 0.2, 0.3])
    assert isinstance(v1, np.ndarray)
    assert np.allclose(v1, [0.1, 0.2, 0.3])

    # Caso 2: String JSON
    v2 = converter_para_vetor_numpy("[0.5, -0.5]")
    assert isinstance(v2, np.ndarray)
    assert np.allclose(v2, [0.5, -0.5])

    # Caso 3: String separada por vírgula
    v3 = converter_para_vetor_numpy("[ 1.2, 3.4 , 5.6 ]")
    assert isinstance(v3, np.ndarray)
    assert np.allclose(v3, [1.2, 3.4, 5.6])

    # Caso 4: Valores inválidos ou nulos
    assert converter_para_vetor_numpy(None) is None
    assert converter_para_vetor_numpy("null") is None
    assert converter_para_vetor_numpy("[]") is None
    assert converter_para_vetor_numpy(float("nan")) is None


@pytest.mark.unit
def test_calcular_similaridade_cosseno():
    # Vetores idênticos
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    assert pytest.approx(calcular_similaridade_cosseno(v1, v2), 0.0001) == 1.0

    # Vetores ortogonais
    v3 = np.array([0.0, 1.0, 0.0])
    assert pytest.approx(calcular_similaridade_cosseno(v1, v3), 0.0001) == 0.0

    # Vetores opostos
    v4 = np.array([-1.0, 0.0, 0.0])
    assert pytest.approx(calcular_similaridade_cosseno(v1, v4), 0.0001) == -1.0

    # Vetor nulo
    v_zero = np.array([0.0, 0.0, 0.0])
    assert calcular_similaridade_cosseno(v1, v_zero) == 0.0

    # Dimensões incompatíveis
    v_diff = np.array([1.0, 2.0])
    with pytest.raises(ValueError):
        calcular_similaridade_cosseno(v1, v_diff)


@pytest.mark.unit
def test_buscar_vizinhos_similares():
    dados = [
        {"kb_id": "doc1", "topico": "T1", "embedding": [1.0, 0.0]},
        {"kb_id": "doc2", "topico": "T2", "embedding": [0.8, 0.6]},
        {"kb_id": "doc3", "topico": "T3", "embedding": [0.0, 1.0]},
        {"kb_id": "doc4", "topico": "T4", "embedding": None},
    ]
    df = pd.DataFrame(dados)
    query = np.array([1.0, 0.0])

    top = buscar_vizinhos_similares(df, query, top_k=2)
    assert len(top) == 2
    assert top[0]["kb_id"] == "doc1"
    assert pytest.approx(top[0]["similarity"], 0.001) == 1.0
    assert top[1]["kb_id"] == "doc2"
    assert pytest.approx(top[1]["similarity"], 0.001) == 0.8


@pytest.mark.unit
def test_diagnostico_distribuicao_tematica_e_tags():
    dados = [
        {"eixo_tematico": "Saúde", "tags": ["sus", "vacina"], "created_at": "2024-01-15T00:00:00Z"},
        {"eixo_tematico": "Saúde", "tags": ["sus", "hormonios"], "created_at": "2024-01-20T00:00:00Z"},
        {"eixo_tematico": "Direitos", "tags": ["stf", "leis"], "created_at": "2024-02-10T00:00:00Z"},
    ]
    df = pd.DataFrame(dados)

    eixos = diagnosticar_distribuicao_tematica(df)
    assert len(eixos) == 2
    assert eixos.iloc[0]["eixo_tematico"] == "Saúde"
    assert eixos.iloc[0]["quantidade"] == 2

    tags = diagnosticar_frequencia_tags(df, top_n=5)
    assert len(tags) == 5
    # "sus" aparece duas vezes
    assert tags.iloc[0]["tag"] == "sus"
    assert tags.iloc[0]["frequencia"] == 2

    evolucao = diagnosticar_evolucao_temporal(df)
    assert len(evolucao) == 2
    assert evolucao.iloc[0]["periodo"] == "2024-01"
    assert evolucao.iloc[0]["novos_itens"] == 2
    assert evolucao.iloc[1]["acumulado"] == 3


@pytest.mark.unit
def test_gerar_grafico_barras_ascii():
    rotulos = ["Saúde", "Direito"]
    valores = [10, 5]
    chart = gerar_grafico_barras_ascii(rotulos, valores, titulo="Teste")
    assert "=== Teste ===" in chart
    assert "Saúde" in chart
    assert "(10)" in chart
    assert "Direito" in chart
    assert "(5)" in chart


@pytest.mark.unit
def test_auditoria_flashcard():
    auditor = AuditoriaFlashcard(revisor="auditor_test")
    item = {
        "kb_id": "vox-kb-9999",
        "topico": "Direito Trans",
        "eixo_tematico": "Cidadania",
        "descricao": "Texto de demonstração para o flashcard de auditoria.",
        "tags": ["stf", "direitos"],
        "embedding": [0.1, 0.2],
    }

    card = auditor.formatar_flashcard(item, numero=1, total=1)
    assert "FLASHCARD DE AUDITORIA KB" in card
    assert "vox-kb-9999" in card
    assert "Direito Trans" in card
    assert "✅ Presente" in card

    registro = auditor.auditar_item(item, decisao="APPROVED", notas="Conteúdo aprovado na íntegra")
    assert registro["decisao"] == "APPROVED"
    assert registro["revisor"] == "auditor_test"
    assert len(auditor.historico_auditoria) == 1

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        auditor.exportar_auditoria(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            salvo = json.load(f)
        assert len(salvo) == 1
        assert salvo[0]["kb_id"] == "vox-kb-9999"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@pytest.mark.unit
def test_funcoes_com_dataframe_vazio():
    df_vazio = pd.DataFrame()

    assert detectar_anomalias(df_vazio).empty
    assert limpar_base_conhecimento(df_vazio).empty
    assert diagnosticar_distribuicao_tematica(df_vazio).empty
    assert diagnosticar_frequencia_tags(df_vazio).empty
    assert diagnosticar_evolucao_temporal(df_vazio).empty
    assert buscar_vizinhos_similares(df_vazio, np.array([1.0, 2.0])) == []
    assert "Nenhum dado disponível" in gerar_grafico_barras_ascii([], [])


@pytest.mark.unit
def test_limpar_base_tags_malformadas():
    dados = [
        {"kb_id": "item-1", "descricao": "Descricao valida", "tags": None},
        {"kb_id": "item-2", "descricao": "Descricao valida", "tags": ""},
        {"kb_id": "item-3", "descricao": "Descricao valida", "tags": "{}"},
        {"kb_id": "item-4", "descricao": "Descricao valida", "tags": "invalid [ json"},
        {"kb_id": "item-5", "descricao": "Descricao valida", "tags": "[saude, sus, cnj]"},
    ]
    df = pd.DataFrame(dados)
    df_limpo = limpar_base_conhecimento(df)
    assert len(df_limpo) == 5
    # Todas as tags devem ser listas limpas
    for tags in df_limpo["tags"]:
        assert isinstance(tags, list)
    assert df_limpo.iloc[4]["tags"] == ["saude", "sus", "cnj"]


@pytest.mark.unit
def test_converter_para_vetor_numpy_postgres_array():
    v = converter_para_vetor_numpy("{0.1, 0.2, 0.3}")
    assert isinstance(v, np.ndarray)
    assert np.allclose(v, [0.1, 0.2, 0.3])

    v_espacos = converter_para_vetor_numpy(" {  0.5 , -0.5 } ")
    assert isinstance(v_espacos, np.ndarray)
    assert np.allclose(v_espacos, [0.5, -0.5])


@pytest.mark.unit
def test_converter_para_vetor_numpy_corrupted_e_vazios():
    # Lista vazia deve retornar None (vetores de 0 dimensões não são utilizáveis em RAG)
    assert converter_para_vetor_numpy([]) is None
    assert converter_para_vetor_numpy("[]") is None
    assert converter_para_vetor_numpy("{}") is None

    # Lista contendo elementos não conversíveis
    assert converter_para_vetor_numpy([0.1, "corrompido", 0.3]) is None

    # Vetores contendo NaN ou Infinito
    assert converter_para_vetor_numpy([0.1, float("nan")]) is None
    assert converter_para_vetor_numpy([0.1, float("inf")]) is None


@pytest.mark.unit
def test_calcular_similaridade_cosseno_com_nan_e_invalidos():
    v1 = np.array([1.0, 1.0], dtype=np.float32)
    v_nan = np.array([np.nan, 1.0], dtype=np.float32)
    v_inf = np.array([np.inf, 1.0], dtype=np.float32)

    # Não deve avaliar NaN para 1.0
    assert calcular_similaridade_cosseno(v1, v_nan) == 0.0
    assert calcular_similaridade_cosseno(v_nan, v1) == 0.0
    assert calcular_similaridade_cosseno(v1, v_inf) == 0.0


@pytest.mark.unit
def test_detectar_anomalias_com_dimensoes_e_embeddings_vazios():
    dados = [
        {
            "kb_id": "v-vazio",
            "topico": "Direito",
            "eixo_tematico": "Cidadania",
            "descricao": "Descrição perfeitamente válida e longa o suficiente para passar no teste.",
            "tags": ["tag1"],
            "embedding": [],  # Lista vazia
        },
        {
            "kb_id": "v-dim-errada",
            "topico": "Direito",
            "eixo_tematico": "Cidadania",
            "descricao": "Descrição perfeitamente válida e longa o suficiente para passar no teste.",
            "tags": ["tag1"],
            "embedding": [0.1] * 5,  # 5 dimensões quando esperado 768 ou 1536
        },
    ]
    df = pd.DataFrame(dados)
    anomalias = detectar_anomalias(df, dimensoes_validas=(768, 1536))
    assert len(anomalias) == 2
    assert "embedding_nulo" in anomalias.iloc[0]["motivos_anomalia"]
    assert "embedding_dimensao_invalida (5)" in anomalias.iloc[1]["motivos_anomalia"]


@pytest.mark.unit
def test_diagnosticar_evolucao_temporal_criado_em():
    dados = [
        {"criado_em": "2024-05-10T12:00:00Z"},
        {"criado_em": "2024-05-15T12:00:00Z"},
        {"criado_em": "2024-06-01T12:00:00Z"},
    ]
    df = pd.DataFrame(dados)
    evolucao = diagnosticar_evolucao_temporal(df)
    assert len(evolucao) == 2
    assert evolucao.iloc[0]["periodo"] == "2024-05"
    assert evolucao.iloc[0]["novos_itens"] == 2
    assert evolucao.iloc[0]["acumulado"] == 2
    assert evolucao.iloc[1]["acumulado"] == 3


@pytest.mark.unit
def test_buscar_vizinhos_similares_com_string_query():
    dados = [
        {"kb_id": "doc1", "embedding": [1.0, 0.0]},
        {"kb_id": "doc2", "embedding": [0.0, 1.0]},
    ]
    df = pd.DataFrame(dados)

    # Consulta como string
    top = buscar_vizinhos_similares(df, "[1.0, 0.0]", top_k=1)
    assert len(top) == 1
    assert top[0]["kb_id"] == "doc1"
    assert pytest.approx(top[0]["similarity"], 0.001) == 1.0


@pytest.mark.unit
def test_formatar_flashcard_sem_nan():
    auditor = AuditoriaFlashcard()
    item_com_nans = {
        "kb_id": "vox-123",
        "topico": None,
        "eixo_tematico": None,
        "descricao": None,
        "referencias": None,
        "tags": None,
        "embedding": None,
    }
    card = auditor.formatar_flashcard(item_com_nans)
    assert "nan" not in card.lower()
    assert "Nenhuma informada" in card
    assert "Nenhuma" in card
    assert "❌ Ausente" in card

