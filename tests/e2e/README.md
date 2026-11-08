# Rotinas de Testes E2E Reutilizáveis — Vox AI (Dev)

Este diretório contém os testes end-to-end automatizados desenvolvidos durante o ciclo de QA do Vox AI no ambiente de Desenvolvimento.

## Estrutura dos Testes

- `test_qa_e2e_suite.py`: Suíte de testes automatizados com `pytest` cobrindo conexão Dev, integridade vetorial da KB, recuperação semântica RAG, geração conversacional, síntese (TTS) e transcrição (STT) de voz, endpoints REST da API desacoplada (`/api/v1/health`, `/api/v1/chat`, erro 422) e rotina de backup.
- `test_audio_scenarios.py`: Validação de cenários de áudio (silêncio, tom curto, tom longo, áudio vazio/nulo, áudio corrompido com cascata de fallback e síntese).
- `test_performance_benchmarks.py`: Benchmark automatizado de latências (3 repetições por cenário), calculando mediana e percentil 95 (P95) para TTFB e tempo total.

---

## Como Executar

### 1. Pré-requisitos
Certifique-se de que o ambiente virtual está configurado com `uv` e que as credenciais do Supabase Dev e Google Gemini estão presentes em `.streamlit/secrets.toml` ou `.env`.

### 2. Executar a Suíte Principal de QA
```bash
uv run pytest tests/e2e/test_qa_e2e_suite.py -v
```

### 3. Executar Testes de Robustez de Áudio (STT / TTS)
```bash
uv run python -m tests.e2e.test_audio_scenarios
```

### 4. Executar Benchmark de Latência e Desempenho
```bash
uv run python -m tests.e2e.test_performance_benchmarks
```
Os resultados detalhados serão salvos em `docs/qa/metricas_latencia.json`.

---

## Verificação de Diagnóstico da Base de Conhecimento
Para auditar os 356 chunks da Knowledge Base diretamente no Supabase Dev:
```bash
uv run python scripts/audit_kb.py --db --acao diagnostico
```
