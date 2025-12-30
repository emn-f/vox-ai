import time

import streamlit as st

from src.config import CSS_PATH
from src.core.database import salvar_report, get_categorias_erro, salvar_erro


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


@st.dialog("🚩 Reportar Problema")
def dialog_reportar():
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
                    sucesso = salvar_report(
                        sess_id,
                        version,
                        str(historico_conversa),
                        cat_id,
                        comentario,
                    )
                    if sucesso:
                        st.success("Denúncia enviada com sucesso! Obrigado.")
                        time.sleep(2)
                        st.rerun()

                except Exception as e:
                    error_id = salvar_erro(
                        st.session_state.session_id, st.session_state.git_version_str, e
                    )

                    st.error(
                        f"""
                        Erro ao enviar denúncia. Por favor, reporte este erro para nossa equipe informando o código: **{error_id}**
                        """
                    )
                    return


def carregar_sidebar(sidebar_content, git_version, kb_version):
    with st.sidebar:
        col_clear, col_report = st.columns([0.4, 0.6])

        with col_clear:
            if st.button("🧹 Limpar", help="Limpar histórico do chat"):
                st.session_state.pop("hist", None)
                st.session_state.pop("hist_exibir", None)
                st.rerun()

        with col_report:
            if st.button("🚩 Reportar", help="Reportar conversa inadequada"):
                dialog_reportar()

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
