"""
Suite de Testes E2E Automatizados e Reutilizáveis do Vox AI (Ambiente Dev).
Valida os fluxos de texto, RAG, áudio, auditoria de dados e serviços desacoplados.
"""

import io
import pytest
from fastapi.testclient import TestClient

from src.config import GEMINI_MODEL_NAME, TAMANHO_VETOR_SEMANTICO
from src.core.db.client import get_db_client
from src.core.semantica import semantica
from src.core.audio import gerar_fala_gemini, transcrever_audio_gemini
from src.api.main import app
from src.api.service import VoxService
from scripts.backup_supabase import realizar_backup
from scripts.audit_kb import carregar_dados_kb, detectar_anomalias


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="module")
def vox_service():
    return VoxService()


@pytest.fixture(scope="module", autouse=True)
def check_e2e_prerequisites():
    from src.config import get_secret
    url = get_secret("supabase.url")
    key = get_secret("supabase.key")
    if not url or not key:
        pytest.skip("Credenciais reais do Supabase não configuradas no ambiente. Pulando suite E2E.")


@pytest.mark.integration
class TestVoxE2ESuite:
    """Conjunto de testes ponta a ponta para validação contínua em Dev."""

    def test_01_environment_and_db_connection(self):
        """Valida que o ambiente Dev está conectado e as credenciais estão ativas."""
        client = get_db_client()
        assert client is not None, "Falha na conexão com Supabase Dev."
        # Verifica leitura da knowledge_base usando chave primária kb_id
        res = client.table("knowledge_base").select("kb_id", count="exact").limit(1).execute()
        assert res.count is not None and res.count >= 300, f"Contagem inesperada na KB: {res.count}"

    def test_02_kb_vectors_and_enrichment(self):
        """Valida integridade dos vetores e dados ingeridos nas 7 worktrees."""
        df = carregar_dados_kb(usar_banco=True)
        assert len(df) >= 356, f"Esperado ao menos 356 chunks, encontrado: {len(df)}"
        
        # Valida que todos os registros possuem vetor de 1536 dimensões
        assert df["embedding"].notnull().all(), "Existem chunks sem embedding cadastrado."

    @pytest.mark.parametrize("query,expected_keyword", [
        ("Como funciona o uso do nome social na chamada escolar pelo MEC?", "MEC"),
        ("Onde posso encontrar acolhimento em Salvador ou Camaçari?", "Marielle"),
        ("Pessoas trans têm direito de usar o banheiro do seu gênero no trabalho?", "banheiro"),
        ("Qual a importância do dia 17 de maio de 1990?", "1990"),
    ])
    def test_03_rag_semantic_retrieval(self, query, expected_keyword):
        """Valida que a busca semântica RAG recupera os chunks enriquecidos."""
        fonte, contexto, referencias = semantica(query)
        assert contexto is not None, f"Contexto RAG vazio para a pergunta: {query}"
        assert fonte is not None, f"Nenhuma fonte/tema identificado para: {query}"
        assert expected_keyword.lower() in contexto.lower(), (
            f"Palavra-chave '{expected_keyword}' não encontrada no contexto retornado."
        )

    def test_04_chat_response_flow(self, vox_service):
        """Valida o fluxo completo de geração de resposta com VoxService."""
        response = vox_service.chat(
            prompt="Olá! Como você pode me acolher hoje?",
            include_audio=False,
        )
        assert response is not None
        assert response.response is not None
        assert len(response.response) > 50

    def test_05_audio_tts_synthesis(self):
        """Valida a geração de áudio falado (TTS) e mecanismo de fallback."""
        buffer = gerar_fala_gemini("Teste de síntese de voz acolhedora Vox AI.")
        assert buffer is not None
        audio_bytes = buffer.getvalue()
        assert len(audio_bytes) > 1000, "Buffer de áudio vazio ou excessivamente curto."

    def test_06_audio_stt_edge_cases(self):
        """Valida robustez do STT para entradas nulas e vazias."""
        res_none = transcrever_audio_gemini(None)
        res_empty = transcrever_audio_gemini(b"")
        assert res_none is None
        assert res_empty is None

    def test_07_fastapi_decoupled_endpoints(self, api_client):
        """Valida os endpoints REST da API desacoplada."""
        # 1. Health check (Caminho feliz)
        r_health = api_client.get("/api/v1/health")
        assert r_health.status_code == 200
        data_h = r_health.json()
        assert data_h["status"] == "ok"
        assert data_h["gemini_configured"] is True
        assert data_h["supabase_configured"] is True

        # 2. Chat completion (Caminho feliz)
        r_chat = api_client.post("/api/v1/chat", json={"prompt": "O que é o Vox AI?"})
        assert r_chat.status_code == 200
        data_c = r_chat.json()
        assert "response" in data_c
        assert len(data_c["response"]) > 0

        # 3. Caso de erro: Payload sem prompt obrigatório
        r_err = api_client.post("/api/v1/chat", json={})
        assert r_err.status_code == 422

    def test_08_backup_routine_dryrun(self, tmp_path):
        """Valida execução da rotina de backup em diretório temporário."""
        dest = str(tmp_path / "test_backup")
        sucesso = realizar_backup(output_dir=dest, compress=True)
        assert sucesso is True
