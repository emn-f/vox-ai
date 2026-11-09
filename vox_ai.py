"""
Inicializa e orquestra a interface web do Vox AI construída com Streamlit.

Gerencia o fluxo de interação com o usuário (chat), incluindo suporte a entrada por
texto e áudio (com transcrição via IA), inicializa a sessão do usuário, realiza a busca
semântica de contexto (RAG) no banco de dados Supabase e chama o modelo Gemini para gerar
a resposta final de maneira assistida e personalizada.

Fluxo de Execução Principal:
1. Configuração inicial da página e carregamento do estilo CSS personalizado.
2. Inicialização de identificadores únicos de sessão.
3. Carregamento da barra lateral (sidebar) contendo informações e créditos do projeto.
4. Conexão/Autenticação com a API do Google GenAI.
5. Captura de entrada do usuário (campo de chat ou gravação de voz).
6. Processamento semântico de contexto relevante para o prompt.
7. Solicitação de resposta do modelo e exibição em fluxo contínuo (streaming).
8. Persistência de logs da conversa e tratamento centralizado de erros no banco de dados.
"""

import os
import uuid

import streamlit as st

import startup_patch

from data.prompts.ui_content import SAUDACAO, SIDEBAR_BODY, SIDEBAR_FOOTER
from src.app.ui import (
    carregar_sidebar,
    configurar_pagina,
    stream_resposta,
    exibir_historico_chat,
    exibir_mensagem_erro,
)
from src.config import logger
from src.core.database import salvar_erro, salvar_log_chat, salvar_sessao
from src.core.genai import (
    configurar_api_gemini,
    gerar_resposta,
    inicializar_chat_modelo,
    transcrever_audio,
)
from src.core.semantica import semantica
from src.utils import git_version

configurar_pagina()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    salvar_sessao(st.session_state.session_id)

if "hist_exibir" not in st.session_state:
    st.session_state.hist_exibir = [{"role": "model", "parts": [SAUDACAO]}]

carregar_sidebar(SIDEBAR_BODY, SIDEBAR_FOOTER)

st.session_state.key_api = configurar_api_gemini()

if st.session_state.get("key_api"):
    try:
        inicializar_chat_modelo()
    except Exception as e_init:
        logger.warning(f"Aviso ao inicializar chat conversacional: {e_init}")

exibir_historico_chat(st.session_state.hist_exibir)

if st.session_state.get("key_api"):
    prompt = st.chat_input("Digite aqui...")

    with st.popover("🎙️ Falar com Vox", help="Grave sua pergunta por voz para o Vox AI"):
        st.markdown(
            "<p style='font-size: 0.88rem; color: #CBD5E1; margin: 0 0 8px 0;'>"
            "🎙️ <b>Grave sua dúvida por voz:</b> Pressione o microfone abaixo para iniciar a gravação."
            "</p>",
            unsafe_allow_html=True,
        )
        audio_val = st.audio_input("Fale sua pergunta", label_visibility="collapsed")

    prompt_final = None

    if prompt and prompt.strip():
        prompt_final = prompt.strip()
    elif audio_val:
        if (
            "ultimo_audio_id" not in st.session_state
            or st.session_state.ultimo_audio_id != audio_val.name
        ):
            with st.spinner("Ouvindo e transcrevendo... 🎧"):
                texto_transcrito = transcrever_audio(audio_val)
                if texto_transcrito and texto_transcrito.strip():
                    prompt_final = texto_transcrito.strip()
                    st.session_state.ultimo_audio_id = audio_val.name

    if prompt_final:
        st.session_state.prompt = prompt_final
        st.session_state.hist_exibir.append({"role": "user", "parts": [prompt_final]})

        with st.chat_message("user"):
            st.markdown(prompt_final)

        try:
            avatar_assistant = "static/branding/icon.png" if os.path.exists("static/branding/icon.png") else "🌈"
            with st.chat_message("assistant", avatar=avatar_assistant):
                with st.spinner("Vox está pensando com carinho e acolhimento... 💜"):
                    tema_match, descricao_match, ids_referencia = semantica(prompt_final)

                    info_adicional_contexto = ""
                    if tema_match:
                        info_adicional_contexto = descricao_match
                    else:
                        descricao_match = "N/A"

                    resposta = gerar_resposta(
                        inicializar_chat_modelo(), prompt_final, info_adicional_contexto
                    )
                msg_placeholder = st.empty()
                msg_placeholder.write_stream(stream_resposta(resposta))

            st.session_state.hist_exibir.append({"role": "model", "parts": [resposta]})

            try:
                if isinstance(resposta, list):
                    resposta_log = " ".join(resposta)
                else:
                    resposta_log = str(resposta)

                salvar_log_chat(
                    st.session_state.session_id,
                    git_version(),
                    prompt_final,
                    resposta_log,
                    ids_referencia,
                )

            except Exception as e_log:
                logger.error(f"Falha silenciosa ao registrar log de conversa: {e_log}", exc_info=True)

            st.rerun()

        except Exception as e:
            error_id = salvar_erro(st.session_state.session_id, git_version(), e)
            exibir_mensagem_erro(error_id)