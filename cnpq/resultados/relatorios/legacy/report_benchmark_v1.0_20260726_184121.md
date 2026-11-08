
# Relatório de Avaliação Quantitativa RAG - Vox AI

**Data e Horário de Geração:** 26/07/2026 às 20:01:41
**Versão do Dataset:** Golden Dataset v1.0
**Framework de Avaliação:** Custom LLM-as-a-Judge (Gemini 2.5 Flash Lite)
**Tamanho da Amostra:** 35 cenários
**Tempo de Execução:** 197.06 segundos

## 1. Visão Geral das Métricas Globais

O pipeline RAG do Vox AI foi submetido a uma avaliação de quatro dimensões para medir a confiabilidade das respostas e a eficiência da recuperação de dados.

| Métrica | Pontuação Média | Status | Descrição Técnica |
| --- | --- | --- | --- |
| **Fidelidade (Faithfulness)** | 0.8171 | 🟢 Bom | 81,7% das afirmações geradas estão ancoradas no contexto. |
| **Revocação (Context Recall)** | 0.6680 | 🟡 Regular | O sistema encontra 66,8% da informação necessária no banco. |
| **Relevância (Answer Relevance)** | 0.6471 | 🟡 Regular | As respostas são razoavelmente diretas, com algum ruído. |
| **Precisão (Context Precision)** | 0.3923 | 🔴 Crítico | Apenas 39,2% dos fragmentos recuperados são realmente úteis. |

## 2. Diagnóstico Arquitetural e Gargalos

A análise detalhada dos 35 cenários revela comportamentos específicos do motor de busca semântica e da geração do modelo de linguagem.

**Destaques Positivos (O que funcionou bem):**

* **Blindagem Ética e Defesa de Direitos:** Em cenários críticos de direitos civis (IDs 1, 2, 8, 9, 12) e ataques éticos (IDs 34, 35), a Fidelidade bateu 1.0. O modelo respeitou rigorosamente os limites do *system prompt* e os documentos oficiais, refutando tentativas de indução a discursos patologizantes.
* **Segurança e Privacidade:** O sistema orientou corretamente sobre a retificação de documentos sem expor ou alucinar procedimentos falsos (IDs 6 e 7).

**Gargalos Técnicos (Onde o sistema falhou):**

* **A Crise da Precisão de Contexto (0.39):** O banco de dados vetorial está sofrendo de *Prompt Bloating*. A busca está recuperando muitos fragmentos (chunks) irrelevantes para montar o contexto. Isso confunde o LLM, diminui a relevância da resposta e aumenta a latência da API.
* **Vácuo de Informações Locais (Salvador/BA):** Nas perguntas sobre boletins de ocorrência específicos (ID 13), casas de acolhimento locais (ID 30) e restaurantes/hotéis inclusivos (IDs 31 e 32), a Precisão caiu para 0.0 e a Fidelidade desabou (chegando a 0.2). O modelo não encontrou dados regionais suficientes e acabou alucinando recomendações genéricas ou se perdendo no escopo.
* **Buracos na Base de Conhecimento (Context Recall = 0.0):** Cenários focados em normas educacionais (IDs 26 e 27) e uso de banheiros em ambiente corporativo (ID 15) tiveram Revocação zero. Isso indica que a base de conhecimento atual no Supabase carece de diretrizes do MEC e do Ministério do Trabalho sobre esses temas específicos.

## 3. Plano de Ação e Recomendações de Engenharia

Para elevar as métricas do Vox AI para padrões de produção de alta confiabilidade, as seguintes intervenções arquiteturais são recomendadas:

1. **Refinamento do Retriever (Supabase pgvector):**
* Reduzir o número de `Top-K` chunks na busca de "Tópicos Mistos". Trazer 5 fragmentos pode estar injetando lixo semântico. Teste reduzir para os 3 mais relevantes.
* Implementar um *Threshold* (limite de corte) de similaridade de cosseno. Se o chunk tiver uma similaridade baixa com a pergunta, ele não deve ser enviado ao LLM. Isso corrigirá imediatamente a métrica de Precisão de Contexto.


2. **Enriquecimento Estratégico da Knowledge Base:**
* Ingerir documentos do MEC sobre o uso do nome social em chamadas escolares e emissão de diplomas de ensino superior.
* Catalogar formalmente as redes de apoio de Salvador e Camaçari, adicionando cartilhas locais de atendimento para melhorar as métricas nos IDs 13 e 30.


3. **Ajuste Fino do System Prompt (Combate à Alucinação):**
* Reforçar a instrução de *fallback*: "Se a resposta para a pergunta não estiver explicitamente contida no contexto fornecido, responda APENAS: 'Não possuo essa informação na minha base de dados atual.'". Isso evitará que a Fidelidade caia para 0.2 em perguntas fora de escopo.