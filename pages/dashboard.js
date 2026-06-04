
const SUPABASE_URL_DEV = "__SUPABASE_URL_DEV__";
const SUPABASE_ANON_KEY_DEV = "__SUPABASE_ANON_KEY_DEV__";

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
        return;
    }

    const headers = {
        'apikey': SUPABASE_ANON_KEY_DEV,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY_DEV}`,
        'Content-Type': 'application/json'
    };

    // Buscar contagem de registros da base de conhecimento
    const urlCount = new URL(`${SUPABASE_URL_DEV}/rest/v1/knowledge_base`);
    urlCount.searchParams.set('select', 'kb_id');
    urlCount.searchParams.set('limit', '1');

    fetch(urlCount.toString(), {
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
                    if (el) el.innerText = Math.max(0, parseInt(parts[1]) - 1);
                    return;
                }
            }

            console.warn("Header Content-Range indisponível. Usando fallback de contagem manual.");
            const urlFallback = new URL(`${SUPABASE_URL_DEV}/rest/v1/knowledge_base`);
            urlFallback.searchParams.set('select', 'kb_id');
            return fetch(urlFallback.toString(), { headers })
                .then(r => r.json())
                .then(data => {
                    const el = document.getElementById('kb-count');
                    if (el) el.innerText = Math.max(0, (data.length || 0) - 1);
                });
        })
        .catch(error => {
            console.error("Erro KB Count:", error);
            const el = document.getElementById('kb-count');
            if (el) el.innerHTML = '<span style="font-size:0.5em">Indisponível</span>';
        });

    // Buscar última versão da base de conhecimento
    const urlVersion = new URL(`${SUPABASE_URL_DEV}/rest/v1/knowledge_base`);
    urlVersion.searchParams.set('select', 'modificado_em');
    urlVersion.searchParams.set('order', 'modificado_em.desc');
    urlVersion.searchParams.set('limit', '1');

    fetch(urlVersion.toString(), {
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
});