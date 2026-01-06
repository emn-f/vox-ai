# Changelog do Vox AI

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

Arquivo gerado automaticamente via `git-cliff`.

## v3.2.24 - 06/01/2026

### ✨ Funcionalidades

* Adiciona workflow para atualizar o ambiente de homologação


### 📚 Documentação

* Revisão do CHANGELOG.md


### 🔧 Tarefas Internas

* Adicionar nova linha no cabeçalho do changelog

## v3.2.23 - 04/01/2026

### 🐛 Correções

* (ci) Usa snapshot raso no deploy hf e remove docs/imgs para corrigir erros de binários

## v3.2.19 - 04/01/2026

### 🎨 Estilo e Formatação

* Padroniza o nome do projeto nas descrições

* Corrige a formatação da seção de tema no config.toml


### 📦 Build & Dependências

* Adicionar suporte para arquivos de imagem no Git LFS


### 🔧 Tarefas Internas

* Atualiza o Python para a versão 3.11 para corrigir a dependência do tomllib


### 🤖 CI/CD & Automação

* Code Reviwer deve ignorar commits do changelog.md

* Adiciona job de teste ao pipeline de produção


### 🧪 Testes Unitários e de Integração

* Remover variáveis ​​de ambiente sensíveis do pipeline de testes e melhora utilização do mocking para a API do Gemini

## v3.2.18 - 04/01/2026

### ♻️ Refatoração & Melhorias

* Substitui import * por imports explícitos em external_links


### ✨ Funcionalidades

* Criação dos diagramas dos fluxos da aplicação e esquema do banco de dados no Eraser.io


### 📚 Documentação

* Melhorias e revisão da Política de Privacidade

* Definição de rodapé nas documentações do Vox


### 📦 Build & Dependências

* Remove configuração de tema base do arquivo config.toml

## v3.2.17 - 03/01/2026

### ♻️ Refatoração & Melhorias

* Atualização do diretório das docs


### 📚 Documentação

* Reorganização de documentações do projeto

* Criação de Termos de Uso do Vo AI

* Cria arquivo ARCHITECTURE.md com desenho do sistema e fluxo RAG


### 🔧 Tarefas Internas

* Atualiza o cabeçalho do CHANGELOG para incluir nota sobre geração automática

## v3.2.16 - 02/01/2026

### ♻️ Refatoração & Melhorias

* Correção de erro no sumário

## v3.2.15 - 02/01/2026

### 🐛 Correções

* Corrigido nome da função que busca versão atual do Vox para registro de log

### 📚 Documentação
* README atualizado de acordo com o status atual do projeto


### 📦 Build & Dependências

* Remoção de libs que não são mais utilizadas


### 🔧 Tarefas Internas

* Adição de arquivos do pytest no .gitginore


### 🤖 CI/CD & Automação

* Adiciona log automatico de bloqueios e sugestões do Code Reviewer

* Melhorias na mensagem exibida pelo Code Reviewer

* Tenta abrir o arquivo de log do code reviewer automaticamente


### 🧪 Testes Unitários e de Integração

* Implementa testes automatizados para o fluxo de code review da IA

## v3.2.14 - 30/12/2025

### 🐛 Correções

* Adiciona tags obrigatórias no README.md para deploy no HF

* (gatekeeper) Refina keywords para evitar falsos positivos em XSS e RCE

* Implementa verificação via regex boundaries (\b) para evitar falsos positivos

* (sidebar) Corrige erro que fazia fluxo de report fechar sozinho em telas menores

### ✨ Funcionalidades

* Não executa code review se os arquivos modificados forem markdown

* Melhorias na organização da Sidebar organizada

### ♻️ Refatoração & Melhorias
* Corrige nome do Vox AI na exibição do log

### 📚 Documentação

* Documentações atualizadas para melhor clareza

 ### 🤖 CI/CD & Automação

* (fix) Remove push de tags para evitar erro de metadata em commits antigos

### 🧪 Testes Unitários e de Integração

* Implementação de testes unitários e de integração utilizando `pytest`

### 🔧 Tarefas Internas

* Utilizaçao de @st.cache_resource para previnir execução redundante da configuração da key do Gemini

* Atualiza as dependências do projeto.

* Padroniza geração de changelog de testes

* (startup_patch) Adição de comentário explicando necessidade do arquivo

* Padroniza utilização de `logger` para exibição de logs no terminal

## v3.2.5 - 30/12/2025

### ♻️ Refatoração & Melhorias

* Centraliza configuração de secrets principais e aplica logging

### 🤖 CI/CD & Automação

* Adiciona paths-ignore para ignorar arquivos .md no fluxo de revisão de segurança


## v3.2.1 - 30/12/2025

### ♻️ Refatoração & Melhorias

* Melhorias na formatação de `security_check`

### ✨ Funcionalidades

* Implementa fluxo completo de denúncia com seleção de categorias e campo de comentário


### 📚 Documentação

* Adiciona guias de convenção para commits e migrations (`CONVENTIONAL_COMMITS.md` e `CONVETIONAL_MIGRATIONS.md`)

* Adiciona instalação de Git Hooks, diretrizes de migração e referência para commits convencionais nas instruções de contribuição

* Altera licença de MIT para GNU GPLv3

* Atualiza guia de contribuição com fluxo de hooks e migrations


### 🔧 Tarefas Internas

* Configura git hook para validar mensagens de commit


### 🤖 CI/CD & Automação

* Adiciona trava de segurança para migrations de banco de dados

* Ativa cache do pip e utiliza novo requirements-gatekeep para acelerar code review
### 🧪 Testes

* Adiciona scripts de teste de conexão e banco de dados

## v3.1.37 - 29/12/2025

### ✨ Funcionalidades

* Adiciona política RLS para leitura da tabela `knowledge_base` utilizando key anon.


### 🐛 Correções

* Ajustes no prompt de segurança

* Corrige erro de conexão com supabase do hugging face


## v3.1.36 - 29/12/2025

### 🐛 Correções

* Correção no nome do secret do supabase.

## v3.1.35 - 29/12/2025

### ✨ Funcionalidades

* Melhorias no code reviewer

### 🐛 Correções

* Correção na forma como que a key do Gemini é buscada

* Correções na lógica de bloqueio da IA e ajustes no prompt de segurança

## v3.1.34 - 28/12/2025

### ♻️ Refatoração & Melhorias

* Chave anon do supabase é utilizada por padrão quando necessário

### ✨ Funcionalidades

* Code review vai ignorar valores que começam com _ (underline)

* Adiciona scripts de teste locais ao .gitignore.

* Adiciona script de verificação de segurança com detecção de segredos e revisão de código por IA para hooks Git.

### 🐛 Correções

* Correção no nome do secret

### 🤖 CI/CD & Automação

* Corrige nome incorreto de secrets de deploy no Git Pages

## v3.1.33 - 28/12/2025

### ✨ Funcionalidades

* Adiciona .agent ao .gitignore.

## v3.1.32 - 28/12/2025

### 🎨 Estilo e Formatação

* Melhor formatação do .gitignore
* 
## v3.1.22 - 28/12/2025

### 🐛 Correções

* Fix (dashboard): Versão da Base de Conhecimento agora é exibida corretamente.

## v3.1.21 - 27/12/2025

### ✨ Funcionalidades

* Adicionar coluna 'modificado_em' na tabela knowledge_base.

### 🐛 Correções

* Fix (dashboard): Versão da KB agora é exibida corretamente.

## v3.1.20 - 27/12/2025

### 🐛 Correções

* Fix (dashboard): Versão da KB agora é exibida corretamente.

## v3.1.19 - 27/12/2025

### ✨ Funcionalidades

* Feat (database): nova trigger que conta quantas vezes a kb foi utilizada.

## v3.1.18 - 27/12/2025

### ✨ Funcionalidades

* Feat (database): estrutura do banco de dados atualizada.

## v3.1.16 - 27/12/2025

### ♻️ Refatoração & Melhorias

* Refatoração do código.

* Remoção de exibição de logs desnecessários no console.

### ✨ Funcionalidades

* Feat (database): melhoria na estrutura da knowledge_base; Vox agora utiliza um contexto expandido durante busca semântica.

* Criação de testes para validar funcionamento de funções semanticas e de registro de log

### 📚 Documentação

* Revisão e melhorias na documentação.

## v3.1.15 - 19/12/2025
### ✨ Funcionalidades
* Adiciona `id` sequencial na tabela `sessions`.

### 🔧 Tarefas Internas
* Estrutura inicial do banco de prod importada.

### 🤖 CI/CD & Automação
* Exibição de logs na execução do deploy do database.

## v3.1.10 - 18/12/2025

### ✨ Funcionalidades
* Criação de testes de integração com o Supabase.
* Código revisado/ajustado para garantir integridade em conexão com o Supabase.

### 🎨 Estilo e Formatação
* Correções visuais no dashboard.

### 🔧 Tarefas Internas

* Pasta do ambiente virtual não deve ser comitada.
* Reorganizção do `.gitignore`.
* Criação de script para gerar embeddings.

## v3.1.9 - 17/12/2025

### ♻️ Refatoração & Melhorias

* CHANGELOG.md ajustado para melhor clareza


### 🔧 Tarefas Internas

* Atualiza regras de formatação, data e filtros do git-cliff

## v3.1.8 - 17/12/2025

### 🐛 Correções
- *(dashboard)* Ajusta parser do changelog para exibir versões corretamente.

### 🤖 CI/CD & Automação
- Deploy do Git Pages será feito sempre que o CHANGELOG for alterado.
- Melhorias no formato do changelog
- Renomeação estrutural dos workflows para maior clareza.
- Atualização dos gatilhos (`workflow_run`) no Deploy do GitPages e do Hugging Face para escutarem corretamente o `🚀 Main Pipeline`.

### 🔧 Tarefas Internas
- Limpeza de comentários antigos e ajustes na mensagem de commit do changelog.

## v3.1.3 - 17/12/2025

### ✨ Funcionalidades
- *(dashboard)* Expande visualização do changelog para 5 últimas versões.

### 📚 Documentação
- Atualiza branding de extensão para tecnologia social open source.
- Padroniza escrita "Vox AI".

## v3.1.2 - 16/12/2025

### 📚 Documentação
- Documentações atualizadas para refletir implementação do Supabase.
- Criação de `SUPPORT.md`.

## v3.1.1 - 16/12/2025

### 🔧 Tarefas Internas
- Sincronização do Changelog entre branchs agora é feita de forma automática e imediata.

## v3.1.0 - 16/12/2025

### ♻️ Refatoração & Melhorias
- Dashboard puxa métricas direto do Supabase.

### ✨ Funcionalidades
- Adição de botão para contribuir com a base de conhecimento.

### ⚡ Performance
- *(database)* [**breaking**] Migra arquitetura de dados e rag para Supabase.
- Vox agora utiliza o modelo mais recente disponível do Gemini Flash.

### 📦 Build & Dependências
- Remoção de scripts que não são mais necessários pra comunicação com a base de conhecimento.

## v3.0.1 - 06/12/2025

### 🤖 CI/CD & Automação
- Correção na `Sync Changelog from main to develop`.

## v3.0.0 - 06/12/2025

### ✨ Funcionalidades
- Adição de botão que permite reportar comportamento inadequado do Vox.

### 🎨 Estilo e Formatação
- Dashboard do GitPages exibe até 10 atualizações recentes.

### 🤖 CI/CD & Automação
- Ajuste no comando de push para `main` na action `tag_prod.yml`.
- Criada action para incremento manual de tags.
- Correção de bug da `sync_changelog`.

## v2.8.4 - 04/12/2025

### 📦 Build & Dependências
- Versão mínima do Streamlit especificada para funcionamento do Vox no Hugging Face.

## v2.8.3 - 04/12/2025

### 🐛 Correções
- Atualiza config do Hugging Face Space para Python 3.11 (resolve FutureWarning de google.api_core).

## v2.8.2 - 03/12/2025

### ✨ Funcionalidades
- Adição de função "texto pra voz" que permite escutar a resposta do Vox em voz alta. #66
- Implementação de função que permite que usuário converse com o Vox por áudio.

## v2.8.1 - 26/11/2025

### ✨ Funcionalidades
- Adiciona issue Templates para bug reports, feature requests e outras tarefas.

### 📚 Documentação
- Update `CHANGELOG.md`.
- Ajustes no `CONTRIBUTING.md`.

### 🤖 CI/CD & Automação
- Adição de action para sinc do `CHANGELOG.md` da branch `main` para a `develop`.

## v2.7.7 - 26/11/2025

### 🎨 Estilo e Formatação
- Melhorias gerais no GitPages #90.

### 🐛 Correções
- Versão do Vox não era exibida no Hugging Face.

### 🤖 CI/CD & Automação
- Alteração do nome da action do HF.
- Criada Action para controle de deploy do Git Pages.

## v2.7.6 - 24/11/2025

### ✨ Funcionalidades
- Correção do link de deploy no GitPages.

## v2.7.5 - 23/11/2025

### ♻️ Refatoração & Melhorias
- Remoção de comentários.

### ✨ Funcionalidades
- Links externos centralizados em `src/external_links.py`,

### 📚 Documentação
- Criação de `ASSETS.md` com todos os links e ativos digitais do Vox.
- Criação de Guia de Contribuição para o Vox.
- Atualização do `PRIVACY_POLICY.md`.
- Atualização do `README.md`.

## v2.7.4 - 23/11/2025

### ⚡ Performance
- Add caching and create `config.py`.

## v2.7.3 - 21/11/2025

### 🎨 Estilo e Formatação
- Identação no `sync_from_sheets.yml.

### 🤖 CI/CD & Automação
- Impede loop de execução ao atualizar apenas o `CHANGELOG.md`.

## v2.7.1 - 21/11/2025

### ✨ Funcionalidades
- Vox leva em consideração o código de conduta interno.
- Adição de form de avaliação na sidebar.

### 🎨 Estilo e Formatação
- Melhorias no visual da sidebar.
- Remoção de comentários.
- Redesign completo do GitPages com efeito glassmorphism e responsividade.

### 🐛 Correções
- Versão do Vox agora é exibida corretamente no Hugging Face.

## v2.6.4 - 21/11/2025

### ✨ Funcionalidades
- Erros no Vox serão salvos em planilha para análise posterior.

### 📚 Documentação
- Criação de Código de Conduta do Projeto Vox (`CODE_OF_CONDUCT.md`).

## v2.6.3 - 21/11/2025

### 🤖 CI/CD & Automação
- O deploy no Hugging Face olha para a branch `main`.

## v2.6.1 - 21/11/2025

### 📚 Documentação
- Revisão da Política de Segurança (`SECURITY.md`).

### 🤖 CI/CD & Automação
- Correções na action geradora do `CHANGELOG.md`.
- O deploy no Hugging Face olha para a branch `main`.

## v1.0.25 - 14/11/2025

### ✨ Funcionalidades
* Adiciona dashboard no Git Pages.

## v1.0.23 - 13/11/2025

### ♻️ Refatoração & Melhorias
* Ajustes no CSS principal.

## v1.0.22 - 12/11/2025

### ✨ Funcionalidades
* Adiciona cache.

## v1.0.19 - 08/11/2025

### ♻️ Refatoração & Melhorias
* Melhora o `sinc_kb.py`.

## v1.0.18 - 07/11/2025

### ♻️ Refatoração & Melhorias
* Melhora o design da UI (sidebar).

## v1.0.17 - 20/05/2025

### ✨ Funcionalidades
* Nova fonte de dados.
* Adoção da função nativa do Streamlit para exibição de texto em streaming.

## v1.0.16 - 20/05/2025

### ♻️ Refatoração & Melhorias
* Melhorias na personalidade do Vox.

### 🐛 Correções
* Correção da quebra do Markdown da mensagem de boas-vindas.
* Remoção de importações e comentários desnecessários.
* Adição de arquivos internos do Python.

## v1.0.15 - 19/05/2025

### ♻️ Refatoração & Melhorias
* Atualização do `.gitignore`.
* Atualização do `sobre.py`.
* Melhorias na sidebar.

## v1.0.11 - 19/05/2025

### ♻️ Refatoração & Melhorias
* Atualização na personalidade do Vox.

## v1.0.10 - 19/05/2025

### ♻️ Refatoração & Melhorias
* Atualização do `README.MD`.

## v1.0.9 - 19/05/2025

### ♻️ Refatoração & Melhorias
* Modularização de funções e melhorias na UI do Vox AI (PR #4).

## v1.0.8 - 19/05/2025

### ♻️ Refatoração & Melhorias
* Ajusta o padrão da tag na função `git_version`.

## v1.0.7 - 19/05/2025

### 🐛 Correções
* Exibição correta da versão em produção.

## v1.0.6 - 19/05/2025

### ♻️ Refatoração & Melhorias
* Melhora na estrutura do código e adição de comentários explicativos para facilitar a compreensão do fluxo do chat e do tratamento de erros.

## v1.0.4 - 19/05/2025

### 🐛 Correções
* Testes e correções no workflow de tagueamento automático.
* Mudança na cor da versão.

### ♻️ Refatoração & Melhorias
* Tema dark definido como padrão no Streamlit.

## v1.0.2 - 19/05/2025

### 🐛 Correções
* Adiciona tratamento de exceção para a obtenção do hash do commit na função `git_version`.

## v1.0.1 - 19/05/2025

### ♻️ Refatoração & Melhorias
* Remoção de comentários no `git_version`.

## 🚀 Lançamento da primeira versão estável do Vox AI | [1.0.0] - 2025-05-18

### ✨ Funcionalidades
* Primeira versão estável.
* Integração com Gemini API.
* Interface de chat com Streamlit.
* Animação de digitação nas respostas do assistente.
* Workflow de versionamento automático.
* Customização visual com CSS e spinner personalizado.
* Inclusão do `huggingface_hub` para melhorias de desempenho.
* Exibe versão e hash do commit na sideba

### ♻️ Refatoração & Melhorias
* Limiar de similaridade reduzido para 0.4 na função semântica.
* Diversas melhorias de interface e organização do código.
* Adição de instruções de contexto.
* Revisão do `.gitignore`.
* Adição de informações relacionadas ao projeto.
* Ajustes organizacionais.
* Novo arquivo de instruções.
* Melhorias no contexto.
* Melhorias de UI.
* Ajustes relacionados à API.
* Adição do arquivo de `requirements.txt` e melhorias de segurança.

## 🚧 first commit | dev-v0.0.1 - 17/05/2025
* Nascimento do Vox AI.
* Estrutura inicial do projeto.
* MVP funcional com interface.
* Scripts e workflows para automação.
* Primeiras versões do README, temas e JSON.
* Configuração inicial da API e chamadas.
* Organização da base de dados e lógica de contexto.
* Adição de personalidade ao chatbot.
* Saudação transferida para arquivo separado.
* Iniciando preparação da base de dados.
* Exibição da última interação do usuário.
* Adição de informações relacionadas ao projeto.
* Configuração da API no GenAI.
* Exibição e alerta de status da API.

---

<div align="center">
    <p>🤖 Vox AI: conversas que importam 🏳️‍🌈</p>
    <p>© 2026 Projeto Vox</p>
</div>
