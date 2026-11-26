const SUPABASE_URL_DEV = "__SUPABASE_URL_DEV__";
const SUPABASE_ANON_KEY_DEV = "__SUPABASE_ANON_KEY_DEV__";

const DEV_ONLY_TOPICS = new Set([
    "Como Contribuir",
    "Padrões de Commit",
    "Acesso ao Banco de Dados",
    "Código Aberto e Git",
]);

function escapeHtml(unsafe) {
    if (unsafe == null) return "";
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function t(key, vars) {
    if (typeof window.voxT === "function") {
        return window.voxT(key, vars);
    }
    return key;
}

function bindExternalLinks() {
    if (typeof VOX_LINKS === "undefined") return;
    const lang = typeof window.voxGetLang === "function" ? window.voxGetLang() : "pt";
    const baseStreamlit = VOX_LINKS.VOX_STREAMLIT || "";
    const streamlitHref = lang === "en" && baseStreamlit
        ? (baseStreamlit.includes("?") ? `${baseStreamlit}&lang=en` : `${baseStreamlit}?lang=en`)
        : baseStreamlit;

    const elementLinks = {
        owner_vox: VOX_LINKS.OWNER_VOX,
        github_repo: VOX_LINKS.GITHUB_REPO,
        changelog: VOX_LINKS.CHANGELOG,
        license: VOX_LINKS.LICENSE,
        privacy_policy: VOX_LINKS.PRIVACY_POLICY,
        code_of_conduct: VOX_LINKS.CODE_OF_CONDUCT,
        security: VOX_LINKS.SECURITY,
        contributing: VOX_LINKS.CONTRIBUTING,
        vox_streamlit: streamlitHref,
        hugging_face: VOX_LINKS.HUGGING_FACE,
        instagram: VOX_LINKS.INSTAGRAM,
        linkedin: VOX_LINKS.LINKEDIN,
        feedback: VOX_LINKS.FEEDBACK,
        contribute_kb_form: VOX_LINKS.CONTRIBUTE_KB_FORM,
        linktree: VOX_LINKS.LINKTREE,
        rodrigo_santos: VOX_LINKS.RODRIGO_SANTOS,
        camila_fernandes: VOX_LINKS.CAMILA_FERNANDES,
    };

    for (const [key, url] of Object.entries(elementLinks)) {
        if (!url) continue;
        document.querySelectorAll(`[data-link="${key}"]`).forEach((el) => {
            el.href = url;
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {
    bindExternalLinks();

    const kbState = {
        status: "loading", // 'loading' | 'unconfigured' | 'ready' | 'empty' | 'error'
        allTopics: [],
        totalEntries: 0,
        maxTopicQty: 0,
        maxDate: 0,
        searchQuery: "",
        visibleHighCount: 9,
        cardsPerPage: 9,
        userExpandedEarly: false,
    };

    const statsEl = document.getElementById("kb-health-stats");
    const elVersion = document.getElementById("kb-version");

    function setVersionText(text) {
        if (elVersion) elVersion.innerText = text;
    }

    function renderKbErrorOrStatus(message, isError = false) {
        if (!statsEl) return;
        const color = isError ? "#ef4444" : "var(--text-secondary)";
        statsEl.innerHTML = `<p style="color: ${color};">${escapeHtml(message)}</p>`;
    }

    function renderKbReady() {
        if (!statsEl) return;

        const totalTopicsCount = kbState.allTopics.length;
        const highTopicsAll = kbState.allTopics.filter((item) => item.quantidade >= 3);
        const lowTopicsAll = kbState.allTopics.filter((item) => item.quantidade <= 2);

        const existingSearch = document.getElementById("kb-search");
        const hadFocus = existingSearch && document.activeElement === existingSearch;
        const cursorPos = existingSearch ? existingSearch.selectionStart : null;

        const contributeFormUrl =
            (typeof VOX_LINKS !== "undefined" && VOX_LINKS.CONTRIBUTE_KB_FORM) ||
            "https://forms.gle/Bwb3NEurV7YoZFXG8";

        statsEl.innerHTML = `
            <div class="kb-stats-summary">
                <div class="kb-stat-widget">
                    <div class="stat-val">${totalTopicsCount}</div>
                    <div class="stat-lbl">${escapeHtml(t("kb_stat_mapped"))}</div>
                </div>
                <div class="kb-stat-widget">
                    <div class="stat-val">${highTopicsAll.length}</div>
                    <div class="stat-lbl">${escapeHtml(t("kb_stat_indepth"))}</div>
                </div>
                <div class="kb-stat-widget">
                    <div class="stat-val">${kbState.totalEntries}</div>
                    <div class="stat-lbl">${escapeHtml(t("kb_stat_entries"))}</div>
                </div>
            </div>

            <div class="kb-controls-row">
                <div class="kb-search-container">
                    <span class="kb-search-icon" aria-hidden="true">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                    </span>
                    <input
                        type="text"
                        id="kb-search"
                        class="kb-search-input"
                        value="${escapeHtml(kbState.searchQuery)}"
                        placeholder="${escapeHtml(t("kb_search_placeholder"))}"
                        aria-label="${escapeHtml(t("kb_search_placeholder"))}"
                    >
                    <button
                        type="button"
                        id="kb-search-clear"
                        class="kb-search-clear${kbState.searchQuery.trim() ? "" : " is-hidden"}"
                        aria-label="${escapeHtml(t("kb_search_clear_aria"))}"
                    >✕</button>
                </div>
                <p id="kb-filter-status" class="kb-filter-status"></p>
            </div>

            <div id="kb-results-container"></div>
        `;

        const searchInput = document.getElementById("kb-search");
        const clearBtn = document.getElementById("kb-search-clear");
        const statusEl = document.getElementById("kb-filter-status");
        const resultsContainer = document.getElementById("kb-results-container");

        if (hadFocus && searchInput) {
            searchInput.focus();
            if (cursorPos !== null) {
                searchInput.setSelectionRange(cursorPos, cursorPos);
            }
        }

        function renderTopicCard(item) {
            const pct = kbState.totalEntries > 0
                ? Math.max(1, Math.round((item.quantidade / kbState.totalEntries) * 100))
                : 0;
            const barWidth = kbState.maxTopicQty > 0
                ? Math.round((item.quantidade / kbState.maxTopicQty) * 100)
                : 0;
            const unitLabel = item.quantidade === 1
                ? t("kb_entries_singular")
                : t("kb_entries_plural");

            return `
                <div class="kb-topic-card">
                    <div class="kb-topic-header">
                        <h4 class="kb-topic-title">${escapeHtml(item.tema)}</h4>
                        <span class="kb-topic-badge">${item.quantidade} ${escapeHtml(unitLabel)}</span>
                    </div>
                    <div>
                        <div class="kb-topic-bar-container">
                            <div class="kb-topic-bar" data-width="${barWidth}%" style="width: 0%"></div>
                        </div>
                        <div class="kb-topic-percentage">${pct}% ${escapeHtml(t("kb_pct_of_total"))}</div>
                    </div>
                </div>
            `;
        }

        function updateResults() {
            if (!resultsContainer) return;
            const q = kbState.searchQuery.trim().toLowerCase();

            if (clearBtn) {
                clearBtn.classList.toggle("is-hidden", !q);
            }
            if (statusEl) {
                statusEl.textContent = q
                    ? `${t("kb_filter_search_status")} "${kbState.searchQuery.trim()}"`
                    : t("kb_filter_all_status");
            }

            const highList = highTopicsAll.filter((item) => item.tema.toLowerCase().includes(q));
            const lowList = lowTopicsAll.filter((item) => item.tema.toLowerCase().includes(q));

            if (highList.length === 0 && lowList.length === 0) {
                resultsContainer.innerHTML = `<p class="kb-empty-message">${escapeHtml(t("kb_empty_search"))}</p>`;
                return;
            }

            let html = "";

            if (highList.length > 0) {
                const visibleHigh = q ? highList : highList.slice(0, kbState.visibleHighCount);
                html += `
                    <div class="kb-section-header">${escapeHtml(t("kb_high_heading"))} (${highList.length})</div>
                    <div class="kb-health-grid">
                        ${visibleHigh.map(renderTopicCard).join("")}
                    </div>
                `;

                if (!q && highList.length > kbState.visibleHighCount) {
                    const remaining = highList.length - kbState.visibleHighCount;
                    html += `
                        <div class="kb-pagination-container">
                            <button type="button" id="kb-btn-load-more" class="kb-load-more-btn">
                                ${escapeHtml(t("kb_show_more"))} (+${remaining})
                            </button>
                        </div>
                    `;
                }
            }

            if (lowList.length > 0) {
                const isOpenAttr = (q || kbState.userExpandedEarly) ? " open" : "";
                const summaryKey = q ? "kb_early_summary_filtered" : "kb_early_summary";
                const summaryText = t(summaryKey, { count: lowList.length });

                html += `
                    <details id="kb-early-details" class="kb-early-details"${isOpenAttr}>
                        <summary class="kb-early-summary">
                            <span>${escapeHtml(summaryText)}</span>
                            <svg class="kb-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </summary>
                        <div class="kb-early-body">
                            <p class="kb-early-invite">
                                <span>${escapeHtml(t("kb_early_invite"))}</span>
                                <a href="${escapeHtml(contributeFormUrl)}" target="_blank" rel="noopener noreferrer" class="kb-early-link">
                                    ${escapeHtml(t("kb_early_link"))}
                                </a>
                            </p>
                            <div class="kb-tags-container">
                                ${lowList.map((item) => `
                                    <span class="kb-topic-tag">${escapeHtml(item.tema)}</span>
                                `).join("")}
                            </div>
                        </div>
                    </details>
                `;
            }

            resultsContainer.innerHTML = html;

            requestAnimationFrame(() => {
                resultsContainer.querySelectorAll(".kb-topic-bar[data-width]").forEach((bar) => {
                    bar.style.width = bar.getAttribute("data-width");
                });
            });

            const loadMoreBtn = document.getElementById("kb-btn-load-more");
            if (loadMoreBtn) {
                loadMoreBtn.addEventListener("click", () => {
                    kbState.visibleHighCount += 12;
                    updateResults();
                });
            }

            const detailsEl = document.getElementById("kb-early-details");
            if (detailsEl) {
                detailsEl.addEventListener("toggle", () => {
                    if (!kbState.searchQuery.trim()) {
                        kbState.userExpandedEarly = detailsEl.open;
                    }
                });
            }
        }

        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                kbState.searchQuery = e.target.value || "";
                kbState.visibleHighCount = kbState.cardsPerPage;
                updateResults();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener("click", () => {
                kbState.searchQuery = "";
                kbState.visibleHighCount = kbState.cardsPerPage;
                if (searchInput) searchInput.value = "";
                updateResults();
            });
        }

        updateResults();
    }

    function renderKbByState() {
        if (kbState.status === "ready") {
            renderKbReady();
            return;
        }
        if (kbState.status === "unconfigured") {
            setVersionText(t("kb_unavailable"));
            renderKbErrorOrStatus(t("kb_local_unavailable"));
            return;
        }
        if (kbState.status === "empty") {
            setVersionText("v1.0.0");
            renderKbErrorOrStatus(t("kb_empty_db"));
            return;
        }
        if (kbState.status === "error") {
            setVersionText(t("kb_unavailable"));
            renderKbErrorOrStatus(t("kb_fetch_error"), true);
        }
    }

    window.voxRenderKb = renderKbByState;

    // Carregar changelog (3 últimas versões)
    const changelogEl = document.getElementById("latest-changelog");
    if (changelogEl) {
        fetch("CHANGELOG.md", { headers: { "Cache-Control": "no-cache" } })
            .then((response) => {
                if (!response.ok) throw new Error("Erro ao buscar CHANGELOG.md");
                return response.text();
            })
            .then((markdown) => {
                const start = markdown.indexOf("## ");
                if (start !== -1) {
                    let end = start;
                    for (let i = 0; i < 3; i++) {
                        const next = markdown.indexOf("\n## ", end + 1);
                        if (next === -1) {
                            end = markdown.length;
                            break;
                        }
                        end = next;
                    }
                    const entryMarkdown = markdown.substring(start, end);

                    if (typeof marked !== "undefined" && typeof DOMPurify !== "undefined") {
                        changelogEl.innerHTML = DOMPurify.sanitize(marked.parse(entryMarkdown));
                    } else {
                        changelogEl.innerText = entryMarkdown;
                    }
                }
            })
            .catch((error) => {
                console.error("Erro Changelog:", error);
                changelogEl.innerHTML = `<p style="color: #ef4444;">${escapeHtml(t("changelog_error"))}</p>`;
            });
    }

    // Verificar credenciais do Supabase
    let supabaseConfigured = false;
    if (
        SUPABASE_URL_DEV &&
        SUPABASE_ANON_KEY_DEV &&
        !SUPABASE_URL_DEV.startsWith("__") &&
        !SUPABASE_ANON_KEY_DEV.startsWith("__")
    ) {
        try {
            new URL(SUPABASE_URL_DEV);
            supabaseConfigured = true;
        } catch (e) {
            console.warn("URL do Supabase inválida:", e);
        }
    }

    if (!supabaseConfigured) {
        console.warn("Supabase não configurado ou indisponível localmente.");
        kbState.status = "unconfigured";
        renderKbByState();
        return;
    }

    const headers = {
        apikey: SUPABASE_ANON_KEY_DEV,
        Authorization: `Bearer ${SUPABASE_ANON_KEY_DEV}`,
        "Content-Type": "application/json",
    };

    const urlStats = new URL(`${SUPABASE_URL_DEV}/rest/v1/knowledge_base_public_stats`);
    urlStats.searchParams.set("select", "tema,quantidade,modificado_em");

    fetch(urlStats.toString(), {
        method: "GET",
        headers: headers,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Erro HTTP ${response.status} ao buscar estatísticas da base`);
            }
            return response.json();
        })
        .then((data) => {
            if (Array.isArray(data) && data.length > 0) {
                const allTopics = [];
                let totalEntries = 0;
                let maxDate = 0;

                data.forEach((item) => {
                    if (item.modificado_em) {
                        const d = new Date(item.modificado_em).getTime();
                        if (d > maxDate) maxDate = d;
                    }

                    if (!item.tema || DEV_ONLY_TOPICS.has(item.tema)) {
                        return;
                    }

                    const qty = parseInt(item.quantidade, 10) || 0;
                    totalEntries += qty;
                    allTopics.push({ tema: item.tema, quantidade: qty });
                });

                allTopics.sort((a, b) => b.quantidade - a.quantidade || a.tema.localeCompare(b.tema));

                if (maxDate > 0) {
                    const lastDate = new Date(maxDate);
                    const versionString = `v${lastDate.getFullYear()}.${String(lastDate.getMonth() + 1).padStart(2, "0")}.${String(lastDate.getDate()).padStart(2, "0")}`;
                    setVersionText(versionString);
                } else {
                    setVersionText("v1.0.0");
                }

                if (allTopics.length === 0) {
                    kbState.status = "empty";
                    renderKbByState();
                    return;
                }

                kbState.allTopics = allTopics;
                kbState.totalEntries = totalEntries;
                kbState.maxTopicQty = allTopics[0].quantidade;
                kbState.maxDate = maxDate;
                kbState.status = "ready";
                renderKbByState();
            } else {
                kbState.status = "empty";
                renderKbByState();
            }
        })
        .catch((error) => {
            console.error("Erro ao carregar estatísticas da base:", error);
            kbState.status = "error";
            renderKbByState();
        });
});
