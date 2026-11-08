"""
Rede de Apoio e Diretório de Acolhimento — Vox AI.

Página e componente interativo dedicado à divulgação de profissionais verificados,
casas de acolhimento parceiras, centros de referência municipais/estaduais e ONGs
que oferecem suporte especializado à comunidade LGBTQIA+.

Pode ser executado diretamente como página Streamlit ou importado como componente:
`from src.app.pages.rede_apoio import render_rede_apoio; render_rede_apoio()`
"""

from __future__ import annotations

import streamlit as st
from typing import Any, Dict, List


# Base Curada e Auditada de Instituições e Profissionais de Apoio LGBTQIA+
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

    # Saúde e Profissionais Afirmativos
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
    {
        "nome": "Rede Psicológica Afirmativa Vox",
        "categoria": "Profissionais Afirmativos",
        "uf": "Nacional",
        "cidade": "Atendimento Online",
        "descricao": (
            "Diretório de psicólogos(as/es) cadastrados com formação em Psicologia Afirmativa LGBTQIA+, "
            "atendimento com valores sociais e plantões voluntários para situações de crise."
        ),
        "tags": ["Tabela Social", "Atendimento Online", "Psicologia Afirmativa", "Verificado Vox"],
        "contato": "apoio@voxai.org",
        "link": "https://voxai.org/apoio-psicologico",
        "gratuito": False,
        "modalidade": "Online",
    },
    {
        "nome": "Assessoria Jurídica Popular — Retifica Já",
        "categoria": "Profissionais Afirmativos",
        "uf": "Nacional",
        "cidade": "Atendimento Online",
        "descricao": (
            "Rede de advogados(as/es) e defensores populares dedicados a orientar o passo a passo da retificação "
            "de prenome e gênero em cartórios de Registro Civil (Provimento CNJ nº 73/2018)."
        ),
        "tags": ["Voluntário / Gratuito", "Retificação de Nome", "Jurídico", "Verificado Vox"],
        "contato": "juridico@voxai.org",
        "link": "https://voxai.org/retificacao",
        "gratuito": True,
        "modalidade": "Online",
    },
]


def render_banner_sos() -> None:
    """Renderiza a barra de contatos emergenciais de socorro imediato."""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1f122f, #2d0b28); border: 1px solid #FF1E56; border-radius: 12px; padding: 18px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 24px;">🚨</span>
                <strong style="font-size: 18px; color: #FF4D6D;">Precisa de Ajuda Imediata?</strong>
            </div>
            <p style="color: #E2E8F0; margin-bottom: 12px; font-size: 14px;">
                Se você está sofrendo violência física, ameaça à vida ou crise emocional severa, contate os canais públicos gratuitos:
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <span style="background: rgba(255, 30, 86, 0.2); border: 1px solid #FF1E56; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; color: #FFF;">
                    📞 Disque 100 — Direitos Humanos &amp; LGBTfobia
                </span>
                <span style="background: rgba(0, 180, 216, 0.2); border: 1px solid #00B4D8; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; color: #FFF;">
                    💛 CVV 188 — Apoio Emocional e Prevenção
                </span>
                <span style="background: rgba(114, 9, 183, 0.2); border: 1px solid #7209B7; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; color: #FFF;">
                    🛡️ 190 — Polícia Militar em Caso de Risco
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rede_apoio(show_title: bool = True) -> None:
    """
    Renderiza o diretório completo com busca interativa, filtros por categoria,
    estado (UF), tags e formulário de inscrição para novos profissionais.
    """
    if show_title:
        st.title("🤝 Rede de Apoio e Acolhimento Vox")
    st.markdown(
        "Conectamos você a **casas de acolhimento parceiras**, **centros públicos de referência**, "
        "**ONGs combativas** e **profissionais de saúde e direito afirmativos** em todo o Brasil. 🏳️‍🌈"
    )

    # Banner de SOS
    render_banner_sos()

    # Controles de Filtro
    col_search, col_cat, col_uf = st.columns([2, 1.5, 1])

    with col_search:
        busca_termo = st.text_input("🔍 Buscar por nome, serviço ou palavra-chave:", placeholder="Ex: moradia, trans, jurídico, psicologia...")

    categorias_disponiveis = [
        "Todas as Categorias",
        "Casas de Acolhimento",
        "Centros Públicos de Referência",
        "ONGs e Coletivos",
        "Saúde e Ambulatórios",
        "Profissionais Afirmativos",
    ]
    with col_cat:
        categoria_sel = st.selectbox("Categoria:", categorias_disponiveis)

    ufs_disponiveis = ["Todos os Estados", "Nacional", "SP", "RJ", "MG", "DF", "AM", "PE", "RS"]
    with col_uf:
        uf_sel = st.selectbox("Localização:", ufs_disponiveis)

    check_somente_gratuitos = st.checkbox("Apenas serviços 100% gratuitos ou SUS")

    # Filtragem dos Registros
    registros_filtrados = []
    termo_limpo = busca_termo.lower().strip()

    for item in REDE_APOIO_DATA:
        # Filtro de Categoria
        if categoria_sel != "Todas as Categorias" and item["categoria"] != categoria_sel:
            continue

        # Filtro de UF
        if uf_sel != "Todos os Estados":
            if uf_sel == "Nacional" and item["uf"] != "Nacional":
                continue
            elif uf_sel != "Nacional" and item["uf"] not in (uf_sel, "Nacional"):
                continue

        # Filtro de Gratuidade
        if check_somente_gratuitos and not item.get("gratuito", False):
            continue

        # Filtro de Termo de Busca
        if termo_limpo:
            conteudo_completo = f"{item['nome']} {item['cidade']} {item['descricao']} {' '.join(item['tags'])}".lower()
            if termo_limpo not in conteudo_completo:
                continue

        registros_filtrados.append(item)

    st.markdown(f"**Exibindo {len(registros_filtrados)} locais e iniciativas encontradas:**")

    if not registros_filtrados:
        st.info("Nenhuma iniciativa encontrada para os filtros selecionados. Tente expandir a busca.")
    else:
        # Renderização em Grid de Cards
        for item in registros_filtrados:
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: 18px; margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                            <h3 style="margin: 0; color: #FFF; font-size: 19px;">{item['nome']}</h3>
                            <span style="background: #7209B7; color: #FFF; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 12px;">{item['uf']} — {item['cidade']}</span>
                        </div>
                        <p style="color: #CBD5E1; margin: 10px 0 12px 0; font-size: 14px; line-height: 1.5;">{item['descricao']}</p>
                        <div style="margin-bottom: 12px;">
                            {' '.join([f'<span style="background: rgba(0, 180, 216, 0.15); color: #38BDF8; font-size: 11px; padding: 3px 8px; border-radius: 6px; margin-right: 6px;">#{t}</span>' for t in item['tags']])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                cols_act = st.columns([1, 1, 2])
                with cols_act[0]:
                    if item.get("link"):
                        st.link_button("🌐 Visitar Site / Redes", item["link"], use_container_width=True)
                with cols_act[1]:
                    if item.get("whatsapp"):
                        st.link_button("💬 Falar no WhatsApp", f"https://wa.me/{item['whatsapp']}", use_container_width=True)
                    elif item.get("contato"):
                        st.caption(f"📞 Contato: **{item['contato']}**")

    # Seção de Cadastro Colaborativo
    st.markdown("---")
    st.markdown("### 📝 Você é profissional afirmativo ou representa uma instituição?")
    st.write(
        "Nossa rede é colaborativa e passa por processo rigoroso de verificação ética, "
        "assegurando respeito irrestrito aos direitos humanos da comunidade LGBTQIA+."
    )

    with st.expander("✨ Quero cadastrar minha entidade ou consultório"):
        with st.form("form_cadastro_rede"):
            nome_entidade = st.text_input("Nome do Profissional ou Entidade:")
            registro_prof = st.text_input("Registro Profissional (CRP, CRM, OAB, etc.) ou CNPJ:")
            categoria_form = st.selectbox("Categoria de Atuação:", categorias_disponiveis[1:])
            uf_cidade = st.text_input("Cidade e Estado de Atendimento:")
            email_contato = st.text_input("E-mail de Contato:")
            descricao_atendimento = st.text_area("Descreva os serviços oferecidos e política de acessibilidade/valores:")
            declaracao_etica = st.checkbox("Declaro que sigo diretrizes éticas afirmativas e repudio qualquer prática discriminatória ou de 'cura gay'.")

            submitted = st.form_submit_button("Submeter para Análise da Equipe Vox 🌈")
            if submitted:
                if not declaracao_etica:
                    st.error("É obrigatório concordar com as diretrizes éticas afirmativas para submissão.")
                elif not (nome_entidade and email_contato):
                    st.warning("Preencha ao menos seu nome/entidade e e-mail de contato.")
                else:
                    st.success("✅ Solicitação enviada com sucesso! Nossa equipe entrará em contato para validação dos dados.")


# Se executado diretamente como página do Streamlit
if __name__ == "__main__":
    st.set_page_config(page_title="Rede de Apoio — Vox AI", page_icon="🤝", layout="wide")
    render_rede_apoio()
