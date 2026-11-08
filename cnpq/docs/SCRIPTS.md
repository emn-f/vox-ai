# Scripts — Guia Técnico de Execução e Arquitetura Modular

Este documento descreve a arquitetura modular, o gerenciamento de ambiente com `uv`/`venv`, o funcionamento interno e os outputs do diretório `scripts/`.

## Ambiente Virtual e Gerenciamento de Dependências com `uv`

O projeto utiliza **`uv`** como gerenciador rápido de pacotes e **`venv`** para isolamento de ambiente virtual Python.

### 1. Inicialização do Ambiente Virtual

```bash
# Criar o ambiente virtual com uv
uv venv .venv

# Instalar todas as dependências declaradas
uv pip install -r requirements.txt
```

### 2. Execução do Pipeline

Para rodar qualquer script dentro do ambiente virtual isolado:

```bash
# Usando o assistente uv
uv run python scripts/run_pipeline.py

# Ou ativando a venv diretamente
source .venv/bin/activate
python scripts/run_pipeline.py
```

## Estrutura Arquitetural Modular (`scripts/`)

A estrutura do código foi refatorada e organizada segundo o princípio da **Separação de Responsabilidades (Separation of Concerns)**, eliminando scripts monolíticos e garantindo facilidade de manutenção e extensibilidade.

```
scripts/
├── run_pipeline.py                  # Engine unificada de benchmark, LLM Juiz e governança (CLI)
├── 01_executar_pipeline_completo.py # Wrapper de compatibilidade que redireciona para run_pipeline.py
├── 02_avaliar_ragas.py              # Avaliação legada via Ragas Framework (opcional/legado)
├── modules/
│   ├── __init__.py
│   ├── config.py                    # Gestão de credenciais, modelo padrão, rotação de chaves Gemini, paths e LoggerTee
│   ├── rag_runner.py                # Execução da busca semântica (Supabase pgvector) e geração Gemini (Top-3 / 0.58 threshold)
│   ├── llm_judge.py                 # Avaliador LLM-as-a-Judge com Chain-of-Thought (F, A, CP, CR)
│   ├── audio_eval.py                # Ensaio multimodal de síntese gTTS e transcrição de voz
│   ├── lgpd_audit.py                # Auditoria automatizada de segurança e conformidade LGPD
│   └── reporter.py                  # Exportação do JSON consolidado e síntese do relatório Markdown via IA
└── logs/                            # Histórico de execuções com timestamps
```

## Módulos do Pipeline Unificado

### 1. Módulo `config.py`
- Resolve caminhos dinâmicos do repositório `vox-ai` (`/workspaces/vox-ai` ou local).
- Centraliza a escolha dos modelos nas variáveis globais `MODELO_GERACAO_PADRAO = "gemini-2.5-flash-lite"` e `MODELOS_JUIZ_ELEGIVEIS`.
- Carrega as credenciais e lista de chaves de API (`GEMINI_API_KEY_6` ... `GEMINI_API_KEY`) de `.streamlit/secrets.toml` em ordem decrescente.
- Implementa rotação automática transparente de chaves quando a cota da API Gemini é esgotada (`429 RESOURCE_EXHAUSTED`).
- Redireciona `stdout`/`stderr` com `LoggerTee`, ocultando logs ruidosos de bibliotecas de terceiros.

### 2. Módulo `rag_runner.py`
- Detecta automaticamente a versão mais recente do Golden Dataset em `data/dataset_*.json` (ex: `dataset_1.1.json`).
- Executa a consulta de similaridade vetorial via `src.core.semantica.semantica`.
- Busca os metadados enriquecidos dos fragmentos recuperados no Supabase (`knowledge_base`).
- Envia o prompt ao modelo gerador com o *System Prompt* oficial de blindagem ética e antirregras de alucinação.

### 3. Módulo `llm_judge.py`
- Executa a avaliação da Tríade RAG com severidade científica via **Custom LLM-as-a-Judge**.
- Utiliza raciocínio antecipado (*Chain-of-Thought*) exigindo que o juiz explique as falhas e ruídos antes de emitir as notas numéricas (0,00 a 1,00).
- Calcula as 4 métricas globais:
  - **Fidelidade (`faithfulness`)**: Ausência de extrapolações ou alucinações.
  - **Relevância (`answer_relevance`)**: Direcionamento e brevidade da resposta.
  - **Precisão de Contexto (`context_precision`)**: Qualidade dos chunks recuperados (*Prompt Bloating*).
  - **Revocação de Contexto (`context_recall`)**: Cobertura das exigências do gabarito.

### 4. Módulo `audio_eval.py`
- Gera falas sintéticas de teste em formato `.mp3` via `gTTS`.
- Processa o áudio em memória RAM através de `transcrever_audio()`.
- Calcula a taxa percentual de acerto de palavras em linguagem informal/gírias e termos técnicos.

### 5. Módulo `lgpd_audit.py`
- Conecta-se à tabela `chat_logs` no Supabase.
- Valida a ausência de dados pessoais identificáveis (PII), verificando o cumprimento das diretrizes de *Anonymity by Design*.

### 6. Módulo `reporter.py`
- Consolida os resultados detalhados e métricas no arquivo JSON `resultados/benchmarks/benchmark_completo_v{version}_{timestamp}.json`.
- Compila o relatório executivo em Markdown em `resultados/relatorios/relatorio_avaliacao_quantitativa.md` e `docs/relatorio_pendencias_finais.md`, contendo data, horário de geração (`DD/MM/YYYY às HH:MM:SS`) e a versão do dataset utilizado.

## Outputs do Pipeline

| Diretório / Arquivo | Descrição |
|---|---|
| `resultados/benchmarks/benchmark_completo_v*.json` | Dataset consolidado com respostas do RAG + pontuações e CoT do LLM Juiz |
| `resultados/relatorios/relatorio_avaliacao_quantitativa.md` | Relatório técnico de avaliação quantitativa sintetizado por IA |
| `docs/relatorio_pendencias_finais.md` | Cópia sincronizada do relatório executivo final |
| `scripts/logs/*.log` | Log estruturado e limpo da sessão de execução |
