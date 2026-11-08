# Registro de Mudança 003: Desacoplamento da Lógica Core da Interface UI (Streamlit)

**Repositório Alvo:** `vox-ai`  
**Data:** 26/07/2026  
**Tipo:** `refactor(core)`


## 1. A Mudança (O que foi alterado)

1. **Cliente Supabase (`src/core/db/client.py`):**
   - Removidos o decorador `@st.cache_resource` e a chamada visual `st.error()` da camada de banco de dados.
   - Implementado o padrão singleton em memória (`_db_client_instance`) e tratamento de exceções via `logger.error()`.
2. **Módulo de IA Gemini (`src/core/genai.py`):**
   - Removidas todas as dependências visuais e bloqueios de fluxo da camada core (`st.session_state`, `st.empty()`, `st.spinner()`, `st.stop()`, `st.error()`).
   - Refatorada a função `gerar_resposta_stream()` como geradora pura (`Generator[str, None, None]`), mantendo a função de compatibilidade `gerar_resposta()`.
   - Tornadas assíncronas/puras as funções de inicialização de chat e transcrição de áudio.

## 2. O Motivo (Rationale Técnico)

- **Princípio da Separação de Responsabilidades (*Separation of Concerns*):** A camada core em `src/core/` não deve depender do framework de interface gráfica (Streamlit). Essa acoplamento violava a testabilidade automatizada e impedia a execução lisa dos scripts de benchmark (CLI) sem erros de contexto de sessão (`ScriptRunContext`).
- **Resiliência e Reutilização:** Permitir que clientes de banco de dados e de inteligência artificial possam ser invocados por qualquer interface (CLI, API FastAPI, Streamlit ou scripts de homologação) de forma agnóstica.
