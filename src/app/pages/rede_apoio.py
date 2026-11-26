"""
Rede de Apoio e Diretório de Acolhimento — Vox AI.

Página e componente interativo dedicado à divulgação de casas de acolhimento parceiras,
centros de referência municipais/estaduais, ambulatórios especializados e ONGs
que oferecem suporte à comunidade LGBTQIA+.

Pode ser executado diretamente como página Streamlit ou importado como componente:
`from src.app.pages.rede_apoio import render_rede_apoio; render_rede_apoio()`
"""

from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from src.external_links import EMAIL_CONTATO
from src.i18n import get_active_lang, normalize_lang, t, translate_support_category

CONTRIBUTE_KB_FORM_URL = "https://forms.gle/Bwb3NEurV7YoZFXG8"


# Base Curada e Auditada de Instituições e Iniciativas de Apoio LGBTQIA+
REDE_APOIO_DATA: List[Dict[str, Any]] = [
    # Casas de Acolhimento
    {
        "nome": "Casa 1 — Centro de Cultura e Acolhimento",
        "categoria": "Casas de Acolhimento",
        "uf": "SP",
        "cidade": "São Paulo",
        "descricao": (
            "República de acolhimento para jovens LGBTQIA+ de 18 a 25 anos expulsos de casa por suas orientações "
            "ou identidades. Conta com clínica social multidisciplinar (psicologia, psiquiatria, acupuntura) e centro cultural."
        ),
        "tags": ["Gratuito", "Moradia", "Psicologia Social", "Cultura", "Verificado Vox"],
        "contato": "(11) 3104-5858",
        "whatsapp": "551131045858",
        "link": "https://www.casa-um.org/",
        "gratuito": True,
        "modalidade": "Presencial e Online",
    },
    {
        "nome": "Casinha Acolhimento",
        "categoria": "Casas de Acolhimento",
        "uf": "RJ",
        "cidade": "Rio de Janeiro",
        "descricao": (
            "Espaço de acolhimento, convivência e fomento de autonomia para pessoas LGBTQIA+ "
            "em situação de vulnerabilidade e rua na capital fluminense."
        ),
        "tags": ["Gratuito", "Moradia", "Assistência Social", "Verificado Vox"],
        "contato": "contato@casinha.org.br",
        "link": "https://www.casinha.org.br/",
        "gratuito": True,
        "modalidade": "Presencial",
    },
    {
        "nome": "Casa Chama",
        "categoria": "Casas de Acolhimento",
        "uf": "SP",
        "cidade": "São Paulo",
        "descricao": (
            "Organização sociocultural e rede de apoio continuado voltada a pessoas trans e travestis, "
            "atuando em assistência jurídica, saúde integral, segurança alimentar e artes."
        ),
        "tags": ["Gratuito", "Acolhimento Trans", "Apoio Jurídico", "Saúde", "Verificado Vox"],
        "contato": "contato@casachama.org",
        "link": "https://casachama.org/",
        "gratuito": True,
        "modalidade": "Presencial e Online",
    },
    {
        "nome": "Casa Miga",
        "categoria": "Casas de Acolhimento",
        "uf": "AM",
        "cidade": "Manaus",
        "descricao": (
            "Primeira casa de acolhimento para pessoas LGBTQIA+ em situação de refúgio e migração da Amazônia "
            "e de vulnerabilidade social na região Norte."
        ),
        "tags": ["Gratuito", "Refugiados/Migrantes", "Amazônia", "Moradia", "Verificado Vox"],
        "contato": "casamigamanaus@gmail.com",
        "link": "https://casamiga.org/",
        "gratuito": True,
        "modalidade": "Presencial",
    },
    {
        "nome": "Casa Florescer",
        "categoria": "Casas de Acolhimento",
        "uf": "SP",
        "cidade": "São Paulo",
        "descricao": (
            "Centro de acolhida exclusivo para mulheres trans e travestis em situação de vulnerabilidade social, "
            "focando em inserção educacional, mercado de trabalho e cidadania."
        ),
        "tags": ["Gratuito", "Acolhimento Trans", "Inserção Profissional", "Verificado Vox"],
        "contato": "(11) 3228-5684",
        "link": "https://croph.org.br/casa-florescer/",
        "gratuito": True,
        "modalidade": "Presencial",
    },

    # Centros Públicos de Referência
    {
        "nome": "Centro de Cidadania LGBTI Claudia Wonder (Zona Leste)",
        "categoria": "Centros Públicos de Referência",
        "uf": "SP",
        "cidade": "São Paulo",
        "descricao": (
            "Equipamento público da Prefeitura de São Paulo com atendimento social, psicológico e jurídico gratuito "
            "para vítimas de discriminação e apoio para retificação de prenome e gênero."
        ),
        "tags": ["SUS/Público", "Gratuito", "Retificação de Nome", "Jurídico", "Verificado Vox"],
        "contato": "(11) 2965-1555",
        "link": "https://www.prefeitura.sp.gov.br/cidade/secretarias/direitos_humanos/lgbti/",
        "gratuito": True,
        "modalidade": "Presencial",
    },
    {
        "nome": "Centro Estadual de Referência LGBT de Minas Gerais",
        "categoria": "Centros Públicos de Referência",
        "uf": "MG",
        "cidade": "Belo Horizonte",
        "descricao": (
            "Serviço governamental que atende pessoas LGBTQIA+ de todo o estado de Minas Gerais em casos de "
            "violações de direitos, prestando acolhimento psicológico e encaminhamentos jurídicos."
        ),
        "tags": ["Público", "Gratuito", "Atendimento Social", "Minas Gerais", "Verificado Vox"],
        "contato": "(31) 3270-3639",
        "link": "https://social.mg.gov.br/",
        "gratuito": True,
        "modalidade": "Presencial e Telefone",
    },
    {
        "nome": "Centro de Referência LGBT Thina Rodrigues",
        "categoria": "Centros Públicos de Referência",
        "uf": "PE",
        "cidade": "Recife",
        "descricao": (
            "Serviço municipal do Recife de defesa e promoção dos direitos da população LGBT, "
            "com equipe interdisciplinar de assistentes sociais, psicólogos e advogados."
        ),
        "tags": ["Público", "Gratuito", "Nordeste", "Apoio Jurídico", "Verificado Vox"],
        "contato": "(81) 3355-3456",
        "link": "https://recife.pe.gov.br/",
        "gratuito": True,
        "modalidade": "Presencial",
    },
    {
        "nome": "Centro de Referência em Direitos Humanos LGBT do DF",
        "categoria": "Centros Públicos de Referência",
        "uf": "DF",
        "cidade": "Brasília",
        "descricao": (
            "Unidade pública de proteção e orientação legal à população LGBTQIA+ do Distrito Federal e Entorno, "
            "com apoio a denúncias de crimes de ódio e mediação de conflitos."
        ),
        "tags": ["Público", "Gratuito", "Centro-Oeste", "Denúncias", "Verificado Vox"],
        "contato": "(61) 3325-9600",
        "link": "https://www.sejus.df.gov.br/",
        "gratuito": True,
        "modalidade": "Presencial",
    },

    # ONGs e Coletivos Nacionais
    {
        "nome": "ANTRA — Associação Nacional de Travestis e Transexuais",
        "categoria": "ONGs e Coletivos",
        "uf": "Nacional",
        "cidade": "Brasil",
        "descricao": (
            "Principal rede nacional de articulação política, produção de dados científicos "
            "(Dossiê de Assassinatos de Pessoas Trans) e incidência legislativa pelos direitos trans no Brasil."
        ),
        "tags": ["Nacional", "Pesquisa", "Advocacy", "Ativismo Trans", "Verificado Vox"],
        "contato": "secretariageralantra@gmail.com",
        "link": "https://antrabrasil.org/",
        "gratuito": True,
        "modalidade": "Online / Nacional",
    },
    {
        "nome": "ABGLT — Associação Brasileira de Lésbicas, Gays, Bissexuais, Travestis e Intersexos",
        "categoria": "ONGs e Coletivos",
        "uf": "Nacional",
        "cidade": "Brasil",
        "descricao": (
            "Rede histórica com mais de 30 anos atuando pela conquista de direitos humanos, união estável, "
            "criminalização da homofobia e políticas públicas federais."
        ),
        "tags": ["Nacional", "Advocacy", "Direitos Civis", "Verificado Vox"],
        "contato": "abglt@abglt.org.br",
        "link": "https://www.abglt.org.br/",
        "gratuito": True,
        "modalidade": "Online / Nacional",
    },
    {
        "nome": "Mães pela Diversidade",
        "categoria": "ONGs e Coletivos",
        "uf": "Nacional",
        "cidade": "Brasil",
        "descricao": (
            "Coletivo nacional formado por mães, pais e familiares de pessoas LGBTQIA+, acolhendo famílias em processo "
            "de aceitação e combatendo o preconceito dentro e fora do ambiente doméstico."
        ),
        "tags": ["Nacional", "Apoio Familiar", "Acolhimento", "Gratuito", "Verificado Vox"],
        "contato": "contato@maespeladiversidade.org.br",
        "link": "https://maespeladiversidade.org.br/",
        "gratuito": True,
        "modalidade": "Online e Núcleos Estaduais",
    },
    {
        "nome": "Eternamente SOU",
        "categoria": "ONGs e Coletivos",
        "uf": "SP",
        "cidade": "São Paulo / Online",
        "descricao": (
            "ONG pioneira na atuação pela garantia dos direitos humanos, convivência intergeracional "
            "e dignidade de pessoas idosas LGBTQIA+ (50+)."
        ),
        "tags": ["Gratuito", "Pessoas Idosas (50+)", "Convivência", "Verificado Vox"],
        "contato": "contato@eternamentesou.org",
        "link": "https://www.eternamentesou.org/",
        "gratuito": True,
        "modalidade": "Presencial e Online",
    },

    # Saúde e Ambulatórios
    {
        "nome": "Ambulatório Transdisciplinar de Identidade de Gênero e Orientação Sexual (AMTIGOS - IPq/HCFMUSP)",
        "categoria": "Saúde e Ambulatórios",
        "uf": "SP",
        "cidade": "São Paulo",
        "descricao": (
            "Centro de excelência do Hospital das Clínicas da USP para acolhimento de pessoas trans e não-binárias, "
            "com equipes de psiquiatria, psicologia e endocrinologia via SUS."
        ),
        "tags": ["SUS", "Gratuito", "Hormonioterapia", "Saúde Mental", "Verificado Vox"],
        "contato": "(11) 2661-7890",
        "link": "https://www.ipqhc.org.br/",
        "gratuito": True,
        "modalidade": "Presencial",
    },
]


def render_banner_sos(lang: str | None = None) -> None:
    """
    Renderiza a barra de contatos emergenciais de socorro imediato.

    Args:
        lang (str | None): Idioma da interface ('pt' ou 'en').
    """
    active_lang = normalize_lang(lang) if lang is not None else get_active_lang()
    sos_title = t("support_sos_title", active_lang)
    sos_desc = t("support_sos_desc", active_lang)
    sos_100 = t("support_sos_100", active_lang)
    sos_188 = t("support_sos_188", active_lang)
    sos_190 = t("support_sos_190", active_lang)

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1f122f, #2d0b28); border: 1px solid #FF1E56; border-radius: 12px; padding: 18px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 24px;">🚨</span>
                <strong style="font-size: 18px; color: #FF4D6D;">{sos_title}</strong>
            </div>
            <p style="color: #E2E8F0; margin-bottom: 12px; font-size: 14px;">
                {sos_desc}
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <span style="background: rgba(255, 30, 86, 0.2); border: 1px solid #FF1E56; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; color: #FFF;">
                    {sos_100}
                </span>
                <span style="background: rgba(0, 180, 216, 0.2); border: 1px solid #00B4D8; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; color: #FFF;">
                    {sos_188}
                </span>
                <span style="background: rgba(114, 9, 183, 0.2); border: 1px solid #7209B7; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; color: #FFF;">
                    {sos_190}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rede_apoio(show_title: bool = True, lang: str | None = None) -> None:
    """
    Renderiza o diretório completo com busca interativa, filtros por categoria,
    estado (UF), tags e links reais de colaboração.

    Args:
        show_title (bool): Exibe o título principal quando renderizado como página dedicada.
        lang (str | None): Idioma da interface ('pt' ou 'en').
    """
    active_lang = normalize_lang(lang) if lang is not None else get_active_lang()

    if show_title:
        st.title(t("support_page_title", active_lang))
    st.markdown(t("support_intro", active_lang))

    # Banner de SOS
    render_banner_sos(lang=active_lang)

    # Controles de Filtro
    col_search, col_cat, col_uf = st.columns([2, 1.5, 1])

    with col_search:
        busca_termo = st.text_input(
            t("support_search_label", active_lang),
            placeholder=t("support_search_placeholder", active_lang),
        )

    categorias_disponiveis = [
        "Todas as Categorias",
        "Casas de Acolhimento",
        "Centros Públicos de Referência",
        "ONGs e Coletivos",
        "Saúde e Ambulatórios",
    ]
    with col_cat:
        categoria_sel = st.selectbox(
            t("support_cat_label", active_lang),
            categorias_disponiveis,
            format_func=lambda c: (
                t("support_cat_all", active_lang)
                if c == "Todas as Categorias"
                else translate_support_category(c, active_lang)
            ),
        )

    ufs_disponiveis = ["Todos os Estados", "Nacional", "SP", "RJ", "MG", "DF", "AM", "PE", "RS"]
    with col_uf:
        uf_sel = st.selectbox(
            t("support_uf_label", active_lang),
            ufs_disponiveis,
            format_func=lambda u: (
                t("support_uf_all", active_lang)
                if u == "Todos os Estados"
                else (t("support_uf_national", active_lang) if u == "Nacional" else u)
            ),
        )

    check_somente_gratuitos = st.checkbox(t("support_free_only", active_lang))

    # Filtragem dos Registros
    registros_filtrados = []
    termo_limpo = (busca_termo or "").lower().strip()

    for item in REDE_APOIO_DATA:
        if categoria_sel != "Todas as Categorias" and item["categoria"] != categoria_sel:
            continue

        if uf_sel != "Todos os Estados":
            if uf_sel == "Nacional" and item["uf"] != "Nacional":
                continue
            elif uf_sel != "Nacional" and item["uf"] not in (uf_sel, "Nacional"):
                continue

        if check_somente_gratuitos and not item.get("gratuito", False):
            continue

        if termo_limpo:
            conteudo_completo = (
                f"{item['nome']} {item['cidade']} {item['descricao']} {' '.join(item['tags'])}"
            ).lower()
            if termo_limpo not in conteudo_completo:
                continue

        registros_filtrados.append(item)

    st.markdown(t("support_results_count", active_lang, count=len(registros_filtrados)))

    if not registros_filtrados:
        st.info(t("support_empty", active_lang))
    else:
        for item in registros_filtrados:
            uf_display = t("support_uf_national", active_lang) if item["uf"] == "Nacional" else item["uf"]
            cidade_display = "Brazil" if active_lang == "en" and item["cidade"] == "Brasil" else item["cidade"]

            with st.container():
                st.markdown(
                    f"""
                    <div style="background: rgba(22, 18, 38, 0.85); border: 1px solid rgba(114, 9, 183, 0.25); border-radius: 14px; padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3); backdrop-filter: blur(8px);">
                        <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px;">
                            <h3 style="margin: 0; color: #FFFFFF; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.15rem; font-weight: 700;">{item['nome']}</h3>
                            <span style="background: linear-gradient(135deg, #7209B7 0%, #B5179E 100%); color: #FFF; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 12px; box-shadow: 0 2px 8px rgba(114, 9, 183, 0.3);">{uf_display} — {cidade_display}</span>
                        </div>
                        <p style="color: #CBD5E1; margin: 10px 0 12px 0; font-size: 14px; line-height: 1.5;">{item['descricao']}</p>
                        <div style="margin-bottom: 12px;">
                            {' '.join([f'<span style="background: rgba(114, 9, 183, 0.15); border: 1px solid rgba(114, 9, 183, 0.3); color: #C084FC; font-size: 11px; padding: 3px 8px; border-radius: 6px; margin-right: 6px;">#{tag}</span>' for tag in item['tags']])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                cols_act = st.columns([1, 1, 2])
                with cols_act[0]:
                    if item.get("link"):
                        st.link_button(t("support_visit_btn", active_lang), item["link"], use_container_width=True)
                with cols_act[1]:
                    if item.get("whatsapp"):
                        st.link_button(
                            t("support_whatsapp_btn", active_lang),
                            f"https://wa.me/{item['whatsapp']}",
                            use_container_width=True,
                        )
                    elif item.get("contato"):
                        st.caption(t("support_contact_caption", active_lang, contact=item["contato"]))

    # Seção de Colaboração Real (formulário oficial + e-mail)
    st.markdown("---")
    st.markdown(t("support_collab_heading", active_lang))
    st.write(t("support_collab_desc", active_lang))

    cols_collab = st.columns(2)
    with cols_collab[0]:
        st.link_button(
            t("support_collab_form_btn", active_lang),
            CONTRIBUTE_KB_FORM_URL,
            use_container_width=True,
        )
    with cols_collab[1]:
        st.link_button(
            t("support_collab_email_btn", active_lang),
            EMAIL_CONTATO,
            use_container_width=True,
        )


# Se executado diretamente como página do Streamlit
if __name__ == "__main__":
    active = get_active_lang()
    st.set_page_config(page_title=t("support_page_title", active), page_icon="🤝", layout="wide")
    render_rede_apoio(lang=active)
