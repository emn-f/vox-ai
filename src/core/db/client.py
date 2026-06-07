import streamlit as st
from supabase import Client, create_client
from src.config import get_secret, logger

@st.cache_resource
def get_db_client() -> Client | None:
    """
    Retorna a instância singleton do cliente Supabase, configurado com as chaves do projeto.
    O recurso é cacheado para otimizar conexões.

    Returns:
        Client | None: O cliente Supabase configurado, ou None se ocorrer um erro de conexão/credenciais.
    """
    try:
        url = get_secret("supabase.url")
        key = get_secret("supabase.key")

        if not url or not key:
            logger.error("Credenciais do Supabase não encontradas.")
            return None

        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar no banco de dados: {e}")
        return None
