# Guia de Contribuição do Vox AI

Primeiramente, **obrigado** por seu interesse em contribuir com o Vox AI! 🎉

Somos um projeto de código aberto focado em tecnologia social e inclusão. Seja corrigindo um bug, melhorando a documentação, aprimorando nossa base de conhecimento ou propondo novas features, sua ajuda é essencial para tornarmos este assistente cada vez mais seguro e útil para a comunidade LGBTQIA+.

Este documento é um guia para ajudá-lo a contribuir da melhor forma possível.

## 📚 Índice

1.  [Código de Conduta](#-código-de-conduta)
2.  [Como começar](#-como-começar)
3.  [Fluxo de desenvolvimento](#-fluxo-de-desenvolvimento)
4.  [Padrões e Convenções](#-padrões-e-convenções)
5.  [Base de conhecimento (RAG)](#-base-de-conhecimento-rag)
6.  [Abrindo um pull request](#-abrindo-um-pull-request)


## 🤝 Código de Conduta

Este projeto e todos os seus participantes estão sob o nosso [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, espera-se que você mantenha este código. Por favor, reporte comportamentos inaceitáveis para `assistentedeapoiolgbtvox@gmail.com`.


## 🚀 Como Começar

Se você quer rodar o projeto localmente para testar mudanças:

1.  **Fork** este repositório.
2.  **Clone** o seu fork:
    ```bash
    git clone https://github.com/SEU-USUARIO/vox-ai.git
    cd vox-ai
    ```
3.  **Crie um ambiente virtual** (Recomendado Python 3.11+):
    ```bash
    python -m venv .venv
    .venv\Scripts\activate     # Windows
    # ou
    source .venv/bin/activate  # Linux/Mac
    ```
4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo `.streamlit/secrets.toml` na raiz do projeto.
    O arquivo deve seguir este formato:

    ```toml
    GEMINI_API_KEY = "SUA_CHAVE_AQUI"
    
    [supabase]
    url = "SUA_URL_SUPABASE"
    key = "SUA_CHAVE_ANON_SUPABASE"
    ```

    > **🔒 Credenciais do Supabase (Interno):**
    > O Vox utiliza o **Supabase** para RAG e Logs. Essas credenciais não são públicas.
    > 
    > * **Sem credenciais:** <u>O projeto rodará sem conexão com a base de dados do projeto usando apenas a resposta da IA</u>. Você verá avisos de conexão no terminal, o que é esperado.
    > * **Precisa de acesso ao banco?** Se a feature que você deseja implementar depende estritamente do acesso ao banco de dados, envie um e-mail para a equipe. Podemos fornecer credenciais temporárias ou um ambiente de sandbox.
6.  **Instale os Git Hooks (Segurança):**
    Para garantir que nenhum segredo seja commitado, que o banco de dados esteja consistente e que as **mensagens de commit estejam no padrão**, instale os hooks de pré-commit:
    ```bash
    python scripts/install_hooks.py
    ```

7.  **Execute o projeto:**
    ```bash
    streamlit run vox_ai.py
    ```

## 🔄 Fluxo de Desenvolvimento

Utilizamos um fluxo simples baseado em branches:

* **`master`**: Código em produção (estável). Não é possível comitar diretamente aqui.
* **`dev`**: Branch principal de desenvolvimento. **Suas PRs devem apontar para cá.**

**Para nova feature ou correção:**
1.  Crie uma branch a partir de `dev`:
    ```bash
    git checkout -b feat/minha-nova-feature
    ```

##  📝 Padrões e Convenções

### Padrões de Commit

Utilizamos a especificação **Conventional Commits**. Isso é **obrigatório**, pois nosso Changelog é gerado automaticamente. Nossos hooks bloquearão seu commit se ele estiver fora do padrão.

Consulte o nosso arquivo **[CONVENTIONAL_COMMITS.md](CONVENTIONAL_COMMITS.md)** para ver a lista completa de tipos, escopos aceitos e exemplos específicos do projeto.

**Tipos aceitos:**

| Tipo | Descrição | Exemplo |
| :--- | :--- | :--- |
| **feat** | Nova funcionalidade para o usuário | `feat: adiciona botão de feedback` |
| **fix** | Correção de bug | `fix: corrige erro na sidebar mobile` |
| **docs** | Mudanças apenas na documentação | `docs: atualiza README com instruções de setup` |
| **style** | Formatação, CSS, espaços em branco (sem mudar lógica) | `style: melhora contraste do botão dark mode` |
| **refactor** | Refatoração de código (sem mudar funcionalidade) | `refactor: simplifica função de busca semântica` |
| **perf** | Melhoria de performance | `perf: otimiza carregamento do JSON` |
| **test** | Adição ou correção de testes | `test: adiciona teste unitário para utils.py` |
| **chore** | Tarefas de build, configs, auxiliares | `chore: atualiza dependências do requirements.txt` |
| **ci** | Alterações em arquivos de CI/CD (GitHub Actions) | `ci: ajusta workflow de deploy no hugging face` |
| **build** | Alterações no sistema de build ou dependências externas. | `build: atualiza versão do streamlit no requirements.txt`

### Migrations e Alterações de Schema

Se você alterar a estrutura do banco (tabelas, colunas), **é obrigatório incluir o arquivo de migração (.sql)** no commit. Nossos hooks bloquearão seu commit se detectarem mudanças no código de banco sem o respectivo SQL.

Use nomes descritivos para suas migrations. Consulte **[CONVENTIONAL_MIGRATIONS.md](CONVENTIONAL_MIGRATIONS.md)** para o padrão de nomenclatura.


## 🧠 Base de Conhecimento (RAG)

O Vox utiliza uma arquitetura RAG (Retrieval-Augmented Generation). Os dados são armazenados e consultados via **Supabase** (PostgreSQL com `pgvector`).
    
⚠️ **Atenção:**
A base de conhecimento é gerida internamente.
* Se você encontrou um erro de informação ou quer sugerir um novo tema, por favor, utilize nosso **[Formulário de Sugestão de Conteúdo](https://docs.google.com/forms/d/e/1FAIpQLSemqzlBCsI8LmKNtCRccoHcvP6R8QTvZ7WmbPweBqcpJzqrBQ/viewform)**. A equipe de curadoria analisará sua contribuição.
* Se planeja codar algo relacionado a base de dados e precisa de acesso a tudo que está presente lá, entre em contato conosco por [e-mail](mailto:assistentedeapoiolgbtvox@gmail.com).

## 📥 Abrindo um Pull Request

1.  Certifique-se de que seu código está rodando sem erros.
2.  Faça o Push da sua branch para o seu fork.
3.  Abra um Pull Request para a branch **`dev`** do repositório original.
4.  Na descrição do PR, explique o que foi feito e vincule a issue relacionada (se houver).
5.  Aguarde a revisão da equipe! 💜


## 💬 Dúvidas e Discussões

Antes de abrir uma issue, verifique se sua dúvida já não foi respondida.

* **Tem uma pergunta geral ou ideia?** Use o nosso [GitHub Discussions](https://github.com/emn-f/vox-ai/discussions). É o melhor lugar para sugerir melhorias que ainda não são features concretas ou tirar dúvidas de setup.
* **Encontrou um bug ou quer uma feature específica?** Abra uma [issue](https://github.com/emn-f/vox-ai/issues/new/choose) utilizando os templates oficiais.
* **Assuntos sensíveis/segurança?** Envie um e-mail para `assistentedeapoiolgbtvox@gmail.com` (veja nossa [Política de Segurança](SECURITY.md)).


---

<div align="center">
    <p>🤖 Vox AI: conversas que importam 🏳️‍🌈</p>
</div>