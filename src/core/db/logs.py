import uuid
from typing import Any
from src.config import logger
import src.core.db.client as db_client

def salvar_log_chat(
    session_id: str,
    git_version: str,
    prompt: str,
    response: str,
    fonte_info: str,
    lista_kb_ids: list | None = None,
) -> None:
    client = db_client.get_db_client()
    if not client:
        logger.error("❌ Não foi possível conectar com o banco de dados.")
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
            logger.warning("⚠️ Erro: Log salvo mas sem retorno de ID.")
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
                    logger.error(f"❌ ERRO ao inserir em chat_logs_kb: {e_kb}")
                    logger.error(f"❌ Dados tentados: {dados_relacao}")
            else:
                logger.info("⚠️ Nenhuma relação válida para inserir.")
        else:
            pass

    except Exception as e:
        logger.error(f"❌ ERRO ao salvar log: {type(e).__name__}")
        logger.error(f"❌ Mensagem de erro: {e}", exc_info=True)

def salvar_erro(session_id: str, git_version: str, error_msg: Any) -> str:
    logger.error(f"🔥 Exceção capturada e registrada: {error_msg}", exc_info=True)

    client = db_client.get_db_client()
    if not client:
        logger.error("Falha ao obter cliente DB para salvar log de erro.")
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
        logger.error(f"⚠️ CRÍTICO: Falha ao salvar o erro no Supabase: {e}")
        return "N/A"
