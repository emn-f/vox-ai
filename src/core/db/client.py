"""
Cliente Supabase desacoplado da interface Streamlit.

Este módulo provê a instância singleton do cliente Supabase para acesso ao banco de dados,
operando de forma resiliente tanto na interface Streamlit quanto em execuções independentes (CLI/Scripts).
"""
from typing import Optional
from supabase import Client, create_client
from src.config import get_secret, logger

_db_client_instance: Optional[Client] = None


def get_db_client() -> Optional[Client]:
    """
    Retorna a instância singleton do cliente Supabase, configurado com as chaves do projeto.

    Returns:
        Optional[Client]: Instância autenticada do Supabase Client ou None em caso de falha.
    """
    global _db_client_instance
    if _db_client_instance is not None:
        return _db_client_instance

    try:
        url: str = get_secret("supabase.url")
        key: str = get_secret("supabase.key")

        if not url or not key:
            logger.error("⚠️ Credenciais do Supabase não encontradas no ambiente/secrets.")
            return None

        _db_client_instance = create_client(url, key)
        return _db_client_instance
    except Exception as e:
        logger.error(f"❌ Erro ao conectar no banco de dados Supabase: {e}")
        return None
