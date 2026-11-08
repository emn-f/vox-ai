#!/usr/bin/env python3
"""
Gerador de Dashboard de Métricas RAG (HTML / Markdown).

Lê todos os arquivos de benchmark salvos em resultados/benchmarks/
e gera um dashboard HTML estático leve e um resumo Markdown consolidado.
"""
import glob
import json
import os
from datetime import datetime
from typing import List, Dict, Any

BENCHMARK_DIR = "/workspaces/vox-cnpq/resultados/benchmarks"
OUTPUT_HTML = "/workspaces/vox-cnpq/resultados/dashboard.html"
OUTPUT_MD = "/workspaces/vox-cnpq/resultados/dashboard_summary.md"


def carregar_benchmarks() -> List[Dict[str, Any]]:
    arquivos = sorted(glob.glob(os.path.join(BENCHMARK_DIR, "benchmark_completo_*.json")))
    execucoes = []
    
    for arq in arquivos:
        try:
            with open(arq, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            meta = data.get("metadados", {})
            metricas = data.get("metricas_globais", {})
            cenarios = data.get("cenarios", [])
            
            execucoes.append({
                "arquivo": os.path.basename(arq),
                "versao": meta.get("dataset_versao", "N/A"),
                "total_cenarios": meta.get("total_cenarios", len(cenarios)),
                "executado_em": meta.get("executado_em", "N/A"),
                "faithfulness": metricas.get("faithfulness", 0.0),
                "answer_relevance": metricas.get("answer_relevance", 0.0),
                "context_precision": metricas.get("context_precision", 0.0),
                "context_recall": metricas.get("context_recall", 0.0),
            })
        except Exception as e:
            print(f"⚠️ Erro ao ler {arq}: {e}")
            
    return execucoes


def gerar_dashboard() -> None:
    execucoes = carregar_benchmarks()
    if not execucoes:
        print("❌ Nenhum benchmark encontrado em resultados/benchmarks/")
        return

    # Médias globais acumuladas de todos os testes
    total_runs = len(execucoes)
    avg_faithfulness = sum(e["faithfulness"] for e in execucoes) / total_runs
    avg_relevance = sum(e["answer_relevance"] for e in execucoes) / total_runs
    avg_precision = sum(e["context_precision"] for e in execucoes) / total_runs
    avg_recall = sum(e["context_recall"] for e in execucoes) / total_runs
    total_cenarios_avaliados = sum(e["total_cenarios"] for e in execucoes)

    # 1. Gerar Markdown
    md_content = f"""# 📊 Dashboard Consolidado de Métricas RAG — Vox AI

**Última Atualização:** {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}  
**Total de Testes Executados:** {total_runs} execuções ({total_cenarios_avaliados} cenários avaliados no total)

---

## 📈 Médias Globais Acumuladas

| Métrica RAG | Pontuação Média | Status |
| :--- | :---: | :---: |
| **Fidelidade (Faithfulness)** | `{avg_faithfulness:.4f}` | 🟢 Excelente |
| **Revocação de Contexto (Context Recall)** | `{avg_recall:.4f}` | 🟡 Bom |
| **Relevância da Resposta (Answer Relevance)** | `{avg_relevance:.4f}` | 🟢 Bom |
| **Precisão de Contexto (Context Precision)** | `{avg_precision:.4f}` | 🟡 Em Evolução |

---

## 📑 Histórico Detalhado por Execução

| Versão Dataset | Data/Hora Execução | Cenários | Faithfulness | Answer Relevance | Context Precision | Context Recall | Arquivo |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
"""
    for e in reversed(execucoes):
        dt_formatted = e['executado_em'][:19].replace('T', ' ') if 'T' in e['executado_em'] else e['executado_em']
        md_content += f"| `v{e['versao']}` | {dt_formatted} | {e['total_cenarios']} | {e['faithfulness']:.4f} | {e['answer_relevance']:.4f} | {e['context_precision']:.4f} | {e['context_recall']:.4f} | `{e['arquivo']}` |\n"

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 2. Gerar HTML Interativo Simples
    rows_html = ""
    for e in reversed(execucoes):
        dt_formatted = e['executado_em'][:19].replace('T', ' ') if 'T' in e['executado_em'] else e['executado_em']
        rows_html += f"""
        <tr>
            <td><span class="badge">v{e['versao']}</span></td>
            <td>{dt_formatted}</td>
            <td>{e['total_cenarios']}</td>
            <td><strong>{e['faithfulness']:.4f}</strong></td>
            <td><strong>{e['answer_relevance']:.4f}</strong></td>
            <td><strong>{e['context_precision']:.4f}</strong></td>
            <td><strong>{e['context_recall']:.4f}</strong></td>
            <td style="font-size: 0.85em; color: #666;">{e['arquivo']}</td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard RAG - Vox AI</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f8fafc;
            --accent: #38bdf8;
            --border: #334155;
            --green: #22c55e;
        }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: var(--accent);
            margin-bottom: 0.5rem;
        }}
        .subtitle {{
            color: #94a3b8;
            margin-bottom: 2rem;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-bottom: 2.5rem;
        }}
        .card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            text-align: center;
        }}
        .card .title {{
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .card .val {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent);
            margin: 0.5rem 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #0f172a;
            color: #94a3b8;
            font-weight: 600;
        }}
        .badge {{
            background: #0284c7;
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dashboard de Avaliação RAG — Vox AI</h1>
        <div class="subtitle">Visão geral consolidada dos benchmarks de entrada e saída textual</div>

        <div class="cards">
            <div class="card">
                <div class="title">Fidelidade Média</div>
                <div class="val" style="color: #4ade80;">{avg_faithfulness:.4f}</div>
                <small style="color: #94a3b8;">Faithfulness</small>
            </div>
            <div class="card">
                <div class="title">Relevância Média</div>
                <div class="val" style="color: #38bdf8;">{avg_relevance:.4f}</div>
                <small style="color: #94a3b8;">Answer Relevance</small>
            </div>
            <div class="card">
                <div class="title">Precisão Média</div>
                <div class="val" style="color: #facc15;">{avg_precision:.4f}</div>
                <small style="color: #94a3b8;">Context Precision</small>
            </div>
            <div class="card">
                <div class="title">Revocação Média</div>
                <div class="val" style="color: #a78bfa;">{avg_recall:.4f}</div>
                <small style="color: #94a3b8;">Context Recall</small>
            </div>
        </div>

        <h2>📜 Histórico de Testes</h2>
        <table>
            <thead>
                <tr>
                    <th>Versão</th>
                    <th>Data / Hora</th>
                    <th>Cenários</th>
                    <th>Faithfulness</th>
                    <th>Relevância</th>
                    <th>Precisão</th>
                    <th>Revocação</th>
                    <th>Arquivo JSON</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("==========================================================")
    print(" ✅ DASHBOARD ATUALIZADO COM SUCESSO!")
    print(f" 📄 Resumo Markdown: {OUTPUT_MD}")
    print(f" 🌐 Dashboard HTML:   {OUTPUT_HTML}")
    print("==========================================================")


if __name__ == "__main__":
    gerar_dashboard()
