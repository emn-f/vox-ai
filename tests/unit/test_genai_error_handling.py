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
         patch("streamlit.toast") as mock_toast, \
         patch("streamlit.stop", side_effect=StopException) as mock_stop:
        st.session_state["session_id"] = "test-session-id"
        st.session_state["git_version_str"] = "test-git-version"
        mock_placeholder = MagicMock()
        mock_empty.return_value = mock_placeholder
        yield {"empty": mock_empty, "placeholder": mock_placeholder, "error": mock_error, "stop": mock_stop, "toast": mock_toast}

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


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_fallback_success_on_second_model(mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta

    mock_chat = MagicMock()
    chunk1 = MagicMock(text="Resposta do ")
    chunk2 = MagicMock(text="modelo de fallback")
    mock_chat.send_message_stream.side_effect = [
        Exception("429 ResourceExhausted: Quota exceeded for model"),
        [chunk1, chunk2],
    ]

    resposta = gerar_resposta(mock_chat, "Olá", "contexto")

    assert resposta == "Resposta do modelo de fallback"
    assert mock_chat.send_message_stream.call_count == 2
    mock_salvar_erro.assert_not_called()
    mock_streamlit["error"].assert_not_called()
    mock_streamlit["toast"].assert_called_once()


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_fallback_cascade_three_models_success_on_third(mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta

    mock_chat = MagicMock()
    chunk = MagicMock(text="Sucesso no terceiro modelo")
    mock_chat.send_message_stream.side_effect = [
        Exception("503 Service Unavailable: Overloaded"),
        Exception("Connection timeout while contacting API"),
        [chunk],
    ]

    resposta = gerar_resposta(mock_chat, "Olá", "contexto")

    assert resposta == "Sucesso no terceiro modelo"
    assert mock_chat.send_message_stream.call_count == 3
    mock_salvar_erro.assert_not_called()
    mock_streamlit["error"].assert_not_called()
    assert mock_streamlit["toast"].call_count == 2


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_safety_block_does_not_trigger_fallback(mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta

    mock_chat = MagicMock()
    mock_chat.send_message_stream.side_effect = Exception("Prompt blocked by safety policy violation")
    mock_salvar_erro.return_value = "ERR-SAFETY"

    with pytest.raises(StopException):
        gerar_resposta(mock_chat, "Pergunta sensível", "contexto")

    # Garante que não tentou fallback para os outros modelos (apenas 1 chamada)
    assert mock_chat.send_message_stream.call_count == 1
    mock_salvar_erro.assert_called_once()
    args, kwargs = mock_streamlit["error"].call_args
    assert "diretrizes de proteção" in args[0]
    assert "ERR-SAFETY" in args[0]
    assert kwargs.get("icon") == "🚫"


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_all_fallback_models_fail_calls_salvar_erro_once(mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta
    from src.config import GEMINI_FALLBACK_MODELS

    mock_chat = MagicMock()
    mock_chat.send_message_stream.side_effect = Exception("429 ResourceExhausted")
    mock_salvar_erro.return_value = "ERR-429-ALL"

    with pytest.raises(StopException):
        gerar_resposta(mock_chat, "Olá", "contexto")

    # Garante que tentou cada modelo da lista exatamente uma vez
    assert mock_chat.send_message_stream.call_count == len(GEMINI_FALLBACK_MODELS)
    mock_salvar_erro.assert_called_once()


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_headless_execution_returns_empty_string_when_all_fail(mock_salvar_erro):
    from src.core.genai import gerar_resposta

    mock_chat = MagicMock()
    mock_chat.send_message_stream.side_effect = Exception("503 Service Unavailable")
    mock_salvar_erro.return_value = "ERR-503-HEADLESS"

    # Sem mock_streamlit ativo, st.stop() em modo bare não levanta exceção
    resposta = gerar_resposta(mock_chat, "Olá", "contexto")

    assert resposta == ""
    mock_salvar_erro.assert_called_once()


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_fallback_updates_chat_model_attribute(mock_salvar_erro, mock_streamlit):
    from src.core.genai import gerar_resposta

    class DummyChat:
        def __init__(self):
            self._model = "gemini-3.6-flash"
            self.calls = []

        def send_message_stream(self, prompt):
            self.calls.append(self._model)
            if self._model == "gemini-3.6-flash":
                raise Exception("429 ResourceExhausted")
            chunk = MagicMock(text="ok")
            return [chunk]

    chat = DummyChat()
    resposta = gerar_resposta(chat, "Olá", "")

    assert resposta == "ok"
    assert chat.calls == ["gemini-3.6-flash", "gemini-3.5-flash"]
    assert chat._model == "gemini-3.5-flash"


@pytest.mark.unit
@patch("src.core.genai.inicializar_chat_modelo")
def test_gerar_resposta_initializes_chat_if_none(mock_inicializar, mock_streamlit):
    from src.core.genai import gerar_resposta

    mock_chat = MagicMock()
    mock_chat.send_message_stream.return_value = [MagicMock(text="Resposta automática")]
    mock_inicializar.return_value = mock_chat

    resposta = gerar_resposta(None, "Olá", "")

    assert resposta == "Resposta automática"
    mock_inicializar.assert_called_once()


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_rate_limit_with_blocked_keyword_still_triggers_fallback(mock_salvar_erro, mock_streamlit):
    """
    Garante que erros de cota (429) contendo a palavra 'blocked' (ex: IP temporariamente bloqueado)
    acionam o fallback normalmente e não são falsamente confundidos com violação de diretrizes de segurança.
    """
    from src.core.genai import gerar_resposta

    mock_chat = MagicMock()
    chunk = MagicMock(text="Resposta do segundo modelo")
    # Simula erro de rate limit contendo termo 'blocked'
    mock_chat.send_message_stream.side_effect = [
        Exception("429 Rate limit exceeded. Requests are temporarily blocked for 60 seconds."),
        [chunk],
    ]

    resposta = gerar_resposta(mock_chat, "Pergunta normal", "contexto")

    assert resposta == "Resposta do segundo modelo"
    assert mock_chat.send_message_stream.call_count == 2
    mock_salvar_erro.assert_not_called()
    mock_streamlit["error"].assert_not_called()


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_fallback_candidate_model_not_found_404(mock_salvar_erro, mock_streamlit):
    """
    Garante que se um modelo não for encontrado ou estiver descontinuado (HTTP 404 / NOT_FOUND),
    o Vox AI aciona o fallback para o próximo modelo disponível.
    """
    from src.core.genai import gerar_resposta
    from google.genai.errors import ClientError

    mock_chat = MagicMock()
    chunk = MagicMock(text="Resposta do modelo estável")
    err_404 = ClientError(
        404,
        {"error": {"code": 404, "message": "models/gemini-3.6-flash is not found", "status": "NOT_FOUND"}},
    )
    mock_chat.send_message_stream.side_effect = [
        err_404,
        [chunk],
    ]

    resposta = gerar_resposta(mock_chat, "Olá", "")

    assert resposta == "Resposta do modelo estável"
    assert mock_chat.send_message_stream.call_count == 2
    mock_salvar_erro.assert_not_called()


@pytest.mark.unit
@patch("src.core.db.logs.salvar_erro")
def test_mid_stream_error_does_not_trigger_fallback_and_handles_error(mock_salvar_erro, mock_streamlit):
    """
    Garante que se ocorrer uma falha no meio do streaming (após tokens já terem sido emitidos),
    o fallback NÃO é acionado para evitar duplicar ou corromper a resposta no frontend, e o erro é tratado.
    """
    from src.core.genai import gerar_resposta_stream

    mock_chat = MagicMock()
    mock_salvar_erro.return_value = "ERR-MIDSTREAM"

    def faulty_stream(*args, **kwargs):
        yield MagicMock(text="Início da resposta...")
        raise Exception("503 Service Unavailable: Connection dropped during streaming")

    mock_chat.send_message_stream.side_effect = faulty_stream

    gen = gerar_resposta_stream(mock_chat, "Olá", "")
    primeiro_chunk = next(gen)
    assert primeiro_chunk == "Início da resposta..."

    # Ao continuar o gerador, deve tratar o erro e interromper via st.stop()
    with pytest.raises(StopException):
        next(gen)

    # Não deve ter tentado modelo de fallback (call_count deve permanecer 1)
    assert mock_chat.send_message_stream.call_count == 1
    mock_salvar_erro.assert_called_once()
    mock_streamlit["error"].assert_called_once()


@pytest.mark.unit
def test_obter_lista_modelos_fallback_deduplication():
    """
    Valida se _obter_lista_modelos_fallback remove duplicatas preservando a ordem de prioridade.
    """
    from src.core.genai import _obter_lista_modelos_fallback

    mock_chat = MagicMock()
    mock_chat._model = "gemini-3.1-flash-lite"

    with patch("src.core.genai.GEMINI_FALLBACK_MODELS", ["gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-3.6-flash"]):
        modelos = _obter_lista_modelos_fallback(mock_chat)
        assert modelos == ["gemini-3.1-flash-lite", "gemini-3.6-flash", "gemini-2.5-flash"]

