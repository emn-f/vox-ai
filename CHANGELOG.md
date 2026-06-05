# 🤖 Vox AI - Changelog

Todas as mudanças no Vox AI serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

> _Arquivo gerado automaticamente via `git-cliff`._


## v3.3.16 - 04/06/2026


### ♻️ Refatoração & Melhorias

* Remover condicional duplicada e extrair logica de fallback de semantica ([0855038](https://github.com/emn-f/vox-ai/commit/0855038ac96555f52b9bacd243322c92ae940abe))

* Remover historico duplicado inutil do estado de sessao ([c76428e](https://github.com/emn-f/vox-ai/commit/c76428e3cc02bfd98adada747c083e857bd4e043))

* Modularizar historico de chat e erros de vox_ai.py para ui.py ([123f164](https://github.com/emn-f/vox-ai/commit/123f1645723e08f56acbf7a16d4e433178b2c14a))


### ⚡ Performance

* Cachear checagens de git e melhorar tipagem de get_current_branch ([c96b969](https://github.com/emn-f/vox-ai/commit/c96b969c6febaef0b42e03ca8539cd1e55c71257))


### ✨ Funcionalidades

* Remove acesso anon a KB do Vox para implementação futura de fluxo mais adequado ([f29c933](https://github.com/emn-f/vox-ai/commit/f29c93379831d8c3c2692e90c0d52bdd7b5ad13b))

* Implementar exclusao fisica de dados, minimizacao de logs e descarte automatico via pg_cron ([5408138](https://github.com/emn-f/vox-ai/commit/540813863ead5e76896f14a6c307ed2b87e9b7a1))

* Adicionar observabilidade e saude da base de conhecimento ([dc3b49e](https://github.com/emn-f/vox-ai/commit/dc3b49ef14f6cb25e79288451947cb3b990c486a))


### 🐛 Correções

* Corrigir variável de arquivo alvo para múltiplos arquivos na verificação de migrações de banco de dados ([0f85957](https://github.com/emn-f/vox-ai/commit/0f85957089e7c31541f50d72a1649e5435f74cf5))

* Corrigir conversao de tupla para lista de arquivos no diff do git ([28cb4db](https://github.com/emn-f/vox-ai/commit/28cb4dbae2a7e26a5b7582d69ebd4fedfc7a4df2))

* Corrigir checagem do diff e adicionar IF EXISTS no DROP POLICY ([863cd3e](https://github.com/emn-f/vox-ai/commit/863cd3ee4b845ae527e53a9e00c8f70f01317856))

* Corrigir AttributeError ao reportar e resetar sessao do chat Gemini ([9b17085](https://github.com/emn-f/vox-ai/commit/9b17085093a4871722fb431def07540966994793))

* Mitigar XSS/SQLi no dashboard e remover utilitario.py morto ([8fcb361](https://github.com/emn-f/vox-ai/commit/8fcb3616eb419d46ac6611a9b7d0aa39acf88d05))

* Padronizar uso do logger em semantica.py e utils.py ([a75f849](https://github.com/emn-f/vox-ai/commit/a75f849f13c6a515ab51b7297fa328db1edea23c))

* Resolver alertas de requirements.txt redundante na raiz e ajustar assercao nos testes ([688d24d](https://github.com/emn-f/vox-ai/commit/688d24db88283c44c017bba72967e4617a7f608d))

* Corrigir comandos de instalacao e testes no pipeline de producao ([d6f203a](https://github.com/emn-f/vox-ai/commit/d6f203a2b5bce44cf97ae6a9b3a4e9072bdd8217))

* Pular teste de integracao do Gemini na CI se a chave for mockada ([3400ec9](https://github.com/emn-f/vox-ai/commit/3400ec9a735ccae197be79eb7bd07bb5cbb2f85f))


### 📚 Documentação

* Atualizar arquitetura, politica de privacidade, acessos do Supabase e criar guia para nao-devs ([b987d43](https://github.com/emn-f/vox-ai/commit/b987d439b23a42ad80149ac5129638a162e281ac))


### 🔧 Tarefas Internas

* Ignore .antigravity/ directory in gitignore ([54be022](https://github.com/emn-f/vox-ai/commit/54be022f6b7828ac7af8d3111535246da7113d14))

* Renomear seção de relatórios do Antigravity para CLI e adicionar diretório .agents ao .gitignore ([1567aae](https://github.com/emn-f/vox-ai/commit/1567aaec87829b27b1b0e8549474e3270b1c8450))

* Adicionar .queries ao .gitignore para evitar rastreamento de arquivos de consulta ([889eb19](https://github.com/emn-f/vox-ai/commit/889eb1918ded209f68b691eb86092c7dc4ae1e1d))

* Registrar marcadores unit e integration no pyproject.toml ([fa1b9c6](https://github.com/emn-f/vox-ai/commit/fa1b9c6864496abde4f4da506892be7b2237b8df))

* Silenciar warnings e enxugar traceback no console ([79c5368](https://github.com/emn-f/vox-ai/commit/79c5368faa5f6ea4adfbc4856963d2d345ed4c68))

* Habilitar modo verbose para exibir nomes dos testes no terminal ([b3bafa2](https://github.com/emn-f/vox-ai/commit/b3bafa2952660b92953c49ce507998817bd70e02))

* Atualizar dependencias com uv lock para corrigir alertas do dependabot ([1528608](https://github.com/emn-f/vox-ai/commit/1528608d44b561b41f5111730e56226b402a4f25))

* Atualizar modelo do Gemini para gemini-2.5-flash ([076fc4d](https://github.com/emn-f/vox-ai/commit/076fc4d100f32c921d1f3a0af8e835a280af5d1f))

* Usar gemini-3.1-flash-lite e travar push em falha da API ([136c52a](https://github.com/emn-f/vox-ai/commit/136c52af3f6a198b56414e4b874c879f7e6c59b7))


### 🧪 Testes Unitários e de Integração

* Evitar interceptacao de mocks globais em testes de integracao ([05b836a](https://github.com/emn-f/vox-ai/commit/05b836a54190251e64ebee12675487aa934a6c76))

* Aplicar marcadores e usar constante de modelo do projeto no teste do Gemini ([e952120](https://github.com/emn-f/vox-ai/commit/e9521203ab439c73551ff265954b3f2688331c20))

* Categorizar testes de unidade com marcacao pytestmark no escopo de modulo ([ac1567b](https://github.com/emn-f/vox-ai/commit/ac1567b318ad8e2839df4df4dd71be56a6dae71e))


## v3.3.15 - 30/05/2026


### 📚 Documentação

* Criação de doc para configuração do Supabase ([25519b1](https://github.com/emn-f/vox-ai/commit/25519b127b7993e1f5d57accd6b06246cf1939bf))

* Atualizar caminhos para arquivos de padrões de commits e migrações no guia de contribuição ([1cbaa86](https://github.com/emn-f/vox-ai/commit/1cbaa8609502735840252b86ae40c6ad8c30325b))


## v3.3.14 - 30/05/2026


### 📚 Documentação

* Atualizar caminhos para arquivos de padrões de commits e migrações no guia de contribuição ([3cad7f3](https://github.com/emn-f/vox-ai/commit/3cad7f3e7c4dc0f5fb3f08b41dc086e6cad022d8))


## v3.3.13 - 13/05/2026


### 🐛 Correções

* Remoção de espaço extra no header do Git Cliff ([b0b0210](https://github.com/emn-f/vox-ai/commit/b0b02105bc57c4a2ce5587f000e1ef28511caafd))


## v3.3.12 - 13/05/2026


### ♻️ Refatoração & Melhorias

* Substitui atributos id por data-link para melhor organização e acessibilidade ([72c577a](https://github.com/emn-f/vox-ai/commit/72c577ab02bc0ecd1f29b9cc438cad5deb8f6923))


### ✨ Funcionalidades

* Atualiza modelo gemini para versão `gemini-3-flash-preview` ([d459560](https://github.com/emn-f/vox-ai/commit/d4595607a27e2041097ffde00d199559fc9e51ad))

* Adiciona arquivo de configuração com links para recursos do projeto; adição de nova colaboradora @cfmiila na sessão equipe ([7c1acfe](https://github.com/emn-f/vox-ai/commit/7c1acfe4601b489bad46fbd29ad2d23184e89403))


### 📚 Documentação

* Changelog agora exibe id dos commits e autoria; melhorias no header e no body. ([8afa10f](https://github.com/emn-f/vox-ai/commit/8afa10f42e118c1d63c9f90eb98b1d02c3a5e48a))

### 🔧 Tarefas Internas

* Melhorias no header. ([91124f1](https://github.com/emn-f/vox-ai/commit/91124f1d6040db20f7bcbe9833f49328763794b3))

## v3.3.11 - 13/05/2026

### 🐛 Correções (por [@cfmiila](https://github.com/cfmiila))

* Corrige alinhamento do link @casamariellefrancobr na sidebar

* Corrige tags não fechadas no `index.html`

* Corrige bugs visuais na sidebar e no `index.html`

## v3.3.9 - 21/04/2026

### ✨ Funcionalidades

* Verificação de conexão com o supabase será executa se houver mudanças em `supabase/migrations/*.sql` ou `supabase/config.toml`

### 🎨 Estilo e Formatação

* Melhorias na organização do changelog

### 🐛 Correções

* Ignorar o teste de conexão do Supabase quando as credenciais ou a biblioteca não estiverem disponíveis (contexto de PR de fork)

## v3.3.8 - 21/04/2026

### ♻️ Refatoração & Melhorias
* Conexão com banco de dados é testada se houver modificações que afetem o database
* Redução de complexidade na função `run_ai_code_review`
* Code Review utiliza modelo `gemini-3.1-flash-lite-preview` para atuar como gatekeep

### 🐛 Correções
* Corrigido erro que não exibia versão corretamente no Hugging Face
* Correção no diretório que contém binários para serem removidos antes do push para HF

## v3.3.7 - 21/04/2026

### 📚 Documentação
* Reorganização das documentações do projeto

### ♻️ Refatoração & Melhorias
* Adiciona `type hints` nas funções do Python para melhor legibilidade (by [@rodrigosantos-eng](https://github.com/rodrigosantos-eng))

## v3.3.6 - 20/04/2026

### ✨ Funcionalidades
* Adiciona codificação UTF-8 ao criar hooks
* Code review será executando em PRs que aponta para `develop`. Remoção da execuçao no push para main, que estava causando execução extra desnecessária.

## v3.3.5 - 18/04/2026

### ✨ Funcionalidades
* Adiciona script `gerar_embedding` para reindexação de embeddings na tabela `knowledge_base`

### 🐛 Correções
* Corrige tipo de tarefa para 'RETRIEVAL_QUERY' na função semantica

### 🤖 CI/CD & Automação
* Adiciona .bat de migração automática para o Supabase
* Realiza redefinição da variável SUPABASE_DB_PASSWORD após erro na geração da migration

### 📚 Documentação
* Corrige links para arquivos de convenções no Guia de Contribuição
* Corrige link para o arquivo CONVENTIONAL_COMMITS.md
* Correção do nome do modelo e de caminhos de outras docs

## v3.3.4 - 10/04/2026

### ✨ Funcionalidades
**BREAKING CHANGE:** Altera modelo de RAG para `gemini-embedding-001`


### 🐛 Correções

* Corrige nome do workflow para 'Production Pipeline' no arquivo deploy_pages.yml

## v3.2.30 - 10/01/2026

### ♻️ Refatoração & Melhorias

* Atualiza versão e descrição do projeto no `pyproject.toml`


### 🐛 Correções

* Corrige nome do workflow para 'Production Pipeline' e atualiza diagrama de arquitetura

* Corrige parâmetros de chamada da função `embed_content` e ajusta importação do types

## v3.2.29 - 10/01/2026

### ♻️ Refatoração & Melhorias

* Centraliza scripts de code reviee em `gatekeep/`


### ✨ Funcionalidades

* Adiciona item de verificação para execução do script de gatekeep no template de criação de PR


### 🐛 Correções

* Corrige caminho do `gatekeep` para permitir a importação do `security_check`


### 📚 Documentação

* Corrige versão do Python para 3.13 e corrige caminho do Guia de Contribuição

## v3.2.28 - 10/01/2026

### ♻️ Refatoração & Melhorias

* Migra SDK do Google AI para `google-genai`

* Move função para inserir conhecimento na base de dados para um script separado


### ✨ Funcionalidades

* Exibe erro detalhado caso o prompt não possa ser respondido


### 🐛 Correções

* Corrige erro de chamada de função para salvar versão do git em error_logs


### 📚 Documentação

* Atualiza CHANGELOG.md com novas entradas


### 📦 Build & Dependências

* Migra gerenciamento de dependencias para uv


### 🔧 Tarefas Internas

* Adiciona scripts/debug_models.py ao .gitignore


### 🧪 Testes Unitários e de Integração

* Corrige testes de integração

* Testes unitários atualizados para usar lib `google.genai`

* Remove importação que não existe

## v3.2.27 - 06/01/2026

### ♻️ Refatoração & Melhorias

* Atualiza URLs para refletir a nova estrutura do projeto e corrige gatilhos de workflow

## v3.2.25 - 06/01/2026

### 🐛 Correções

* Corrige o fluxo de atualização do ambiente de homologação

### 🔧 Tarefas Internas

* Refatora projeto para renomeação das branches (master->main)

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
