import base64
import os
import time

from src.external_links import CONTRIBUTING
import streamlit as st

from collections.abc import Iterator
from src.config import CSS_PATH
from src.core.database import salvar_report, get_categorias_erro, salvar_erro, excluir_dados_sessao


def carregar_icone_base64() -> str:
    """Carrega o ícone oficial em formato Base64 para exibição no cabeçalho."""
    caminho_icone = "static/branding/icon.png"
    if os.path.exists(caminho_icone):
        try:
            with open(caminho_icone, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""


def configurar_pagina() -> None:
    """
    Configura as propriedades básicas da página web (título, ícone) no Streamlit 
    e renderiza o cabeçalho estilizado da aplicação.
    """
    st.set_page_config(page_title="Vox AI: Assistente de Apoio e Informação LGBTQIA+", page_icon="🌈")
    
    # Injeta script para atualizar as meta tags no head principal para visual móvel
    st.markdown(
        """
        <script>
            const doc = window.parent.document;
            
            // Atualiza ou cria a tag meta theme-color para a barra de endereços do celular
            let metaTheme = doc.querySelector('meta[name="theme-color"]');
            if (!metaTheme) {
                metaTheme = doc.createElement('meta');
                metaTheme.name = "theme-color";
                doc.getElementsByTagName('head')[0].appendChild(metaTheme);
            }
            metaTheme.content = "#7209b7";
            
            // Configurações para Safari no iOS
            let appleCapable = doc.querySelector('meta[name="apple-mobile-web-app-capable"]');
            if (!appleCapable) {
                appleCapable = doc.createElement('meta');
                appleCapable.name = "apple-mobile-web-app-capable";
                doc.getElementsByTagName('head')[0].appendChild(appleCapable);
            }
            appleCapable.content = "yes";

            let appleStatus = doc.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]');
            if (!appleStatus) {
                appleStatus = doc.createElement('meta');
                appleStatus.name = "apple-mobile-web-app-status-bar-style";
                doc.getElementsByTagName('head')[0].appendChild(appleStatus);
            }
            appleStatus.content = "black-translucent";
        </script>
        """,
        unsafe_allow_html=True,
    )

    icone_b64 = carregar_icone_base64()
    if icone_b64:
        img_tag = f'<img src="data:image/png;base64,{icone_b64}" class="vox-header-icon" alt="Vox AI Logo" />'
    else:
        img_tag = '<span style="font-size: 2.8rem; margin-right: 0.8rem;">🌈</span>'

    st.markdown(
        f"""
        <div class="vox-header-container">
            <div class="vox-header-card">
                <div class="vox-header-brand">
                    {img_tag}
                    <div class="vox-header-titles">
                        <div class="vox-brand-title">Vox<span class="vox-brand-ai">AI</span></div>
                        <div class="vox-brand-slogan">Informação é uma forma de cuidado</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def carregar_css(path=CSS_PATH) -> None:
    """
    Carrega e injeta arquivos CSS estáticos na página para customização visual do Streamlit.

    Args:
        path (str): Caminho local do arquivo CSS.
    """
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.dialog("🚩 Reportar Problema")
def dialog_reportar() -> None:
    """
    Exibe um modal/diálogo interativo para o usuário reportar comportamentos inadequados da IA,
    com formulário de categorização e minimização automática do histórico (LGPD Art. 6).
    """
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


@st.dialog("🤝 Rede de Apoio e Acolhimento", width="large")
def dialog_rede_apoio() -> None:
    """
    Exibe o diretório da Rede de Apoio e Acolhimento em modal interativo.
    """
    from src.app.pages.rede_apoio import render_rede_apoio
    render_rede_apoio(show_title=False)


def carregar_sidebar(sidebar_content: str, sidebar_footer: str) -> None:
    """
    Renderiza os elementos da barra lateral (sidebar), incluindo links de redes sociais,
    contatos, botão de limpeza de histórico, denúncias e o botão de exclusão de dados (LGPD).

    Args:
        sidebar_content (str): Código HTML/Markdown do conteúdo principal da barra lateral.
        sidebar_footer (str): Código HTML/Markdown do rodapé da barra lateral.
    """
    with st.sidebar:
        st.markdown(sidebar_content, unsafe_allow_html=True)

        st.link_button(
            label="❤️‍🔥 Quer contribuir com o Vox AI?",
            url=f"{CONTRIBUTING}",
            use_container_width=True,
        )

        if st.button("🤝 Rede de Apoio & Acolhimento", use_container_width=True):
            dialog_rede_apoio()

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
    """
    Gera um efeito de digitação ('typewriter') letra por letra na exibição da resposta do chat.

    Args:
        resposta (str): A resposta em string a ser transmitida.

    Yields:
        Iterator[str]: Caracteres da resposta um a um.
    """
    for letra in resposta:
        yield letra
        time.sleep(0.009)


def exibir_historico_chat(historico_conversa: list) -> None:
    """
    Exibe o histórico de conversa com o avatar e estilização apropriados.
    Também adiciona o player de áudio para respostas da inteligência artificial.
    """
    from src.utils import texto_para_audio
    
    avatar_assistant = "static/branding/icon.png" if os.path.exists("static/branding/icon.png") else "🌈"

    for i, msg in enumerate(historico_conversa):
        if msg["role"] == "model":
            with st.chat_message("assistant", avatar=avatar_assistant):
                st.markdown(msg["parts"][0], unsafe_allow_html=False)

                chave_botao = f"btn_audio_{i}"
                chave_audio_cache = f"audio_cache_{i}"

                # Exibe reprodutor direto se já foi sintetizado nesta sessão
                if chave_audio_cache in st.session_state:
                    audio_bytes = st.session_state[chave_audio_cache]
                    formato_audio = "audio/wav" if audio_bytes.startswith(b"RIFF") else "audio/mp3"
                    st.audio(audio_bytes, format=formato_audio)
                else:
                    if st.button("🔊 Ouvir resposta", key=chave_botao):
                        with st.spinner("🎙️ Gerando áudio..."):
                            audio_data = texto_para_audio(msg["parts"][0])
                            audio_bytes = audio_data.getvalue() if audio_data else b""
                            if audio_bytes:
                                st.session_state[chave_audio_cache] = audio_bytes
                                formato_audio = "audio/wav" if audio_bytes.startswith(b"RIFF") else "audio/mp3"
                                st.audio(audio_bytes, format=formato_audio)
        else:
            avatar_user = "static/branding/user_avatar.png" if os.path.exists("static/branding/user_avatar.png") else "👤"
            with st.chat_message("user", avatar=avatar_user):
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
