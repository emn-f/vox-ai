import time

import streamlit as st

from collections.abc import Iterator
from src.config import CSS_PATH
from src.core.database import salvar_report, get_categorias_erro, salvar_erro, excluir_dados_sessao


def configurar_pagina() -> None:
    st.set_page_config(page_title="Vox AI", page_icon="🏳️‍🌈")
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <h1 style="text-align: center">Vox AI</h1>
            <p style="text-align: center; color: gray;">Assistente de Apoio e Informação LGBTQIA+</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def carregar_css(path=CSS_PATH) -> None:
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.dialog("🚩 Reportar Problema")
def dialog_reportar() -> None:
    historico_conversa = st.session_state.get("hist_exibir", [])

    if len(historico_conversa) <= 1:
        st.warning("Sem histórico de conversa para reportar!")
        if st.button("Fechar"):
            st.rerun()
        return

    st.markdown("### Nova Denúncia 🚧")
    st.write("Identificou algum comportamento inadequado? Nos ajude a melhorar.")

    lista_categorias = get_categorias_erro()
    find_categorias = {item["label"]: item["id"] for item in lista_categorias}

    if not find_categorias:
        st.error("Erro ao carregar categorias. Tente novamente mais tarde.")
        return

    categoria = st.selectbox("Qual o motivo?", list(find_categorias.keys()))
    comentario = st.text_area(
        "Descreva o que aconteceu:", placeholder="Ex: A IA foi agressiva...", height=70
    )

    col_cancel, col_submit = st.columns([1, 1])

    with col_cancel:
        if st.button("Cancelar"):
            st.rerun()

    with col_submit:
        if st.button("Enviar Denúncia", type="primary"):
            with st.spinner("Enviando..."):
                version = st.session_state.get("git_version_str", "Unknown")
                sess_id = st.session_state.get("session_id", "Unknown")
                cat_id = find_categorias[categoria]

                try:
                    # Minimização de dados (LGPD Art. 6, III): envia apenas os últimos 3 turnos de conversa (6 mensagens)
                    historico_minimizado = historico_conversa[-6:] if len(historico_conversa) > 6 else historico_conversa
                    sucesso = salvar_report(
                        sess_id,
                        version,
                        str(historico_minimizado),
                        cat_id,
                        comentario,
                    )
                    if sucesso:
                        st.success("Denúncia enviada com sucesso! Obrigado.")
                        time.sleep(2)
                        st.rerun()

                except Exception as e:
                    error_id = salvar_erro(
                        st.session_state.get("session_id", "Unknown"),
                        st.session_state.get("git_version_str", "Unknown"),
                        e
                    )

                    st.error(
                        f"""
                        Erro ao enviar denúncia. Por favor, reporte este erro para nossa equipe informando o código: **{error_id}**
                        """
                    )
                    return


def carregar_sidebar(sidebar_content: str, sidebar_footer: str) -> None:
    with st.sidebar:
        # Body
        st.markdown(sidebar_content, unsafe_allow_html=True)

        st.link_button(
            label="💛 Ajude o Vox a crescer!",
            url="https://forms.gle/fw8CNXaFme3FnNxn6",
            use_container_width=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 Limpar conversa", use_container_width=True):
                st.session_state.pop("hist_exibir", None)
                st.session_state.pop("chat", None)
                st.rerun()
        with col2:
            if st.button("🚩 Reportar", use_container_width=True):
                dialog_reportar()

        if st.button("🗑️ Excluir meus dados desta sessão", use_container_width=True, type="secondary"):
            import time
            with st.spinner("Excluindo dados do servidor..."):
                if excluir_dados_sessao(st.session_state.get("session_id", "")):
                    st.session_state.pop("session_id", None)
                    st.session_state.pop("hist_exibir", None)
                    st.session_state.pop("chat", None)
                    st.success("Dados excluídos com sucesso! 🛡️")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Falha ao excluir dados. Por favor, tente novamente.")
        st.markdown("---")

        # Footer
        st.markdown(sidebar_footer, unsafe_allow_html=True)


def stream_resposta(resposta: str) -> Iterator[str]:
    for letra in resposta:
        yield letra
        time.sleep(0.009)


def exibir_historico_chat(historico_conversa: list) -> None:
    """
    Exibe o histórico de conversa com o avatar e estilização apropriados.
    Também adiciona o player de áudio para respostas da inteligência artificial.
    """
    from src.utils import texto_para_audio
    
    for i, msg in enumerate(historico_conversa):
        if msg["role"] == "model":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["parts"][0], unsafe_allow_html=False)

                chave_botao = f"btn_audio_{i}"
                if st.button("🔊 Ouvir", key=chave_botao):
                    audio_data = texto_para_audio(msg["parts"][0])
                    st.audio(audio_data, format="audio/mp3")
        else:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(msg["parts"][0])


def exibir_mensagem_erro(error_id: str) -> None:
    """
    Renderiza um painel de erro amigável instruindo o usuário a reportar o ID do erro.
    """
    st.error(
        f"""
        Putz, algo deu errado por aqui :/
        
        Por favor, reporte este erro para nossa equipe informando o código: **{error_id}**
        """,
        icon="🚫",
    )
