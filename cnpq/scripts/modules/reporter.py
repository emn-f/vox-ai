"""
Módulo Gerador de Relatórios e Exportação de Benchmarks RAG.

Este módulo consolida as execuções dos cenários RAG e do LLM Juiz em um arquivo JSON completo
e invoca o modelo Gemini para sintetizar o relatório executivo Markdown no formato de report.md.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from scripts.modules.config import gerar_resposta_com_fallback, MODELO_GERACAO_PADRAO

TEMPLATE_PATH: str = "/workspaces/vox-cnpq/resultados/relatorios/report.md"


def salvar_json_benchmark(
    resultados_dataset: List[Dict[str, Any]],
    metricas_globais: Dict[str, float],
    dataset_version: str,
    output_dir: str = "/workspaces/vox-cnpq/resultados/benchmarks"
) -> str:
    """
    Persiste o dataset completo com respostas RAG, metadados de chunks e pontuações do LLM Juiz
    em um arquivo JSON estruturado e indexado por timestamp.

    Args:
        resultados_dataset (List[Dict[str, Any]]): Lista de dicionários dos cenários processados.
        metricas_globais (Dict[str, float]): Dicionário com as médias globais da tríade RAG.
        dataset_version (str): Versão do Golden Dataset utilizado.
        output_dir (str): Diretório de destino para salvamento do arquivo JSON.

    Returns:
        str: Caminho absoluto do arquivo JSON gravado.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp_str: str = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path: str = os.path.join(output_dir, f"benchmark_completo_v{dataset_version}_{timestamp_str}.json")

    documento: Dict[str, Any] = {
        "metadados": {
            "dataset_versao": dataset_version,
            "total_cenarios": len(resultados_dataset),
            "executado_em": datetime.now().isoformat(),
            "modelo_geracao": MODELO_GERACAO_PADRAO,
            "modelo_juiz": "custom-llm-as-a-judge (Chain-of-Thought)"
        },
        "metricas_globais": metricas_globais,
        "cenarios": resultados_dataset
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(documento, f, ensure_ascii=False, indent=4)

    return json_path


def gerar_relatorio_com_ia(
    resultados_dataset: List[Dict[str, Any]],
    metricas_globais: Dict[str, float],
    dataset_version: str,
    tempo_total_segundos: float,
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Submete o consolidado de resultados ao modelo Gemini para sintetizar o relatório executivo
    em formato Markdown aderente ao modelo de referência 'report.md'.

    O nome do arquivo segue o padrão: report_benchmark_v{version}_{YYYYMMDD}_{HHMMSS}.md

    Args:
        resultados_dataset (List[Dict[str, Any]]): Lista de cenários com avaliações do juiz.
        metricas_globais (Dict[str, float]): Médias globais das quatro métricas RAG.
        dataset_version (str): Versão do dataset avaliado.
        tempo_total_segundos (float): Tempo total de execução do pipeline em segundos.
        output_path (Optional[str]): Caminho absoluto de destino. Se None, gera automaticamente.

    Returns:
        Optional[str]: Caminho do relatório gerado ou None em caso de falha.
    """
    timestamp_str: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_path is None:
        output_dir = "/workspaces/vox-cnpq/resultados/relatorios"
        output_path = os.path.join(
            output_dir,
            f"report_benchmark_v{dataset_version}_{timestamp_str}.md"
        )

    print("\n🤖 [5/5] Gerando Relatório de Avaliação Quantitativa via IA...")

    modelo_referencia: str = ""
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            modelo_referencia = f.read()

    resumo_cenarios: List[Dict[str, Any]] = []
    for item in resultados_dataset:
        juiz: Dict[str, Any] = item.get("avaliacao_juiz", {})
        resumo_cenarios.append({
            "id": item.get("id"),
            "categoria": item.get("categoria"),
            "pergunta": item.get("pergunta"),
            "metricas": {
                "faithfulness": juiz.get("faithfulness", 0.0),
                "answer_relevance": juiz.get("answer_relevance", 0.0),
                "context_precision": juiz.get("context_precision", 0.0),
                "context_recall": juiz.get("context_recall", 0.0)
            },
            "raciocinio_juiz": juiz.get("raciocinio", "")
        })

    payload_analise: Dict[str, Any] = {
        "data_horario_geracao": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        "tamanho_amostra": len(resultados_dataset),
        "versao_dataset": f"Golden Dataset v{dataset_version}",
        "tempo_execucao_segundos": round(tempo_total_segundos, 2),
        "metricas_globais": metricas_globais,
        "detalhes_cenarios": resumo_cenarios
    }

    prompt_relatorio: str = f"""Você é um Engenheiro de IA Sênior e Consultor de Engenharia de Dados do projeto Vox AI.
Sua missão é sintetizar um **Relatório de Avaliação Quantitativa RAG** técnico, profundo e rigoroso, utilizando os dados empíricos da execução recente.

MODELO DE ESTRUTURA REQUISITADO (SIGA EXATAMENTE ESTE FORMATO):
{modelo_referencia if modelo_referencia else '''
# Relatório de Avaliação Quantitativa RAG - Vox AI

**Data da Avaliação:** DD/MM/YYYY
**Framework de Avaliação:** Custom LLM-as-a-Judge (Gemini 3.6 Flash)
**Tamanho da Amostra:** N cenários (Golden Dataset vX.X)
**Tempo de Execução:** N segundos

## 1. Visão Geral das Métricas Globais

| Métrica | Pontuação Média | Status | Descrição Técnica |
| --- | --- | --- | --- |
| **Fidelidade (Faithfulness)** | X.XXXX | 🟢/🟡/🔴 | ... |
| **Revocação (Context Recall)** | X.XXXX | 🟢/🟡/🔴 | ... |
| **Relevância (Answer Relevance)** | X.XXXX | 🟢/🟡/🔴 | ... |
| **Precisão (Context Precision)** | X.XXXX | 🟢/🟡/🔴 | ... |

## 2. Diagnóstico Arquitetural e Gargalos

**Destaques Positivos (O que funcionou bem):**
* ... (Cite IDs específicos do dataset com altas notas)

**Gargalos Técnicos (Onde o sistema falhou):**
* ... (Cite IDs específicos de cenários com falhas de precisão, revocação ou fidelidade)

## 3. Plano de Ação e Recomendações de Engenharia
...
'''}

DADOS DA EXECUÇÃO ATUAL:
{json.dumps(payload_analise, ensure_ascii=False, indent=2)}

INSTRUÇÕES DE ESCRITA:
1. Mantenha os valores numéricos exatos fornecidos nas métricas globais e nos cenários.
2. Identifique os IDs reais dos cenários nos "Destaques Positivos" e "Gargalos Técnicos" com base nos raciocínios e notas da execução.
3. Forneça recomendações técnicas acionáveis (Top-K, threshold pgvector, enriquecimento de base).
4. No cabeçalho inicial do documento Markdown, você DEVE incluir OBRIGATORIAMENTE os seguintes metadados explicitados nos dados da execução:
   - **Data e Horário de Geração:** (usar o valor de 'data_horario_geracao', ex: 26/07/2026 às 20:01:41)
   - **Versão do Dataset:** (usar o valor de 'versao_dataset', ex: Golden Dataset v1.1)
5. Retorne APENAS o conteúdo em Markdown, sem blocos adicionais de texto antes ou depois.
"""

    try:
        conteudo_md: str = gerar_resposta_com_fallback(prompt_relatorio)
        if conteudo_md.startswith("```markdown"):
            conteudo_md = conteudo_md.split("```markdown")[1]
        if conteudo_md.endswith("```"):
            conteudo_md = conteudo_md.rsplit("```", 1)[0]
        conteudo_md = conteudo_md.strip()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(conteudo_md)

        docs_path: str = "/workspaces/vox-cnpq/docs/relatorio_pendencias_finais.md"
        with open(docs_path, "w", encoding="utf-8") as f:
            f.write(conteudo_md)

        print(f"  ✅ Relatório técnico gerado via IA em: {output_path}")
        return output_path
    except Exception as e:
        print(f"  ⚠️ Erro ao gerar relatório por IA: {e}")
        return None
