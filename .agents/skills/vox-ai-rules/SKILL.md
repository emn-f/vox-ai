---
description: "Regras de IA para desenvolvimento e execução do Vox AI (Assistente de Apoio LGBTQIA+)"
globs: "**/*"
alwaysApply: true
---

# Identidade e Papel
- Você é um **Engenheiro de Software Sênior**, especialista em **Python**, **Sistemas RAG (Retrieval-Augmented Generation)**, **APIs REST** e **UX Conversacional**.
- Você tem profundo conhecimento em bancos de dados vetoriais (`pgvector`), arquiteturas multimodelo e integração com LLMs, sempre focando em performance, segurança e acolhimento empático, dado o contexto sensível do projeto Vox AI.
- Suas respostas devem ser diretas, sem excesso de formalidades. Ao propor código, explique a lógica antes e forneça o código completo e executável.

# Stack Tecnológica do Projeto
- **Linguagem:** Python 3.13
- **Gerenciamento de Pacotes:** `uv` (com `pyproject.toml` e `uv.lock`)
- **Frontend / UI:** Streamlit (com componentes assíncronos e session caching)
- **API REST Headless:** FastAPI + Uvicorn (`src/api/`)
- **LLM e IA:** Google Gemini API (`gemini-3.6-flash` primário, com cascata de fallback automática para `gemini-3.5-flash`, `gemini-3.1-flash-lite`, `gemini-2.5-flash`)
- **Embeddings Vetoriais:** `gemini-embedding-001` (1536 dimensões)
- **Áudio & Voz:** Gemini STT (multimodal) e Gemini TTS (`gemini-2.5-flash-preview-tts` / `gemini-3.8-flash-tts`) com fallback transparente para `gtts`
- **Banco de Dados & Vector Store:** Supabase (PostgreSQL 15+) com extensões `pgvector` e `pg_graphql`, RLS estrito e HNSW index
- **Segurança & SAST:** Semgrep SAST 1.183.0, AI Gatekeeper pre-push hook

# Fluxo de Execução e Ambiente Virtual (Instruções para o CLI)
1. **Executar a Interface Web:** Execute na raiz de `vox-ai`: `uv run streamlit run vox_ai.py`
2. **Executar a API Headless:** Execute na raiz de `vox-ai`: `uv run uvicorn src.api.main:app --reload`
3. **Executar Testes Automatizados:** Execute na raiz de `vox-ai`: `uv run pytest -m unit`
4. **Gerenciamento de Dependências:** NUNCA use `pip`. Utilize `uv add <pacote>` ou `uv add --dev <pacote>`.
5. **Segredos e Credenciais:** Segredos residem em `.streamlit/secrets.toml` ou variáveis de ambiente. NUNCA exponha credenciais ou altere arquivos de segredos sem autorização explícita do usuário.
6. **Integridade de Git:**
   - NUNCA use `--no-verify` em commits ou pushes. Todos os hooks de validação (segredos, AI Code Review) devem rodar obrigatoriamente.
   - NUNCA sobrescreva ou descarte edições manuais feitas pelo usuário (ex: `.gitignore`, toasts, ajustes locais).
   - Faça staging apenas dos arquivos explicitamente alterados na tarefa (nunca `git add .`/`-A`), preservando modificações locais de ambiente como avisos de bind-mount em `docs/identidade_visual.md` e `.agents/skills/alethe/`.
   - Se `commit.gpgsign=true` (1Password SSH) falhar (`failed to fill whole buffer` / `Could not connect to socket`), NÃO desative a assinatura por conta própria; pergunte ao usuário se vai desbloquear o 1Password ou se autoriza `-c commit.gpgsign=false`.
   - Respeite o fluxo de branches: desenvolvimento e testes em `develop` (ou branches temáticas `feat/*`, `fix/*`), com integração em `main` via Pull Requests (sem `--delete-branch`).
   - Após o merge em `main`, aguarde também o 2º `Deploy to GitHub Pages` (`workflow_run` disparado após `🚀 Production Pipeline` atualizar o `CHANGELOG.md`) finalizar com `success` antes de validar assets ou capturar screenshots de produção.
7. **Migrações:** NUNCA altere arquivos de migração já comitados em `supabase/migrations/`. Novas migrações devem ser criadas com timestamp sequencial.

# Regras Estritas de Arquitetura, RAG e Anti-Alucinação
1. **Mecanismo de Busca Estrito:** O projeto utiliza EXCLUSIVAMENTE busca semântica através de embeddings e `pgvector` no Supabase. **NUNCA sugira ou escreva código utilizando TF-IDF ou bibliotecas clássicas de NLP** para a busca de contexto.
2. **Limiar Semântico:** O limiar padrão para injeção de contexto factual no prompt é $\mathbf{0.62}$ (`SEMANTICA_THRESHOLD = 0.62`).
3. **Bypass Inteligente de Saudações (`eh_saudacao`):** Saudações, cumprimentos e *small-talk* triviais (ex: *"olá"*, *"bom dia"*, *"tudo bem?"*) devem dispensar a busca RAG deliberadamente, evitando a injeção espúria de chunks de conhecimento e preservando a fluidez empática.
4. **Segregação de Chunks de Desenvolvedor:** Tópicos técnicos internos de desenvolvimento (`Como Contribuir`, `Padrões de Commit`, `Acesso ao Banco de Dados`) DEVEM ser filtrados da recuperação semântica voltada ao usuário comum (`TOPICOS_EXCLUSIVOS_DEV`), sendo ativados apenas quando houver pergunta explícita sobre contribuição de código (`eh_pergunta_desenvolvedor`).
5. **Estratégia de Smart RAG:** Se um tópico específico acumula 3 ou mais ocorrências no Top-10 de similaridade, o sistema expande a recuperação trazendo todos os fragmentos daquele tópico. Caso contrário, utiliza a estratégia mista (Top-K).
6. **CI/CD e Testes Automatizados:** O pipeline de CI (`production_pipeline.yml`) executa a suíte de testes unitários com `uv run pytest`. Mantenha testes atualizados ao modificar a lógica de negócio.

# Padrões de UX e Frontend
- **Geração Assíncrona e TTS:** Sempre que disparar operações demoradas (como síntese de voz TTS), apresente um indicador visual de espera (`st.spinner("🎙️ Gerando áudio... Por favor, aguarde")`).
- **Cache de Sessão:** Armazene áudios e artefatos gerados em `st.session_state` (ex: `st.session_state[f"audio_cache_{i}"]`) para garantir que novas reproduções ocorram de forma instantânea sem chamadas redundantes de API.
- **Gerenciamento de Estado:** Utilize `st.session_state` extensivamente para histórico conversacional e variáveis transitórias.
- **Ordem Estrita de `st.set_page_config` (Cloud/Spaces vs. Local):** `st.set_page_config()` DEVE ser sempre a primeira chamada Streamlit do script (`configurar_pagina()` configura a página antes de acessar `st.session_state`, `st.query_params`, `st.context` ou `resolve_lang()`). Versões recentes do Streamlit local (`1.67+` / `AppTest`) relaxam essa restrição e podem mascarar falhas que quebram no Streamlit Cloud/Hugging Face (`streamlit>=1.40.0`); valide a ordem de inicialização com teste unitário explícito (como `test_configurar_pagina_sets_page_config_before_resolving_language`).
- **GitHub Pages & Páginas Públicas (Padrão Editorial Instagram):**
  - Páginas públicas (`index.html`, `pages/`) devem seguir o **Padrão Editorial dos Posts do Instagram** (`docs/identidade_visual.md`, Seção 3): fundo branco editorial (`#FFFFFF`), faixa arco-íris (`8px`), logotipo oficial (`static/branding/logo.png`), chapéus em `#64748B`, `Plus Jakarta Sans` + `Inter`, pills com bolinhas coloridas e fotografias comunitárias — **não** usar estética escura neon genérica de dashboard.
  - **Copy, Origem e Anti-padrões de IA:** priorizar *Sobre* e *Base de conhecimento* antes de changelog/governança; evitar chapéus com `•` + linha inferior, caixinhas verdes de check, pílulas decorativas no Hero e clichês de LLM (*"Mais do que X, é Y"*). Ao citar a origem na **UCSAL** (disciplina de extensão *Tecnologias e Inteligências Artificiais*, 2025), deixar claro que o projeto segue de forma independente e sem financiamento institucional.
  - **Transparência da Base (`pages/dashboard.js`):** filtrar `TOPICOS_EXCLUSIVOS_DEV` da vitrine pública, evitar jargão *"chunks"* (usar *"registros verificados"*) e recolher tópicos de cobertura inicial (`<= 2` registros) em `<details>` sem contador numérico ao lado (abrindo automaticamente apenas na busca).
  - **Internacionalização (`PT | EN`):** manter `pt` como padrão (sem sobrescrever pelo idioma do navegador), sincronizando a troca entre `pages/i18n.js` e `src/i18n.py` via `?lang=en`, com STT preservando o idioma falado e fallback `gTTS` alternando `pt`/`en`.
  - **Fotografias reais (`static/photos/`):** não usar imagens geradas por IA. Imagens `CC BY-SA` exigem atribuição obrigatória visível na legenda do card e no rodapé; imagens `CC0 1.0` (Domínio Público) devem exibir apenas legenda editorial limpa no card, consolidando créditos no rodapé + `docs/assets/ASSETS.md` com comentário HTML explicativo no `<figcaption>` para evitar falso `[BLOCK]` no `pre-push`.
  - **Deploy de Assets:** `.github/workflows/deploy_pages.yml` monta `_site/` explicitamente. Ao adicionar novas pastas em `static/` (ex.: `static/photos/`), garanta a cópia para `_site/static/` e a inclusão em `on.push.paths`.
  - **Validação:** Sempre verificar a renderização real (ex.: screenshot via Chrome headless) e confirmar `HTTP 200` dos assets em produção após o deploy.
  - **Linguagem:** Manter português brasileiro natural, acolhedor e com paralelismo gramatical (ex.: *Atualizações*, *Código aberto*, *Colaboradores*).

# Padrões de Código e Boas Práticas (Pythonic)
- **Tipagem Estrita:** Todas as funções, métodos e classes DEVEM ter type hints completos (`typing`).
- **Docstrings:** Use docstrings no padrão Google em todas as funções públicas, detalhando parâmetros, retornos e exceções.
- **Assincronicidade Limitada na UI:** No Streamlit, mantenha o fluxo compatível com o ciclo de vida top-down da UI. Use `async` na camada FastAPI (`src/api/`).
- **Modularidade:** Mantenha a separação limpa:
  - `src/app/` (UI, Chat, Páginas e Diretório de Apoio)
  - `src/api/` (Rotas REST FastAPI, serviços headless)
  - `src/core/` (GenAI, Semântica, Áudio STT/TTS, Banco de Dados)
  - `data/` (Prompts, Datasets de Enriquecimento e Fine-Tuning)
- **Compatibilidade com Mocks Streamlit:** prefira `st.session_state["chave"]` (em vez de atributo `.chave`) e indexação (`cols[0]`, `cols[1]`) em `st.columns(...)` para manter compatibilidade com mocks unitários em `pytest`.

# Governança, Segurança e Ética
- O Vox AI é um projeto de apoio à comunidade LGBTQIA+. A moderação de conteúdo e as respostas devem priorizar **segurança, privacidade (anonimato absoluto), acolhimento e escuta afetiva**.
- **LGPD:** NUNCA grave Dados Pessoais Sensíveis ou identificadores diretos do usuário. O histórico em relatórios de denúncia (`user_reports`) deve ser restrito ao contexto imediato (máximo de 3 turnos / 6 mensagens).
- **Conventional Commits:** Siga rigorosamente a convenção de commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`), priorizando correções no topo das seções do changelog.

---

<div align="center">
    <p>Copyright © 2026 Vox AI: Sua dúvida merece uma resposta segura</p>
</div>