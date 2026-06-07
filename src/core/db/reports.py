from typing import Any
from src.config import logger
import src.core.db.client as db_client

def salvar_report( session_id: str, git_version: str, history_text: str, category_id: int, comment: str, ) -> bool:
    """
    Salva uma denúncia ou relatório de problema enviado pelo usuário no banco de dados.

    Args:
        session_id (str): Identificador único da sessão ativa.
        git_version (str): Versão do commit do Git correspondente.
        history_text (str): Histórico minimizado da conversa para auditoria (LGPD compliance).
        category_id (int): ID correspondente à categoria do erro reportado.
        comment (str): Comentário textual detalhado do usuário.

    Returns:
        bool: True se o relatório foi salvo com sucesso, False caso contrário.
    """
    client = db_client.get_db_client()

    try:
        if not client:
            return False
        data = {
            "session_id": session_id,
            "git_version": git_version,
            "chat_history": history_text,
            "category_id": category_id,
            "comment": comment,
        }
        client.table("user_reports").insert(data).execute()
        return True
    except Exception as e:
        logger.error(f"⚠️ Erro ao salvar report: {e}")
        return False

def get_categorias_erro() -> list[dict[str, Any]]:
    """
    Recupera do banco de dados as categorias de problemas/erros disponíveis para denúncia.

    Returns:
        list[dict[str, Any]]: Lista de dicionários contendo 'id' e 'label' das categorias de erro.
    """
    client = db_client.get_db_client()
    try:
        if not client:
            return []
        response = client.table("report_categories").select("id, label").execute()
        return response.data if response.data else []

    except Exception as e:
        logger.error(f"⚠️ Erro ao buscar categorias: {e}")
        return []
