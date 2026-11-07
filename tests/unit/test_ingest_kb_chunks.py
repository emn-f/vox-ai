import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.ingest_kb_chunks import (
    carregar_chunks_json,
    executar_ingestao,
    gerar_embedding_chunk,
    ingerir_chunk,
    main,
    verificar_registro_existente,
)

pytestmark = pytest.mark.unit


def test_carregar_chunks_json_diretorio(tmp_path: Path):
    d1 = tmp_path / "sub"
    d1.mkdir()
    f1 = d1 / "arquivo1.json"
    f1.write_text(
        json.dumps(
            [
                {"topico": "Tópico 1", "descricao": "Desc 1", "tags": ["a"]},
                {"topico": "Tópico 2", "descricao": "Desc 2"},
            ]
        ),
        encoding="utf-8",
    )

    chunks = carregar_chunks_json(d1)
    assert len(chunks) == 2
    assert chunks[0]["topico"] == "Tópico 1"
    assert chunks[0]["_origem_arquivo"] == "arquivo1.json"


def test_carregar_chunks_json_arquivo_unico(tmp_path: Path):
    f = tmp_path / "unico.json"
    f.write_text(
        json.dumps([{"topico": "Tópico Único", "descricao": "Desc"}]),
        encoding="utf-8",
    )

    chunks = carregar_chunks_json(f)
    assert len(chunks) == 1
    assert chunks[0]["topico"] == "Tópico Único"


def test_carregar_chunks_json_caminho_invalido(tmp_path: Path):
    chunks = carregar_chunks_json(tmp_path / "nao_existe.json")
    assert chunks == []


def test_gerar_embedding_chunk_mock_local():
    vetor = gerar_embedding_chunk("Texto de teste", mock_local=True)
    assert vetor is not None
    assert len(vetor) == 1536
    assert isinstance(vetor[0], float)


def test_gerar_embedding_chunk_gemini_sucesso():
    mock_client = MagicMock()
    mock_embedding = MagicMock()
    mock_embedding.values = [0.05] * 1536
    mock_client.models.embed_content.return_value.embeddings = [mock_embedding]

    vetor = gerar_embedding_chunk("Texto de teste", client_gemini=mock_client)
    assert vetor is not None
    assert len(vetor) == 1536
    assert vetor[0] == 0.05


def test_gerar_embedding_chunk_gemini_falha():
    mock_client = MagicMock()
    mock_client.models.embed_content.side_effect = Exception("API indisponível")

    vetor = gerar_embedding_chunk("Texto", client_gemini=mock_client)
    assert vetor is None


def test_verificar_registro_existente_encontrado():
    mock_db = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"kb_id": "vox-kb-0001", "topico": "Topico Teste", "embedding": [0.1] * 1536}]
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_resp
    )

    registro = verificar_registro_existente(mock_db, "Topico Teste")
    assert registro is not None
    assert registro["kb_id"] == "vox-kb-0001"


def test_verificar_registro_existente_nao_encontrado():
    mock_db = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = []
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_resp
    )

    registro = verificar_registro_existente(mock_db, "Novo Topico")
    assert registro is None


def test_ingerir_chunk_dry_run():
    chunk = {"topico": "Topico Dry", "descricao": "Descricao Dry"}
    status, detalhes = ingerir_chunk(chunk, dry_run=True, local_mode=True)
    assert status == "dry_run"
    assert detalhes["tem_vetor"] is True
    assert detalhes["dim"] == 1536


def test_ingerir_chunk_erro_sem_topico():
    chunk = {"descricao": "Sem tópico"}
    status, detalhes = ingerir_chunk(chunk)
    assert status == "error"
    assert "erro" in detalhes


def test_ingerir_chunk_idempotencia_ja_existe_com_embedding():
    mock_db = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"kb_id": "vox-kb-0001", "topico": "Existe", "embedding": [0.1] * 1536}]
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_resp
    )

    chunk = {"topico": "Existe", "descricao": "Descricao"}
    status, detalhes = ingerir_chunk(chunk, supabase_client=mock_db)

    assert status == "skipped"
    assert detalhes["kb_id"] == "vox-kb-0001"
    mock_db.table("knowledge_base").insert.assert_not_called()


def test_ingerir_chunk_atualiza_embedding_nulo():
    mock_db = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"kb_id": "vox-kb-0002", "topico": "Existe Sem Embedding", "embedding": None}]
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_resp
    )

    chunk = {"topico": "Existe Sem Embedding", "descricao": "Descricao"}
    status, detalhes = ingerir_chunk(chunk, supabase_client=mock_db, local_mode=True)

    assert status == "updated_embedding"
    assert detalhes["kb_id"] == "vox-kb-0002"
    mock_db.table("knowledge_base").update.assert_called_once()


def test_ingerir_chunk_novo_insercao_sucesso():
    mock_db = MagicMock()
    mock_select = MagicMock()
    mock_select.data = []
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_select
    )

    mock_insert = MagicMock()
    mock_insert.data = [{"kb_id": "vox-kb-9999", "topico": "Topico Novo"}]
    mock_db.table.return_value.insert.return_value.execute.return_value = mock_insert

    chunk = {
        "topico": "Topico Novo",
        "eixo_tematico": "Educação",
        "descricao": "Descricao nova",
        "referencias": "Ref",
        "tags": ["tag1"],
    }
    status, detalhes = ingerir_chunk(chunk, supabase_client=mock_db, local_mode=True)

    assert status == "inserted"
    assert detalhes["kb_id"] == "vox-kb-9999"
    mock_db.table.return_value.insert.assert_called_once()


def test_executar_ingestao_fluxo_completo(tmp_path: Path):
    f = tmp_path / "dataset.json"
    f.write_text(
        json.dumps(
            [
                {"topico": "Chunk 1", "descricao": "Desc 1"},
                {"topico": "Chunk 2", "descricao": "Desc 2"},
            ]
        ),
        encoding="utf-8",
    )

    mock_db = MagicMock()
    mock_select = MagicMock()
    mock_select.data = []
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_select
    )

    mock_insert = MagicMock()
    mock_insert.data = [{"kb_id": "vox-kb-1"}]
    mock_db.table.return_value.insert.return_value.execute.return_value = mock_insert

    estatisticas = executar_ingestao(
        caminho=f,
        dry_run=False,
        local_mode=True,
        supabase_client=mock_db,
    )

    assert estatisticas["total"] == 2
    assert estatisticas["inserted"] == 2
    assert estatisticas["error"] == 0


def test_verificar_registro_existente_erro_banco():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.side_effect = Exception("Conexao recusada")

    with pytest.raises(RuntimeError) as exc_info:
        verificar_registro_existente(mock_db, "Topico Erro")

    assert "Falha na consulta ao banco de dados" in str(exc_info.value)


def test_ingerir_chunk_erro_consulta_existencia():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.side_effect = Exception("Timeout DB")

    chunk = {"topico": "Topico Falha", "descricao": "Desc"}
    status, detalhes = ingerir_chunk(chunk, supabase_client=mock_db)

    assert status == "error"
    assert "Timeout DB" in detalhes.get("erro", "")


def test_ingerir_chunk_modo_real_sem_cliente_db():
    chunk = {"topico": "Topico Sem DB", "descricao": "Desc"}
    status, detalhes = ingerir_chunk(chunk, supabase_client=None, local_mode=False)

    assert status == "error"
    assert "Cliente Supabase não configurado" in detalhes.get("erro", "")


def test_ingerir_chunk_falha_geracao_embedding_registro_nulo():
    mock_db = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"kb_id": "vox-kb-9999", "topico": "Existe Sem Embedding", "embedding": None}]
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_resp
    )

    mock_client_gemini = MagicMock()
    mock_client_gemini.models.embed_content.side_effect = Exception("Cota excedida")

    chunk = {"topico": "Existe Sem Embedding", "descricao": "Desc"}
    status, detalhes = ingerir_chunk(
        chunk,
        supabase_client=mock_db,
        client_gemini=mock_client_gemini,
        local_mode=False,
    )

    assert status == "error"
    assert "Falha ao gerar embedding" in detalhes.get("erro", "")


def test_dry_run_com_registro_existente():
    mock_db = MagicMock()
    mock_resp = MagicMock()
    mock_resp.data = [{"kb_id": "vox-kb-0042", "topico": "Topico Dry Existente", "embedding": [0.1] * 1536}]
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
        mock_resp
    )

    chunk = {"topico": "Topico Dry Existente", "descricao": "Descricao Dry"}
    status, detalhes = ingerir_chunk(
        chunk,
        supabase_client=mock_db,
        dry_run=True,
        local_mode=True,
    )

    assert status == "dry_run"
    assert detalhes["existente"] is True
    assert detalhes["kb_id"] == "vox-kb-0042"
    assert detalhes["tem_embedding_db"] is True


def test_carregar_chunks_json_ignora_itens_com_campos_vazios(tmp_path: Path):
    f = tmp_path / "vazios.json"
    f.write_text(
        json.dumps(
            [
                {"topico": "   ", "descricao": "Desc valida"},
                {"topico": "Topico valido", "descricao": "   "},
                {"topico": "Valido", "descricao": "Descricao valida"},
            ]
        ),
        encoding="utf-8",
    )

    chunks = carregar_chunks_json(f)
    assert len(chunks) == 1
    assert chunks[0]["topico"] == "Valido"


def test_main_cli_exit_code_on_errors():
    with patch("sys.argv", ["ingest_kb_chunks.py", "--path", "caminho_inexistente"]), \
         patch("scripts.ingest_kb_chunks.executar_ingestao", return_value={"total": 1, "error": 1}), \
         pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1

