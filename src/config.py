import os
import logging
import streamlit as st

# Configuração de Logging Centralizado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

# Logger principal
logger = logging.getLogger("VoxAI")


def get_secret(key: str, default: str = "") -> str:
    """
    Busca um segredo primeiro no st.secrets (Streamlit Cloud),
    depois nas variáveis de ambiente (Local/Docker).
    """
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
                    return os.environ.get(key.replace(".", "_").upper(), default)
            return val
    except FileNotFoundError:
        pass
    return os.environ.get(key, default)


# Caminhos
CSS_PATH = "static/css/style.css"

# Configurações de IA
MODELO_SEMANTICO_NOME = "models/text-embedding-004"
GEMINI_MODEL_NAME = 'gemini-flash-latest'

# Config da KB
SEMANTICA_THRESHOLD = 0.5
LIMITE_TEMAS = 10
MAX_CHUNCK = 25

# Configurações de UI
PAGE_TITLE = 'Vox AI'
PAGE_ICON = '🏳️‍🌈'

class StatusConhecimento:
    PENDENTE = -1
    REJEITADO = 0
    APROVADO = 1
