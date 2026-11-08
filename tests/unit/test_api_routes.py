from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.unit

from src.api.main import app
from src.api.models import ChatResponse, HealthResponse, RAGQueryResponse, ReferenceItem


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Vox AI Core Service"
    assert data["status"] == "online"
    assert "endpoints" in data


@patch("src.api.routes.VoxService.health_check")
def test_health_endpoint(mock_health, client):
    mock_health.return_value = HealthResponse(
        status="ok",
        version="v3.2.0",
        gemini_configured=True,
        supabase_configured=True,
        environment="test",
    )
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "v3.2.0"


@patch("src.api.routes.VoxService.chat")
def test_chat_endpoint_success(mock_chat, client):
    mock_chat.return_value = ChatResponse(
        session_id="test-session-123",
        response="Olá! Que bom ter você aqui. Acolhemos com respeito.",
        topic="Acolhimento",
        references=[ReferenceItem(kb_id="kb-10", similarity=0.92)],
        audio_base64=None,
    )

    payload = {
        "prompt": "Olá Vox, tudo bem?",
        "session_id": "test-session-123",
        "include_audio": False,
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session-123"
    assert "Acolhemos" in data["response"]
    assert data["topic"] == "Acolhimento"
    assert len(data["references"]) == 1


def test_chat_endpoint_validation_error(client):
    # Prompt vazio ou apenas espaços deve falhar com status 422
    response = client.post("/chat", json={"prompt": ""})
    assert response.status_code == 422
    response_spaces = client.post("/chat", json={"prompt": "     "})
    assert response_spaces.status_code == 422


@patch("src.api.routes.VoxService.chat_stream")
def test_chat_stream_endpoint(mock_stream, client):
    mock_stream.return_value = iter(["Olá ", "mundo ", "acolhedor!"])

    response = client.post("/chat/stream", json={"prompt": "Olá"})
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "data: Olá" in content


@patch("src.api.routes.VoxService.transcribe")
def test_transcribe_endpoint(mock_transcribe, client):
    mock_transcribe.return_value = "Texto transcrito com sucesso"

    fake_file = ("audio.mp3", b"fake audio content", "audio/mp3")
    response = client.post(
        "/transcribe",
        files={"file": fake_file},
    )
    assert response.status_code == 200
    assert response.json()["transcription"] == "Texto transcrito com sucesso"


@patch("src.api.routes.VoxService.rag_query")
def test_rag_query_endpoint(mock_rag, client):
    mock_rag.return_value = RAGQueryResponse(
        topic="Prevenção",
        context="Informações sobre PrEP e PEP",
        references=[{"kb_id": "prep-01"}],
    )

    response = client.post("/rag/query", json={"query": "O que é PrEP?"})
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Prevenção"
    assert "PrEP" in data["context"]


def test_rag_query_endpoint_validation_error(client):
    # Query vazia ou apenas espaços deve falhar com status 422
    response_empty = client.post("/rag/query", json={"query": ""})
    assert response_empty.status_code == 422
    response_spaces = client.post("/rag/query", json={"query": "     "})
    assert response_spaces.status_code == 422


@patch("src.api.routes.VoxService.get_categories")
def test_report_categories_endpoint(mock_categories, client):
    mock_categories.return_value = [
        {"id": 1, "label": "Informação incorreta"},
        {"id": 2, "label": "Linguagem desrespeitosa"},
    ]

    response = client.get("/report/categories")
    assert response.status_code == 200
    assert len(response.json()) == 2


@patch("src.api.routes.VoxService.submit_report")
def test_submit_report_endpoint(mock_report, client):
    mock_report.return_value = True

    payload = {
        "session_id": "sess-xyz",
        "category_id": 1,
        "chat_history": "U: Olá / A: Oi",
        "comment": "Sugestão de melhoria",
    }
    response = client.post("/report", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True


@patch("src.api.routes.VoxService.delete_session")
def test_delete_session_lgpd_endpoint(mock_delete, client):
    mock_delete.return_value = True

    response = client.delete("/session/sess-xyz")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_transcribe_empty_file_returns_400(client):
    empty_file = ("empty.mp3", b"", "audio/mp3")
    response = client.post(
        "/transcribe",
        files={"file": empty_file},
    )
    assert response.status_code == 400
    assert "vazio" in response.json()["detail"]


@patch("src.api.routes.VoxService.transcribe")
def test_transcribe_failure_returns_500(mock_transcribe, client):
    mock_transcribe.side_effect = RuntimeError("Falha no modelo Gemini")

    fake_file = ("audio.mp3", b"invalid-bytes", "audio/mp3")
    response = client.post(
        "/transcribe",
        files={"file": fake_file},
    )
    assert response.status_code == 500


@patch("src.api.routes.VoxService.chat_stream")
def test_chat_stream_endpoint_multiline_sse_spec(mock_stream, client):
    # Garante que chunks com múltiplas linhas geram linhas 'data:' individuais segundo especificação W3C
    mock_stream.return_value = iter(["Primeira linha\nSegunda linha\n"])

    response = client.post("/chat/stream", json={"prompt": "Olá"})
    assert response.status_code == 200
    text = response.text
    assert "data: Primeira linha\n" in text
    assert "data: Segunda linha\n" in text
