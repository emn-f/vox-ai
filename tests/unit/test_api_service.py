import io
from unittest.mock import MagicMock, patch
import pytest

pytestmark = pytest.mark.unit

from src.api.service import VoxService
from src.api.models import ChatResponse, HealthResponse, RAGQueryResponse


@pytest.fixture
def service():
    return VoxService()


def test_ensure_session_generates_uuid_when_empty(service):
    with patch("src.api.service.salvar_sessao") as mock_salvar:
        session_id = service.ensure_session(None)
        assert session_id is not None
        assert len(session_id) > 10
        mock_salvar.assert_called_once_with(session_id)


def test_ensure_session_preserves_valid_id(service):
    with patch("src.api.service.salvar_sessao") as mock_salvar:
        custom_id = "test-custom-session-123"
        session_id = service.ensure_session(custom_id)
        assert session_id == custom_id
        mock_salvar.assert_called_once_with(custom_id)


@patch("src.api.service.salvar_log_chat")
@patch("src.api.service.gerar_resposta")
@patch("src.api.service.inicializar_chat_modelo")
@patch("src.api.service.semantica")
def test_chat_success(
    mock_semantica,
    mock_inicializar_chat,
    mock_gerar_resposta,
    mock_salvar_log,
    service,
):
    mock_semantica.return_value = (
        "Retificação",
        "Contexto de retificação",
        [{"kb_id": "kb-01", "similarity": 0.85}],
    )
    mock_gerar_resposta.return_value = "Dar esse passo é lindo! Acolhimento antes de informar."

    resp = service.chat(
        prompt="Como retificar meu nome?",
        session_id="sess-01",
        include_audio=False,
    )

    assert isinstance(resp, ChatResponse)
    assert resp.session_id == "sess-01"
    assert "Acolhimento" in resp.response
    assert resp.topic == "Retificação"
    assert len(resp.references) == 1
    assert resp.references[0].kb_id == "kb-01"
    assert resp.audio_base64 is None

    mock_salvar_log.assert_called_once()


@patch("src.api.service.texto_para_audio")
@patch("src.api.service.salvar_log_chat")
@patch("src.api.service.gerar_resposta")
@patch("src.api.service.inicializar_chat_modelo")
@patch("src.api.service.semantica")
def test_chat_with_audio(
    mock_semantica,
    mock_inicializar_chat,
    mock_gerar_resposta,
    mock_salvar_log,
    mock_texto_para_audio,
    service,
):
    mock_semantica.return_value = (None, None, None)
    mock_gerar_resposta.return_value = "Resposta com audio"
    mock_texto_para_audio.return_value = io.BytesIO(b"fake-mp3-bytes")

    resp = service.chat(
        prompt="Teste de audio",
        include_audio=True,
    )

    assert resp.audio_base64 is not None
    mock_texto_para_audio.assert_called_once_with("Resposta com audio")


@patch("src.api.service.salvar_erro")
@patch("src.api.service.salvar_log_chat")
@patch("src.api.service.gerar_resposta")
@patch("src.api.service.inicializar_chat_modelo")
@patch("src.api.service.semantica")
def test_chat_handles_quota_error(
    mock_semantica,
    mock_inicializar_chat,
    mock_gerar_resposta,
    mock_salvar_log,
    mock_salvar_erro,
    service,
):
    mock_semantica.return_value = (None, None, None)
    mock_gerar_resposta.side_effect = Exception("429 ResourceExhausted: Quota exceeded")
    mock_salvar_erro.return_value = "ERR-429"

    resp = service.chat(prompt="Olá")

    assert "limite temporário" in resp.response
    mock_salvar_erro.assert_called_once()
    mock_salvar_log.assert_called_once()


@patch("src.api.service.salvar_log_chat")
@patch("src.api.service.gerar_resposta_stream")
@patch("src.api.service.inicializar_chat_modelo")
@patch("src.api.service.semantica")
def test_chat_stream(
    mock_semantica,
    mock_inicializar_chat,
    mock_stream,
    mock_salvar_log,
    service,
):
    mock_semantica.return_value = (None, None, None)
    mock_stream.return_value = iter(["Olá, ", "tudo bem?"])

    chunks = list(service.chat_stream("Oi", session_id="stream-sess"))

    assert chunks == ["Olá, ", "tudo bem?"]
    mock_salvar_log.assert_called_once()


@patch("src.api.service.transcrever_audio")
def test_transcribe_success(mock_transcrever, service):
    mock_transcrever.return_value = "Transcrição concluída com sucesso"
    resultado = service.transcribe(b"bytes_de_audio")
    assert resultado == "Transcrição concluída com sucesso"


@patch("src.api.service.transcrever_audio")
def test_transcribe_failure_raises(mock_transcrever, service):
    mock_transcrever.return_value = None
    with pytest.raises(RuntimeError):
        service.transcribe(b"audio_corrompido")


@patch("src.api.service.semantica")
def test_rag_query(mock_semantica, service):
    mock_semantica.return_value = ("Saúde", "Texto do chunk", [{"kb_id": "kb-1"}])
    res = service.rag_query("Como funciona PEP?")
    assert isinstance(res, RAGQueryResponse)
    assert res.topic == "Saúde"
    assert res.context == "Texto do chunk"


@patch("src.api.service.salvar_report")
def test_submit_report(mock_salvar_report, service):
    mock_salvar_report.return_value = True
    ok = service.submit_report("sess-1", 1, "chat history", "comentario")
    assert ok is True
    mock_salvar_report.assert_called_once()


@patch("src.api.service.excluir_dados_sessao")
def test_delete_session(mock_excluir, service):
    mock_excluir.return_value = True
    ok = service.delete_session("sess-1")
    assert ok is True
    mock_excluir.assert_called_once_with("sess-1")


@patch("src.api.service.get_db_client")
@patch("src.api.service.configurar_api_gemini")
def test_health_check(mock_gemini, mock_db, service):
    mock_gemini.return_value = MagicMock()
    mock_db.return_value = MagicMock()

    health = service.health_check()
    assert isinstance(health, HealthResponse)
    assert health.status == "ok"
    assert health.gemini_configured is True
    assert health.supabase_configured is True


@patch("src.api.service.salvar_log_chat")
@patch("src.api.service.gerar_resposta")
@patch("src.api.service.inicializar_chat_modelo")
@patch("src.api.service.semantica")
def test_chat_with_conversation_history(
    mock_semantica,
    mock_inicializar_chat,
    mock_gerar_resposta,
    mock_salvar_log,
    service,
):
    from src.api.models import ChatMessage

    mock_semantica.return_value = (None, None, None)
    mock_gerar_resposta.return_value = "Entendido, vamos continuar."

    history = [
        ChatMessage(role="user", content="Meu nome é Maya"),
        ChatMessage(role="assistant", content="Olá Maya, muito prazer!"),
    ]

    resp = service.chat(prompt="Como retifico meus documentos?", history=history)

    assert resp.response == "Entendido, vamos continuar."
    mock_inicializar_chat.assert_called_once()
    _, kwargs = mock_inicializar_chat.call_args
    passed_history = kwargs.get("history")
    assert passed_history is not None
    assert len(passed_history) == 2
    assert passed_history[0].role == "user"
    assert passed_history[1].role == "model"


@patch("src.api.service.salvar_log_chat")
@patch("src.api.service.gerar_resposta_stream")
@patch("src.api.service.inicializar_chat_modelo")
@patch("src.api.service.semantica")
def test_chat_stream_client_disconnect_saves_partial_logs(
    mock_semantica,
    mock_inicializar_chat,
    mock_stream,
    mock_salvar_log,
    service,
):
    mock_semantica.return_value = (None, None, None)

    def stream_with_disconnect():
        yield "Primeira parte "
        yield "Segunda parte "
        raise GeneratorExit()

    mock_stream.return_value = stream_with_disconnect()

    gen = service.chat_stream("Oi", session_id="disconnect-sess")
    first = next(gen)
    assert first == "Primeira parte "

    # Simula cliente fechando conexão HTTP/SSE antes do término
    gen.close()

    mock_salvar_log.assert_called_once()
    log_args, log_kwargs = mock_salvar_log.call_args
    assert "Primeira parte" in log_kwargs.get("response", "")


@patch("src.api.service.semantica")
def test_rag_query_with_custom_threshold_and_limit(mock_semantica, service):
    mock_semantica.return_value = ("Direitos", "Texto legal", [{"kb_id": "kb-99"}])

    res = service.rag_query("Como retificar certidão?", threshold=0.75, limit=5)

    assert res.topic == "Direitos"
    mock_semantica.assert_called_once_with("Como retificar certidão?", threshold=0.75, limit=5)
