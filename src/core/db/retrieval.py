from typing import Any
from src.config import (
    LIMITE_TEMAS,
    MAX_CHUNCK,
    SEMANTICA_THRESHOLD,
    TAMANHO_VETOR_SEMANTICO,
    logger,
)
import src.core.db.client as db_client

def buscar_referencias_db(
    vector_embedding: list[float],
    threshold: float = SEMANTICA_THRESHOLD,
    limit: int = LIMITE_TEMAS,
    filter_topic: str | None = None,
) -> list[dict[str, Any]]:
    client = db_client.get_db_client()
    if not client:
        logger.error("⚠️ Erro: Cliente Supabase não inicializado.")
        return []
    try:
        if len(vector_embedding) != TAMANHO_VETOR_SEMANTICO:
            logger.error(
                f"⚠️ Erro de Dimensão: O vetor gerado tem {len(vector_embedding)} dimensões, mas o banco espera {TAMANHO_VETOR_SEMANTICO}."
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
            logger.info("⚠️ Nenhum match encontrado na base com esse threshold.")
        return []

    except Exception as e:
        logger.critical(f"❌ Erro CRÍTICO na busca vetorial (Supabase): {e}")
        return []

def buscar_chunks_por_topico(topico_alvo: str, limit: int = 30) -> list[dict[str, Any]]:
    client = db_client.get_db_client()
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
        logger.error(f"❌ Erro ao buscar tópico completo: {e}")
        return []

def recuperar_contexto_inteligente(
    vector_embedding: list[float],
) -> tuple[str | None, str, list[dict[str, Any]] | None]:
    client = db_client.get_db_client()
    if not client:
        logger.error("⚠️ Erro: Cliente Supabase não inicializado.")
        return None, "Erro DB", None
    resultados_iniciais = buscar_referencias_db(
        vector_embedding, SEMANTICA_THRESHOLD, LIMITE_TEMAS, None
    )
    if not resultados_iniciais:
        return None, "Nenhuma referencia encontrada na base de conhecimento.", None

    def _gerar_fallback_top5() -> tuple[list[str], list[dict[str, Any]]]:
        top_5 = resultados_iniciais[:5]
        contexto = [item["descricao"] for item in top_5]
        ids_usados = []
        for item in top_5:
            kid = item.get("kb_id") or item.get("id")
            if kid:
                ids_usados.append(
                    {"kb_id": kid, "similarity": item.get("similarity")}
                )
        return contexto, ids_usados

    contagem_topicos = {}

    for item in resultados_iniciais:
        topico = item.get("topico")
        if topico:
            contagem_topicos[topico] = contagem_topicos.get(topico, 0) + 1

    contexto_final = []
    lista_ids_usados = []
    fonte_origem = "Busca por similaridade (Fragmentos)"

    if not contagem_topicos:
        contexto_final, lista_ids_usados = _gerar_fallback_top5()
        return "\n---\n".join(contexto_final), fonte_origem, lista_ids_usados

    topico_vencedor = max(contagem_topicos, key=contagem_topicos.get)
    votos = contagem_topicos[topico_vencedor]

    if votos >= 3:
        logger.info(
            f"🚀 Estratégia: Contexto Expandido para o tópico '{topico_vencedor}'"
        )
        try:
            dados = buscar_chunks_por_topico(topico_vencedor, limit=MAX_CHUNCK)

            contexto_final = [row["descricao"] for row in dados]
            for row in dados:
                kid = row.get("kb_id") or row.get("id")
                if kid:
                    lista_ids_usados.append({"kb_id": kid, "similarity": None})

            fonte_origem = f"Contexto Completo: {topico_vencedor}"

        except Exception as e:
            logger.warning(f"⚠️ Erro ao expandir contexto: {e}. Usando fallback.")
            contexto_final, lista_ids_usados = _gerar_fallback_top5()

    else:
        logger.info(f"🔍 Estratégia: Tópicos mistos (Vencedor '{topico_vencedor}')")
        fonte_origem = f"Tópicos mistos (Vencedor: {topico_vencedor})"
        contexto_final, lista_ids_usados = _gerar_fallback_top5()

    return "\n---\n".join(contexto_final), fonte_origem, lista_ids_usados
