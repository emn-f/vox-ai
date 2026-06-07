"""
Este módulo atua como uma Facade (Fachada) de re-exportação para as operações de banco de dados.

Após a modularização do antigo arquivo gigante 'database.py' no pacote focado 'src/core/db/',
este arquivo foi mantido para fins de compatibilidade retroativa, permitindo que outros
módulos do projeto continuem importando as funções diretamente deste ponto centralizador.
"""

from src.core.db.client import get_db_client
from src.core.db.sessions import salvar_sessao, excluir_dados_sessao
from src.core.db.logs import salvar_log_chat, salvar_erro
from src.core.db.reports import salvar_report, get_categorias_erro
from src.core.db.retrieval import (
    buscar_referencias_db,
    buscar_chunks_por_topico,
    recuperar_contexto_inteligente,
)
