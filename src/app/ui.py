import base64
import os
import time
from collections.abc import Iterator

import streamlit as st

from src.config import CSS_PATH
from src.core.database import (
    excluir_dados_sessao,
    get_categorias_erro,
    salvar_erro,
    salvar_report,
)
from src.external_links import CONTRIBUTING
from src.i18n import (
    SUPPORTED_LANGS,
    get_active_lang,
    get_saudacao,
    normalize_lang,
    resolve_lang,
    t,
    translate_report_category,
)


def carregar_icone_base64() -> str:
    """Carrega o ícone oficial como data URI Base64 (SVG vetorial com fallback PNG) para o cabeçalho."""
    fontes = (
        ("static/branding/icon.svg", "image/svg+xml"),
        ("static/branding/icon.png", "image/png"),
    )
    for caminho_icone, mime_type in fontes:
        if os.path.exists(caminho_icone):
            try:
                with open(caminho_icone, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime_type};base64,{b64}"
            except Exception:
                continue
    return ""


def configurar_pagina(lang: str | None = None) -> str:
    """
    Configura as propriedades básicas da página web (título, ícone) no Streamlit
    e renderiza o cabeçalho estilizado da aplicação.

    Args:
        lang (str | None): Idioma ativo da interface ('pt' ou 'en').

    Returns:
        str: Idioma ativo da interface.
    """
    page_lang = normalize_lang(lang) if lang is not None else "pt"
    page_icon = "static/branding/icon.png" if os.path.exists("static/branding/icon.png") else "🌈"
    st.set_page_config(page_title=t("page_title", page_lang), page_icon=page_icon)
    # Resolve o idioma só depois da configuração, pois isso acessa o estado do Streamlit.
    active_lang = normalize_lang(lang) if lang is not None else resolve_lang()

    # O CSS precisa ser injetado antes do cabeçalho; caso contrário a logo
    # aparece sem estilo (tamanho original) por um instante e depois "pula".
    carregar_css()

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
        icone_src = (
            icone_b64 if icone_b64.startswith("data:") else f"data:image/png;base64,{icone_b64}"
        )
        img_tag = f'<img src="{icone_src}" class="vox-header-icon" alt="Vox AI Logo" />'
    else:
        img_tag = '<span style="font-size: 2.8rem; margin-right: 0.8rem;">🌈</span>'

    slogan = t("slogan", active_lang)
    st.markdown(
        f"""
        <div class="vox-header-container">
            <div class="vox-header-card">
                <div class="vox-header-brand">
                    {img_tag}
                    <div class="vox-header-titles">
                        <div class="vox-brand-title">Vox<span class="vox-brand-ai">AI</span></div>
                        <div class="vox-brand-slogan">{slogan}</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return active_lang


def carregar_css(path: str = CSS_PATH) -> None:
    """
    Carrega e injeta arquivos CSS estáticos na página para customização visual do Streamlit.

    Args:
        path (str): Caminho local do arquivo CSS.
    """
    with open(path) as f:
        linhas = f.read().splitlines()

    # @import bloqueia a aplicação das demais regras do <style> até a fonte
    # chegar; por isso é injetado em um bloco separado, depois do CSS principal.
    imports = [ln for ln in linhas if ln.lstrip().startswith("@import")]
    corpo = "\n".join(ln for ln in linhas if not ln.lstrip().startswith("@import"))

    st.markdown(f"<style>{corpo}</style>", unsafe_allow_html=True)
    if imports:
        st.markdown(f"<style>{' '.join(imports)}</style>", unsafe_allow_html=True)


def _render_dialog_reportar(lang: str) -> None:
    """
    Renderiza o conteúdo do modal de denúncia no idioma ativo.

    Args:
        lang (str): Idioma ativo ('pt' ou 'en').
    """
    active_lang = normalize_lang(lang)
    historico_conversa = st.session_state.get("hist_exibir", [])

    if len(historico_conversa) <= 1:
        st.warning(t("report_no_history", active_lang))
        if st.button(t("report_close", active_lang)):
            st.rerun()
        return

    st.markdown(t("report_heading", active_lang))
    st.write(t("report_subtitle", active_lang))

    lista_categorias = get_categorias_erro()
    find_categorias = {
        translate_report_category(int(item["id"]), str(item["label"]), active_lang): item["id"]
        for item in lista_categorias
    }

    if not find_categorias:
        st.error(t("report_cat_load_error", active_lang))
        return

    categoria = st.selectbox(t("report_reason_label", active_lang), list(find_categorias.keys()))
    comentario = st.text_area(
        t("report_comment_label", active_lang),
        placeholder=t("report_comment_placeholder", active_lang),
        height=70,
    )

    col_cancel, col_submit = st.columns([1, 1])

    with col_cancel:
        if st.button(t("report_cancel", active_lang)):
            st.rerun()

    with col_submit:
        if st.button(t("report_submit", active_lang), type="primary"):
            with st.spinner(t("report_sending", active_lang)):
                version = st.session_state.get("git_version_str", "Unknown")
                sess_id = st.session_state.get("session_id", "Unknown")
                cat_id = find_categorias[categoria]

                try:
                    # Minimização de dados (LGPD Art. 6, III): envia apenas os últimos 3 turnos de conversa (6 mensagens)
                    historico_minimizado = (
                        historico_conversa[-6:] if len(historico_conversa) > 6 else historico_conversa
                    )
                    sucesso = salvar_report(
                        sess_id,
                        version,
                        str(historico_minimizado),
                        cat_id,
                        comentario,
                    )
                    if sucesso:
                        st.success(t("report_success", active_lang))
                        time.sleep(2)
                        st.rerun()

                except Exception as e:
                    error_id = salvar_erro(
                        st.session_state.get("session_id", "Unknown"),
                        st.session_state.get("git_version_str", "Unknown"),
                        e,
                    )
                    st.error(t("report_error", active_lang, error_id=error_id))
                    return


@st.dialog("🚩 Reportar Problema")
def _dialog_reportar_pt() -> None:
    """Modal de denúncia em português."""
    _render_dialog_reportar("pt")


@st.dialog("🚩 Report an Issue")
def _dialog_reportar_en() -> None:
    """Modal de denúncia em inglês."""
    _render_dialog_reportar("en")


def dialog_reportar(lang: str | None = None) -> None:
    """
    Exibe o modal/diálogo interativo para o usuário reportar comportamentos inadequados da IA,
    com formulário de categorização e minimização automática do histórico (LGPD Art. 6).

    Args:
        lang (str | None): Idioma ativo ('pt' ou 'en'). Se omitido, lê de st.session_state.
    """
    active_lang = normalize_lang(lang) if lang is not None else get_active_lang()
    if active_lang == "en":
        _dialog_reportar_en()
    else:
        _dialog_reportar_pt()


def _render_dialog_rede_apoio(lang: str) -> None:
    """Renderiza o diretório da Rede de Apoio no idioma especificado."""
    from src.app.pages.rede_apoio import render_rede_apoio

    render_rede_apoio(show_title=False, lang=normalize_lang(lang))


@st.dialog("🤝 Rede de Apoio e Acolhimento", width="large")
def _dialog_rede_apoio_pt() -> None:
    """Modal da Rede de Apoio em português."""
    _render_dialog_rede_apoio("pt")


@st.dialog("🤝 Support Network Directory", width="large")
def _dialog_rede_apoio_en() -> None:
    """Modal da Rede de Apoio em inglês."""
    _render_dialog_rede_apoio("en")


def dialog_rede_apoio(lang: str | None = None) -> None:
    """
    Exibe o diretório da Rede de Apoio e Acolhimento em modal interativo.

    Args:
        lang (str | None): Idioma ativo ('pt' ou 'en'). Se omitido, lê de st.session_state.
    """
    active_lang = normalize_lang(lang) if lang is not None else get_active_lang()
    if active_lang == "en":
        _dialog_rede_apoio_en()
    else:
        _dialog_rede_apoio_pt()


def _limpar_cache_audio_sessao() -> None:
    """Remove caches temporários de áudio sintetizado do st.session_state."""
    for key in list(st.session_state.keys()):
        if isinstance(key, str) and key.startswith("audio_cache_"):
            st.session_state.pop(key, None)


def _aplicar_troca_idioma(novo_idioma: str) -> None:
    """
    Atualiza o idioma ativo na sessão, sincroniza query params e atualiza a saudação inicial.

    Args:
        novo_idioma (str): Idioma selecionado ('pt' ou 'en').
    """
    norm = normalize_lang(novo_idioma)
    st.session_state["lang"] = norm

    try:
        if hasattr(st, "query_params"):
            if norm == "en":
                st.query_params["lang"] = "en"
            elif "lang" in st.query_params:
                del st.query_params["lang"]
    except Exception:
        pass

    # Se o chat só tem a saudação inicial, atualiza para o novo idioma na hora
    hist = st.session_state.get("hist_exibir")
    if isinstance(hist, list) and len(hist) == 1 and hist[0].get("role") == "model":
        st.session_state["hist_exibir"] = [{"role": "model", "parts": [get_saudacao(norm)]}]
        st.session_state.pop("audio_cache_0", None)


def _render_seletor_idioma(active_lang: str) -> str | None:
    """
    Renderiza o controle de seleção de idioma (Português | English) na sidebar.

    Args:
        active_lang (str): Idioma atualmente ativo.

    Returns:
        str | None: Novo idioma selecionado ou None.
    """
    lang_labels = {"pt": "Português", "en": "English"}
    if hasattr(st, "segmented_control"):
        try:
            return st.segmented_control(
                t("sidebar_lang_label", active_lang),
                options=list(SUPPORTED_LANGS),
                default=active_lang,
                required=True,
                format_func=lambda code: lang_labels.get(code, code),
                key="sidebar_lang_selector",
                width="stretch",
            )
        except TypeError:
            return st.segmented_control(
                t("sidebar_lang_label", active_lang),
                options=list(SUPPORTED_LANGS),
                default=active_lang,
                format_func=lambda code: lang_labels.get(code, code),
                key="sidebar_lang_selector",
            )

    return st.radio(
        t("sidebar_lang_label", active_lang),
        options=list(SUPPORTED_LANGS),
        index=0 if active_lang == "pt" else 1,
        format_func=lambda code: lang_labels.get(code, code),
        horizontal=True,
        key="sidebar_lang_selector",
    )


def carregar_sidebar(sidebar_content: str, sidebar_footer: str, lang: str | None = None) -> None:
    """
    Renderiza os elementos da barra lateral (sidebar), incluindo seletor de idioma,
    links de redes sociais, contatos, limpeza de histórico, denúncias e exclusão de dados (LGPD).

    Args:
        sidebar_content (str): Código HTML/Markdown do conteúdo principal da barra lateral.
        sidebar_footer (str): Código HTML/Markdown do rodapé da barra lateral.
        lang (str | None): Idioma ativo ('pt' ou 'en').
    """
    active_lang = normalize_lang(lang) if lang is not None else get_active_lang()

    with st.sidebar:
        selected_lang = _render_seletor_idioma(active_lang)
        if selected_lang and selected_lang != active_lang:
            _aplicar_troca_idioma(selected_lang)
            st.rerun()

        st.markdown(sidebar_content, unsafe_allow_html=True)

        st.link_button(
            label=t("sidebar_btn_contribute", active_lang),
            url=f"{CONTRIBUTING}",
            use_container_width=True,
        )

        if st.button(t("sidebar_btn_support", active_lang), use_container_width=True):
            dialog_rede_apoio(active_lang)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("sidebar_btn_clear", active_lang), use_container_width=True):
                st.session_state.pop("hist_exibir", None)
                st.session_state.pop("chat", None)
                _limpar_cache_audio_sessao()
                st.rerun()
        with col2:
            if st.button(t("sidebar_btn_report", active_lang), use_container_width=True):
                dialog_reportar(active_lang)

        if st.button(
            t("sidebar_btn_delete", active_lang),
            use_container_width=True,
            type="secondary",
        ):
            with st.spinner(t("sidebar_deleting_spinner", active_lang)):
                if excluir_dados_sessao(st.session_state.get("session_id", "")):
                    st.session_state.pop("session_id", None)
                    st.session_state.pop("hist_exibir", None)
                    st.session_state.pop("chat", None)
                    _limpar_cache_audio_sessao()
                    st.success(t("sidebar_deleted_ok", active_lang))
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error(t("sidebar_deleted_err", active_lang))
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


def exibir_historico_chat(historico_conversa: list, lang: str | None = None) -> None:
    """
    Exibe o histórico de conversa com o avatar e estilização apropriados.
    Também adiciona o player de áudio para respostas da inteligência artificial.

    Args:
        historico_conversa (list): Lista de mensagens do histórico.
        lang (str | None): Idioma ativo ('pt' ou 'en').
    """
    from src.utils import texto_para_audio

    active_lang = normalize_lang(lang) if lang is not None else get_active_lang()
    avatar_assistant = (
        "static/branding/icon.png" if os.path.exists("static/branding/icon.png") else "🌈"
    )

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
                    if st.button(t("listen_btn", active_lang), key=chave_botao):
                        with st.spinner(t("spinner_audio", active_lang)):
                            if active_lang == "pt":
                                audio_data = texto_para_audio(msg["parts"][0])
                            else:
                                audio_data = texto_para_audio(msg["parts"][0], lang=active_lang)
                            audio_bytes = audio_data.getvalue() if audio_data else b""
                            if audio_bytes:
                                st.session_state[chave_audio_cache] = audio_bytes
                                formato_audio = (
                                    "audio/wav" if audio_bytes.startswith(b"RIFF") else "audio/mp3"
                                )
                                st.audio(audio_bytes, format=formato_audio)
        else:
            with st.chat_message("user"):
                st.markdown(msg["parts"][0])


def exibir_mensagem_erro(error_id: str, lang: str | None = None) -> None:
    """
    Renderiza um painel de erro amigável instruindo o usuário a reportar o ID do erro.

    Args:
        error_id (str): Código identificador do erro registrado.
        lang (str | None): Idioma ativo ('pt' ou 'en').
    """
    active_lang = normalize_lang(lang) if lang is not None else get_active_lang()
    st.error(t("error_generic", active_lang, error_id=error_id), icon="🚫")
