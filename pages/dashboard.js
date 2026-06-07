
const SUPABASE_URL_DEV = "__SUPABASE_URL_DEV__";
const SUPABASE_ANON_KEY_DEV = "__SUPABASE_ANON_KEY_DEV__";

function escapeHtml(unsafe) {
    if (unsafe == null) return '';
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

document.addEventListener('DOMContentLoaded', function () {

    // Carregar changelog (sempre executa, independente do Supabase)
    const changelogEl = document.getElementById('latest-changelog');
    if (changelogEl) {
        fetch('CHANGELOG.md', { headers: { 'Cache-Control': 'no-cache' } })
            .then(response => {
                if (!response.ok) throw new Error('Erro ao buscar CHANGELOG.md');
                return response.text();
            })
            .then(markdown => {
                // Pega os 5 primeiros blocos que começam com "## "
                const start = markdown.indexOf('## ');
                if (start !== -1) {
                    let end = start;
                    for (let i = 0; i < 5; i++) {
                        const next = markdown.indexOf('\n## ', end + 1);
                        if (next === -1) {
                            end = markdown.length;
                            break;
                        }
                        end = next;
                    }
                    const entryMarkdown = markdown.substring(start, end);

                    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                        changelogEl.innerHTML = DOMPurify.sanitize(marked.parse(entryMarkdown));
                    } else {
                        changelogEl.innerText = entryMarkdown;
                    }
                }
            })
            .catch(error => {
                console.error("Erro Changelog:", error);
                changelogEl.innerHTML = '<p style="color: #ef4444;">Erro ao carregar histórico.</p>';
            });
    }

    // Verificar se as credenciais do Supabase estão configuradas e válidas
    let supabaseConfigured = false;
    if (SUPABASE_URL_DEV && SUPABASE_ANON_KEY_DEV && 
        !SUPABASE_URL_DEV.startsWith('__') && !SUPABASE_ANON_KEY_DEV.startsWith('__')) {
        try {
            new URL(SUPABASE_URL_DEV);
            supabaseConfigured = true;
        } catch (e) {
            console.warn("URL do Supabase inválida:", e);
        }
    }

    if (!supabaseConfigured) {
        console.warn("Supabase não configurado ou indisponível localmente.");
        const elCount = document.getElementById('kb-count');
        if (elCount) elCount.innerHTML = '<span style="font-size:0.5em">Indisponível</span>';
        const elVersion = document.getElementById('kb-version');
        if (elVersion) elVersion.innerText = 'Indisponível';
        const statsEl = document.getElementById('kb-health-stats');
        if (statsEl) statsEl.innerHTML = '<p style="color: var(--text-secondary);">Métricas indisponíveis em ambiente local de desenvolvimento.</p>';
        return;
    }

    const headers = {
        'apikey': SUPABASE_ANON_KEY_DEV,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY_DEV}`,
        'Content-Type': 'application/json'
    };

    // Buscar estatísticas agregadas da base de conhecimento
    const urlStats = new URL(`${SUPABASE_URL_DEV}/rest/v1/knowledge_base_public_stats`);
    urlStats.searchParams.set('select', 'tema,quantidade,modificado_em');

    fetch(urlStats.toString(), {
        method: 'GET',
        headers: headers
    })
        .then(response => response.json())
        .then(data => {
            let totalChunks = 0;
            let maxDate = 0;
            const statsEl = document.getElementById('kb-health-stats');
            
            if (Array.isArray(data) && data.length > 0) {
                const allTopics = [];
                data.forEach(item => {
                    const qty = parseInt(item.quantidade) || 0;
                    totalChunks += qty;
                    if (item.tema) {
                        allTopics.push({ tema: item.tema, quantidade: qty });
                    }
                    if (item.modificado_em) {
                        const d = new Date(item.modificado_em).getTime();
                        if (d > maxDate) maxDate = d;
                    }
                });

                // Ordenar tópicos por quantidade decrescente
                allTopics.sort((a, b) => b.quantidade - a.quantidade);

                // Calcular estatísticas rápidas
                const totalTopicsCount = allTopics.length;
                const highCoverageCount = allTopics.filter(t => t.quantidade >= 3).length;
                const lowCoverageCount = allTopics.filter(t => t.quantidade <= 2).length;
                const avgChunksPerTopic = totalTopicsCount > 0 ? (totalChunks / totalTopicsCount).toFixed(1) : 0;

                // Atualizar Contagem
                const elCount = document.getElementById('kb-count');
                if (elCount) elCount.innerText = totalChunks;

                // Atualizar Versão
                const elVersion = document.getElementById('kb-version');
                if (elVersion) {
                    if (maxDate > 0) {
                        const lastDate = new Date(maxDate);
                        const versionString = `v${lastDate.getFullYear()}.${String(lastDate.getMonth() + 1).padStart(2, '0')}.${String(lastDate.getDate()).padStart(2, '0')}`;
                        elVersion.innerText = versionString;
                    } else {
                        elVersion.innerText = "v1.0.0";
                    }
                }

                // Atualizar Distribuição de Temas de forma interativa e concisa
                if (statsEl) {
                    let currentFilter = 'all'; // 'all', 'high', 'low'
                    let searchQuery = '';
                    let visibleCardsCount = 12;
                    const cardsPerPage = 12;

                    // Estrutura básica dos controles
                    statsEl.innerHTML = `
                        <!-- Resumo Executivo da Base -->
                        <div class="kb-stats-summary">
                            <div class="kb-stat-widget">
                                <div class="stat-val">${totalTopicsCount}</div>
                                <div class="stat-lbl">Tópicos Cadastrados</div>
                            </div>
                            <div class="kb-stat-widget">
                                <div class="stat-val">${highCoverageCount}</div>
                                <div class="stat-lbl">Alta Cobertura (3+)</div>
                            </div>
                            <div class="kb-stat-widget">
                                <div class="stat-val">${lowCoverageCount}</div>
                                <div class="stat-lbl">Baixa Cobertura (1-2)</div>
                            </div>
                            <div class="kb-stat-widget">
                                <div class="stat-val">${avgChunksPerTopic}</div>
                                <div class="stat-lbl">Média de Chunks</div>
                            </div>
                        </div>

                        <!-- Barra de Ações (Filtro e Busca) -->
                        <div class="kb-controls-row">
                            <div class="kb-search-container">
                                <span class="kb-search-icon">🔍</span>
                                <input type="text" id="kb-search" class="kb-search-input" placeholder="Buscar tópico por nome...">
                            </div>
                            <div class="kb-filter-tabs">
                                <button class="kb-filter-tab active" data-filter="all">Todos (${totalTopicsCount})</button>
                                <button class="kb-filter-tab" data-filter="high">Alta Cobertura (${highCoverageCount})</button>
                                <button class="kb-filter-tab" data-filter="low">Baixa Cobertura (${lowCoverageCount})</button>
                            </div>
                        </div>

                        <!-- Container para renderizar os tópicos -->
                        <div id="kb-results-container"></div>
                    `;

                    const resultsContainer = document.getElementById('kb-results-container');
                    const searchInput = document.getElementById('kb-search');
                    const filterTabs = document.querySelectorAll('.kb-filter-tab');

                    function renderResults() {
                        if (!resultsContainer) return;

                        // Aplicar filtros de busca e aba selecionada
                        let filtered = allTopics.filter(topic => {
                            const matchesSearch = topic.tema.toLowerCase().includes(searchQuery.toLowerCase());
                            if (!matchesSearch) return false;

                            if (currentFilter === 'high') return topic.quantidade >= 3;
                            if (currentFilter === 'low') return topic.quantidade <= 2;
                            return true;
                        });

                        if (filtered.length === 0) {
                            resultsContainer.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 2rem;">Nenhum tópico encontrado com os filtros selecionados.</p>';
                            return;
                        }

                        let html = '';

                        if (currentFilter === 'low') {
                            // Apenas tópicos de baixa cobertura: renderizar em formato de Tags compactas
                            html += `
                                <div class="kb-section-header">Tópicos com Baixa Cobertura (${filtered.length})</div>
                                <div class="kb-tags-container">
                                    ${filtered.map(t => `
                                        <div class="kb-topic-tag" title="${escapeHtml(t.tema)}">
                                            <span>${escapeHtml(t.tema)}</span>
                                            <span class="tag-count">${t.quantidade}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            `;
                        } else if (currentFilter === 'high') {
                            // Apenas tópicos de alta cobertura: renderizar em formato de cards com barra de progresso
                            const paginated = filtered.slice(0, visibleCardsCount);
                            html += `
                                <div class="kb-section-header">Tópicos com Alta Cobertura (${filtered.length})</div>
                                <div class="kb-health-grid">
                                    ${paginated.map(t => {
                                        const pct = totalChunks > 0 ? Math.round((t.quantidade / totalChunks) * 100) : 0;
                                        return `
                                            <div class="kb-topic-card">
                                                <div class="kb-topic-header">
                                                    <h4 class="kb-topic-title">${escapeHtml(t.tema)}</h4>
                                                    <span class="kb-topic-badge">${t.quantidade} ${t.quantidade === 1 ? 'chunk' : 'chunks'}</span>
                                                </div>
                                                <div>
                                                    <div class="kb-topic-bar-container">
                                                        <div class="kb-topic-bar" style="width: ${pct}%"></div>
                                                    </div>
                                                    <div class="kb-topic-percentage">${pct}% do total</div>
                                                </div>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            `;

                            if (filtered.length > visibleCardsCount) {
                                html += `
                                    <div class="kb-pagination-container">
                                        <button id="kb-btn-load-more" class="kb-load-more-btn">Carregar Mais Tópicos</button>
                                    </div>
                                `;
                            }
                        } else {
                            // Aba "Todos": Dividir o espaço. Cards para os de Alta Cobertura (paginados) e Tags compactas para Baixa Cobertura
                            const highList = filtered.filter(t => t.quantidade >= 3);
                            const lowList = filtered.filter(t => t.quantidade <= 2);

                            if (highList.length > 0) {
                                const paginatedHigh = highList.slice(0, visibleCardsCount);
                                html += `
                                    <div class="kb-section-header">Tópicos com Alta Cobertura (${highList.length})</div>
                                    <div class="kb-health-grid">
                                        ${paginatedHigh.map(t => {
                                            const pct = totalChunks > 0 ? Math.round((t.quantidade / totalChunks) * 100) : 0;
                                            return `
                                                <div class="kb-topic-card">
                                                    <div class="kb-topic-header">
                                                        <h4 class="kb-topic-title">${escapeHtml(t.tema)}</h4>
                                                        <span class="kb-topic-badge">${t.quantidade} ${t.quantidade === 1 ? 'chunk' : 'chunks'}</span>
                                                    </div>
                                                    <div>
                                                        <div class="kb-topic-bar-container">
                                                            <div class="kb-topic-bar" style="width: ${pct}%"></div>
                                                        </div>
                                                        <div class="kb-topic-percentage">${pct}% do total</div>
                                                    </div>
                                                </div>
                                            `;
                                        }).join('')}
                                    </div>
                                `;

                                if (highList.length > visibleCardsCount) {
                                    html += `
                                        <div class="kb-pagination-container">
                                            <button id="kb-btn-load-more" class="kb-load-more-btn">Carregar Mais Tópicos</button>
                                        </div>
                                    `;
                                }
                            }

                            if (lowList.length > 0) {
                                html += `
                                    <div class="kb-section-header" style="margin-top: 2.5rem;">Tópicos com Baixa Cobertura (${lowList.length})</div>
                                    <div class="kb-tags-container">
                                        ${lowList.map(t => `
                                            <div class="kb-topic-tag" title="${escapeHtml(t.tema)}">
                                                <span>${escapeHtml(t.tema)}</span>
                                                <span class="tag-count">${t.quantidade}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                `;
                            }
                        }

                        resultsContainer.innerHTML = html;

                        // Adicionar listener ao botão Carregar Mais
                        const loadMoreBtn = document.getElementById('kb-btn-load-more');
                        if (loadMoreBtn) {
                            loadMoreBtn.addEventListener('click', () => {
                                visibleCardsCount += cardsPerPage;
                                renderResults();
                            });
                        }
                    }

                    // Ouvinte do campo de busca
                    searchInput.addEventListener('input', (e) => {
                        searchQuery = e.target.value;
                        visibleCardsCount = cardsPerPage; // Resetar paginação
                        renderResults();
                    });

                    // Ouvinte de mudança de abas de filtro
                    filterTabs.forEach(tab => {
                        tab.addEventListener('click', () => {
                            filterTabs.forEach(t => t.classList.remove('active'));
                            tab.classList.add('active');
                            currentFilter = tab.getAttribute('data-filter');
                            visibleCardsCount = cardsPerPage; // Resetar paginação
                            renderResults();
                        });
                    });

                    // Primeira renderização
                    renderResults();
                }
            } else {
                // Dados vazios
                const elCount = document.getElementById('kb-count');
                if (elCount) elCount.innerText = "0";
                
                const elVersion = document.getElementById('kb-version');
                if (elVersion) elVersion.innerText = "v1.0.0";
                
                if (statsEl) {
                    statsEl.innerHTML = '<p style="color: var(--text-secondary);">Nenhum tema cadastrado na base de conhecimento.</p>';
                }
            }
        })
        .catch(error => {
            console.error("Erro ao carregar estatísticas da base:", error);
            const elCount = document.getElementById('kb-count');
            if (elCount) elCount.innerHTML = '<span style="font-size:0.5em">Indisponível</span>';
            const elVersion = document.getElementById('kb-version');
            if (elVersion) elVersion.innerText = 'Online';
            const statsEl = document.getElementById('kb-health-stats');
            if (statsEl) statsEl.innerHTML = '<p style="color: #ef4444;">Falha ao carregar estatísticas da base.</p>';
        });
});