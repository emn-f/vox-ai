(function () {
    "use strict";

    const STORAGE_KEY = "vox_lang";

    const DICT = {
        pt: {
            meta_title: "Vox AI — Informação é uma forma de cuidado",
            meta_description: "Vox AI: assistente gratuito, anônimo e open source sobre direitos, saúde e acolhimento LGBTQIA+ no Brasil.",
            nav_aria: "Navegação principal",
            nav_about: "Sobre",
            nav_kb: "Base de conhecimento",
            nav_contribute: "Contribuir",
            nav_updates: "Atualizações",
            lang_group_aria: "Selecionar idioma",
            header_cta: "Acessar o Vox AI",

            hero_eyebrow: "Projeto Vox",
            hero_title: "Informação é uma forma de cuidado.",
            hero_lead: "Assistente gratuito e anônimo para tirar dúvidas sobre direitos, saúde e acolhimento LGBTQIA+ no Brasil. Código aberto, feito em Salvador (BA).",
            hero_btn_chat: "Conversar com o Vox AI",
            hero_btn_github: "Ver código no GitHub",
            hero_facts: "100% gratuito · Sem cadastro (LGPD) · Texto e voz · Código aberto",
            hero_photo_alt: "Grupo diverso da comunidade LGBTQIA+ sorrindo reunido com leque e vestido nas cores do arco-íris após a Parada do Orgulho em São Paulo",
            hero_photo_caption: "Comunidade que acolhe e fortalece",
            photo_credit_label: "Foto:",

            about_eyebrow: "Sobre o projeto",
            about_title: "Como o Vox AI nasceu e o que ele cobre",
            about_p1: "O Vox AI nasceu em 2025 como projeto de extensão na disciplina <em>Tecnologias e Inteligências Artificiais</em> da <strong>Universidade Católica do Salvador (UCSAL)</strong>, com o objetivo de facilitar o acesso a informações confiáveis sobre direitos, saúde e acolhimento para a comunidade LGBTQIA+ em Salvador (BA).",
            about_p2: "Encerrada a disciplina, o projeto continuou em desenvolvimento de forma <strong>independente, gratuita e open source</strong>, mantido sem financiamento institucional, com base de conhecimento verificada e escuta de iniciativas locais como a Casa Marielle Franco.",
            pillar1_title: "Direitos e legislação",
            pillar1_desc: "Leis, retificação de nome e proteção contra discriminação.",
            pillar2_title: "Saúde integral",
            pillar2_desc: "SUS, prevenção (PrEP/PEP), hormonioterapia e saúde mental.",
            pillar3_title: "Rede de acolhimento",
            pillar3_desc: "Casas de acolhida, centros de referência e canais seguros.",
            pillar4_title: "Memória e cultura",
            pillar4_desc: "História do movimento, representatividade e educação inclusiva.",
            about_photo_alt: "Quatro pessoas amigas abraçadas de costas observando o horizonte ao pôr do sol em um morro",
            about_photo_caption: "Rede de apoio e escuta ativa",
            partner_eyebrow: "Parceria comunitária",
            partner_desc: "Instituição de acolhimento independente em Salvador, coordenada por Sandra Muñoz. Entrevistas e uma visita presencial em 2025 orientaram a linguagem, o acolhimento e os recursos de acessibilidade do Vox AI.",
            team_eyebrow: "Quem constrói o projeto",
            team_role_lead: "Idealizador e manutenção",
            team_role_devs: "Desenvolvimento (contribuições)",
            team_role_ext: "Equipe inicial do projeto de extensão (UCSAL, 2025.1)",

            kb_eyebrow: "Transparência",
            kb_title: "O que o Vox AI sabe hoje",
            kb_desc: "Temas verificados na base de conhecimento do assistente. Assuntos com cobertura inicial ficam recolhidos e abertos a sugestões da comunidade.",
            kb_loading: "Carregando estatísticas da base...",
            kb_unavailable: "Indisponível",
            kb_local_unavailable: "Métricas indisponíveis em ambiente local de desenvolvimento.",
            kb_empty_db: "Nenhum tema cadastrado na base de conhecimento.",
            kb_fetch_error: "Falha ao carregar estatísticas da base.",
            kb_stat_mapped: "Temas mapeados",
            kb_stat_indepth: "Temas aprofundados",
            kb_stat_entries: "Registros verificados",
            kb_search_placeholder: "Buscar tema...",
            kb_search_clear_aria: "Limpar busca",
            kb_filter_all_status: "Exibindo temas verificados da base pública",
            kb_filter_search_status: "Filtro ativo:",
            kb_high_heading: "Temas aprofundados",
            kb_entries_singular: "registro",
            kb_entries_plural: "registros",
            kb_pct_of_total: "do total",
            kb_show_more: "Ver mais temas",
            kb_early_summary: "Temas com cobertura inicial ({count}) — ajude a expandir",
            kb_early_summary_filtered: "Temas com cobertura inicial encontrados ({count})",
            kb_early_invite: "Esses assuntos ainda têm poucos registros na base. Quer ajudar a ampliar ou revisar algum deles?",
            kb_early_link: "Sugerir conteúdo →",
            kb_empty_search: "Nenhum tema encontrado para o termo buscado.",

            cta_photo_alt: "Grupo diverso de amigos sorrindo e conversando em um piquenique ao ar livre em um parque",
            cta_photo_caption: "Comunidade e troca colaborativa",
            cta_eyebrow: "Código aberto",
            cta_title: "Contribua com o projeto Vox AI",
            cta_desc: "O código e a curadoria do Vox AI são abertos. Você pode ajudar corrigindo bugs, melhorando a documentação, traduzindo ou sugerindo novos temas para a base de conhecimento.",
            cta_btn_guide: "Guia de contribuição",
            cta_btn_feedback: "Sugerir conteúdo / feedback",
            gov_license: "Licença GNU GPLv3",
            gov_privacy: "Privacidade (LGPD)",
            gov_conduct: "Código de conduta",
            gov_security: "Segurança",
            tech_label: "Tecnologias",

            updates_eyebrow: "Atualizações",
            updates_title: "Últimas versões",
            changelog_card_title: "Changelog recente",
            changelog_link: "Histórico completo no GitHub",
            changelog_loading: "Carregando changelog...",
            changelog_error: "Erro ao carregar histórico.",
            kb_version_label: "Versão da base",
            kb_version_note: "Última atualização registrada na base verificada.",
            quick_open_note: "Quer testar o assistente agora?",

            footer_slogan: "Informação é uma forma de cuidado",
            footer_copy: "© 2026 Projeto Vox · Tecnologia social open source",
            footer_credits: "Fotografias reais sob licença livre: <a href=\"https://commons.wikimedia.org/wiki/File:After_Parada_LGBTQIAP%2B_na_NAVE_%C2%B7_19_06_2022_%C2%B7_S%C3%A3o_Paulo_(SP)_(52433767424).jpg\" target=\"_blank\" rel=\"noopener noreferrer\">Oliver Kornblihtt / Mídia NINJA</a> (<a href=\"https://creativecommons.org/licenses/by-sa/2.0/\" target=\"_blank\" rel=\"noopener noreferrer\">CC BY-SA 2.0</a>) · <a href=\"https://stocksnap.io/photo/friends-hugging-6ZYX4YY4IR\" target=\"_blank\" rel=\"noopener noreferrer\">Helena Lopes — Apoio</a> e <a href=\"https://stocksnap.io/photo/friends-picnic-3IVBNKC2JH\" target=\"_blank\" rel=\"noopener noreferrer\">Comunidade</a> (<a href=\"https://creativecommons.org/publicdomain/zero/1.0/\" target=\"_blank\" rel=\"noopener noreferrer\">Domínio Público · CC0 1.0</a>)"
        },
        en: {
            meta_title: "Vox AI — Information is a form of care",
            meta_description: "Vox AI: a free, anonymous, open-source assistant on LGBTQIA+ rights, healthcare, and support networks in Brazil.",
            nav_aria: "Main navigation",
            nav_about: "About",
            nav_kb: "Knowledge base",
            nav_contribute: "Contribute",
            nav_updates: "Updates",
            lang_group_aria: "Select language",
            header_cta: "Open Vox AI",

            hero_eyebrow: "Vox Project",
            hero_title: "Information is a form of care.",
            hero_lead: "A free, anonymous assistant for questions about LGBTQIA+ rights, healthcare, and support networks in Brazil. Open source, built in Salvador, Bahia.",
            hero_btn_chat: "Chat with Vox AI",
            hero_btn_github: "View on GitHub",
            hero_facts: "100% free · No sign-up (LGPD) · Text & voice · Open source",
            hero_photo_alt: "Diverse group from the LGBTQIA+ community smiling together with a rainbow fan and dress after the São Paulo Pride Parade",
            hero_photo_caption: "Community that welcomes and strengthens",
            photo_credit_label: "Photo:",

            about_eyebrow: "About",
            about_title: "How Vox AI started and what it covers",
            about_p1: "Vox AI started in 2025 as a university extension project in the <em>Technologies and Artificial Intelligence</em> course at <strong>Universidade Católica do Salvador (UCSAL)</strong> in Salvador, Brazil, created to make reliable information on rights, healthcare, and support networks easier to reach for the LGBTQIA+ community.",
            about_p2: "After the course ended, development continued as an <strong>independent, free, open-source project</strong> with no institutional funding, grounded in verified content and dialogue with local initiatives such as Casa Marielle Franco.",
            pillar1_title: "Rights & legislation",
            pillar1_desc: "Brazilian laws, legal name/gender change, and anti-discrimination protections.",
            pillar2_title: "Healthcare",
            pillar2_desc: "Public health (SUS), prevention (PrEP/PEP), hormone care, and mental health.",
            pillar3_title: "Support network",
            pillar3_desc: "Shelters, public reference centers, and safe community channels.",
            pillar4_title: "History & culture",
            pillar4_desc: "Movement history, representation, and inclusive education.",
            about_photo_alt: "Four friends embracing from behind while looking out at the horizon at sunset on a hilltop",
            about_photo_caption: "Support network and active listening",
            partner_eyebrow: "Community partner",
            partner_desc: "An independent shelter in Salvador coordinated by Sandra Muñoz. Interviews and a 2025 field visit shaped Vox AI's tone, guidance, and accessibility priorities.",
            team_eyebrow: "People behind the project",
            team_role_lead: "Creator & maintainer",
            team_role_devs: "Development contributors",
            team_role_ext: "Initial extension project team (UCSAL, 2025.1)",

            kb_eyebrow: "Transparency",
            kb_title: "What Vox AI covers today",
            kb_desc: "Curated topics in the assistant's knowledge base. Early-coverage topics stay collapsed and open for community input. Knowledge base entries are currently maintained in Portuguese.",
            kb_loading: "Loading knowledge base stats...",
            kb_unavailable: "Unavailable",
            kb_local_unavailable: "Metrics unavailable in local development environment.",
            kb_empty_db: "No topics found in the knowledge base.",
            kb_fetch_error: "Failed to load knowledge base statistics.",
            kb_stat_mapped: "Mapped topics",
            kb_stat_indepth: "In-depth topics",
            kb_stat_entries: "Verified entries",
            kb_search_placeholder: "Search topic...",
            kb_search_clear_aria: "Clear search",
            kb_filter_all_status: "Showing curated public topics",
            kb_filter_search_status: "Active filter:",
            kb_high_heading: "In-depth topics",
            kb_entries_singular: "entry",
            kb_entries_plural: "entries",
            kb_pct_of_total: "of total",
            kb_show_more: "Show more topics",
            kb_early_summary: "Early-coverage topics ({count}) — help expand them",
            kb_early_summary_filtered: "Matching early-coverage topics ({count})",
            kb_early_invite: "These topics currently have limited entries. Want to help expand or review them?",
            kb_early_link: "Suggest content →",
            kb_empty_search: "No topics found for your search.",

            cta_photo_alt: "Diverse group of friends smiling and talking during an outdoor picnic in a park",
            cta_photo_caption: "Community and open collaboration",
            cta_eyebrow: "Open source",
            cta_title: "Contribute to Vox AI",
            cta_desc: "Both the code and content curation of Vox AI are open source. You can help by fixing bugs, improving documentation, translating, or suggesting new topics for the knowledge base.",
            cta_btn_guide: "Contributing guide",
            cta_btn_feedback: "Suggest content / feedback",
            gov_license: "GNU GPLv3 License",
            gov_privacy: "Privacy (LGPD)",
            gov_conduct: "Code of conduct",
            gov_security: "Security",
            tech_label: "Stack",

            updates_eyebrow: "Updates",
            updates_title: "Latest releases",
            changelog_card_title: "Recent changelog",
            changelog_link: "Full history on GitHub",
            changelog_loading: "Loading changelog...",
            changelog_error: "Failed to load changelog.",
            kb_version_label: "Knowledge base version",
            kb_version_note: "Latest update recorded in the verified base.",
            quick_open_note: "Want to try the assistant right now?",

            footer_slogan: "Information is a form of care",
            footer_copy: "© 2026 Vox Project · Open-source social technology",
            footer_credits: "Real photographs under free licenses: <a href=\"https://commons.wikimedia.org/wiki/File:After_Parada_LGBTQIAP%2B_na_NAVE_%C2%B7_19_06_2022_%C2%B7_S%C3%A3o_Paulo_(SP)_(52433767424).jpg\" target=\"_blank\" rel=\"noopener noreferrer\">Oliver Kornblihtt / Mídia NINJA</a> (<a href=\"https://creativecommons.org/licenses/by-sa/2.0/\" target=\"_blank\" rel=\"noopener noreferrer\">CC BY-SA 2.0</a>) · <a href=\"https://stocksnap.io/photo/friends-hugging-6ZYX4YY4IR\" target=\"_blank\" rel=\"noopener noreferrer\">Helena Lopes — Support</a> &amp; <a href=\"https://stocksnap.io/photo/friends-picnic-3IVBNKC2JH\" target=\"_blank\" rel=\"noopener noreferrer\">Community</a> (<a href=\"https://creativecommons.org/publicdomain/zero/1.0/\" target=\"_blank\" rel=\"noopener noreferrer\">Public Domain · CC0 1.0</a>)"
        }
    };

    function normalizeLang(lang) {
        if (typeof lang !== "string") return "pt";
        const clean = lang.trim().toLowerCase();
        return clean === "en" ? "en" : "pt";
    }

    function detectInitialLang() {
        try {
            const params = new URLSearchParams(window.location.search);
            const paramLang = params.get("lang");
            if (paramLang) {
                const cleanParam = paramLang.trim().toLowerCase();
                if (cleanParam === "en" || cleanParam === "pt") return cleanParam;
            }
        } catch (e) {
            // Ignora falha de leitura de URL
        }

        try {
            const saved = window.localStorage.getItem(STORAGE_KEY);
            if (saved === "en" || saved === "pt") return saved;
        } catch (e) {
            // Ignora ambiente sem localStorage
        }

        return "pt";
    }

    let currentLang = detectInitialLang();

    function voxT(key, vars) {
        const table = DICT[currentLang] || DICT.pt;
        let text = table[key] !== undefined ? table[key] : (DICT.pt[key] !== undefined ? DICT.pt[key] : key);
        if (vars && typeof text === "string") {
            Object.keys(vars).forEach(function (k) {
                text = text.replace(new RegExp("\\{" + k + "\\}", "g"), String(vars[k]));
            });
        }
        return text;
    }

    function syncStreamlitLinks(lang) {
        if (typeof VOX_LINKS === "undefined" || !VOX_LINKS.VOX_STREAMLIT) return;
        const base = VOX_LINKS.VOX_STREAMLIT;
        const targetHref = lang === "en"
            ? (base.includes("?") ? base + "&lang=en" : base + "?lang=en")
            : base;

        document.querySelectorAll('[data-link="vox_streamlit"]').forEach(function (el) {
            el.href = targetHref;
        });
    }

    function applyLanguage(lang, updateUrl) {
        currentLang = normalizeLang(lang);
        document.documentElement.lang = currentLang === "en" ? "en" : "pt-BR";
        document.title = voxT("meta_title");

        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) {
            metaDesc.setAttribute("content", voxT("meta_description"));
        }

        document.querySelectorAll("[data-i18n]").forEach(function (el) {
            const key = el.getAttribute("data-i18n");
            if (key) el.textContent = voxT(key);
        });

        document.querySelectorAll("[data-i18n-html]").forEach(function (el) {
            const key = el.getAttribute("data-i18n-html");
            if (key) el.innerHTML = voxT(key);
        });

        document.querySelectorAll("[data-i18n-aria]").forEach(function (el) {
            const key = el.getAttribute("data-i18n-aria");
            if (key) el.setAttribute("aria-label", voxT(key));
        });

        document.querySelectorAll("[data-i18n-alt]").forEach(function (el) {
            const key = el.getAttribute("data-i18n-alt");
            if (key) el.setAttribute("alt", voxT(key));
        });

        const searchInput = document.getElementById("kb-search");
        if (searchInput) {
            const ph = voxT("kb_search_placeholder");
            searchInput.setAttribute("placeholder", ph);
            searchInput.setAttribute("aria-label", ph);
        }

        const clearBtn = document.getElementById("kb-search-clear");
        if (clearBtn) {
            clearBtn.setAttribute("aria-label", voxT("kb_search_clear_aria"));
        }

        document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
            const active = btn.getAttribute("data-lang-btn") === currentLang;
            btn.classList.toggle("active", active);
            btn.setAttribute("aria-pressed", active ? "true" : "false");
        });

        const changelogNote = document.getElementById("changelog-en-note");
        if (changelogNote) {
            changelogNote.hidden = currentLang !== "en";
        }

        syncStreamlitLinks(currentLang);

        try {
            window.localStorage.setItem(STORAGE_KEY, currentLang);
        } catch (e) {
            // Ignora ambiente sem localStorage
        }

        if (updateUrl) {
            try {
                const url = new URL(window.location.href);
                if (currentLang === "en") {
                    url.searchParams.set("lang", "en");
                } else {
                    url.searchParams.delete("lang");
                }
                window.history.replaceState({}, "", url.pathname + url.search + url.hash);
            } catch (e) {
                // Ignora se history API não estiver disponível
            }
        }

        if (typeof window.voxRenderKb === "function") {
            window.voxRenderKb();
        }
    }

    window.VOX_I18N = DICT;
    window.voxT = voxT;
    window.voxGetLang = function () { return currentLang; };
    window.voxSetLanguage = function (lang) { applyLanguage(lang, true); };

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                const targetLang = btn.getAttribute("data-lang-btn");
                if (targetLang && targetLang !== currentLang) {
                    applyLanguage(targetLang, true);
                }
            });
        });

        applyLanguage(currentLang, false);
    });
})();
