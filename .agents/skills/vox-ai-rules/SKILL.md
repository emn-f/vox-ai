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
   - Respeite o fluxo de branches: desenvolvimento e testes em `develop` (ou branches temáticas `feat/*`, `fix/*`), com integração em `main` via Pull Requests.
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

# Padrões de Código e Boas Práticas (Pythonic)
- **Tipagem Estrita:** Todas as funções, métodos e classes DEVEM ter type hints completos (`typing`).
- **Docstrings:** Use docstrings no padrão Google em todas as funções públicas, detalhando parâmetros, retornos e exceções.
- **Assincronicidade Limitada na UI:** No Streamlit, mantenha o fluxo compatível com o ciclo de vida top-down da UI. Use `async` na camada FastAPI (`src/api/`).
- **Modularidade:** Mantenha a separação limpa:
  - `src/app/` (UI, Chat, Páginas e Diretório de Apoio)
  - `src/api/` (Rotas REST FastAPI, serviços headless)
  - `src/core/` (GenAI, Semântica, Áudio STT/TTS, Banco de Dados)
  - `data/` (Prompts, Datasets de Enriquecimento e Fine-Tuning)

# Governança, Segurança e Ética
- O Vox AI é um projeto de apoio à comunidade LGBTQIA+. A moderação de conteúdo e as respostas devem priorizar **segurança, privacidade (anonimato absoluto), acolhimento e escuta afetiva**.
- **LGPD:** NUNCA grave Dados Pessoais Sensíveis ou identificadores diretos do usuário. O histórico em relatórios de denúncia (`user_reports`) deve ser restrito ao contexto imediato (máximo de 3 turnos / 6 mensagens).
- **Conventional Commits:** Siga rigorosamente a convenção de commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`), priorizando correções no topo das seções do changelog.

---

<div align="center">
    <p>Copyright © 2026 Vox AI: Sua dúvida merece uma resposta segura</p>
</div>