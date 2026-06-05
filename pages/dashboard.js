
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
                const sortedTopics = [];
                data.forEach(item => {
                    const qty = parseInt(item.quantidade) || 0;
                    totalChunks += qty;
                    if (item.tema) {
                        sortedTopics.push([item.tema, qty]);
                    }
                    if (item.modificado_em) {
                        const d = new Date(item.modificado_em).getTime();
                        if (d > maxDate) maxDate = d;
                    }
                });

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

                // Atualizar Distribuição de Temas
                if (statsEl) {
                    sortedTopics.sort((a, b) => b[1] - a[1]);
                    if (sortedTopics.length > 0) {
                        let html = '<div class="kb-health-grid">';
                        sortedTopics.forEach(([topic, count]) => {
                            const pct = totalChunks > 0 ? Math.round((count / totalChunks) * 100) : 0;
                            html += `
                                <div class="kb-topic-card">
                                    <div class="kb-topic-header">
                                        <h4 class="kb-topic-title">${escapeHtml(topic)}</h4>
                                        <span class="kb-topic-badge">${count} ${count === 1 ? 'chunk' : 'chunks'}</span>
                                    </div>
                                    <div>
                                        <div class="kb-topic-bar-container">
                                            <div class="kb-topic-bar" style="width: ${pct}%"></div>
                                        </div>
                                        <div class="kb-topic-percentage">${pct}% do total</div>
                                    </div>
                                </div>
                            `;
                        });
                        html += '</div>';
                        statsEl.innerHTML = html;
                    } else {
                        statsEl.innerHTML = '<p style="color: var(--text-secondary);">Nenhum tema cadastrado na base de conhecimento.</p>';
                    }
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