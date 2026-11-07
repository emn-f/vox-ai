# 📄 Pesquisa e Arquitetura: Agentes Autônomos e RPA para Ingestão Contínua na Knowledge Base (Vox AI)

> **Documento de Pesquisa e Arquitetura Técnica**  
> **Issues Relacionadas:** [#97](https://github.com/emn-f/vox-ai/issues/97), [#255](https://github.com/emn-f/vox-ai/issues/255), [#285](https://github.com/emn-f/vox-ai/issues/285), [#331](https://github.com/emn-f/vox-ai/issues/331)  
> **Status:** Concluído / Proposta Arquitetural Aprovada para Implementação  
> **Data:** Novembro de 2026  

---

## 1. Sumário Executivo e Motivação

Atualmente, o processo de curadoria da Base de Conhecimento (`knowledge_base`) do **Vox AI** é predominantemente manual. Para acompanhar a dinâmica das legislações, decisões jurídicas (STF, STJ, CNJ), portarias de saúde pública (SUS) e cartilhas de direitos da população LGBTQIA+, a alimentação manual torna-se um gargalo operacional que compromete a escalabilidade e a atualização temporal do assistente.

Esta pesquisa avalia a viabilidade de adotar **Agentes Autônomos de IA** e **RPA (Robotic Process Automation)** combinados com um fluxo estrito de **Human-in-the-Loop (HITL)** para coletar, estruturar e auditar novos conhecimentos antes da indexação vetorial no banco de produção.

---

## 2. Análise Tecnológica: Ferramentas de Ingestão de Ponta

### 2.1 Google ADK (Agent Development Kit)
O **Google ADK** ([google.github.io/adk-docs](https://google.github.io/adk-docs/)) é um framework moderno de desenvolvimento de agentes focado em orquestração, ciclo de vida e integração nativa com modelos Google GenAI (família Gemini).

- **Principais Características:**
  - **Tool Orchestration:** Definição declarativa de ferramentas e chamadas de funções (*function calling*) com tipagem estrita via schemas.
  - **Memory & Session State:** Suporte nativo para retenção de contexto entre iterações e chamadas de múltiplos passos (*multi-turn reasoning*).
  - **Evaluators & Guardrails:** Camadas nativas de validação da saída gerada pelo agente antes do disparo de ações colaterais no banco de dados.
- **Aplicação no Vox AI:**
  - Um agente ADK pode atuar como **Observador Legislativo**: executando periodicamente consultas estruturadas nos diários oficiais e sintetizando decisões do STF sobre a criminalização da homotransfobia (ADO 26) ou diretrizes do SUS.

### 2.2 Firecrawl
O **Firecrawl** ([firecrawl.dev](https://www.firecrawl.dev/)) é uma engine de raspagem e crawling web desenvolvida especificamente para alimentar aplicações de LLMs e sistemas RAG.

- **Principais Características:**
  - **Clean Markdown Output:** Converte páginas HTML complexas, portais de notícias e PDFs diretamente em Markdown limpo e semântico, eliminando scripts, anúncios e headers irrelevantes.
  - **Dynamic Rendering:** Executa JavaScript em navegadores headless internos, contornando proteções básicas de scraping e renderizando SPAs (Single Page Applications).
  - **Endpoint `/crawl` e `/map`:** Mapeia subpáginas de um domínio inteiro (ex: portal da ANTRA ou ABGLT) estruturando grafos de links temáticos.
- **Aplicação no Vox AI:**
  - Ingestão automatizada de cartilhas de saúde, manuais de retificação de nome/gênero em cartório (Provimento 73/CNJ) e cartilhas universitárias de diversidade.

### 2.3 Quadro Comparativo de Abordagens de Ingestão

| Critério | Scraping Tradicional (Selenium / Playwright) | Firecrawl (LLM Crawling) | Agentes Google ADK | Soluções RPA Clássicas (UiPath / Automation Anywhere) |
| :--- | :--- | :--- | :--- | :--- |
| **Custo de Manutenção** | Alto (quebra com mudanças de CSS/DOM) | Muito Baixo (extração semântica) | Baixo (orquestração por objetivos) | Muito Alto (licenciamento corporativo e rigidez) |
| **Output para RAG** | HTML bruto ou texto ruidoso | Markdown limpo e estruturado | JSON tipado pronto para banco | Tabelas relacionais rígidas |
| **Raciocínio Contextual** | Inexistente (apenas script determinístico) | Moderado (focado em extração) | Elevado (decide o que é relevante com base em personas) | Inexistente |
| **Velocidade de Implementação** | Média | Alta (API pronta) | Média-Alta (requer prompts e tools) | Baixa |
| **Aderência ao Vox AI** | Baixa | **Alta (Camada de Extração)** | **Alta (Camada de Orquestração)** | Baixa (Inadequado para o ecossistema) |

---

## 3. Arquitetura de Pipeline Human-in-the-Loop (HITL)

A automação de dados sobre direitos humanos e saúde para populações vulneráveis **jamais deve dispensar a curadoria humana**, sob risco de propagar jurisprudências desatualizadas, fake news ou procedimentos médicos equivocados.

```
┌─────────────────┐       ┌──────────────────────┐       ┌────────────────────────┐
│  Fontes Web     │       │ Firecrawl / Scraping │       │ LLM Structuring Agent  │
│  (URLs, PDFs,   │ ────> │ Extrator de Texto    │ ────> │ (Gemini Flash Anti-    │
│  Cartilhas, DOU)│       │ e Markdown Limpo     │       │  Alucinação)           │
└─────────────────┘       └──────────────────────┘       └───────────┬────────────┘
                                                                     │
                                                                     ▼
                                                         ┌────────────────────────┐
                                                         │ Staging Supabase       │
                                                         │ [conteudo_pendente]    │
                                                         │ (Status: PENDING_REV)  │
                                                         └───────────┬────────────┘
                                                                     │
                                                   ┌─────────────────┴─────────────────┐
                                                   │                                   │
                                                   ▼ [Rejeitado]                       ▼ [Aprovado]
                                          ┌──────────────────┐               ┌──────────────────┐
                                          │ Status: REJECTED │               │ Curadoria Humana │
                                          │ (Registra motivo)│               │ (Painel/Flashcard│
                                          └──────────────────┘               └─────────┬────────┘
                                                                                       │
                                                                                       ▼
                                                                             ┌──────────────────┐
                                                                             │ Geração de Vetor │
                                                                             │ (1536 dimensões) │
                                                                             └─────────┬────────┘
                                                                                       │
                                                                                       ▼
                                                                             ┌──────────────────┐
                                                                             │ Production KB    │
                                                                             │ [knowledge_base] │
                                                                             └──────────────────┘
```

### 3.1 Camadas do Pipeline
1. **Camada de Coleta (Extraction):** Agentes disparam tarefas no Firecrawl para extrair texto íntegro de fontes autoritativas cadastradas numa *whitelist* institucional.
2. **Camada de Estruturação com IA (Transformation):** O modelo `gemini-3.6-flash` processa o conteúdo com um prompt estrito de sistema anti-alucinação, gerando pares de pergunta-resposta, identificando tópicos, eixos temáticos e tags padronizadas.
3. **Camada de Isolamento em Staging (Load):** Os dados são gravados na tabela `conteudo_pendente` com status fixo de `PENDING_REVIEW`. Nenhuma linha entra em contato com o mecanismo de busca semântica do Vox.
4. **Camada de Curadoria Humana (Human-in-the-Loop):** Curadores utilizam a interface de flashcards ou rotinas de auditoria (`scripts/audit_kb.py` e `scripts/pipeline_ingestao_ia.py review`) para inspecionar, corrigir e validar o conteúdo.
5. **Indexação Vetorial e Promoção:** Ao receber a aprovação (`APPROVED`), o embedding de 1536 dimensões é gerado via `gemini-embedding-001` e o chunk é indexado em produção na tabela `knowledge_base`.

---

## 4. Salvaguardas Éticas, Anti-Alucinação e Conformidade LGPD

1. **Anti-Alucinação Jurídica e Médica:**
   - O prompt de extração instrui categoricamente a não inferir leis, portarias ou artigos que não constem na fonte textual.
   - Qualquer citação legal exige indicação da fonte original (`fonte_original` e `data_referencia`).
2. **Proteção de Dados Pessoais (LGPD):**
   - Vetada a ingestão de nomes de partes processuais, testemunhas ou indivíduos particulares em litígios judiciais. Apenas teses jurídicas genéricas e direitos coletivos são salvos.
3. **Imutabilidade e Trilha de Auditoria:**
   - A tabela de staging armazena quem revisou (`revisado_por`), a data exata da revisão (`revisado_em`) e observações técnicas (`notas_revisao`).

---

## 5. Roteiro de Implementação Proposto (Roadmap)

- [x] **Fase 1 (MVP Staging & Scripting - Concluída):**
  - Criação da tabela de staging `conteudo_pendente` no Supabase via migration `20261107210000_staging_conteudo_pendente.sql`.
  - Implementação do script de pipeline `scripts/pipeline_ingestao_ia.py` com suporte a CLI de extração, estruturação, revisão e promoção.
  - Implementação da suíte de auditoria e diagnóstico `scripts/audit_kb.py` com flashcards para curadores.
- [ ] **Fase 2 (Conectores Automatizados Firecrawl):**
  - Adicionar webhook/cron semanal para consultar domínios de ONGs e Diários Oficiais utilizando a API do Firecrawl.
- [ ] **Fase 3 (Agente Orquestrador Google ADK com Notificações):**
  - Configurar agente autônomo com Google ADK para monitorar novidades e alertar os curadores em canal de comunicação (Slack/Discord/GitHub Issue) sobre novos conteúdos aguardando revisão humana.
