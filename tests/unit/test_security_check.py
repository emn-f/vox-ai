import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Garante que 'scripts' esteja no path para permitir a importação do security_check
scripts_path = os.path.join(os.getcwd(), 'scripts')
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import security_check

class TestSanitizeDiff:
    def test_sanitize_secrets(self):
        # Constrói o segredo dinamicamente para não ser pego pelo próprio security_check estático
        fake_secret = "sk-" + "1234567890abcdef" * 3  # 48 chars
        diff = f"\n+ {fake_secret}\n+ clean line\n"
        sanitized = security_check.sanitize_diff_for_ai(diff)
        assert "[REDACTED SECRET DETECTED]" in sanitized
        assert "sk-1234567890" not in sanitized
        assert "clean line" in sanitized

@patch("security_check.log_ai_event")
@patch("security_check.load_secrets")
class TestAICodeReview:

    @pytest.fixture(autouse=True)
    def setup_genai(self):
        # Mocking the new google.genai.Client
        self.patcher_client = patch("google.genai.Client")
        self.mock_client_cls = self.patcher_client.start()

        self.mock_client_instance = MagicMock()
        self.mock_client_cls.return_value = self.mock_client_instance

        # Setup hierarchy: client.models.generate_content
        self.mock_models = MagicMock()
        self.mock_client_instance.models = self.mock_models

        yield
        self.patcher_client.stop()

    @property
    def mock_genai_client(self):
        return self.mock_client_cls

    def test_missing_api_key(self, mock_load, mock_log):
        # Configuração: Sem chave de API
        mock_load.return_value = {}
        with patch.dict(os.environ, {}, clear=True):
            result = security_check.run_ai_code_review("diff content")

        assert result is True
        # Ensure client was not initialized if no key found
        self.mock_client_cls.assert_not_called()

    def test_block_keyword_in_response(self, mock_load, mock_log):
        # Configuração: Chave presente, palavra proibida na resposta
        mock_load.return_value = {"GEMINI_API_KEY": "fake-key"}

        mock_response = MagicMock()
        mock_response.text = "[PASS] Approved, but I found a password exposed in the logs."

        # Mocking generate_content response
        self.mock_models.generate_content.return_value = mock_response

        # Executa
        result = security_check.run_ai_code_review("diff content")

        # Verifica
        assert result is False
        mock_log.assert_called_with("BLOCK (Keyword Trigger)", mock_response.text)

    def test_explicit_block(self, mock_load, mock_log):
        # Configuração: Resposta com [BLOCK]
        mock_load.return_value = {"GEMINI_API_KEY": "fake-key"}

        mock_response = MagicMock()
        mock_response.text = "[BLOCK] Critical issue found."
        self.mock_models.generate_content.return_value = mock_response

        # Executa
        result = security_check.run_ai_code_review("diff content")

        # Verifica
        assert result is False
        mock_log.assert_called_with("BLOCK (AI Explicit)", mock_response.text)

    def test_pass_clean(self, mock_load, mock_log):
        # Configuração: Resposta limpa [PASS]
        mock_load.return_value = {"GEMINI_API_KEY": "fake-key"}

        mock_response = MagicMock()
        mock_response.text = "[PASS] Aprovado."
        self.mock_models.generate_content.return_value = mock_response

        # Executa
        result = security_check.run_ai_code_review("diff content")

        # Verifica
        assert result is True
        mock_log.assert_not_called()

    def test_pass_with_suggestions(self, mock_load, mock_log):
        # Configuração: [PASS] com sugestões
        mock_load.return_value = {"GEMINI_API_KEY": "fake-key"}

        mock_response = MagicMock()
        mock_response.text = "[PASS] Aprovado.\nSugestão: Melhore a variável X."
        self.mock_models.generate_content.return_value = mock_response

        # Executa
        result = security_check.run_ai_code_review("diff content")

        # Verifica
        assert result is True
        mock_log.assert_called_with("PASS (With Suggestions)", mock_response.text)

    def test_api_exception(self, mock_load, mock_log):
        # Configuração: Erro na API
        mock_load.return_value = {"GEMINI_API_KEY": "fake-key"}
        self.mock_models.generate_content.side_effect = Exception("API Error")

        # Executa
        result = security_check.run_ai_code_review("diff content")

        # Verifica
        assert result is True # Falha aberta (permite continuar)
        mock_log.assert_not_called()
