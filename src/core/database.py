from src.core.db.client import get_db_client
from src.core.db.sessions import salvar_sessao, excluir_dados_sessao
from src.core.db.logs import salvar_log_chat, salvar_erro
from src.core.db.reports import salvar_report, get_categorias_erro
from src.core.db.retrieval import (
    buscar_referencias_db,
    buscar_chunks_por_topico,
    recuperar_contexto_inteligente,
)
