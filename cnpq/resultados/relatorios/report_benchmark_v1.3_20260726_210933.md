# Relatório de Avaliação Quantitativa RAG - Vox AI

**Data da Avaliação:** 26/07/2026
**Data e Horário de Geração:** 26/07/2026 às 21:09:33
**Versão do Dataset:** Golden Dataset v1.3
**Framework de Avaliação:** Custom LLM-as-a-Judge (Gemini 3.6 Flash)
**Tamanho da Amostra:** 10 cenários (Golden Dataset v1.3)
**Tempo de Execução:** 102.18 segundos

## 1. Visão Geral das Métricas Globais

| Métrica | Pontuação Média | Status | Descrição Técnica |
| --- | --- | --- | --- |
| **Fidelidade (Faithfulness)** | 0.9700 | 🟢 | Mede o grau em que a resposta gerada é fundamentada exclusivamente no contexto recuperado, penalizando alucinações. |
| **Revocação (Context Recall)** | 0.7400 | 🟡 | Avalia se o recuperador foi capaz de trazer todos os trechos necessários do gabarito para responder exaustivamente à pergunta. |
| **Relevância (Answer Relevance)** | 0.7350 | 🟡 | Analisa a aderência da resposta ao problema do usuário, penalizando a prolixidade e preâmbulos emocionais excessivos. |
| **Precisão (Context Precision)** | 0.7200 | 🟡 | Mensura a proporção de chunks relevantes recuperados em relação ao total de ruído e gordura semântica trazida pelo retriever. |

## 2. Diagnóstico Arquitetural e Gargalos

**Destaques Positivos (O que funcionou bem):**
* **Fidelidade e Alinhamento Jurídico Excepcionais:** O pipeline demonstrou altíssima robustez contra alucinações, com nota máxima (Faithfulness = 1.0) em cenários complexos de direitos e acolhimento, como nos IDs 1, 2, 5, 6, 7, 8, 9 e 10.
* **Excelência em Casos de Resgate e Urgência:** Os cenários ID 6 e ID 7 destacaram-se pelo resgate preciso de informações operacionais cruciais de Salvador (como a DECRIN, Casa Marielle Franco e contatos de suporte), garantindo 1.0 de revocação e alto desempenho global.
* **Consistência Normativa:** A interpretação de jurisprudências do TST e resoluções educacionais foi mantida estritamente dentro dos fatos fornecidos nos chunks.

**Gargalos Técnicos (Onde o sistema falhou):**
* **Colapso Total de Revocação em Consultas de Canais Externos:** Falhas graves registradas nos IDs 9 e 10 (Context Recall = 0.0), onde o retriever falhou em recuperar órgãos de denúncia externos (como MPT, MTE, Disque 100) e centros de apoio psicossocial exigidos pelo gabarito.
* **Poluição de Ruído Semântico (Baixa Precisão de Contexto):** O ID 9 apresentou a pior precisão de contexto (Context Precision = 0.40) devido à recuperação de chunks irrelevantes (feiras populares, microcrédito) para uma pergunta estritamente trabalhista.
* **Prolixidade e Viés Conversacional Excessivo:** Impacto direto na Relevância da Resposta (IDs 3, 9 e 10 com pontuações de 0.40 a 0.50), caracterizado por preâmbulos emocionais longos ("Sinto muito", "Respira fundo") que violam a concisão e objetividade técnica esperada de um assistente RAG.

## 3. Plano de Ação e Recomendações de Engenharia

1. **Ajuste Fino de Hiperparâmetros do Retriever (Top-K e Threshold):** Reduzir o parâmetro `Top-K` e implementar um limiar de corte (*similarity threshold*) mais restrito no `pgvector` para mitigar a injeção de ruídos genéricos (observados nos IDs 3, 4 e 9).
2. **Reestruturação e Enriquecimento da Base de Conhecimento:** Criar metadados e tags específicas para documentos de canais de denúncia externa (MPT, MTE, Disque 100) e centros de acolhimento universitário, resolvendo os gargalos de revocação zerada (IDs 9 e 10).
3. **Refinamento de Prompt para Controle de Tom (System Prompt Engineering):** Atualizar as diretrizes do LLM gerador para impor uma restrição rigorosa contra respostas excessivamente prolixas e saudações emocionais excessivas, priorizando a densidade técnica e a objetividade imediata (correção direta para as baixas pontuações de *Answer Relevance*).
4. **Implementação de Camada de Re-ranking (Reranker):** Adotar um modelo de Cross-Encoder (ex: BGE-Reranker) após a recuperação inicial do `pgvector` para reordenar os chunks por relevância semântica real, elevando a *Context Precision* global acima da meta de 0.85.