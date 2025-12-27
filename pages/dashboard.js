// ==========================================================
// CONFIGURAÇÕES DO SUPABASE
// Estas strings são substituídas automaticamente pelo script de deploy/python
// ==========================================================
const SUPABASE_URL = "__SUPABASE_URL__";
const SUPABASE_KEY = "__SUPABASE_KEY__";

async function updateDashboardMetrics() {
    // Verificação de segurança: Se as chaves não foram injetadas, avisa no console
    if (SUPABASE_URL.startsWith("__") || SUPABASE_KEY.startsWith("__")) {
        console.warn("⚠️ Vox AI Dashboard: Variáveis de ambiente não foram substituídas. O dashboard pode não carregar.");
    }

    const headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json'
    };

    try {
        // --- 1. BUSCAR A VERSÃO (Data da última modificação) ---
        const versionEl = document.getElementById('kb-version');
        
        if (versionEl) {
            // Busca apenas o campo 'modificado_em' do registro mais recente
            const versionRes = await fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=modificado_em&order=modificado_em.desc&limit=1`, {
                headers: headers
            });
            
            if (versionRes.ok) {
                const versionData = await versionRes.json();
                
                if (versionData.length > 0 && versionData[0].modificado_em) {
                    const date = new Date(versionData[0].modificado_em);
                    // Formata a data: vYYYY.MM.DD (ex: v2025.12.27)
                    const fmtDate = `v${date.getFullYear()}.${String(date.getMonth()+1).padStart(2,'0')}.${String(date.getDate()).padStart(2,'0')}`;
                    versionEl.innerText = fmtDate;
                } else {
                    versionEl.innerText = "v1.0.0"; // Fallback padrão
                }
            }
        }

        // --- 2. BUSCAR O TOTAL DE REGISTROS (Count) ---
        const countEl = document.getElementById('kb-count');
        
        if (countEl) {
            // Usa method: 'HEAD' com 'Prefer: count=exact' para contar sem baixar o JSON (muito mais rápido)
            const countRes = await fetch(`${SUPABASE_URL}/rest/v1/knowledge_base?select=id`, {
                method: 'HEAD',
                headers: {
                    ...headers,
                    'Prefer': 'count=exact'
                }
            });

            if (countRes.ok) {
                // O total vem no cabeçalho 'Content-Range' (formato "0-5/6", onde 6 é o total)
                const contentRange = countRes.headers.get('Content-Range');
                if (contentRange) {
                    const total = contentRange.split('/')[1]; 
                    countEl.innerText = total;
                } else {
                    countEl.innerText = "0";
                }
            }
        }

    } catch (err) {
        console.error("❌ Erro ao conectar no Supabase:", err);
        // Em caso de erro, tira o "Carregando..." para não confundir
        const vEl = document.getElementById('kb-version');
        if (vEl && vEl.innerText === "Carregando...") vEl.innerText = "-";
    }
}

// Inicia a função assim que o HTML estiver pronto
document.addEventListener('DOMContentLoaded', updateDashboardMetrics);