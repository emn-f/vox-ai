
const SUPABASE_URL = "__SUPABASE_URL__";
const SUPABASE_KEY = "__SUPABASE_KEY__";

async function updateDashboardMetrics() {

    if (SUPABASE_URL.startsWith("__") || SUPABASE_KEY.startsWith("__")) {
        console.warn("⚠️ Dashboard: Variáveis de ambiente não injetadas. Verifique o GitHub Secrets.");

    }

    const headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json'
    };

    try {

        const versionEl = document.getElementById('kb-version');
        if (versionEl) {
            const versionRes = await fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=modificado_em&order=modificado_em.desc&limit=1`, { headers });

            if (versionRes.ok) {
                const data = await versionRes.json();
                if (data.length > 0 && data[0].modificado_em) {
                    const date = new Date(data[0].modificado_em);
                    const fmt = `v${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
                    versionEl.innerText = fmt;
                } else {
                    versionEl.innerText = "v1.0.0";
                }
            }
        }


        const countEl = document.getElementById('kb-count');
        if (countEl) {
            const countRes = await fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=id`, {
                method: 'HEAD',
                headers: { ...headers, 'Prefer': 'count=exact' }
            });

            if (countRes.ok) {
                const range = countRes.headers.get('Content-Range');
                if (range) countEl.innerText = range.split('/')[1];
            }
        }

    } catch (err) {
        console.error("❌ Erro Supabase:", err);
        const vEl = document.getElementById('kb-version');
        if (vEl && vEl.innerText.includes("Carregando")) vEl.innerText = "-";
    }
}

async function loadChangelog() {
    const el = document.getElementById('latest-changelog');
    if (!el) return;

    try {
        const response = await fetch('CHANGELOG.md', {
            headers: { 'Cache-Control': 'max-age=300' }
        });

        if (!response.ok) throw new Error("Changelog não encontrado");

        const markdown = await response.text();


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
                el.innerHTML = marked.parse(entryMarkdown);
            } else {
                el.innerText = "Erro: Biblioteca Markdown não carregada.";
            }
        }
    } catch (error) {
        console.error("Erro Changelog:", error);
        el.innerHTML = '<p style="color: #ef4444;">Não foi possível carregar o histórico.</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateDashboardMetrics();
    loadChangelog();
});