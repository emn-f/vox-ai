import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def set_dummy_env_vars():
    """
    Define variáveis de ambiente fictícias para evitar erros de 'chave faltando'
    antes mesmo de chegar nos mocks de cliente.
    """
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
def mock_supabase_global():
    """
    Mock global para o cliente Supabase.
    Intercepta qualquer chamada a 'supabase.create_client'.
    """
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
def mock_gemini_global():
    """
    Mock global para o Google Generative AI (Gemini).
    Intercepta 'google.generativeai' para evitar chamadas reais à API.
    """
    with patch("google.generativeai.configure") as mock_config, patch(
        "google.generativeai.GenerativeModel"
    ) as mock_model_cls, patch("google.generativeai.list_models") as mock_list, patch(
        "google.generativeai.embed_content"
    ) as mock_embed:

        # Mock do modelo e resposta
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.text = "Mocked AI Response [PASS]"
        mock_instance.generate_content.return_value = mock_response

        # Mock de list_models
        mock_list_models = [
            MagicMock(
                name="models/gemini-pro",
                supported_generation_methods=["generateContent"],
            ),
            MagicMock(
                name="models/gemini-1.5-flash",
                supported_generation_methods=["generateContent"],
            ),
        ]
        # Atribuir o nome como string para simular o objeto real do SDK
        mock_list_models[0].name = "models/gemini-pro"
        mock_list_models[1].name = "models/gemini-1.5-flash"

        mock_list.return_value = mock_list_models

        # Mock de embed_content
        mock_embed.return_value = {"embedding": [0.1] * 768}

        yield {
            "config": mock_config,
            "model_class": mock_model_cls,
            "model_instance": mock_instance,
            "list_models": mock_list,
            "embed_content": mock_embed,
        }
