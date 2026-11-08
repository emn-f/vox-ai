"""
Módulo do Avaliador Quantitativo Customizado (LLM-as-a-Judge) com Chain-of-Thought (CoT).

Este módulo submete cada resposta gerada pelo pipeline RAG a um modelo de linguagem avaliador
que analisa com rigor científico as quatro métricas da Tríade RAG:
Fidelidade (Faithfulness), Relevância (Answer Relevance), Precisão de Contexto (Context Precision)
e Revocação de Contexto (Context Recall).
"""
import json
import time
from typing import List, Dict, Any
from scripts.modules.config import gerar_avaliacao_juiz_com_fallback

PROMPT_JUIZ: str = """Você é um Engenheiro de IA Sênior e Avaliador Rigoroso de um sistema RAG.
Sua tarefa é avaliar a qualidade da resposta gerada com extrema severidade científica, penalizando alucinações, enrolações e contextos com excesso de ruído.

Entradas:
- PERGUNTA DO USUÁRIO: {pergunta}
- CONTEXTO RECUPERADO (CHUNKS): {contexto}
- RESPOSTA GERADA PELO RAG: {resposta}
- OBJETIVO DA RESPOSTA (GABARITO): {objetivo}

AVALIAÇÃO CRÍTICA (SEJA SEVERO):
1. faithfulness (Fidelidade): A resposta extrapolou o contexto ou inventou algo? Penalize se houver qualquer afirmação não suportada pelo contexto.
2. answer_relevance (Relevância): A resposta é excessivamente longa ou tem informações inúteis para a pergunta? Penalize se não for direta.
3. context_precision (Precisão de Contexto): O RAG trouxe muito texto inútil que não ajudou a responder? (1.0 = contexto enxuto e perfeito, 0.0 = contexto cheio de lixo semântico).
4. context_recall (Revocação de Contexto): A resposta cobriu TODOS os pontos exigidos pelo Objetivo (Gabarito)? Penalize se faltou algo.

Responda EXCLUSIVAMENTE em formato JSON válido com a seguinte estrutura. Você DEVE preencher o campo "raciocinio" detalhando os defeitos encontrados ANTES de dar as notas (use valores numericos de 0.00 a 1.00):
{{
    "raciocinio": "Escreva aqui uma análise dura e técnica, apontando o que sobrou, o que faltou ou o que teve de ruído...",
    "faithfulness": 0.00,
    "answer_relevance": 0.00,
    "context_precision": 0.00,
    "context_recall": 0.00
}}
"""


def avaliar_cenario_com_juiz(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Avalia um único cenário RAG utilizando o LLM Juiz com raciocínio antecipado (Chain-of-Thought).

    Args:
        item (Dict[str, Any]): Dicionário contendo a pergunta, resposta gerada, gabarito e chunks.

    Returns:
        Dict[str, Any]: Dicionário contendo o campo 'raciocinio' e as quatro notas numéricas (0.0 a 1.0).
    """
    pergunta: str = item.get("pergunta", "")
    resposta: str = item.get("resposta_gerada", "")
    objetivo: str = item.get("objetivo", "")
    chunks: List[str] = [c.get("descricao", "") for c in item.get("chunks_knowledge_base", []) if isinstance(c, dict)]
    contexto_str: str = "\n---\n".join(chunks) if chunks else "Sem contexto recuperado"

    prompt_formatted: str = PROMPT_JUIZ.format(
        pergunta=pergunta,
        contexto=contexto_str,
        resposta=resposta,
        objetivo=objetivo
    )

    try:
        raw_res: str = gerar_avaliacao_juiz_com_fallback(prompt_formatted)
        scores: dict = json.loads(raw_res)

        return {
            "raciocinio": scores.get("raciocinio", "Análise não fornecida."),
            "faithfulness": round(float(scores.get("faithfulness", 0.0)), 4),
            "answer_relevance": round(float(scores.get("answer_relevance", 0.0)), 4),
            "context_precision": round(float(scores.get("context_precision", 0.0)), 4),
            "context_recall": round(float(scores.get("context_recall", 0.0)), 4)
        }
    except Exception as e:
        print(f"⚠️ Erro ao avaliar cenário {item.get('id')}: {e}")
        return {
            "raciocinio": f"Falha na execução do LLM Juiz: {e}",
            "faithfulness": 0.0,
            "answer_relevance": 0.0,
            "context_precision": 0.0,
            "context_recall": 0.0
        }


def executar_avaliacao_llm_juiz(dataset_resultados: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Orquestra a avaliação quantitativa para todos os itens do dataset de resultados
    e calcula as pontuações médias globais das quatro dimensões.

    Args:
        dataset_resultados (List[Dict[str, Any]]): Lista de dicionários dos cenários processados.

    Returns:
        Dict[str, float]: Dicionário contendo a média global de cada métrica da tríade RAG.
    """
    print(f"\n⚖️ [2/4] Executando Avaliação LLM-as-a-Judge ({len(dataset_resultados)} itens)...")
    avaliacoes: List[Dict[str, Any]] = []

    for idx, item in enumerate(dataset_resultados, 1):
        print(f" Avaliando [{idx}/{len(dataset_resultados)}] Scenario ID: {item.get('id')}...", end=" ")
        eval_data: Dict[str, Any] = avaliar_cenario_com_juiz(item)

        item["avaliacao_juiz"] = eval_data
        avaliacoes.append(eval_data)

        print(f"OK -> F:{eval_data['faithfulness']} | A:{eval_data['answer_relevance']} | CP:{eval_data['context_precision']} | CR:{eval_data['context_recall']}")
        time.sleep(2)

    total: int = len(avaliacoes) if avaliacoes else 1
    metricas_globais: Dict[str, float] = {
        "faithfulness": round(sum(a["faithfulness"] for a in avaliacoes) / total, 4),
        "answer_relevance": round(sum(a["answer_relevance"] for a in avaliacoes) / total, 4),
        "context_precision": round(sum(a["context_precision"] for a in avaliacoes) / total, 4),
        "context_recall": round(sum(a["context_recall"] for a in avaliacoes) / total, 4)
    }

    print("\n" + "="*60)
    print(" 📊 MÉTRICAS CONSOLIDADAS DO PIPELINE (LLM-AS-A-JUDGE):")
    print(f"    • Fidelidade (Faithfulness):       {metricas_globais['faithfulness']:.4f}")
    print(f"    • Relevância (Answer Relevance):   {metricas_globais['answer_relevance']:.4f}")
    print(f"    • Precisão (Context Precision):    {metricas_globais['context_precision']:.4f}")
    print(f"    • Revocação (Context Recall):      {metricas_globais['context_recall']:.4f}")
    print("="*60)

    return metricas_globais
