# Registro de Mudança 001: Otimização do Retriever RAG e System Prompt Anti-Alucinação

**Repositório Alvo:** `vox-ai`  
**Commit:** `5716e209469510dee156811fdb0232b240d75be5`  
**Data:** 26/07/2026  
**Tipo:** `perf(rag)`

## 1. A Mudança (O que foi alterado)

1. **Retriever (`src/core/db/retrieval.py`):**
   - Substituída a função interna `_gerar_fallback_top5()` por `_gerar_fallback_top3()`, reduzindo a quantidade de chunks recuperados no fallback de 5 para no máximo 3.
2. **Parâmetros de Configuração (`src/config.py`):**
   - Elevado o `SEMANTICA_THRESHOLD` de `0.50` para `0.58`.
   - Ajustado `LIMITE_TEMAS` de 10 para 6 e `MAX_CHUNCK` de 25 para 15.
3. **System Prompt (`data/prompts/system_prompt.py`):**
   - Reforçada a **Regra de Ouro 1** em `INSTRUCOES` para instruir o modelo a declarar afetuosamente a ausência de dados cadastrados e redirecionar para canais oficiais (100 / 188) quando a pergunta envolver normas ou estabelecimentos locais ausentes da base.


## 2. O Motivo (Rationale Técnico)

- **Combate à Crise de Precisão de Contexto (`0.3923`):** O benchmark com o Golden Dataset v1.0 revelou que 60.8% dos fragmentos recuperados no modo fallback eram irrelevantes (*Prompt Bloating*), injetando ruído e confundindo a geração do modelo.
- **Redução de Alucinações Regionais:** Cenários focados em boletins de ocorrência locais e casas de acolhimento (IDs 13, 30, 31, 32) apresentaram queda de fidelidade porque o LLM tentava inventar procedimentos na ausência do dado real. A nova diretriz garante o *fallback* seguro.
