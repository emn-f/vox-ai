import streamlit as st

from supabase import create_client

st.title("🕵️ Diagnóstico de Conexão Supabase")

# 1. Testar Credenciais
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    st.success("✅ Credenciais encontradas no secrets.toml")
    st.write(f"**URL:** `{url}`")
    st.write(f"**Key (início):** `{key[:10]}...`")
except Exception as e:
    st.error(f"❌ Erro ao ler secrets: {e}")
    st.stop()

# 2. Testar Conexão
try:
    supabase = create_client(url, key)
    st.success("✅ Cliente Supabase iniciado")
except Exception as e:
    st.error(f"❌ Falha ao criar cliente: {e}")
    st.stop()

# 3. Testar Inserção (Onde costuma falhar)
if st.button("Testar Inserção na Tabela chat_logs"):
    try:
        data = {
            "session_id": "teste-diagnostico",
            "git_version": "v3.1-debug",
            "prompt": "Teste de conexão",
            "response": "Se você ler isso, funcionou!",
            "tema_match": "Teste",
            "desc_match": "N/A"
        }
        
        # Tenta inserir e pede retorno
        response = supabase.table("chat_logs").insert(data).execute()
        
        st.success("🎉 SUCESSO! Dados inseridos.")
        st.json(response.data)
        st.balloons()
        
    except Exception as e:
        st.error("❌ ERRO NA INSERÇÃO:")
        st.code(str(e))
        st.info("Dica: Se o erro for 'new row violates row-level security policy', precisamos arrumar as políticas no Supabase.")