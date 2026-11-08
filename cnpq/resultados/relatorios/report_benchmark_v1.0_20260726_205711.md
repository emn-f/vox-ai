# Relatório de Avaliação Quantitativa RAG - Vox AI

**Data e Horário de Geração:** 26/07/2026 às 20:57:11
**Versão do Dataset:** Golden Dataset v1.0
**Framework de Avaliação:** Custom LLM-as-a-Judge (Gemini 3.6 Flash)
**Tamanho da Amostra:** 35 cenários (Golden Dataset v1.0)
**Tempo de Execução:** 326.7 segundos

## 1. Visão Geral das Métricas Globais

| Métrica | Pontuação Média | Status | Descrição Técnica |
| --- | --- | --- | --- |
| **Fidelidade (Faithfulness)** | 0.9000 | 🟢 | Mede a aderência factual da resposta gerada em relação estrita ao contexto recuperado (ausência de alucinações). |
| **Revocação (Context Recall)** | 0.8171 | 🟢 | Mede se o contexto recuperado continha todas as informações necessárias para satisfazer o gabarito do cenário. |
| **Relevância (Answer Relevance)** | 0.7114 | 🟡 | Mede a concisão, objetividade e alinhamento direto da resposta com a dúvida do usuário, penalizando prolixidade e "enrolação". |
| **Precisão (Context Precision)** | 0.5546 | 🔴 | Mede a proporção de chunks estritamente úteis versus ruído semântico recuperado pelo sistema de busca vetorial. |

## 2. Diagnóstico Arquitetural e Gargalos

**Destaques Positivos (O que funcionou bem):**
* **Alta Fidelidade Factual e Cobertura de Revocação em Temas Jurídicos:** Cenários como o ID 3 (isenção de menoridade e via judicial), ID 4 (direitos de pessoas não-binárias), ID 7 (sigilo e ausência de menção de alteração em certidões) e ID 9 (adoção homoafetiva) demonstraram excelente ancoragem nos chunks recuperados (Faithfulness = 1.00 e Context Recall = 1.00).
* **Robustez na Contenção de Escopo e Segurança:** Cenários de limitação de escopo (IDs 31 e 32) e blindagem ética (IDs 34 e 35) provaram que o sistema é capaz de impor barreiras de segurança e recusar adequadamente desvios temáticos e premissas discriminatórias, mantendo a integridade da plataforma Vox AI.
* **Acolhimento Especializado em Salvador:** Cenários focados em redes locais de suporte e saúde (IDs 13, 20 e 30) recuperaram com precisão endereços e delegacias especializadas (como a DECRIN e o CEDAP/SESAB), fornecendo suporte factual de alta relevância humanizada.

**Gargalos Técnicos (Onde o sistema falhou):**
* **Grave Ruído Semântico e Baixa Precisão de Contexto:** A métrica global de *Context Precision* (0.5546) evidencia um problema crítico no retriever. Cenários como o ID 2 (apenas 1 chunk útil entre 9 recuperados), ID 6 (ruído com múltiplos temas periféricos) e ID 31 (onde o retriever trouxe dados jurídicos para uma pergunta puramente turística, resultando em Precision = 0.00) demonstram poluição semântica severa na fase de recuperação.
* **Excesso de Conversacionalismo ("Chatbot Politeness" e Prolixidadade):** A métrica de *Answer Relevance* (0.7114) foi puxada para baixo de forma recorrente devido a saudações excessivas, preâmbulos empáticos longos e frases de encerramento desnecessárias (observado em IDs 1, 2, 3, 5, 6, 11, 15, 18, 21, 24, 27 e 28). O modelo gerador carece de diretrizes estritas de concisão técnica.
* **Falhas Críticas no Pipeline de Recuperação e Guardrails Ativos:** O ID 16 apresentou *Context Recall* 0.00 por recuperar a norma errada (Resolução Conjunta nº 1/2014 em vez da Resolução 348 do CNJ). Nos IDs 34 e 35, embora os guardrails éticos tenham bloqueado com sucesso as premissas de ódio, o sistema não acionou o contexto para refutar cientificamente os argumentos falsos, resultando em *Context Recall* 0.00. O ID 33 falhou catastroficamente com *Faithfulness* e *Relevance* zerados devido a um contexto totalmente vazio.

## 3. Plano de Ação e Recomendações de Engenharia

1. **Otimização do Retriever e Ajuste do Top-K:** 
   * Reduzir o parâmetro `Top-K` atual para focar em blocos mais coesos e implementar uma estratégia de **Reranking** baseada em modelos de cross-encoder (ex: `bge-reranker-large`) para filtrar chunks marginais e mitigar o baixo índice de *Context Precision* (0.5546).

2. **Refinamento do *System Prompt* para Consciência de Concisão:**
   * Atualizar as diretrizes do LLM gerador para remover o tom conversacional excessivo e empático ("enrolação" inicial e final), impondo um perfil estritamente técnico, objetivo e direto ao ponto, elevando o indicador de *Answer Relevance*.

3. **Enriquecimento e Segmentação da Base de Conhecimento (Chunking Strategy):**
   * Revisar a estratégia de particionamento (*chunking*) dos documentos legais e institucionais (como Provimentos do CNJ, resoluções do SUS e guias de segurança), utilizando janelas menores com sobreposição (*overlap*) inteligente para evitar a mistura de tópicos distintos (ex: misturar regras de estrangeiros, menores e gratuidade no mesmo bloco).

4. **Aprimoramento do Módulo de Refutação para Guardrails Éticos:**
   * Calibrar o comportamento do assistente em cenários de blindagem ética (IDs 34 e 35) para que, além de acionar a recusa de segurança, o pipeline seja capaz de injetar e sintetizar ativamente os argumentos científicos e jurídicos presentes no contexto para refutar premissas discriminatórias de forma educativa e fundamentada.