# Relatório de Avaliação Quantitativa RAG - Vox AI

**Data da Avaliação:** 26/07/2026
**Data e Horário de Geração:** 26/07/2026 às 21:07:36
**Framework de Avaliação:** Custom LLM-as-a-Judge (Gemini 3.6 Flash)
**Versão do Dataset:** Golden Dataset v1.2
**Tamanho da Amostra:** 10 cenários (Golden Dataset v1.2)
**Tempo de Execução:** 113.38 segundos

## 1. Visão Geral das Métricas Globais

| Métrica | Pontuação Média | Status | Descrição Técnica |
| --- | --- | --- | --- |
| **Fidelidade (Faithfulness)** | 0.9650 | 🟢 | Mede a aderência factual da resposta gerada em relação estrita ao contexto recuperado (evita alucinações). |
| **Revocação (Context Recall)** | 0.8500 | 🟢 | Avalia se o recuperador foi capaz de trazer todos os trechos essenciais do gabarito necessários para a resposta completa. |
| **Relevância (Answer Relevance)** | 0.7800 | 🟡 | Mede o quão direta, concisa e livre de ruídos conversacionais ou prolixidade é a resposta entregue ao usuário. |
| **Precisão (Context Precision)** | 0.6900 | 🔴 | Avalia a proporção de chunks estritamente úteis versus ruído semântico recuperado pelo sistema de busca. |

## 2. Diagnóstico Arquitetural e Gargalos

**Destaques Positivos (O que funcionou bem):**
* **Alta Fidelidade e Cobertura Crítica em Situações de Emergência:** O sistema demonstrou excelente robustez conceitual ao lidar com casos de alto risco e suporte direto, mantendo fidelidade impecável e revocação perfeita (nota 1.0 em *faithfulness* e *context_recall* nos cenários **ID 7**, **ID 5** e **ID 6**). A recuperação de redes de apoio e delegacias especializadas (como a DECRIN em Salvador e a Casa de Acolhimento Marielle Franco) ocorreu sem alucinações.
* **Consistência Jurídica Especializada:** Cenários focados em direitos trabalhistas e jurisprudência atualizada do TST (**ID 4**) obtiveram pontuações máximas de fidelidade e revocação, provando que a base de conhecimento sobre legislação é sólida quando o contexto é bem recuperado.

**Gargalos Técnicos (Onde o sistema falhou):**
* **Baixa Precisão de Contexto e Ruído Semântico (Context Precision):** O sistema sofreu severamente com a recuperação de lixo semântico e chunks irrelevantes (como leis de cartórios, convenções internacionais genéricas e centros de outras cidades, a exemplo de São Paulo). O pior desempenho ocorreu no cenário **ID 2** (*Context Precision* de **0.20** e *Context Recall* de **0.30**), onde o recuperador falhou em encontrar diretrizes do CNE/MEC sobre reemissão de diplomas e trouxe excesso de ruído sobre o Provimento 73/2018. Outros cenários como **ID 3**, **ID 9** e **ID 10** também sofreram quedas devido a esse fator (precisão variando entre 0.50 e 0.75).
* **Prolixidade e Viés Conversacional (Answer Relevance):** Vários cenários apresentaram notas baixas de relevância da resposta devido a preâmbulos e pós-escritos excessivamente empáticos, coloquiais ou com saudações/perguntas de encerramento desnecessárias ("enrolação emocional"). Isso foi notado com intensidade nos cenários **ID 3** (relevância **0.60**), **ID 8** (relevância **0.70**) e **ID 10** (relevância **0.70**), distanciando o comportamento do modelo de um padrão técnico e direto de assistência jurídica/social.
* **Falhas de Revocação por Lacunas na Busca (Context Recall):** No **ID 3**, o sistema não conseguiu recuperar prazos numéricos ou datas específicas sobre o Enem. No **ID 9**, falhou em resgatar a Resolução CNE/1/2018 exigida no gabarito, limitando-se aos dados da ANTRA/OAB, o que derrubou o *context_recall* para **0.50**.

## 3. Plano de Ação e Recomendações de Engenharia

Para mitigar os gargalos identificados na execução do *Golden Dataset v1.2* e elevar as métricas de Precisão de Contexto e Relevância da Resposta, recomendo as seguintes intervenções técnicas no pipeline do Vox AI:

1. **Refinamento do Mecanismo de Recuperação (Top-K e Re-ranking):**
   * **Implementar um Cross-Encoder (Re-ranker):** Atualmente, a recuperação vetorial pura no pgvector está trazendo chunks ruidosos (vistos nos IDs 2, 3, 9 e 10). Recomenda-se adicionar uma camada de re-ranking baseada em modelos cruzados (ex: *Cohere Re-rank* ou *BGE-Reranker-Large*) para filtrar os Top-K resultados antes de enviá-los ao LLM, elevando o *Context Precision* da média atual de 0.69 para a faixa de >0.85.
   * **Ajustar os Thresholds de Distância do pgvector:** Elevar o limiar de similaridade de cosseno/distância para descartar blocos periféricos (como referências a outras cidades ou legislações de cartório não aplicadas à pergunta).

2. **Otimização do *Chunking Strategy* (Estratégia de Recorte de Documentos):**
   * Revisar a ingestão de documentos longos (manuais do MEC, cartilhas de segurança e leis). Implementar um particionamento baseado em semântica estruturada (*Semantic Chunking*) com sobreposição (*overlap*) menor, garantindo que metadados geográficos (ex: "Salvador", "Bahia") fiquem rigidamente vinculados aos blocos locais correspondentes para evitar confusões interestaduais.

3. **Ajuste de Prompt Engineering (System Prompt & Persona Guidelines):**
   * **Mitigar o Ruído Conversacional:** Atualizar o prompt do sistema para penalizar preâmbulos sentimentais extensos e frases de acolhimento prolixas. Exigir uma postura estritamente objetiva, direta e técnica logo na primeira frase, reservando o acolhimento humanizado estritamente para casos de risco de vida (como o ID 7), o que elevará diretamente o *Answer Relevance*.
   * **Forçar Citação de Normas:** Inserir diretrizes explícitas no prompt instruindo o modelo a validar a presença de resoluções e prazos exatos no contexto antes de responder, reduzindo falhas de *Context Recall* (como observado nos IDs 3 e 9).