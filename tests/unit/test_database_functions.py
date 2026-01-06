import pytest
from unittest.mock import MagicMock, patch
from src.core.database import (
    salvar_sessao,
    salvar_log_chat,
    salvar_erro,
    salvar_report,
    get_categorias_erro,
    add_conhecimento_db,
    buscar_referencias_db,
    buscar_chunks_por_topico,
    recuperar_contexto_inteligente,
)


@pytest.fixture
def mock_db_client():
    """
    Mocka o cliente do database para todas as funções, simulando o cliente supabase.
    """
    with patch("src.core.database.get_db_client") as mock_get:
        mock_client = MagicMock()
        mock_get.return_value = mock_client

        mock_execute_return = MagicMock()
        mock_execute_return.data = [{"id": "mock_id", "chat_id": 123}]

        mock_client.table.return_value.insert.return_value.execute.return_value = (
            mock_execute_return
        )
        mock_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = (
            mock_execute_return
        )
        mock_client.table.return_value.select.return_value.execute.return_value = (
            mock_execute_return
        )
        mock_client.rpc.return_value.execute.return_value = mock_execute_return

        yield mock_client


# ==========================================
# 1. Testes de Salvamento (Inserts)
# ==========================================


def test_salvar_sessao(mock_db_client):
    salvar_sessao("sessao-123")
    mock_db_client.table.assert_called_with("sessions")
    mock_db_client.table("sessions").insert.assert_called_with(
        {"session_id": "sessao-123"}
    )


def test_salvar_erro(mock_db_client):
    err_id = salvar_erro("sessao-123", "v1", "Erro Teste")

    assert err_id != "N/A"
    assert err_id != "ERRO-DB"
    mock_db_client.table.assert_called_with("error_logs")
    args, _ = mock_db_client.table("error_logs").insert.call_args
    assert args[0]["error_message"] == "Erro Teste"


def test_salvar_report(mock_db_client):
    sucesso = salvar_report("sessao-1", "v1", "historico", 1, "comentario")

    assert sucesso is True
    mock_db_client.table.assert_called_with("user_reports")
    mock_db_client.table("user_reports").insert.assert_called()


def test_add_conhecimento_db(mock_db_client):
    # Precisamos mockar o genai.embed_content também, pois o add_conhecimento chama ele
    with patch("src.core.database.genai.embed_content") as mock_embed:
        mock_embed.return_value = {"embedding": [0.1] * 768}

        sucesso = add_conhecimento_db("Tema", "Desc", "Ref", "Autor")

        assert sucesso is True
        mock_db_client.table.assert_called_with("knowledge_base")
        mock_db_client.table("knowledge_base").insert.assert_called()


# ==========================================
# 2. Testes de Busca (Selects/RPC)
# ==========================================


def test_get_categorias_erro(mock_db_client):
    mock_retorno = MagicMock()
    mock_retorno.data = [{"id": 1, "label": "Teste"}]
    mock_db_client.table("report_categories").select().execute.return_value = (
        mock_retorno
    )

    cats = get_categorias_erro()

    assert isinstance(cats, list)
    assert len(cats) == 1
    assert cats[0]["label"] == "Teste"


def test_buscar_referencias_db(mock_db_client):
    vetor = [0.1] * 768

    res = buscar_referencias_db(vetor)

    mock_db_client.rpc.assert_called_with(
        "match_knowledge_base",
        {
            "query_embedding": vetor,
            "match_threshold": 0.5,
            "match_count": 10,
            "filter_topic": None,
        },
    )
    assert res is not None


def test_buscar_chunks_por_topico(mock_db_client):
    res = buscar_chunks_por_topico("Topico Teste")

    mock_db_client.table.assert_called_with("knowledge_base")
    # Devido à complexidade dos mocks encadeados, verificamos apenas se não quebrou e se retornou a lista mockada
    assert isinstance(res, list)


# ==========================================
# 3. Teste de Lógica Complexa (RAG)
# ==========================================


def test_recuperar_contexto_inteligente(mock_db_client):
    """
    Testa a lógica de recuperação de contexto.
    Depende internamente de buscar_referencias_db e buscar_chunks_por_topico.
    """

    # 1. Simula retorno inicial da busca vetorial (buscar_referencias_db)
    mock_docs_iniciais = MagicMock()
    # Cria lista de matches falsos
    # Para ativar a "Estratégia Mista", retornamos tópicos variados (menos de 3 votos no mesmo)
    mock_docs_iniciais.data = [
        {
            "kb_id": "vox-kb-0001",
            "descricao": "Desc A",
            "topico": "A",
            "similarity": 0.9,
        },
        {
            "kb_id": "vox-kb-0002",
            "descricao": "Desc B",
            "topico": "B",
            "similarity": 0.8,
        },
    ]
    # O mock do RPC deve retornar isso
    mock_db_client.rpc.return_value.execute.return_value = mock_docs_iniciais

    vetor = [0.1] * 768
    contexto, fonte, ids = recuperar_contexto_inteligente(vetor)

    assert "Desc A" in contexto
    assert "Desc B" in contexto
    assert "Tópicos mistos" in fonte
    assert len(ids) == 2
