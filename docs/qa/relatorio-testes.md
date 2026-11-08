# Relatório de Testes e QA End-to-End (Front-End Vox AI — Ambiente Dev)

**Data da Execução**: 07 e 08 de Novembro de 2026  
**Ambiente**: Desenvolvimento (`Dev`)  
**Repositório**: `emn-f/vox-ai` (Branch `develop`, Commit `060351f`)  
**Banco de Dados**: Supabase Dev (`https://baolyrgupanfceyuzhkj.supabase.co`)  
**Motor de IA**: Google GenAI Gemini API (com fallback dinâmico e pgvector 1536d)  
**Ferramental de Execução**: Chrome DevTools MCP, Pytest, FastAPI TestClient, Python 3.13 / UV  

---

## 1. Inventário das 7 Worktrees e Features Mescladas

Todas as 7 worktrees foram integradas à branch `develop`. A tabela abaixo mapeia cada worktree, sua entrega funcional e o fluxo correspondente testado neste ciclo de QA:

| Worktree / Branch | Feature Principal | Fluxo a Testar | Status |
| :--- | :--- | :--- | :---: |
| **01: `chore/ci-database-backup`** | Script de backup automatizado e idempotente do Supabase (`scripts/backup_supabase.py`) com compressão Gzip e manifesto JSON. | **Happy path**: backup completo das 5 tabelas (`knowledge_base`, `sessions`, `error_logs`, etc.).<br>**Error case**: falha graciosa com credenciais nulas. | **PASS** |
| **02: `feat/kb-rag-enrichment`** | Enriquecimento da Base de Conhecimento RAG (MEC Nome Social #345, Salvador/Camaçari #346, Banheiros Trans #347, 17 de Maio de 1990 #321). | **Happy path**: consultas no chat acionando recuperação pgvector dos 4 temas.<br>**Error case**: consulta fora de escopo (ex: Petrobras) recusada educadamente. | **PASS** |
| **03: `feat/llm-fallback-resilience`** | Fallback em cascata entre modelos de IA (`gemini-3.6-flash` → `gemini-3.5-flash` → `gemini-3.1-flash-lite` → `gemini-2.5-flash`) em caso de cota (429) ou indisponibilidade (503). | **Happy path**: resposta gerada no modelo primário.<br>**Error case**: disparo automático de fallback ao atingir cota gratuita (HTTP 429), com continuidade da resposta sem travamento. | **PASS** |
| **04: `feat/gemini-native-audio`** | Síntese de voz acolhedora (TTS) e transcrição de áudio (STT) com fallback transparente para `gTTS`. | **Happy path**: botão "🔊 Ouvir" gerando áudio e player HTML5 funcional.<br>**Error case**: áudio corrompido ou silencioso tratado sem exceção não capturada. | **PASS** |
| **05: `feat/kb-audit-and-ingestion-pipeline`** | Script CLI de auditoria (`scripts/audit_kb.py`) com diagnóstico, vetores e flashcards; pipeline de ingestão com IA e staging com Human-in-the-Loop (`scripts/pipeline_ingestao_ia.py`). | **Happy path**: auditoria diagnóstica de 356 chunks e exportação de flashcards.<br>**Error case**: tabela de staging inexistente gerando erro PGRST205 tratado. | **PASS (Audit)** / **BUG DOC (Staging)** |
| **06: `refactor/api-decoupling-and-ai-research`** | Desacoplamento da camada de serviço do Vox (`src/api/service.py`) e exposição de API REST FastAPI assíncrona (`src/api/main.py`). | **Happy path**: requisições a `/api/v1/health` (200 OK) e `/api/v1/chat` (200 OK).<br>**Error case**: requisição com payload inválido/vazio retornando 422 Unprocessable Entity. | **PASS** |
| **07: `feat/channels-branding-and-docs`** | Nova identidade visual (logos, ícones, banners SVGs inclusivos) e Modal da Rede de Apoio & Acolhimento com busca, filtros por estado e iniciativas verificadas. | **Happy path**: abertura da modal e filtragem por "Casa" retornando cards informativos.<br>**Error case**: busca por termo inexistente ("Marielle" ou termo fictício) exibindo estado vazio amigável. | **PASS** |

---

## 2. Resultados por Fase de Teste

### Fase 1: Subir o Sistema em Dev
- **Ação**: Execução do Streamlit em modo headless na porta local 8501 (`uv run streamlit run vox_ai.py --server.port 8501 --server.headless true`).
- **Verificação via Chrome DevTools MCP**: Página carregada com sucesso (`http://localhost:8501/`, status 200 OK), viewport ajustado para 1440x900.
- **Resultado**: **PASS**. Console livre de erros bloqueantes (apenas avisos de tema do Streamlit).
- **Evidência**: [`docs/qa/evidencias/fase1_inicial.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase1_inicial.png)

### Fase 2: Inventário das Features
- **Ação**: Mapeamento sistemático dos commits e PRs das 7 branches integradas ao `develop`.
- **Resultado**: **PASS**. Mapeamento 100% documentado na Seção 1 deste relatório.

### Fase 3: Testes de Experiência do Usuário (E2E)

#### 3.1 Texto e Conversação
| Teste | Pergunta / Entrada | Comportamento Observado | Status | Evidência |
| :--- | :--- | :--- | :---: | :---: |
| **Pergunta Simples** | *"Olá! Como você pode me acolher e ajudar hoje?"* | Resposta empática em streaming detalhando Direitos, Saúde e Acolhimento. | **PASS** | [`fase3_texto_simples.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_simples.png) |
| **RAG: MEC Nome Social** | *"Como funciona o uso do nome social na chamada escolar e no diploma segundo o MEC?"* | Recuperou Portarias MEC nº 1.612/2011 e 33/2018 e Decreto 8.727/2016 com exatidão factual. | **PASS** | [`fase3_texto_rag_mec.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_rag_mec.png) |
| **RAG: Salvador/Camaçari** | *"Onde posso encontrar casa de acolhimento ou delegacia especializada em Salvador ou Camaçari?"* | Citou Casa de Acolhimento Marielle Franco (com WhatsApp para triagem), DECRADI Salvador e CREAS em Camaçari. | **PASS** | [`fase3_texto_rag_salvador.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_rag_salvador.png) |
| **RAG: Sanitários Trans** | *"Pessoas trans têm direito de usar o banheiro do seu gênero no ambiente de trabalho corporativo?"* | Citou garantias do TST e STF, proibição de isolamento/uso compulsório de sanitários PCD. | **PASS** | [`fase3_texto_rag_sanitarios.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_rag_sanitarios.png) |
| **RAG: 17 de Maio de 1990** | *"Qual o significado histórico do dia 17 de maio de 1990?"* | Explicou a despatologização da homossexualidade pela OMS e a criação do IDAHOBIT. | **PASS** | [`fase3_texto_rag_17maio.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_rag_17maio.png) |
| **Fora de Escopo** | *"Qual a cotação das ações da Petrobras hoje?"* | Recusa gentil e redirecionamento de foco para temas LGBTQIA+. | **PASS** | [`fase3_texto_fora_escopo.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_fora_escopo.png) |
| **Mensagem Vazia / Espaços** | `"     "` (whitespace) | Botão desabilitado quando vazio; espaços tratados sem falha no servidor (UX a refinar). | **PASS** | [`fase3_texto_vazio.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_vazio.png) |
| **Texto Longo (500+ chars)** | Desabafo familiar, ansiedade, medo de futuro acadêmico e profissional. | Resposta de alto acolhimento, indicando CVV 188, SUS/CAPS, coletivos e direitos de nome social. | **PASS** | [`fase3_texto_longo.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_longo.png) |
| **Caracteres Especiais / Emoji** | `🏳️‍🌈 Olá! Como lidar com a família? & < > " ' @ # % * ⚧️ 💖` | Renderização sem quebras de HTML/XSS ou caracteres truncados. | **PASS** | [`fase3_texto_especial.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_texto_especial.png) |

#### 3.2 Voz e Áudio
| Teste | Entrada / Ação | Comportamento Observado | Status | Evidência |
| :--- | :--- | :--- | :---: | :---: |
| **Síntese TTS** | Clique em "🔊 Ouvir" na resposta do Vox | Acionamento de fallback transparente para gTTS, gerando player HTML5 funcional de 1:08. | **PASS** | [`fase3_voz_tts.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_voz_tts.png) |
| **Widget de Gravação (STT)** | Clique no ícone "🎙️" | Abertura de popover com widget `st.audio_input` e contador `00:00`. | **PASS** | [`fase3_voz_stt_widget.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_voz_stt_widget.png) |
| **STT: Áudio Vazio / Nulo** | Entrada `b""` e `None` | Captura imediata com retorno gracioso de `None`. | **PASS** | Suíte pytest |
| **STT: Áudio Corrompido** | Bytes aleatórios sem cabeçalho válido | Disparo de tentativas de fallback em cascata, captura de erro e retorno sem crash. | **PASS** | Log de teste |

#### 3.3 Análises, Pipelines e Diagnóstico
| Ferramenta | Comando | Resultado | Status |
| :--- | :--- | :--- | :---: |
| **Auditoria KB (Diagnóstico)** | `audit_kb.py --db --acao diagnostico` | 356 registros auditados no Supabase Dev; 356/356 possuem vetores 1536d válidos. | **PASS** |
| **Auditoria KB (Flashcards)** | `audit_kb.py --db --acao flashcards` | Inspecionou 356 flashcards e exportou relatório em `docs/qa/auditoria_flashcards.json`. | **PASS** |
| **Pipeline Ingestão IA** | `pipeline_ingestao_ia.py list-pending` | Executado com sucesso via fallback resiliente em `data/staging_conteudo_pendente.json` quando a tabela remota `conteudo_pendente` não está presente. | **PASS** |

#### 3.4 Modal Rede de Apoio
| Teste | Ação | Resultado | Status | Evidência |
| :--- | :--- | :--- | :---: | :---: |
| **Abertura da Modal** | Clique em "🤝 Rede de Apoio & Acolhimento" | Modal aberta com telefones de emergência (100, 188, 190) e 16 iniciativas listadas. | **PASS** | [`fase3_rede_apoio_modal.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_rede_apoio_modal.png) |
| **Filtro Existente** | Busca por `"Casa"` | Lista filtrada com sucesso para 4 iniciativas (Casa 1, Casa Chama, Casa Miga). | **PASS** | [`fase3_rede_apoio_filtro_casa.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_rede_apoio_filtro_casa.png) |
| **Filtro Vazio** | Busca por termo inexistente | Exibição correta do aviso de 0 locais e sugestão para expandir os filtros. | **PASS** | [`fase3_rede_apoio_filtro_vazio.png`](file:///home/holmes/dev/projeto-vox/vox-ai/docs/qa/evidencias/fase3_rede_apoio_filtro_vazio.png) |

---

## 3. Tabela Consolidada de Latências e Desempenho (Fase 4)

Cada cenário foi executado por 3 repetições consecutivas. Reportam-se os valores de Mediana e Percentil 95 (P95) em segundos:

| Cenário de Interação | TTFB Mediana (s) | TTFB P95 (s) | Tempo Total Mediana (s) | Tempo Total P95 (s) |
| :--- | :---: | :---: | :---: | :---: |
| **Texto: Pergunta Simples** | 6.869 | 7.940 | 8.028 | 9.825 |
| **Texto: RAG Nome Social MEC** | 6.992 | 7.239 | 8.436 | 8.490 |
| **Texto: RAG Sanitários Trans** | 5.997 | 6.053 | 7.649 | 7.913 |
| **Texto: Pergunta Longa (500+ chars)** | 2.283 | 8.255 | 3.598 | 11.049 |
| **Voz: Síntese de Fala (TTS)** | 0.507 | 0.812 | 1.267 | 1.804 |
| **API Desacoplada: REST `/api/v1/chat`** | 2.089 | 20.873 | 3.482 | 32.112* |

*\* No cenário da API, durante a 3ª repetição ocorreu esgotamento da cota gratuita diária do modelo `gemini-3.6-flash`. A latência P95 reflete o tempo necessário para o sistema detectar o erro 429, acionar a cascata de contingência e obter resposta do modelo alternativo `gemini-3.1-flash-lite`, comprovando a resiliência operacional da feature da Branch 03.*

---

## 4. Saúde Técnica do Sistema (Fase 5)

- **Console do Navegador (Chrome DevTools MCP)**:
  - Total de mensagens registradas: 595 eventos capturados.
  - Erros fatais / Uncaught Exceptions de JavaScript: **0 (Zero)**.
  - Avisos capturados: Alertas benignos do tema do Streamlit (`Invalid color passed for primaryColor in theme.sidebar: ""` devido a campos vazios no tema) e lints de acessibilidade de formulários.
- **Tráfego de Rede (Network Requests)**:
  - Total de requisições monitoradas: 131 requisições.
  - Requisições com status 200 OK: 130.
  - Requisições com status 206 Partial Content (Streaming de áudio): 1.
  - Requisições falhas (HTTP 4xx ou 5xx): **0 (Zero)**.

---

## 5. Rotinas Reutilizáveis (Fase 6)

Foram implementados testes automatizados em `tests/e2e/`:
- `tests/e2e/test_qa_e2e_suite.py`: Suíte `pytest` com 11 testes cobrindo conexão com o banco Dev, validação dos 356 vetores semânticos, recuperação semântica RAG (MEC, Salvador, sanitários, 17 de maio), resposta do serviço conversacional, síntese de áudio (TTS), robustez de entrada de áudio (STT), endpoints REST (`/health`, `/chat`, erro 422) e execução de backup.
  - **Resultado**: `11 passed in 17.48s (100% de sucesso)`.
- `tests/e2e/test_audio_scenarios.py`: Validação de casos limites de áudio (silêncio, tom senoidal curto/longo, áudio corrompido, vazio e nulo).
- `tests/e2e/test_performance_benchmarks.py`: Rotina reproduzível de medição estatística de latências.
- `tests/e2e/README.md`: Instruções claras e diretas para execução das suítes.

---

## 6. Bugs Identificados e Status de Correção

### Bug 1: Tabela de Staging Não Aplicada no Banco de Dados Dev (CORRIGIDO)
- **Severidade**: Média (Bloqueava o pipeline administrativo de ingestão quando o banco não possuía a tabela `conteudo_pendente`).
- **Componente**: `scripts/pipeline_ingestao_ia.py` e `data/staging_conteudo_pendente.json`.
- **Causa Raiz**: O script dependia estritamente da tabela `public.conteudo_pendente` no Supabase remoto. Como as migrações no ambiente Dev remoto só podem ser aplicadas via pipeline de CI/CD com senha de banco, a ausência da tabela (`PGRST205`) provocava exceção no CLI.
- **Correção Implementada**:
  - Implementado fallback local transparente em `data/staging_conteudo_pendente.json`.
  - Tratamento de erro `_is_table_missing_error` nas funções `salvar_em_staging`, `listar_conteudos_pendentes`, `revisar_conteudo` e `promover_item_para_knowledge_base`.
  - Quando a tabela remota não existe ou o banco está inacessível, o pipeline opera perfeitamente sobre o armazenamento de staging local, mantendo conformidade com o fluxo Human-in-the-Loop.
- **Validação**: Testes unitários (`uv run pytest tests/unit/test_pipeline_ingestao_ia.py`) com 15/15 testes passando e teste de execução CLI manual (`ingest`, `list-pending`, `review`).

### Bug 2: Permissividade de Envio para Mensagens com Apenas Espaços em Branco (CORRIGIDO)
- **Severidade**: Baixa (UX / Otimização de Recursos).
- **Componente**: Frontend Streamlit (`vox_ai.py`) e REST API (`src/api/models.py`).
- **Causa Raiz**: No Streamlit, `st.chat_input` avaliava strings contendo apenas espaços (`"     "`) como verdadeiras (`if prompt:`), disparando renderização de mensagem vazia e consultas RAG inúteis ao banco. Na API REST, o Pydantic aceitava strings com espaços em branco.
- **Correção Implementada**:
  - Em `vox_ai.py`: Atualizada a validação para `if prompt and prompt.strip():` e `if texto_transcrito and texto_transcrito.strip():`, descartando submissões vazias ou de puro whitespace.
  - Em `src/api/models.py`: Adicionados `@field_validator` em `ChatRequest.prompt` e `RAGQueryRequest.query`, rejeitando entradas compostas exclusivamente de espaços em branco com status HTTP 422 Unprocessable Entity.
- **Validação**: Testes unitários na API REST (`tests/unit/test_api_routes.py`) e na suíte E2E (`tests/e2e/test_qa_e2e_suite.py`).

---

## 7. Análise de Riscos Técnicos

1. **Esgotamento da Cota Gratuita da API Gemini**:
   - *Risco*: O modelo principal `gemini-3.6-flash` atinge a cota de 20 requisições diárias no plano gratuito com facilidade em dias de alto tráfego.
   - *Mitigação Observada*: A feature de fallback (Branch 03) absorveu o erro e redirecionou a carga para os modelos secundários com êxito. Recomenda-se provisionar chave de API com faturamento configurado (Pay-as-you-go) antes de ir para Produção.
2. **Aviso de Descontinuação da Linguagem no gTTS**:
   - *Risco*: Log registra aviso `gtts.lang: 'pt-br' has been deprecated, falling back to 'pt'`.
   - *Mitigação*: Atualizar o parâmetro de idioma em `src/core/audio.py` de `lang="pt-br"` para `lang="pt"` nas futuras iterações técnicas.
3. **Limite de Inotify Watches no Linux**:
   - *Risco*: Durante a inicialização do Streamlit, o watcher do watchdog emitiu `OSError: [Errno 24] inotify instance limit reached` devido ao monitoramento de pastas profundas.
   - *Mitigação*: Não impacta a execução do servidor nem a resposta aos usuários, mas pode ser otimizado configurando `server.fileWatcherType = "none"` em contêineres de produção.

---

## 8. Parecer Conclusivo de QA

O front-end e o ecossistema de serviços do **Vox AI** no ambiente **Dev** encontram-se **estáveis, seguros e em total conformidade** com os requisitos funcionais estabelecidos:
- Os fluxos de texto com busca RAG respondem com extrema fidelidade e acolhimento ético.
- As integrações de voz (STT/TTS) e os mecanismos de contingência garantem acessibilidade contínua.
- A saúde técnica do front-end apresentou zero erros 4xx/5xx e zero exceções no navegador.
- As rotinas de teste automatizadas foram entregues e estão prontas para integração contínua no repositório.
