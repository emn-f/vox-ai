# Guia de Reprodução dos Resultados

Este documento descreve passo a passo como reproduzir os resultados experimentais do artigo **"VOX AI: Inteligência Artificial e Ética no Acesso a Direitos Civis"**, submetido ao 32º Prêmio Jovem Cientista (CNPq / 2026).

## Pré-requisitos

### 1. Repositórios necessários

Dois repositórios precisam estar disponíveis localmente:

| Repositório   | Caminho esperado (DevContainer)         | Caminho esperado (local)                        |
|---------------|------------------------------------------|-------------------------------------------------|
| `vox-ai`      | `/workspaces/vox-ai`                    | `/home/holmes/dev/projeto-vox/vox-ai`           |
| `vox-cnpq`    | `/workspaces/vox-cnpq`                  | `/home/holmes/dev/projeto-vox/vox-cnpq`         |

> Os scripts detectam automaticamente o ambiente e usam o caminho disponível.

### 2. Python

- Versão recomendada: **Python 3.11+** (necessário para `tomllib` nativo)
- Instale as dependências:

```bash
pip install -r requirements.txt
```

### 3. Credenciais (secrets.toml)

Crie o arquivo `.streamlit/secrets.toml` dentro do repositório `vox-ai`:

```toml
# Chave Gemini principal (obrigatória)
GEMINI_API_KEY = "AIza..."

# Chaves de fallback (opcionais — recomendadas para execuções longas)
GEMINI_API_KEY_1 = "AIza..."
GEMINI_API_KEY_2 = "AIza..."
GEMINI_API_KEY_3 = "AIza..."

# Supabase
[supabase]
url = "https://<seu-projeto>.supabase.co"
key = "eyJ..."
```

> **Segurança:** o arquivo `secrets.toml` está no `.gitignore` do `vox-ai`. Nunca o commite. Solicite as credenciais ao responsável pelo projeto.

## Ordem de Execução

### Etapa 1 — Executar o Pipeline Completo

```bash
python scripts/01_executar_pipeline_completo.py
```

**O que acontece:**

1. O script detecta automaticamente o dataset mais recente em `data/dataset_*.json`.
2. Para cada um dos 35 cenários, executa o pipeline RAG completo:
   - `semantica(pergunta)` → busca vetorial no Supabase
   - `gerar_resposta_com_fallback(prompt)` → geração no Gemini
3. Salva o resultado incrementalmente após cada cenário em `resultados/resultados_data_X.X_TIMESTAMP.json`.
4. Executa os 2 testes de transcrição de áudio (gTTS + Gemini).
5. Audita os logs no Supabase para conformidade LGPD.
6. Gera o relatório consolidado em `docs/relatorio_pendencias_finais.md`.

**Duração estimada:** 15–45 minutos (depende da latência da API e das estratégias RAG ativadas).

**Outputs gerados:**

```
resultados/resultados_data_1.0_YYYYMMDD_HHMMSS.json
docs/relatorio_pendencias_finais.md
scripts/logs/01_execucao_pipeline_YYYYMMDD_HHMMSS.log
```

### Etapa 2 — Avaliar as Métricas Ragas

```bash
python scripts/02_avaliar_ragas.py
```

> **Antes de executar:** ajuste a variável `dataset_json_path` no início do script para apontar para o arquivo de resultados gerado na Etapa 1.

**O que acontece:**

1. Carrega o JSON de resultados da Etapa 1.
2. Monta o dataset no formato `{question, contexts, answer}` esperado pelo Ragas.
3. Exibe uma amostra dos metadados da Knowledge Base (chunks, tópicos, eixos temáticos).
4. Imprime as métricas consolidadas do framework Ragas.

**Outputs gerados:**

- Métricas impressas no terminal (e no log, se `LoggerTee` estiver ativo).

## Resultados de Referência (v1.0)

Os resultados da execução de referência estão em:

```
resultados/result_dataset_1.0.json
```

Essa execução foi realizada sobre o dataset `data/dataset_1.0.json` (35 cenários) e produziu os seguintes resultados consolidados:

### Métricas Ragas

| Métrica              | Resultado |
|----------------------|:---------:|
| Faithfulness         | **0.94**  |
| Answer Relevance     | **0.91**  |
| Context Precision    | **0.88**  |
| Context Recall       | **0.93**  |

### Desempenho do Pipeline RAG

| Indicador                          | Valor               |
|------------------------------------|---------------------|
| Cenários executados                | 35                  |
| Estratégia "Contexto Completo"     | Maioria dos cenários de legislação e saúde |
| Estratégia "Tópicos Mistos"        | Cenários de limitação de escopo e blindagem ética |
| Latência média de resposta         | ~17,46s (com streaming) |

### Testes de Transcrição de Áudio

| Tipo de Frase                | Taxa de Acerto |
|------------------------------|:--------------:|
| Gíria / Linguagem Informal   | 100%           |
| Termos Técnicos e Direitos   | 100%           |


## Considerações sobre Reprodutibilidade

### Variações Esperadas

Execuções diferentes podem produzir **respostas levemente diferentes** do Gemini, mesmo com o mesmo prompt e contexto. Isso é esperado em modelos de linguagem probabilísticos. As **métricas Ragas** e a **precisão jurídica estrutural** tendem a ser estáveis entre execuções.

### Paths de Ambiente

| Situação | Path `vox-ai` | Path de saída (resultados/logs) |
|---|---|---|
| DevContainer | `/workspaces/vox-ai` | `/workspaces/vox-cnpq/...` |
| Local (dev) | `/home/holmes/dev/projeto-vox/vox-ai` | `/workspaces/vox-cnpq/...` ⚠️ |

> **Atenção (ambiente local):** os paths de saída no script ainda referenciam `/workspaces/vox-cnpq/`. Se você executar localmente e esse diretório não existir, crie um symlink ou ajuste as constantes `log_dir`, `resultados_dir` e `output_md` no topo do script.

### Cota da API Gemini

O pipeline consome cota significativa da API Gemini (35 chamadas de chat + 2 transcrições de áudio). Para execuções longas:

- Configure ao menos 2 chaves de API (`GEMINI_API_KEY` + `GEMINI_API_KEY_1`).
- O fallback automático garante continuidade em caso de erro `429`.
- Em caso de falha total, o salvamento incremental preserva o progresso já alcançado.
