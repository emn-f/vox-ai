import os

import streamlit as st
from google import genai
from google.genai import types

from data.prompts.system_prompt import INSTRUCOES
from src.app.ui import stream_resposta
from src.config import GEMINI_MODEL_NAME, get_secret, logger


def configurar_api_gemini():
    if "gemini_client" not in st.session_state:
        try:
            st.session_state.gemini_client = genai.Client(
                api_key=get_secret("GEMINI_API_KEY")
            )
            logger.info("API Gemini configurada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao configurar a API do Gemini: {e}")
            st.error(f"Erro ao configurar a API do Gemini: {e}")
            st.stop()

    return st.session_state.gemini_client


def inicializar_chat_modelo():

    if "hist" not in st.session_state:
        st.session_state.hist = [{"role": "user", "parts": [INSTRUCOES]}]
    if "hist_exibir" not in st.session_state:
        st.session_state.hist_exibir = []

    if "chat" not in st.session_state:
        client = configurar_api_gemini()

        sys_config = types.GenerateContentConfig(
            system_instruction=INSTRUCOES,
        )

        st.session_state.chat = client.chats.create(
            model=GEMINI_MODEL_NAME,
            config=sys_config,
            history=[],
        )

    return st.session_state.chat


def gerar_resposta(chat, prompt, info_adicional):
    msg_placeholder = st.empty()

    with st.spinner("🧠 Thinking about it..."):
        try:
            full_prompt_for_model = prompt
            if info_adicional:
                full_prompt_for_model = (
                    f"Prompt do Usuário: {prompt}\n\n"
                    f"Contexto interno da sua base de conhecimento, que o usuário NÃO forneceu "
                    f"(use para embasar sua resposta): {info_adicional}\n\n"
                    f"Responda à pergunta do usuário com base no contexto fornecido."
                )

            resposta = ""
            for chunk in chat.send_message_stream(full_prompt_for_model):
                if chunk.text:
                    resposta += chunk.text

            msg_placeholder.write_stream(stream_resposta(resposta))
            return resposta

        except Exception as e:
            msg_placeholder.empty()
            st.exception(e)
            st.stop()

def transcrever_audio(audio_file):
    client = configurar_api_gemini()

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=[
                "Transcreva este áudio para português do Brasil. Retorne apenas o texto transcrito.",
                types.Part.from_bytes(data=audio_file.read(), mime_type="audio/mp3"),
            ],
        )
        return response.text
    except Exception as e:
        st.error(f"Erro na transcrição: {e}")
        return None
