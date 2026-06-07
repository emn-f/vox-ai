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

import uuid

import streamlit as st

import startup_patch

from data.prompts.ui_content import SAUDACAO, SIDEBAR_BODY, SIDEBAR_FOOTER
from src.app.ui import (
    carregar_css,
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
carregar_css()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    salvar_sessao(st.session_state.session_id)

carregar_sidebar(SIDEBAR_BODY, SIDEBAR_FOOTER)

st.session_state.key_api = configurar_api_gemini()

inicializar_chat_modelo()

exibir_historico_chat(st.session_state.hist_exibir)

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