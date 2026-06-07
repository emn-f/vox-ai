import pytest
from contextlib import nullcontext
from unittest.mock import MagicMock, patch
import streamlit as st

# Exceção personalizada para capturar o st.stop() nos testes
class StopException(Exception):
    pass

@pytest.fixture
def mock_streamlit():
    """Mock de funções chaves do Streamlit utilizadas no fluxo de geração e erro."""
    with patch("streamlit.spinner", return_value=nullcontext()), \
         patch("streamlit.empty") as mock_empty, \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.stop", side_effect=StopException) as mock_stop:
        st.session_state["session_id"] = "test-session-id"
        st.session_state["git_version_str"] = "test-git-version"
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        yield {"empty": mock_empty, "placeholder": mock_placeholder, "error": mock_error, "stop": mock_stop}
            "empty": mock_empty,
            "placeholder": mock_placeholder,
            "error": mock_error,
            "stop": mock_stop
        }

@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_gerar_resposta_quota_error(mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta
    
    mock_chat = MagicMock()
    # Simula o erro de cota 429
    mock_chat.send_message_stream.side_effect = Exception("429 ResourceExhausted: Quota exceeded for model")
    mock_salvar_erro.return_value = "ERR-429"

    with pytest.raises(StopException):
        gerar_resposta(mock_chat, "Olá", "contexto")

    # Verifica se a função de salvar erro no banco foi acionada
    mock_salvar_erro.assert_called_once()
    
    # Verifica se a mensagem amigável de cota/limite foi renderizada no Streamlit
    args, kwargs = mock_streamlit["error"].call_args
    assert "limite de processamento temporário" in args[0]
    assert "ERR-429" in args[0]
    assert kwargs.get("icon") == "⚠️"

@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_gerar_resposta_service_unavailable(mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta
    
    mock_chat = MagicMock()
    # Simula o erro de serviço indisponível 503
    mock_chat.send_message_stream.side_effect = Exception("503 Service Unavailable: Overloaded")
    mock_salvar_erro.return_value = "ERR-503"

    with pytest.raises(StopException):
        gerar_resposta(mock_chat, "Olá", "contexto")

    mock_salvar_erro.assert_called_once()
    
    # Verifica se a mensagem de alta demanda/instabilidade foi renderizada no Streamlit
    args, kwargs = mock_streamlit["error"].call_args
    assert "demanda muito alta agora" in args[0]
    assert "ERR-503" in args[0]
    assert kwargs.get("icon") == "⏳"

@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
@patch("src.app.ui.exibir_mensagem_erro")
def test_gerar_resposta_general_error(mock_exibir_msg_erro, mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta
    
    mock_chat = MagicMock()
    # Simula um erro genérico desconhecido
    mock_chat.send_message_stream.side_effect = Exception("Algum erro desconhecido de rede")
    mock_salvar_erro.return_value = "ERR-999"

    with pytest.raises(StopException):
        gerar_resposta(mock_chat, "Olá", "contexto")

    mock_salvar_erro.assert_called_once()
    
    # Garante que exibiu o painel de erro comum via exibir_mensagem_erro
    mock_exibir_msg_erro.assert_called_once_with("ERR-999")
