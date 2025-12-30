import os

import google.generativeai as genai
import streamlit as st

from data.prompts.system_prompt import INSTRUCOES
from src.app.ui import stream_resposta
from src.config import GEMINI_MODEL_NAME, get_secret, logger


def configurar_api_gemini():
    try:
        api_key = get_secret("GEMINI_API_KEY")
        if not api_key:
            msg = "Chave da API (GEMINI_API_KEY) não encontrada."
            logger.error(msg)
            st.error(msg)
            st.stop()
        else:
            genai.configure(api_key=api_key)
            logger.info("API Gemini configurada com sucesso.")
        return api_key
    except Exception as e:
        logger.error(f"Erro ao configurar a API do Gemini: {e}")
        st.error(f"Erro ao configurar a API do Gemini: {e}")
        st.stop()
        return None


def inicializar_chat_modelo():
    if "hist" not in st.session_state:
        st.session_state.hist = [{"role": "user", "parts": [INSTRUCOES]}]
    if "hist_exibir" not in st.session_state:
        st.session_state.hist_exibir = []

    modelo = genai.GenerativeModel(GEMINI_MODEL_NAME)
    chat = modelo.start_chat(history=st.session_state.hist)
    return chat


def gerar_resposta(chat, prompt, info_adicional):
    msg_placeholder = st.empty()
    with st.spinner("🧠 Thinking about it..."):
        try:
            full_prompt_for_model = prompt
            if info_adicional:
                full_prompt_for_model = f"Prompt do Usuário: {prompt}\n\nContexto interno da sua base de conhecimento, que o usuário NÃO forneceu (use para embasar sua resposta): {info_adicional}\n\nResponda à pergunta do usuário com base no contexto fornecido."
            resposta = ""
            for chunk in chat.send_message(full_prompt_for_model, stream=True):
                resposta += chunk.text
            msg_placeholder.write_stream(stream_resposta(resposta))
            return resposta
        except genai.types.generation_types.BlockedPromptException as e:
            msg_placeholder.empty()
            st.error("⚠️ Essa pergunta não pode ser respondida pelo Vox.")
            st.exception(e)
            return "Desculpe, não posso responder isso."
        except Exception as e:
            msg_placeholder.empty()
            st.exception(e)
            return "❌ Ocorreu um erro inesperado na comunicação com a IA."


def transcrever_audio(audio_file):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(
            [
                "Transcreva este áudio para português do Brasil. Retorne apenas o texto transcrito, sem comentários adicionais.",
                {"mime_type": "audio/mp3", "data": audio_file.read()},
            ]
        )

        return response.text
    except Exception as e:
        st.error(f"Erro na transcrição: {e}")
        return None
