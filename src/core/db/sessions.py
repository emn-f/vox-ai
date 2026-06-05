from src.config import logger
import src.core.db.client as db_client

def salvar_sessao(session_id: str) -> None:
    client = db_client.get_db_client()
    if not client:
        logger.error("Não foi possível conectar com o banco de dados.")
        return
    try:
        registro_sessao = {"session_id": session_id}
        client.table("sessions").insert(registro_sessao).execute()
    except Exception as e:
        logger.error(f"⚠️ Erro ao tentar registrar sessão no banco de dados: {e}")

def excluir_dados_sessao(session_id: str) -> bool:
    """
    Exclui permanentemente todos os registros vinculados ao session_id 
    nas tabelas chat_logs_kb, chat_logs, user_reports, error_logs e sessions 
    para cumprir o Art. 18 da LGPD.
    """
    client = db_client.get_db_client()
    if not client:
        logger.error("Não foi possível conectar ao banco de dados para excluir dados.")
        return False
    try:
        # 1. Obtém os chat_ids dessa sessão para excluir as referências em chat_logs_kb
        res_logs = client.table("chat_logs").select("chat_id").eq("session_id", session_id).execute()
        if res_logs.data:
            chat_ids = [row["chat_id"] for row in res_logs.data]
            client.table("chat_logs_kb").delete().in_("chat_id", chat_ids).execute()
            
        # 2. Deleta os logs de chat
        client.table("chat_logs").delete().eq("session_id", session_id).execute()
        
        # 3. Deleta os relatórios de usuário
        client.table("user_reports").delete().eq("session_id", session_id).execute()
        
        # 4. Deleta os logs de erro
        client.table("error_logs").delete().eq("session_id", session_id).execute()
        
        # 5. Deleta a sessão em si
        client.table("sessions").delete().eq("session_id", session_id).execute()
        
        logger.info(f"Dados da sessão {session_id} foram excluídos permanentemente (LGPD Art. 18).")
        return True
    except Exception as e:
        logger.error(f"Erro ao excluir dados da sessão {session_id} no banco de dados: {e}")
        return False
