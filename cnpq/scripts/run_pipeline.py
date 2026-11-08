#!/usr/bin/env python3
"""
vox-cnpq - Engine Unificada de Benchmark, Avaliação LLM-as-a-Judge e Governança RAG.

Este script é o ponto de entrada principal para a execução do pipeline de testes end-to-end do Vox AI.
Ele coordena as seguintes etapas:
1. Carregamento da versão mais recente do Golden Dataset.
2. Execução da busca semântica no Supabase pgvector e geração de respostas via Gemini.
3. Avaliação quantitativa com LLM-as-a-Judge (Chain-of-Thought) para calcular Faithfulness, Relevance, Precision e Recall.
4. Ensaio multimodal de síntese de voz (gTTS) e transcrição de áudio.
5. Auditoria de privacidade e minimização de dados LGPD na tabela chat_logs.
6. Exportação do dataset JSON consolidado e geração do relatório em Markdown via IA.
"""
import argparse
import os
import sys
import time
from typing import List, Dict, Any, Tuple, Optional

# Garante que a raiz do projeto e o diretório de scripts estejam no sys.path
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.modules.config import init_logging

# Inicializa interceptação de logs limpos antes dos imports do vox-ai / streamlit
log_path: str = init_logging("pipeline_unificado.log")

from scripts.modules.rag_runner import carregar_dataset_mais_recente, executar_benchmark_rag
from scripts.modules.llm_judge import executar_avaliacao_llm_juiz
from scripts.modules.audio_eval import executar_testes_audio
from scripts.modules.lgpd_audit import executar_auditoria_lgpd
from scripts.modules.reporter import salvar_json_benchmark, gerar_relatorio_com_ia


def parse_args() -> argparse.Namespace:
    """
    Parseia os argumentos de linha de comando do pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Pipeline Unificado Vox AI — Benchmark + LLM Juiz + Governança"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help=(
            "Caminho para o arquivo dataset_*.json a ser utilizado. "
            "Se não informado, usa o dataset de maior versão encontrado em data/."
        )
    )
    return parser.parse_args()


def main() -> None:
    """
    Função principal que orquestra e executa todas as fases do pipeline RAG unificado.
    """
    args = parse_args()
    start_time: float = time.time()

    print("==========================================================================")
    print(" 🚀 INICIANDO PIPELINE UNIFICADO VOX AI (BENCHMARK + LLM JUIZ + GOVERNANÇA)")
    print("==========================================================================")
    print(f"📝 Registro de execução capturado em: {log_path}\n")

    # 1. Carregar Dataset (especificado via --dataset ou o mais recente)
    cenarios: List[Dict[str, Any]]
    version: str
    dataset_path: str
    cenarios, version, dataset_path = carregar_dataset_mais_recente(dataset_especifico=args.dataset)

    # 2. FASE 1: Execução do Benchmark RAG
    resultados_dataset: List[Dict[str, Any]] = executar_benchmark_rag(cenarios)

    # 3. FASE 2: Avaliação Quantitativa com LLM-as-a-Judge (Tríade RAG + CoT)
    metricas_globais: Dict[str, float] = executar_avaliacao_llm_juiz(resultados_dataset)

    # 4. FASE 3: Teste Multimodal de Áudio (DESATIVADO TEMPORARIAMENTE - FOCO EM TEXTO)
    # resultados_audio: List[Dict[str, Any]] = executar_testes_audio()
    resultados_audio: List[Dict[str, Any]] = []

    # 5. FASE 4: Auditoria LGPD no Supabase
    auditoria_lgpd: Dict[str, Any] = executar_auditoria_lgpd()

    # Tempo total até a finalização das análises
    tempo_total: float = time.time() - start_time

    # 6. FASE 5: Consolidação de Outputs (JSON & Sintetizador de Relatório via IA)
    json_output: str = salvar_json_benchmark(resultados_dataset, metricas_globais, version)
    report_output: Optional[str] = gerar_relatorio_com_ia(resultados_dataset, metricas_globais, version, tempo_total)

    # 7. FASE 6: Atualização Automática do Dashboard de Métricas
    try:
        from scripts.gerar_dashboard import gerar_dashboard
        gerar_dashboard()
    except Exception as e:
        print(f"⚠️ Erro ao atualizar dashboard: {e}")

    print("\n==========================================================================")
    print(" ✅ PIPELINE UNIFICADO CONCLUÍDO COM SUCESSO!")
    print(f" 📄 Benchmark & Métricas (JSON): {json_output}")
    print(f" 📄 Relatório Quantitativo (IA):  {report_output}")
    print(f" 📊 Dashboard Consolidado:       /workspaces/vox-cnpq/resultados/dashboard.html")
    print(f" 📝 Arquivo de Log:              {log_path}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
