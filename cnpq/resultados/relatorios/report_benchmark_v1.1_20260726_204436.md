# Relatório de Avaliação Quantitativa RAG - Vox AI

**Data e Horário de Geração:** 26/07/2026 às 20:44:36
**Versão do Dataset:** Golden Dataset v1.1
**Framework de Avaliação:** Custom LLM-as-a-Judge (Gemini 2.5 Flash Lite)
**Tamanho da Amostra:** 10 cenários
**Tempo de Execução:** 107.01 segundos

## 1. Visão Geral das Métricas Globais

O pipeline RAG do Vox AI foi submetido a uma avaliação de quatro dimensões para medir a confiabilidade das respostas e a eficiência da recuperação de dados.

| Métrica | Pontuação Média | Status | Descrição Técnica |
| --- | --- | --- | --- |
| **Fidelidade (Faithfulness)** | 0.9450 | 🟢 Excelente | 94,5% das afirmações geradas estão ancoradas no contexto. |
| **Revocação (Context Recall)** | 0.9950 | 🟢 Excelente | O sistema encontra 99,5% da informação necessária no banco. |
| **Relevância (Answer Relevance)** | 0.7650 | 🟡 Regular | As respostas são razoavelmente diretas, mas sofrem com ruídos de tom. |
| **Precisão (Context Precision)** | 0.6250 | 🟡 Regular | 62,5% dos fragmentos recuperados são realmente úteis. |

## 2. Diagnóstico Arquitetural e Gargalos

A análise detalhada dos 10 cenários revela comportamentos específicos do motor de busca semântica e da geração do modelo de linguagem.

**Destaques Positivos (O que funcionou bem):**

* **Blindagem Ética e Ciência (ID 10):** A Fidelidade e a Revocação mantiveram-se em patamares excelentes (0.85 e 0.95, respectivamente), com o modelo desmitificando com sucesso tentativas de patologização de identidades trans e rejeitando terapias de conversão com base nas diretrizes do CFP e do SUS.
* **Resiliência a Erros Ortográficos e Gírias (IDs 1, 2, 3, 5, 6, 8):** O motor de recuperação demonstrou alta capacidade de interpretar termos informais e incorreções gramaticais ("sosinho", "muldar", "gnt"), garantindo uma Revocação de Contexto global quase perfeita (0.995).
* **Segurança e Direitos Civis (IDs 1, 2, 3, 9):** O sistema mapeou com precisão as diretrizes legais (Provimento 73 do CNJ, gratuidade de emolumentos via declaração de hipossuficiência, precedentes do TST para banheiros corporativos e regras de adoção homoparental).

**Gargalos Técnicos (Onde o sistema falhou):**

* **Ruído Semântico e Prompt Bloating (IDs 5, 6, 9):** A Precisão de Contexto caiu para níveis insatisfatórios (0.40 nos IDs 5 e 6) devido à recuperação excessiva de chunks periféricos (como regras para estrangeiros ou menores de idade quando a dúvida era focada em adultos ou atualizações de documentos específicos). Isso injeta lixo semântico no prompt.
* **Excesso de Conversacionalismo e Empatia Excessiva (IDs 1, 3, 5, 6, 9):** A Relevância da Resposta sofreu reduções severas (chegando a 0.3 no ID 5) porque o modelo adota um tom excessivamente efusivo ("Ah, que alegria ver você dar esse passo...", "Sinto muito pela burocracia...") em vez de entregar uma resposta técnica, direta e objetiva.
* **Extrapolações Fora do Contexto (IDs 2, 4, 10):** A Fidelidade sofreu pequenas penalizações devido a floreios informais e introdução de dados de suporte emocional que, embora factualmente corretos, não estavam estritamente contidos nos textos secos recuperados pelo retriever do Supabase.

## 3. Plano de Ação e Recomendações de Engenharia

Para elevar as métricas do Vox AI para padrões de produção de alta confiabilidade, as seguintes intervenções arquiteturais são recomendadas:

1. **Refinamento do Retriever (Supabase pgvector):**
* Reduzir o número de `Top-K` chunks na busca para evitar a injeção de trechos irrelevantes (como chunks sobre menores de idade ou reprodução assistida em consultas sobre retificação de nome de adultos). Testar a redução de 9 para 3-4 fragmentos mais estritamente alinhados.
* Implementar um *Threshold* rigoroso de similaridade de cosseno para descartar fragmentos com baixa aderência semântica à pergunta do usuário, corrigindo a métrica de Precisão de Contexto (atualmente em 0.625).


2. **Ajuste Fino do System Prompt (Diretriz de Tom e Concisão):**
* Atualizar o *system prompt* para penalizar respostas excessivamente prolixas ou com apelo emocional exagerado ("enrolação"). Instruir o modelo a priorizar a assertividade, objetividade e clareza técnica, preservando a acolhida humanizada sem sacrificar a Relevância da Resposta (Answer Relevance).


3. **Controle de Fidelidade Estrita (Grounding):**
* Reforçar restrições no LLM para impedir adições de frases de suporte afetivo que não constem explicitamente no contexto recuperado, garantindo que a Fidelidade (Faithfulness) se aproxime consistentemente de 1.0 em todos os cenários de direitos e legislação.