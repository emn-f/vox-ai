import pytest
from supabase import create_client, Client
import streamlit as st

# Nota: Este é um teste de INTEGRAÇÃO real.
# Ele vai tentar conectar na internet. Se falhar, o teste falha.
# Idealmente, testes de integração são separados de unitários, mas aqui vamos mantê-lo simples.


def test_conexao_supabase_real():
    """
    Verifica se é possível conectar ao Supabase com as credenciais reais
    do ambiente/secrets.
    """

    try:
        from src.config import get_secret

        url = get_secret("supabase.url")
        key = get_secret("supabase.key")
    except ImportError:
        pytest.skip("Módulo src.config não encontrado ou erro de importação")

    if not url or not key:
        pytest.skip("Credenciais do Supabase não encontradas no ambiente de teste.")

    try:
        client: Client = create_client(url, key)
        assert client is not None

        response = client.table("report_categories").select("id").limit(1).execute()
        assert response is not None
    except Exception as e:
        pytest.fail(f"Falha na conexão real com Supabase: {e}")
