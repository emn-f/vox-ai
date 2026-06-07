import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def set_dummy_env_vars(request):
    """
    Define variáveis de ambiente fictícias para evitar erros de 'chave faltando'
    antes mesmo de chegar nos mocks de cliente.
    Não aplica o patch se o teste for de integração real.
    """
    if "integration" in request.node.keywords or "tests/integration" in str(request.node.fspath):
        yield
        return

    with patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "https://mock.supabase.co",
            "SUPABASE_KEY": "mock-key",
            "SUPABASE_KEY_PROD": "mock-prod-key",
            "SUPABASE_KEY_TEST": "mock-test-key",
            "GEMINI_API_KEY": "mock-gemini-key",
            "GEMINI_API_KEY_TEST": "mock-gemini-test-key",
            "TOKEN_DEPLOY_VOX": "mock-github-token",
        },
    ):
        yield


@pytest.fixture(autouse=True)
def mock_supabase_global(request):
    """
    Mock global para o cliente Supabase.
    Intercepta qualquer chamada a 'supabase.create_client'.
    Não aplica o mock se o teste for de integração real.
    """
    if "integration" in request.node.keywords or "tests/integration" in str(request.node.fspath):
        yield
        return

    with patch("supabase.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client

        # Mock básico para operações comuns (insert, select, rpc)
        mock_execute = MagicMock()
        mock_execute.data = [{"id": "mock_id", "status": "success"}]

        # Encadeamento padrão: table -> operation -> execute
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            mock_execute
        )
        mock_client.table.return_value.select.return_value.execute.return_value = (
            mock_execute
        )
        mock_client.table.return_value.update.return_value.execute.return_value = (
            mock_execute
        )
        mock_client.table.return_value.delete.return_value.execute.return_value = (
            mock_execute
        )

        # Mock para RPC
        mock_client.rpc.return_value.execute.return_value = mock_execute

        yield mock_client


@pytest.fixture(autouse=True)
def mock_gemini_global(request):
    """
    Mock global para o Google Gen AI (Gemini - Novo SDK).
    Intercepta 'google.genai.Client' para evitar chamadas reais à API.
    Não aplica o mock se o teste for de integração real.
    """
    if "integration" in request.node.keywords or "tests/integration" in str(request.node.fspath):
        yield
        return

    # Porém, aqui vamos mockar a CLASSE Client.
    with patch("google.genai.Client") as mock_client_cls:

        # Instância do cliente mockado
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Mock de models.generate_content
        mock_response = MagicMock()
        mock_response.text = "Mocked AI Response [PASS]"

        # Hierarquia: client.models.generate_content(...)
        mock_client.models.generate_content.return_value = mock_response

        # Mock de chats.create(...)
        mock_chat = MagicMock()
        mock_client.chats.create.return_value = mock_chat
        mock_chat.send_message_stream.return_value = [
            MagicMock(text="Mocked Stream Chunk 1"),
            MagicMock(text="Mocked Stream Chunk 2"),
        ]

        yield {
            "client_cls": mock_client_cls,
            "client_instance": mock_client,
            "models": mock_client.models,
            "chats": mock_client.chats,
        }
