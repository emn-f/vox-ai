"""
Módulo de internacionalização (i18n) do Vox AI para a interface Streamlit.

Centraliza textos traduzidos entre português brasileiro (pt) e inglês (en),
resolução de idioma via estado de sessão e query params (?lang=en), e
mapeamento de categorias de denúncia vindas do banco de dados.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.external_links import (
    CONTRIBUTING,
    CVV_LINK,
    DISQUE_100,
    EMAIL_CONTATO,
    GITHUB,
    INSTAGRAM_VOX,
    LINKEDIN_VOX,
    LINKTREE_VOX,
    POLICY_PRIVACY,
    TERMS_OF_USE,
)
from src.utils import git_version

SUPPORTED_LANGS: tuple[str, ...] = ("pt", "en")
DEFAULT_LANG: str = "pt"

REPORT_CATEGORY_EN: dict[int, str] = {
    1: "Inaccurate info / Hallucination",
    2: "Code of Conduct violation",
    3: "Offensive content",
    4: "Bug / Technical issue",
    5: "Other",
}

SUPPORT_CATEGORY_EN: dict[str, str] = {
    "Todas as Categorias": "All Categories",
    "Casas de Acolhimento": "Shelters & Housing",
    "Centros Públicos de Referência": "Public Reference Centers",
    "ONGs e Coletivos": "NGOs & Collectives",
    "Saúde e Ambulatórios": "Healthcare & Clinics",
    "Profissionais Afirmativos": "Affirmative Professionals",
}

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt": {
        "page_title": "Vox AI: Assistente de Apoio e Informação LGBTQIA+",
        "slogan": "Informação é uma forma de cuidado",
        "greeting": (
            "\nOi! Que bom te ver por aqui. Sou o Vox AI, seu espaço seguro para tirar dúvidas "
            "sobre saúde, direitos, acolhimento e tudo que envolve a comunidade LGBTQIA+. \n\n"
            "Como posso te ajudar agora?\n"
        ),
        "chat_input": "Digite aqui...",
        "voice_btn": "🎙️ Falar com Vox",
        "voice_help": "Grave sua pergunta por voz para o Vox AI",
        "voice_prompt": (
            "🎙️ <b>Grave sua dúvida por voz:</b> "
            "Pressione o microfone abaixo para iniciar a gravação."
        ),
        "voice_label": "Fale sua pergunta",
        "spinner_transcribing": "Ouvindo e transcrevendo... 🎧",
        "spinner_thinking": "Vox está pensando com carinho e acolhimento... 💜",
        "spinner_audio": "🎙️ Gerando áudio...",
        "listen_btn": "🔊 Ouvir resposta",
        "sidebar_lang_label": "Idioma / Language",
        "sidebar_about_title": "Sobre o Projeto",
        "sidebar_about_body": (
            "O <b>Vox AI</b> é um assistente de apoio e informação <b>LGBTQIA+</b>. "
            "Criado como projeto de extensão na UCSAL e mantido hoje de forma independente "
            "e open source para oferecer um espaço seguro de acolhimento."
        ),
        "sidebar_help_title": "Precisa de ajuda agora?",
        "sidebar_help_188": "Ligue 188 (Apoio Emocional)",
        "sidebar_help_188_title": "Centro de Valorização da Vida",
        "sidebar_help_100": "Disque 100 (Direitos Humanos)",
        "sidebar_help_100_title": "Direitos Humanos",
        "sidebar_social_title": "Redes Sociais do Vox",
        "sidebar_email_title": "E-mail de Contato",
        "sidebar_btn_contribute": "❤️‍🔥 Contribua com o projeto Vox AI",
        "sidebar_btn_support": "🤝 Rede de Apoio & Acolhimento",
        "sidebar_btn_clear": "🧹 Limpar conversa",
        "sidebar_btn_report": "🚩 Reportar",
        "sidebar_btn_delete": "🗑️ Excluir meus dados desta sessão",
        "sidebar_deleting_spinner": "Excluindo dados do servidor...",
        "sidebar_deleted_ok": "Dados excluídos com sucesso! 🛡️",
        "sidebar_deleted_err": "❌ Falha ao excluir dados. Por favor, tente novamente.",
        "sidebar_terms": "Termos de Uso",
        "sidebar_privacy": "Política de Privacidade",
        "report_dialog_title": "🚩 Reportar Problema",
        "report_no_history": "Sem histórico de conversa para reportar!",
        "report_close": "Fechar",
        "report_heading": "### Nova Denúncia 🚧",
        "report_subtitle": "Identificou algum comportamento inadequado? Nos ajude a melhorar.",
        "report_cat_load_error": "Erro ao carregar categorias. Tente novamente mais tarde.",
        "report_reason_label": "Qual o motivo?",
        "report_comment_label": "Descreva o que aconteceu:",
        "report_comment_placeholder": "Ex: A IA foi agressiva...",
        "report_cancel": "Cancelar",
        "report_submit": "Enviar Denúncia",
        "report_sending": "Enviando...",
        "report_success": "Denúncia enviada com sucesso! Obrigado.",
        "report_error": (
            "\n                        Erro ao enviar denúncia. Por favor, reporte este erro "
            "para nossa equipe informando o código: **{error_id}**\n                        "
        ),
        "support_dialog_title": "🤝 Rede de Apoio e Acolhimento",
        "support_page_title": "🤝 Rede de Apoio e Acolhimento Vox",
        "support_intro": (
            "Conectamos você a **casas de acolhimento parceiras**, **centros públicos de referência**, "
            "**ONGs combativas** e **profissionais de saúde e direito afirmativos** em todo o Brasil. 🏳️‍🌈"
        ),
        "support_sos_title": "Precisa de Ajuda Imediata?",
        "support_sos_desc": (
            "Se você está sofrendo violência física, ameaça à vida ou crise emocional severa, "
            "contate os canais públicos gratuitos:"
        ),
        "support_sos_100": "📞 Disque 100 — Direitos Humanos &amp; LGBTfobia",
        "support_sos_188": "💛 CVV 188 — Apoio Emocional e Prevenção",
        "support_sos_190": "🛡️ 190 — Polícia Militar em Caso de Risco",
        "support_search_label": "🔍 Buscar por nome, serviço ou palavra-chave:",
        "support_search_placeholder": "Ex: moradia, trans, jurídico, psicologia...",
        "support_cat_label": "Categoria:",
        "support_cat_all": "Todas as Categorias",
        "support_uf_label": "Localização:",
        "support_uf_all": "Todos os Estados",
        "support_uf_national": "Nacional",
        "support_free_only": "Apenas serviços 100% gratuitos ou SUS",
        "support_results_count": "**Exibindo {count} locais e iniciativas encontradas:**",
        "support_empty": "Nenhuma iniciativa encontrada para os filtros selecionados. Tente expandir a busca.",
        "support_visit_btn": "🌐 Visitar Site / Redes",
        "support_whatsapp_btn": "💬 Falar no WhatsApp",
        "support_contact_caption": "📞 Contato: **{contact}**",
        "support_collab_heading": "### 📝 Representa uma instituição ou quer sugerir um serviço?",
        "support_collab_desc": (
            "Nossa rede é colaborativa e passa por verificação para garantir acolhimento seguro "
            "à comunidade LGBTQIA+. Envie sua sugestão pelo formulário ou fale com a equipe por e-mail."
        ),
        "support_collab_form_btn": "✨ Sugerir instituição pelo formulário",
        "support_collab_email_btn": "✉️ Enviar e-mail para a equipe",
        "error_generic": (
            "\n        Putz, algo deu errado por aqui :/\n        \n        "
            "Por favor, reporte este erro para nossa equipe informando o código: **{error_id}**\n        "
        ),
        "error_safety": (
            "⚠️ **Essa pergunta não pode ser respondida pelo Vox.**\n\n"
            "Por razões de segurança e acolhimento, sua mensagem ativou nossas diretrizes de proteção e não pôde ser processada.\n\n"
            "*(Código do Erro: **{error_id}**)*"
        ),
        "error_quota": (
            "Olá! O Vox está recebendo muitas mensagens de carinho e dúvidas no momento, e atingimos nosso limite de processamento temporário da API do Google. "
            "Por favor, aguarde cerca de um minutinho e tente enviar sua mensagem novamente! 💜\n\n"
            "*(Código do Erro: **{error_id}**)*"
        ),
        "error_unavailable": (
            "Ops! Os servidores da inteligência artificial estão com uma demanda muito alta agora e temporariamente instáveis. "
            "Que tal respirar fundo, tomar uma água e tentar de novo em alguns instantes? Estarei aqui esperando! 🏳️‍🌈\n\n"
            "*(Código do Erro: **{error_id}**)*"
        ),
        "toast_model_fallback": "Servidor ocupado. Alternando para contingência ({proximo_modelo})...",
        "toast_audio_fallback": "Instabilidade no áudio. Tentando modelo alternativo ({proximo})...",
    },
    "en": {
        "page_title": "Vox AI: LGBTQIA+ Support and Information Assistant",
        "slogan": "Information is a form of care",
        "greeting": (
            "\nHi! Glad you're here. I'm Vox AI, a safe space to ask about healthcare, "
            "rights, support services, and LGBTQIA+ topics in Brazil.\n\n"
            "How can I help you today?\n"
        ),
        "chat_input": "Type your message...",
        "voice_btn": "🎙️ Speak with Vox",
        "voice_help": "Record your voice question for Vox AI",
        "voice_prompt": (
            "🎙️ <b>Record your question by voice:</b> "
            "Press the microphone below to start recording."
        ),
        "voice_label": "Speak your question",
        "spinner_transcribing": "Listening and transcribing... 🎧",
        "spinner_thinking": "Vox is thinking with care... 💜",
        "spinner_audio": "🎙️ Generating audio...",
        "listen_btn": "🔊 Listen to response",
        "sidebar_lang_label": "Idioma / Language",
        "sidebar_about_title": "About the Project",
        "sidebar_about_body": (
            "<b>Vox AI</b> is an <b>LGBTQIA+</b> support and information assistant. "
            "Started as a university extension project at UCSAL and now maintained independently "
            "as open-source software to offer a safe, welcoming space."
        ),
        "sidebar_help_title": "Need help right now?",
        "sidebar_help_188": "Call 188 (CVV — Brazil)",
        "sidebar_help_188_title": "Center for the Valorization of Life (Brazil)",
        "sidebar_help_100": "Dial 100 (Human Rights — Brazil)",
        "sidebar_help_100_title": "Human Rights Hotline (Brazil)",
        "sidebar_social_title": "Social & Contact",
        "sidebar_email_title": "Contact Email",
        "sidebar_btn_contribute": "❤️‍🔥 Contribute to Vox AI",
        "sidebar_btn_support": "🤝 Support Network",
        "sidebar_btn_clear": "🧹 Clear chat",
        "sidebar_btn_report": "🚩 Report",
        "sidebar_btn_delete": "🗑️ Delete my session data",
        "sidebar_deleting_spinner": "Deleting session data from server...",
        "sidebar_deleted_ok": "Session data deleted successfully! 🛡️",
        "sidebar_deleted_err": "❌ Failed to delete data. Please try again.",
        "sidebar_terms": "Terms of Use",
        "sidebar_privacy": "Privacy Policy",
        "report_dialog_title": "🚩 Report an Issue",
        "report_no_history": "No conversation history to report yet!",
        "report_close": "Close",
        "report_heading": "### New Report 🚧",
        "report_subtitle": "Spotted inaccurate info or an unexpected response? Let us know.",
        "report_cat_load_error": "Failed to load report categories. Please try again later.",
        "report_reason_label": "Reason",
        "report_comment_label": "Describe what happened:",
        "report_comment_placeholder": "E.g. The response included outdated details...",
        "report_cancel": "Cancel",
        "report_submit": "Submit Report",
        "report_sending": "Sending...",
        "report_success": "Report submitted successfully! Thank you.",
        "report_error": (
            "\nFailed to submit report. Please let our team know and share error code: **{error_id}**\n"
        ),
        "support_dialog_title": "🤝 Support Network Directory",
        "support_page_title": "🤝 Vox Support Network Directory",
        "support_intro": (
            "Connecting you with **partner shelters**, **public reference centers**, "
            "and **vetted LGBTQIA+ NGOs and clinics** across Brazil. 🏳️‍🌈"
        ),
        "support_sos_title": "Need Immediate Help?",
        "support_sos_desc": (
            "If you are facing physical violence, immediate danger, or a severe emotional crisis "
            "in Brazil, contact free public emergency channels:"
        ),
        "support_sos_100": "📞 Dial 100 — Human Rights (Brazil)",
        "support_sos_188": "💛 Call 188 — Emotional Support (CVV, Brazil)",
        "support_sos_190": "🛡️ 190 — Emergency Police (Brazil)",
        "support_search_label": "🔍 Search by name, service, or keyword:",
        "support_search_placeholder": "E.g. housing, trans, legal aid, mental health...",
        "support_cat_label": "Category:",
        "support_cat_all": "All Categories",
        "support_uf_label": "Location:",
        "support_uf_all": "All States",
        "support_uf_national": "National",
        "support_free_only": "Only 100% free or SUS public services",
        "support_results_count": "**Showing {count} verified places and initiatives:**",
        "support_empty": "No initiatives found for the selected filters. Try broadening your search.",
        "support_visit_btn": "🌐 Visit Website",
        "support_whatsapp_btn": "💬 Chat on WhatsApp",
        "support_contact_caption": "📞 Contact: **{contact}**",
        "support_collab_heading": "### 📝 Represent an organization or want to suggest a service?",
        "support_collab_desc": (
            "Our directory is community-curated and vetted to ensure safe support for LGBTQIA+ people. "
            "Send a suggestion through our form or reach out by email."
        ),
        "support_collab_form_btn": "✨ Suggest via form",
        "support_collab_email_btn": "✉️ Email the team",
        "error_generic": (
            "\nOops, something went wrong here :/\n\n"
            "Please report this issue to our team with error code: **{error_id}**\n"
        ),
        "error_safety": (
            "⚠️ **Vox cannot answer this message.**\n\n"
            "For safety and care reasons, your message triggered our protection guidelines and could not be processed.\n\n"
            "*(Error code: **{error_id}**)*"
        ),
        "error_quota": (
            "Hi! Vox is receiving a high volume of messages right now and temporarily hit the Google API rate limit. "
            "Please wait about a minute and try sending your message again! 💜\n\n"
            "*(Error code: **{error_id}**)*"
        ),
        "error_unavailable": (
            "Oops! The AI servers are under heavy demand right now and temporarily unstable. "
            "Take a deep breath and try again in a few moments — I'll be right here! 🏳️‍🌈\n\n"
            "*(Error code: **{error_id}**)*"
        ),
        "toast_model_fallback": "Server busy. Switching to fallback model ({proximo_modelo})...",
        "toast_audio_fallback": "Audio instability. Trying alternative model ({proximo})...",
    },
}


def normalize_lang(lang: str | None) -> str:
    """
    Normaliza um código de idioma para os idiomas suportados ('pt' ou 'en').

    Args:
        lang (str | None): Código de idioma bruto (ex: 'en', 'en-US', 'pt-BR').

    Returns:
        str: 'en' para variantes de inglês, 'pt' caso contrário.
    """
    if not isinstance(lang, str):
        return DEFAULT_LANG
    clean = lang.strip().lower()
    if clean == "en" or clean.startswith("en-") or clean.startswith("en_"):
        return "en"
    return DEFAULT_LANG


def resolve_lang() -> str:
    """
    Resolve o idioma ativo da sessão Streamlit priorizando session_state e query_params (?lang=en).

    Returns:
        str: Código de idioma normalizado ('pt' ou 'en').
    """
    try:
        if hasattr(st, "session_state") and "lang" in st.session_state:
            return normalize_lang(st.session_state.get("lang"))
    except Exception:
        pass

    resolved = DEFAULT_LANG
    try:
        if hasattr(st, "query_params"):
            raw = st.query_params.get("lang")
            if isinstance(raw, list):
                raw = raw[0] if raw else None
            if raw:
                resolved = normalize_lang(str(raw))
    except Exception:
        resolved = DEFAULT_LANG

    try:
        if hasattr(st, "session_state"):
            st.session_state["lang"] = resolved
    except Exception:
        pass

    return resolved


def get_active_lang() -> str:
    """
    Obtém o idioma ativo de st.session_state de forma segura (padrão 'pt').

    Returns:
        str: 'pt' ou 'en'.
    """
    try:
        if hasattr(st, "session_state"):
            return normalize_lang(st.session_state.get("lang"))
    except Exception:
        pass
    return DEFAULT_LANG


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: Any) -> str:
    """
    Retorna a string traduzida correspondente à chave no idioma solicitado.

    Args:
        key (str): Chave da string de tradução.
        lang (str): Idioma desejado ('pt' ou 'en').
        **kwargs: Parâmetros opcionais para formatação da string.

    Returns:
        str: Texto traduzido e formatado.
    """
    norm = normalize_lang(lang)
    table = _TRANSLATIONS.get(norm, _TRANSLATIONS[DEFAULT_LANG])
    template = table.get(key, _TRANSLATIONS[DEFAULT_LANG].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def translate_report_category(category_id: int, fallback_label: str, lang: str = DEFAULT_LANG) -> str:
    """
    Traduz o rótulo de categoria de denúncia do Supabase preservando o ID original.

    Args:
        category_id (int): Identificador numérico da categoria em report_categories.
        fallback_label (str): Rótulo retornado pelo banco em português.
        lang (str): Idioma ativo ('pt' ou 'en').

    Returns:
        str: Rótulo no idioma solicitado.
    """
    if normalize_lang(lang) == "en":
        return REPORT_CATEGORY_EN.get(category_id, fallback_label)
    return fallback_label


def translate_support_category(category: str, lang: str = DEFAULT_LANG) -> str:
    """
    Traduz o nome de categoria do diretório da Rede de Apoio.

    Args:
        category (str): Nome original da categoria em português.
        lang (str): Idioma ativo ('pt' ou 'en').

    Returns:
        str: Nome exibido da categoria no idioma solicitado.
    """
    if normalize_lang(lang) == "en":
        return SUPPORT_CATEGORY_EN.get(category, category)
    return category


def get_saudacao(lang: str = DEFAULT_LANG) -> str:
    """
    Retorna a saudação inicial do chat no idioma especificado.

    Args:
        lang (str): Idioma ('pt' ou 'en').

    Returns:
        str: Mensagem de saudação.
    """
    return t("greeting", lang)


def get_sidebar_body(lang: str = DEFAULT_LANG) -> str:
    """
    Monta o HTML dos cards informativos da barra lateral no idioma especificado.

    Args:
        lang (str): Idioma ('pt' ou 'en').

    Returns:
        str: Bloco HTML da barra lateral.
    """
    norm = normalize_lang(lang)
    about_title = t("sidebar_about_title", norm)
    about_body = t("sidebar_about_body", norm)
    help_title = t("sidebar_help_title", norm)
    help_188 = t("sidebar_help_188", norm)
    help_188_title = t("sidebar_help_188_title", norm)
    help_100 = t("sidebar_help_100", norm)
    help_100_title = t("sidebar_help_100_title", norm)
    social_title = t("sidebar_social_title", norm)
    email_title = t("sidebar_email_title", norm)

    return f"""<div style="display: flex; flex-direction: column; margin-bottom: 1em;">
<div class="vox-sidebar-card">
<div class="vox-sidebar-card-title">{about_title}</div>
<div class="vox-sidebar-section">
{about_body}
</div>
</div>
<div class="vox-sidebar-card">
<div class="vox-sidebar-card-title">{help_title}</div>
<ul class="vox-sidebar-list">
<li class="vox-sidebar-list-item">
<a href="{CVV_LINK}" target="_blank" title="{help_188_title}">
{help_188}
</a>
</li>
<li class="vox-sidebar-list-item">
<a href="{DISQUE_100}" target="_blank" title="{help_100_title}">
{help_100}
</a>
</li>
</ul>
</div>
<div class="vox-sidebar-card">
<div class="vox-sidebar-card-title">{social_title}</div>
<div class="vox-social-grid">
<a href="{INSTAGRAM_VOX}" target="_blank" class="vox-social-icon" title="Instagram">
<img src="https://img.icons8.com/?size=100&id=Xy10Jcu1L2Su&format=png" alt="Instagram" />
</a>
<a href="{LINKTREE_VOX}" target="_blank" class="vox-social-icon" title="Linktree">
<img src="https://img.icons8.com/?size=100&id=GfTOMrwiax2M&format=png&color=000000" alt="Linktree" />
</a>
<a href="{LINKEDIN_VOX}" target="_blank" class="vox-social-icon" title="LinkedIn">
<img src="https://img.icons8.com/?size=100&id=13930&format=png&color=000000" alt="LinkedIn" />
</a>
<a href="{EMAIL_CONTATO}" target="_blank" class="vox-social-icon" title="{email_title}">
<img src="https://img.icons8.com/?size=100&id=ho8QlOYvMuG3&format=png&color=000000" alt="Email" />
</a>
</div>
</div>
</div>"""


def get_sidebar_footer(lang: str = DEFAULT_LANG) -> str:
    """
    Monta o HTML do rodapé da barra lateral no idioma especificado.

    Args:
        lang (str): Idioma ('pt' ou 'en').

    Returns:
        str: Bloco HTML do rodapé da sidebar.
    """
    norm = normalize_lang(lang)
    terms_label = t("sidebar_terms", norm)
    privacy_label = t("sidebar_privacy", norm)

    return f"""
<div style="display: flex; gap: 16px; justify-content: center; margin-bottom: 12px;">
<a href="{GITHUB}" target="_blank" title="GitHub">
<img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/github.svg" alt="GitHub" style="height: 24px; filter: invert(0.5);" />
</a>
</div>
<div class="copyright" style="text-align: center; color: #888; font-size: 0.8em; margin-top: 10px; opacity: 0.8;">
Vox AI {git_version()}
</div>
<div class="footer-links" style="text-align:center; font-size: 0.9em;">
<a href="{TERMS_OF_USE}" target="_blank" style="text-decoration: none;" class="legal-link">{terms_label}</a>
<br>
<a href="{POLICY_PRIVACY}" target="_blank" style="text-decoration: none;" class="legal-link">{privacy_label}</a>
</div>
</div>

"""
