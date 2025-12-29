import os
import traceback
import uuid

import google.generativeai as genai
import streamlit as st

from src.config import LIMITE_TEMAS, MAX_CHUNCK, SEMANTICA_THRESHOLD
from supabase import Client, create_client


@st.cache_resource
def get_db_client() -> Client:
    try:
        if "supabase" in st.secrets:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
        else:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            url = st.secrets.get("SUPABASE_URL")
            key = st.secrets.get("SUPABASE_KEY")

        if not url or not key:
            st.error("❌ Credenciais do Supabase não encontradas (secrets.toml ou ENV variables).")
            return None

        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar no banco de dados: {e}")
        return None


def salvar_sessao(session_id):
    client = get_db_client()
    if not client:
        print("Não foi possível conectar com o banco de dados.")
        return
    try:
        registro_sessao = {"session_id": session_id}
        client.table("sessions").insert(registro_sessao).execute()
    except Exception as e:
        print(f"⚠️ Erro ao tentar registrar sessão no banco de dados: {e}")


def salvar_log_chat(
    session_id, git_version, prompt, response, fonte_info, lista_kb_ids=None
):

    client = get_db_client()
    if not client:
        print("❌ Não foi possível conectar com o banco de dados.")
        return

    try:
        data_log = {
            "session_id": session_id,
            "prompt": prompt,
            "response": str(response),
            "git_version": git_version,
        }

        res = client.table("chat_logs").insert(data_log).execute()

        if not res.data:
            print("⚠️ Erro: Log salvo mas sem retorno de ID.")
            return

        novo_log_id = res.data[0]["chat_id"]

        if lista_kb_ids and len(lista_kb_ids) > 0:
            dados_relacao = []
            for item in lista_kb_ids:
                if isinstance(item, dict):
                    kb_id = item.get("kb_id")
                    similarity = item.get("similarity")
                else:
                    kb_id = item
                    similarity = None

                if kb_id:
                    row_data = {
                        "chat_id": novo_log_id,
                        "kb_id": str(kb_id),
                    }
                    if similarity is not None:
                        row_data["similarity"] = similarity

                    dados_relacao.append(row_data)

            if dados_relacao:
                try:
                    res_kb = (
                        client.table("chat_logs_kb").insert(dados_relacao).execute()
                    )
                except Exception as e_kb:
                    print(f"❌ ERRO ao inserir em chat_logs_kb: {e_kb}")
                    print(f"❌ Dados tentados: {dados_relacao}")
            else:
                print("⚠️ Nenhuma relação válida para inserir.")
        else:
            pass

    except Exception as e:
        print(f"❌ ERRO ao salvar log: {type(e).__name__}")
        print(f"❌ Mensagem de erro: {e}")
        print(f"❌ Traceback completo:")
        traceback.print_exc()


def salvar_erro(session_id, git_version, error_msg):
    client = get_db_client()
    if not client:
        return "ERRO-DB"
    try:
        error_id = str(uuid.uuid4())[:8]

        data = {
            "error_id": error_id,
            "error_message": str(error_msg),
            "session_id": session_id,
            "git_version": git_version,
        }
        client.table("error_logs").insert(data).execute()
        return error_id
    except Exception as e:
        print(f"⚠️ Erro ao salvar exceção: {e}")
        return "N/A"


def salvar_report(session_id, git_version, history_text):
    client = get_db_client()

    if not client:
        return False

    try:
        data = {
            "session_id": session_id,
            "git_version": git_version,
            "chat_history": history_text,
        }
        client.table("user_reports").insert(data).execute()
        return True
    except Exception as e:
        print(f"⚠️ Erro ao salvar report: {e}")
        return False


def add_conhecimento_db(tema, descricao, referencias, autor):
    client = get_db_client()
    if not client:
        return False
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=f"{tema}: {descricao}",
            task_type="retrieval_document",
        )
        vector_embedding = result["embedding"]

        data = {
            "tema": tema,
            "descricao": descricao,
            "embedding": vector_embedding,
            "referencias": referencias,
            "autor": autor,
        }
        client.table("knowledge_base").insert(data).execute()
        return True

    except Exception as e:
        print(f"⚠️ Erro ao adicionar na base de conhecimento: {e}")
        return False


def buscar_referencias_db(
    vector_embedding,
    threshold=SEMANTICA_THRESHOLD,
    limit=LIMITE_TEMAS,
    filter_topic=None,
):
    client = get_db_client()
    if not client:
        print("⚠️ Erro: Cliente Supabase não inicializado.")
        return []
    try:
        if len(vector_embedding) != 768:
            print(
                f"⚠️ Erro de Dimensão: O vetor gerado tem {len(vector_embedding)} dimensões, mas o banco espera 768."
            )
            return []

        params = {
            "query_embedding": vector_embedding,
            "match_threshold": threshold,
            "match_count": limit,
            "filter_topic": filter_topic,
        }

        response = client.rpc("match_knowledge_base", params).execute()

        if response.data:
            return response.data
        else:
            print("⚠️ Nenhum match encontrado na base com esse threshold.")
        return []

    except Exception as e:
        print(f"❌ Erro CRÍTICO na busca vetorial (Supabase): {e}")
        return []


def buscar_chunks_por_topico(topico_alvo, limit=30):
    client = get_db_client()
    if not client:
        return []
    try:
        response = (
            client.table("knowledge_base")
            .select("kb_id, descricao")
            .eq("topico", topico_alvo)
            .limit(limit)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Erro ao buscar tópico completo: {e}")
        return []


def recuperar_contexto_inteligente(vector_embedding):
    client = get_db_client()
    if not client:
        print("⚠️ Erro: Cliente Supabase não inicializado.")
        return [], "Erro DB", []
    resultados_iniciais = buscar_referencias_db(
        vector_embedding, SEMANTICA_THRESHOLD, LIMITE_TEMAS, None
    )
    if not resultados_iniciais:
        return None, "Nenhuma referencia encontrada na base de conhecimento.", None

    if not resultados_iniciais:
        return None, "Nenhuma referencia encontrada na base de conhecimento.", None

    contagem_topicos = {}

    for item in resultados_iniciais:
        topico = item.get("topico")
        if topico:
            contagem_topicos[topico] = contagem_topicos.get(topico, 0) + 1

    contexto_final = []

    lista_ids_usados = []

    fonte_origem = "Busca por similaridade (Fragmentos)"
    if not contagem_topicos:
        top_5 = resultados_iniciais[:5]
        contexto_final = [item["descricao"] for item in top_5]
        # Tenta pegar kb_id ou id, e remove Nones
        for item in top_5:
            kid = item.get("kb_id") or item.get("id")
            if kid:
                lista_ids_usados.append(
                    {"kb_id": kid, "similarity": item.get("similarity")}
                )

        return "\n---\n".join(contexto_final), fonte_origem, lista_ids_usados

    topico_vencedor = max(contagem_topicos, key=contagem_topicos.get)
    votos = contagem_topicos[topico_vencedor]

    if votos >= 3:
        print(f"🚀 Estratégia: Contexto Expandido para o tópico '{topico_vencedor}'")
        try:
            dados = buscar_chunks_por_topico(topico_vencedor, limit=MAX_CHUNCK)

            contexto_final = [row["descricao"] for row in dados]
            for row in dados:
                kid = row.get("kb_id") or row.get("id")
                if kid:
                    lista_ids_usados.append({"kb_id": kid, "similarity": None})

            fonte_origem = f"Contexto Completo: {topico_vencedor}"

        except Exception as e:
            print(f"⚠️ Erro ao expandir contexto: {e}. Usando fallback.")
            top_5 = resultados_iniciais[:5]
            contexto_final = [item["descricao"] for item in top_5]

            for item in top_5:
                kid = item.get("kb_id") or item.get("id")
                if kid:
                    lista_ids_usados.append(
                        {"kb_id": kid, "similarity": item.get("similarity")}
                    )

    else:
        print(f"🔍 Estratégia: Tópicos mistos (Vencedor '{topico_vencedor}')")
        top_5 = resultados_iniciais[:5]
        contexto_final = [item["descricao"] for item in top_5]

        for item in top_5:
            kid = item.get("kb_id") or item.get("id")
            if kid:
                lista_ids_usados.append(
                    {"kb_id": kid, "similarity": item.get("similarity")}
                )

    return "\n---\n".join(contexto_final), fonte_origem, lista_ids_usados
