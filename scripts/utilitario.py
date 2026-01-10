import google.genai as genai

from src.config import logger
from src.core.database import get_db_client


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
        logger.error(f"⚠️ Erro ao adicionar na base de conhecimento: {e}")
        return False
