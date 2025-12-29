import time

import streamlit as st

from src.config import CSS_PATH
from src.core.database import salvar_report, get_categorias_erro


def configurar_pagina():
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


def carregar_css(path=CSS_PATH):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def carregar_sidebar(sidebar_content, git_version, kb_version):
    with st.sidebar:
        col_clear, col_report = st.columns([0.3, 0.3])

        if st.button("🧹 Limpar", help="Limpar histórico do chat"):
            st.session_state.pop("hist", None)
            st.session_state.pop("hist_exibir", None)
            st.rerun()

        with st.popover("🚩 Reportar", help="Reportar conversa inadequada"):

            historico_conversa = st.session_state.get("hist_exibir", [])
            if len(historico_conversa) <= 1:
                st.warning("Sem histórico de conversa para reportar!")
            else:
                st.markdown("### Nova Denúncia 🚧")
                lista_categorias = get_categorias_erro()
                find_categorias = {
                    item["label"]: item["id"] for item in lista_categorias
                }
                if not find_categorias:
                    st.error("Erro ao carregar categorias.")
                else:
                    categoria = st.selectbox(
                        "Selecione a categoria", list(find_categorias.keys())
                    )
                st.text_area("Por favor, descreva o que aconteceu:", key="comment")
                if st.button("Confirmar denúncia", type="primary"):
                    with st.spinner("Enviando..."):
                        version = st.session_state.get("git_version_str", "Unknown")
                        sess_id = st.session_state.get("session_id", "Unknown")
                        cat_id = find_categorias[categoria]
                        sucesso = salvar_report(
                            sess_id,
                            version,
                            str(historico_conversa),
                            cat_id,
                            st.session_state.get("comment", ""),
                        )

                        if sucesso:
                            st.toast("Denúncia enviada!", icon="✅")
                        else:
                            st.toast("Erro ao reportar.", icon="❌")

        st.link_button(
            label="💛 Ajude o Vox a crescer!",
            url="https://forms.gle/fw8CNXaFme3FnNxn6",
            help="Ajude a expandir o conhecimento da IA respondendo um formulário rápido.",
        )

        st.markdown("---")
        st.markdown(sidebar_content, unsafe_allow_html=True)

        version_display = f"""
        <div style='color: #88888888; text-align: center; margin: auto; font-size: 0.9em;'>
            {git_version} | KB: {kb_version}
        </div>
        """
        st.sidebar.markdown(version_display, unsafe_allow_html=True)


def stream_resposta(resposta):
    for letra in resposta:
        yield letra
        time.sleep(0.009)
