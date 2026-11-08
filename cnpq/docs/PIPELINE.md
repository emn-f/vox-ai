# Arquitetura do Pipeline Unificado e Módulos do Sistema

Este documento descreve a organização modular do repositório de scripts em Python que orquestram a execução dos testes e a avaliação do Vox AI.

## Arquitetura Modular (`scripts/`)

O pipeline foi projetado de forma totalmente desacoplada do frontend em Streamlit, permitindo execuções automatizadas em ambientes de integração contínua (CI/CD).

```text
scripts/
├── run_pipeline.py          # Script CLI principal de execução end-to-end
├── gerar_dashboard.py       # Compilador de estatísticas HTML e Markdown
└── modules/
    ├── config.py            # Rotação de chaves Gemini, limites e interceptação de logs
    ├── rag_runner.py        # Busca semântica no Supabase (pgvector) e geração RAG
    ├── llm_judge.py         # Motor de avaliação quantitativa (LLM-as-a-Judge CoT)
    ├── lgpd_audit.py        # Auditoria de privacidade e checagem de PII na tabela chat_logs
    ├── audio_eval.py        # Módulo multimodal (gTTS e transcrição de áudio)
    └── reporter.py          # Exportação do JSON final e relatório de análise via IA

```


## Fluxo de Execução (`python3 scripts/run_pipeline.py`)

1. **Fase 1 - Carregamento do Dataset:** Identifica o dataset de maior versão em `data/` ou o arquivo informado via argumento `--dataset`.
2. **Fase 2 - Busca Semântica & Geração:** Submete cada pergunta à função RPC `recuperar_contexto_inteligente` no Supabase, filtra os chunks via `SEMANTICA_THRESHOLD = 0.58` e gera a resposta via Gemini API com fallback de API Keys.
3. **Fase 3 - Avaliação LLM Juiz (CoT):** Cada par (pergunta, resposta, contexto, gabarito) é analisado em chamada estruturada em JSON por um modelo avaliador que emite notas numéricas (0.00 a 1.00) para a **Tríade RAG** (*Faithfulness*, *Answer Relevance*, *Context Precision*, *Context Recall*).
4. **Fase 4 - Auditoria LGPD:** Consulta a tabela `chat_logs` no Supabase para atestar a ausência de colunas PII e a efemeridade das sessões (`session_id`).
5. **Fase 5 - Consolidação & Dashboard:** Grava o log JSON com timestamp em `resultados/benchmarks/` e atualiza automaticamente o `dashboard.html`.
