import os

import streamlit as st
from google import genai
from google.genai import types

from data.prompts.system_prompt import INSTRUCOES
from src.app.ui import stream_resposta
from src.config import GEMINI_MODEL_NAME, get_secret, logger


def configurar_api_gemini() -> genai.Client:
    """
    Configura e inicializa o cliente da API do Google GenAI utilizando a chave armazenada.
    Armazena a instância no session_state do Streamlit como recurso persistente.

    Returns:
        genai.Client: Cliente configurado do Gemini.
    """
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
    """
    Inicializa a sessão de chat conversacional com o modelo Gemini, definindo
    as diretrizes de comportamento do assistente.

    Returns:
        st.session_state.chat: Instância ativa do chat no estado de sessão.
    """
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


def gerar_resposta(chat, prompt: str, info_adicional: str) -> str:
    """
    Gera a resposta do assistente Vox AI a partir do prompt do usuário e do contexto fornecido,
    realizando o streaming de texto e capturando erros amigavelmente.

    Args:
        chat: Instância ativa do chat conversacional do Gemini.
        prompt (str): Texto da pergunta do usuário.
        info_adicional (str): Informações de contexto recuperadas da base de dados.

    Returns:
        str: Resposta final gerada pelo modelo de linguagem.
    """
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
            sess_id = st.session_state.get("session_id", "Unknown")
            git_ver = st.session_state.get("git_version_str", "Unknown")

            # Evita circular imports importando no escopo do handler
            try:
                from src.utils import git_version
                git_ver = git_version() or git_ver
            except Exception:
                pass

            from src.core.db.logs import salvar_erro
            error_id = salvar_erro(sess_id, git_ver, e)
            
            from google.genai.errors import APIError

            is_safety = False
            is_quota = False
            is_unavailable = False

            # Tenta classificação estruturada usando os atributos do erro da API
            if isinstance(e, APIError):
                if e.code == 429:
                    is_quota = True
                elif e.code == 503:
                    is_unavailable = True
                elif e.code == 400 and ("safety" in str(e).lower() or "blocked" in str(e).lower()):
                    is_safety = True

            # Fallback por correspondência de string para compatibilidade e robustez
            if not (is_safety or is_quota or is_unavailable):
                err_msg = str(e).lower()
                if "safety" in err_msg or "blocked" in err_msg:
                    is_safety = True
                elif "resourceexhausted" in err_msg or "429" in err_msg or "quota" in err_msg:
                    is_quota = True
                elif "503" in err_msg or "serviceunavailable" in err_msg or "overloaded" in err_msg:
                    is_unavailable = True

            if is_safety:
                st.error(
                    f"⚠️ **Essa pergunta não pode ser respondida pelo Vox.**\n\n"
                    f"Por razões de segurança e acolhimento, sua mensagem ativou nossas diretrizes de proteção e não pôde ser processada.\n\n"
                    f"*(Código do Erro: **{error_id}**)*",
                    icon="🚫"
                )
            elif is_quota:
                st.error(
                    f"Olá! O Vox está recebendo muitas mensagens de carinho e dúvidas no momento, e atingimos nosso limite de processamento temporário da API do Google. "
                    f"Por favor, aguarde cerca de um minutinho e tente enviar sua mensagem novamente! 💜\n\n"
                    f"*(Código do Erro: **{error_id}**)*",
                    icon="⚠️"
                )
            elif is_unavailable:
                st.error(
                    f"Ops! Os servidores da inteligência artificial estão com uma demanda muito alta agora e temporariamente instáveis. "
                    f"Que tal respirar fundo, tomar uma água e tentar de novo em alguns instantes? Estarei aqui esperando! 🏳️‍🌈\n\n"
                    f"*(Código do Erro: **{error_id}**)*",
                    icon="⏳"
                )
            else:
                from src.app.ui import exibir_mensagem_erro
                exibir_mensagem_erro(error_id)
            st.stop()

def transcrever_audio(audio_file) -> str | None:
    """
    Realiza a transcrição de um arquivo de áudio de voz para texto utilizando o modelo Gemini.

    Args:
        audio_file (BytesIO): Arquivo de áudio (geralmente MP3/WAV) gravado no frontend.

    Returns:
        str | None: O texto transcrito ou None em caso de erro na API de áudio.
    """
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
