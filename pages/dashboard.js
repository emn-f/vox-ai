
const SUPABASE_URL = "__SUPABASE_URL__";
const SUPABASE_ANON_KEY_DEV = "__SUPABASE_ANON_KEY_DEV__";

document.addEventListener('DOMContentLoaded', function () {

    const headers = {
        'apikey': SUPABASE_ANON_KEY_DEV,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY_DEV}`,
        'Content-Type': 'application/json'
    };

    fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=kb_id&limit=1`, {
        method: 'GET',
        headers: {
            ...headers,
            'Prefer': 'count=exact'
        }
    })
        .then(response => {
            const contentRange = response.headers.get('Content-Range');

            if (contentRange) {
                const parts = contentRange.split('/');
                if (parts.length > 1 && parts[1] !== '*') {
                    const el = document.getElementById('kb-count');
                    // Subtrai 1 para desconsiderar o item "N/A"
                    if (el) el.innerText = Math.max(0, parseInt(parts[1]) - 1);
                    return;
                }
            }

            console.warn("Header Content-Range indisponível. Usando fallback de contagem manual.");
            return fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=kb_id`, { headers })
                .then(r => r.json())
                .then(data => {
                    const el = document.getElementById('kb-count');
                    // Subtrai 1 para desconsiderar o item "N/A"
                    if (el) el.innerText = Math.max(0, (data.length || 0) - 1);
                });
        })
        .catch(error => {
            console.error("Erro KB Count:", error);
            const el = document.getElementById('kb-count');
            if (el) el.innerHTML = '<span style="font-size:0.5em">Indisponível</span>';
        });


    fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=modificado_em&order=modificado_em.desc&limit=1`, {
        method: 'GET',
        headers: headers
    })
        .then(response => response.json())
        .then(data => {
            const el = document.getElementById('kb-version');
            if (el) {
                if (data && data.length > 0 && data[0].modificado_em) {
                    const lastDate = new Date(data[0].modificado_em);
                    const versionString = `v${lastDate.getFullYear()}.${String(lastDate.getMonth() + 1).padStart(2, '0')}.${String(lastDate.getDate()).padStart(2, '0')}`;
                    el.innerText = versionString;
                } else {
                    el.innerText = "v1.0.0";
                }
            }
        })
        .catch(error => {
            console.error("Erro KB Version:", error);
            const el = document.getElementById('kb-version');
            if (el) el.innerText = 'Online';
        });


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

                    if (typeof marked !== 'undefined') {
                        changelogEl.innerHTML = marked.parse(entryMarkdown);
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

});