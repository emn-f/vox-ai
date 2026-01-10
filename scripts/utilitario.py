from google import genai
from google.genai import types

from src.config import logger
from src.core.database import get_db_client
from src.core.genai import configurar_api_gemini


def add_conhecimento_db(tema, descricao, referencias, autor):
    client = get_db_client()
    if not client:
        return False
    try:
        gemini_client = configurar_api_gemini()
        result = gemini_client.models.embed_content(
            model="text-embedding-004",
            contents=f"{tema}: {descricao}",
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT", title="Vox - Knowledge Base"
            ),
        )
        vector_embedding = result.embeddings[0].values

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
