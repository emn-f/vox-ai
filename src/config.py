import logging
import os

import streamlit as st

# Configuração de Logging Centralizado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

# Logger principal
logger = logging.getLogger("Vox AI")


# Caminhos
CSS_PATH = "static/css/style.css"

# Configurações de IA
GEMINI_MODEL_NAME = "gemini-3.5-flash"
GEMINI_MODEL_GATEKEEP = "gemini-3.1-flash-lite"
MODELO_SEMANTICO_NOME = "gemini-embedding-001"
TAMANHO_VETOR_SEMANTICO = 1536

# Config da KB
SEMANTICA_THRESHOLD = 0.5
LIMITE_TEMAS = 10
MAX_CHUNCK = 25

# Configurações de UI
PAGE_TITLE = 'Vox AI'
PAGE_ICON = '🏳️‍🌈'

def get_secret(key: str, default: str = "") -> str:
    """
    Busca um segredo no st.secrets (Streamlit Cloud/Local secrets.toml)
    ou nas variáveis de ambiente (Docker/Cloud env vars).
    """
    # 1. Tenta buscar no Streamlit Secrets (Cloud ou Local secrets.toml)
    try:
        if key in st.secrets:
            return st.secrets[key]
        if "." in key:
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