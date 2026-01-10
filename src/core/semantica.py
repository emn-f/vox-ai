import streamlit as st
from google import genai
from google.genai import types

from src.config import MODELO_SEMANTICO_NOME
from src.core.database import recuperar_contexto_inteligente
from src.core.genai import configurar_api_gemini


def semantica(prompt):
    """
    Gera o embedding do prompt e busca contexto relevante no banco de dados.
    """
    try:
        # Reutiliza o cliente já configurado (com cache e nova Key)
        client = configurar_api_gemini()

        if not client:
            print("Client Gemini não disponível para semântica.")
            return None, None, None

        # Chamada V1 para Embeddings
        # Note que task_type agora vai dentro de config (opcional, mas recomendado para retrieval)
        response = client.models.embed_content(
            model=MODELO_SEMANTICO_NOME,
            contents=prompt,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )

        # A resposta na V1 geralmente vem em response.embeddings[0].values
        vetor_prompt = response.embeddings[0].values

        texto_contexto, fonte_identificaadora, lista_ids = (
            recuperar_contexto_inteligente(vetor_prompt)
        )

        if texto_contexto:
            return fonte_identificaadora, texto_contexto, lista_ids

        return None, None, None

    except Exception as e:
        print(f"Erro na geração do embedding semântico: {e}")
        return None, None, None
