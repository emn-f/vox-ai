import logging
import os

try:
    import streamlit as st
except ImportError:
    st = None

# Configuração de Logging Centralizado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

# Silenciar loggers verbosos de terceiros e clientes HTTP para manter o log limpo e útil
NOISY_LOGGERS = [
    "google_genai",
    "google_genai._api_client",
    "google_genai.models",
    "google_genai._common",
    "google_genai._interactions",
    "httpx",
    "httpcore",
    "urllib3",
    "streamlit",
    "absl",
    "postgrest",
    "asyncio",
    "urllib3.connectionpool",
]
for logger_name in NOISY_LOGGERS:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Logger principal
logger = logging.getLogger("Vox AI")


# Caminhos
CSS_PATH = "static/css/style.css"

# Configurações de IA
GEMINI_MODEL_NAME = "gemini-3.6-flash"
GEMINI_MODEL_GATEKEEP = "gemini-3.1-flash-lite"
GEMINI_FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]
GEMINI_TTS_MODELS = [
    "gemini-2.5-flash-preview-tts",
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
    "gemini-3.1-flash-tts-preview",
]
MODELO_SEMANTICO_NOME = "gemini-embedding-001"
TAMANHO_VETOR_SEMANTICO = 1536

# Config da KB
SEMANTICA_THRESHOLD = 0.62
LIMITE_TEMAS = 6
MAX_CHUNCK = 15

# Configurações de UI
PAGE_TITLE = 'Vox AI'
PAGE_ICON = '🏳️‍🌈'

def get_secret(key: str, default: str = "") -> str:
    """
    Busca um segredo no st.secrets (Streamlit Cloud/Local secrets.toml)
    ou nas variáveis de ambiente (Docker/Cloud env vars).
    """
    # 1. Tenta buscar no Streamlit Secrets (Cloud ou Local secrets.toml)
    if st is not None:
        try:
            if hasattr(st, "secrets") and key in st.secrets:
                return st.secrets[key]
            if hasattr(st, "secrets") and "." in key:
                parts = key.split(".")
                val = st.secrets
                for p in parts:
                    if p in val:
                        val = val[p]
                    else:
                        break
                else:
                    return val
        except Exception:
            # Silencia qualquer exceção ao acessar st.secrets fora do contexto do Streamlit
            pass

    # 2. Fallback para Variáveis de Ambiente
    # Tenta primeiro a chave no formato padrão de variáveis de ambiente (ex: SUPABASE_URL)
    env_key = key.replace(".", "_").upper()
    if env_key in os.environ:
        return os.environ[env_key]

    # Como último recurso, tenta buscar a chave literal (ex: supabase.url)
    return os.environ.get(key, default)