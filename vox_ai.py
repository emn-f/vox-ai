import io
import os
import re
import unicodedata
import uuid
import traceback

import streamlit as st

import startup_patch
from data.prompts.ui_content import SAUDACAO, SIDEBAR_BODY, SIDEBAR_FOOTER
from src.app.ui import (
    carregar_css,
    carregar_sidebar,
    configurar_pagina,
    stream_resposta,
)
from src.core.database import salvar_erro, salvar_log_chat, salvar_sessao
from src.core.genai import (
    configurar_api_gemini,
    gerar_resposta,
    inicializar_chat_modelo,
    transcrever_audio,
)
from src.core.semantica import semantica
from src.utils import texto_para_audio, git_version

configurar_pagina()
carregar_css()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    salvar_sessao(st.session_state.session_id)

carregar_sidebar(SIDEBAR_BODY, SIDEBAR_FOOTER)

st.session_state.key_api = configurar_api_gemini()

inicializar_chat_modelo()

for i, msg in enumerate(st.session_state.hist_exibir):
    if msg["role"] == "model":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["parts"][0], unsafe_allow_html=True)

            chave_botao = f"btn_audio_{i}"
            if st.button("🔊 Ouvir", key=chave_botao):
                audio_data = texto_para_audio(msg["parts"][0])
                st.audio(audio_data, format="audio/mp3")

    else:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(msg["parts"][0])

if "key_api" in st.session_state:
    if "primeira_vez" not in st.session_state:
        mensagem_boas_vindas = SAUDACAO
        st.session_state.hist_exibir.append(
            {"role": "model", "parts": [mensagem_boas_vindas]}
        )
        st.session_state.primeira_vez = True

        with st.chat_message("assistant", avatar="🤖"):
            msg_placeholder = st.empty()
            msg_placeholder.write_stream(stream_resposta(mensagem_boas_vindas))
            st.rerun()
    prompt = st.chat_input("Digite aqui...")

    with st.popover("🎙️", use_container_width=False):
        audio_val = st.audio_input("Fale sua pergunta")

    prompt_final = None

    if prompt:
        prompt_final = prompt
    elif audio_val:
        if (
            "ultimo_audio_id" not in st.session_state
            or st.session_state.ultimo_audio_id != audio_val.name
        ):
            with st.spinner("Ouvindo e transcrevendo... 🎧"):
                texto_transcrito = transcrever_audio(audio_val)
                if texto_transcrito:
                    prompt_final = texto_transcrito
                    st.session_state.ultimo_audio_id = audio_val.name

    if prompt_final:
        st.session_state.prompt = prompt_final
        st.session_state.hist.append({"role": "user", "parts": [prompt_final]})
        st.session_state.hist_exibir.append({"role": "user", "parts": [prompt_final]})

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt_final)

        try:

            tema_match, descricao_match, ids_referencia = semantica(prompt_final)

            info_adicional_contexto = ""
            if tema_match:
                info_adicional_contexto = descricao_match
            else:
                descricao_match = "N/A"

            with st.chat_message("assistant", avatar="🤖"):
                resposta = gerar_resposta(
                    inicializar_chat_modelo(), prompt_final, info_adicional_contexto
                )

            st.session_state.hist.append({"role": "model", "parts": [resposta]})
            st.session_state.hist_exibir.append({"role": "model", "parts": [resposta]})

            try:
                if isinstance(resposta, list):
                    resposta_log = " ".join(resposta)
                else:
                    resposta_log = str(resposta)

                desc_log = str(descricao_match) if descricao_match else "N/A"

                salvar_log_chat(
                    st.session_state.session_id,
                    git_version(),
                    prompt_final,
                    resposta_log,
                    tema_match,
                    ids_referencia,
                )

            except Exception as e_log:
                print(f"⚠️ Falha silenciosa ao registrar log de conversa: {e_log}")
                traceback.print_exc()

            st.rerun()

        except Exception as e:
            error_id = salvar_erro(st.session_state.session_id, git_version(), e)

            st.error(
                f"""
            Putz, algo deu errado por aqui :/
            
            Por favor, reporte este erro para nossa equipe informando o código: **{error_id}**
            """,
                icon="🚫",
            )
