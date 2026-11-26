"""
Testes unitários para internacionalização (PT/EN) do Vox AI no Streamlit.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.app.pages.rede_apoio import REDE_APOIO_DATA, render_rede_apoio
from src.app.ui import _aplicar_troca_idioma, configurar_pagina
from src.i18n import (
    REPORT_CATEGORY_EN,
    _TRANSLATIONS,
    get_saudacao,
    get_sidebar_body,
    get_sidebar_footer,
    normalize_lang,
    resolve_lang,
    t,
    translate_report_category,
    translate_support_category,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw, expected",
    [
        (None, "pt"),
        ("", "pt"),
        ("pt", "pt"),
        ("pt-BR", "pt"),
        ("fr-FR", "pt"),
        ("en", "en"),
        ("EN", "en"),
        ("en-US", "en"),
        ("en_GB", "en"),
    ],
)
def test_normalize_lang(raw, expected):
    assert normalize_lang(raw) == expected


@pytest.mark.unit
def test_translations_parity_pt_en():
    pt_keys = set(_TRANSLATIONS["pt"].keys())
    en_keys = set(_TRANSLATIONS["en"].keys())
    assert pt_keys == en_keys
    assert all(isinstance(_TRANSLATIONS["pt"][k], str) and _TRANSLATIONS["pt"][k].strip() for k in pt_keys)
    assert all(isinstance(_TRANSLATIONS["en"][k], str) and _TRANSLATIONS["en"][k].strip() for k in en_keys)


@pytest.mark.unit
def test_translate_report_category_ids_and_fallback():
    for cat_id, en_label in REPORT_CATEGORY_EN.items():
        assert translate_report_category(cat_id, "Rótulo PT", "en") == en_label
        assert translate_report_category(cat_id, "Rótulo PT", "pt") == "Rótulo PT"

    assert translate_report_category(999, "Categoria Nova", "en") == "Categoria Nova"


@pytest.mark.unit
def test_translate_support_category():
    assert translate_support_category("Casas de Acolhimento", "en") == "Shelters & Housing"
    assert translate_support_category("Casas de Acolhimento", "pt") == "Casas de Acolhimento"


@pytest.mark.unit
def test_saudacao_and_sidebar_pt_en():
    saudacao_pt = get_saudacao("pt")
    saudacao_en = get_saudacao("en")
    assert "Oi!" in saudacao_pt
    assert "Hi!" in saudacao_en

    body_pt = get_sidebar_body("pt")
    body_en = get_sidebar_body("en")
    assert "Sobre o Projeto" in body_pt
    assert "UCSAL" in body_pt
    assert "About the Project" in body_en
    assert "UCSAL" in body_en
    assert "188" in body_en and "100" in body_en

    footer_pt = get_sidebar_footer("pt")
    footer_en = get_sidebar_footer("en")
    assert "Termos de Uso" in footer_pt
    assert "Terms of Use" in footer_en


@pytest.mark.unit
def test_resolve_lang_from_query_params_and_session():
    session_mock = {}
    with patch("src.i18n.st.session_state", session_mock), \
         patch("src.i18n.st.query_params", {"lang": "en"}):
        assert resolve_lang() == "en"
        assert session_mock["lang"] == "en"

    session_mock_pt = {"lang": "pt"}
    with patch("src.i18n.st.session_state", session_mock_pt), \
         patch("src.i18n.st.query_params", {"lang": "en"}):
        assert resolve_lang() == "pt"


@pytest.mark.unit
def test_configurar_pagina_sets_page_config_before_resolving_language():
    calls = []

    def set_page_config(**kwargs):
        calls.append(("config", kwargs))

    def resolve_language():
        calls.append(("resolve", None))
        return "en"

    with patch("src.app.ui.st.set_page_config", side_effect=set_page_config), \
         patch("src.app.ui.resolve_lang", side_effect=resolve_language), \
         patch("src.app.ui.carregar_css"), \
         patch("src.app.ui.carregar_icone_base64", return_value=""), \
         patch("src.app.ui.st.markdown"):
        assert configurar_pagina() == "en"

    assert calls[0] == (
        "config",
        {"page_title": t("page_title", "pt"), "page_icon": "🌈"},
    )
    assert calls[1] == ("resolve", None)


@pytest.mark.unit
def test_aplicar_troca_idioma_updates_initial_greeting():
    session_mock = {
        "lang": "pt",
        "hist_exibir": [{"role": "model", "parts": [get_saudacao("pt")]}],
        "audio_cache_0": b"cached",
    }
    qp_mock = {}
    with patch("src.app.ui.st.session_state", session_mock), \
         patch("src.app.ui.st.query_params", qp_mock):
        _aplicar_troca_idioma("en")
        assert session_mock["lang"] == "en"
        assert qp_mock["lang"] == "en"
        assert session_mock["hist_exibir"][0]["parts"][0] == get_saudacao("en")
        assert "audio_cache_0" not in session_mock


@pytest.mark.unit
@patch("streamlit.title")
def test_render_rede_apoio_english_and_no_voxai_org_placeholders(mock_st_title):
    for item in REDE_APOIO_DATA:
        assert "voxai.org" not in str(item.get("link", "")).lower()
        assert "voxai.org" not in str(item.get("contato", "")).lower()

    with patch("streamlit.text_input", return_value=""), \
         patch("streamlit.selectbox", return_value="Todas as Categorias"), \
         patch("streamlit.checkbox", return_value=False), \
         patch("streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock()]):
        render_rede_apoio(show_title=True, lang="en")
        mock_st_title.assert_called_once_with(t("support_page_title", "en"))
