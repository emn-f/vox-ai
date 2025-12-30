# Guia de Conventional Commits

### 🛠️ Funcionalidades & Correções

* **`feat`**: Uma nova funcionalidade para o utilizador.
  * *Exemplo:* `feat: adiciona botão para limpar histórico do chat`
* **`fix`**: Correção de um erro que afeta o utilizador.
  * *Exemplo:* `fix: corrige erro de conexão com a API do Gemini`
* **`perf`**: Uma mudança de código que melhora o desempenho.
  * *Exemplo:* `perf: otimiza carregamento do modelo de busca semântica`

### 🏗️ Estrutura & Manutenção

* **`docs`**: Alterações apenas na documentação.
  * *Exemplo:* `docs: atualiza instruções de instalação no README.md`
* **`style`**: Alterações de formatação (espaços, pontuação) que não afetam o código.
  * *Exemplo:* `style: formata arquivos .py conforme padrão PEP8`
* **`refactor`**: Alteração no código que não corrige bug nem adiciona feature.
  * *Exemplo:* `refactor: simplifica lógica de tratamento de erros no chat`
* **`test`**: Adição ou correção de testes automatizados.
  * *Exemplo:* `test: adiciona testes unitários para a função de busca`
* **`build`**: Alterações no sistema de build ou dependências externas.
  * *Exemplo:* `build: atualiza versão do streamlit no requirements.txt`
* **`ci`**: Alterações nos arquivos de configuração de CI/CD.
  * *Exemplo:* `ci: corrige script de deploy para o Hugging Face`
* **`chore`**: Outras alterações menores que não modificam arquivos de código ou teste.
  * *Exemplo:* `chore: remove arquivos temporários e de cache`
* **`revert`**: Reverte um commit anterior.
  * *Exemplo:* `revert: feat: remove integração experimental com WhatsApp`

### 🎯 Escopos (Opcional)

Você pode especificar **onde** fez a alteração colocando o contexto entre parênteses logo após o tipo.

*   `feat(ui):` adiciona novo botão na sidebar
*   `fix(db):` corrige erro de conexão no supabase
*   `refactor(core):` melhora estrutura de logs

### 💥 Breaking Changes (Atenção!)

Se a mudança **quebra compatibilidade** (ex: o usuário precisa atualizar algo para continuar usando), use um `!` antes dos dois pontos ou adicione uma nota de rodapé.

*   `feat!: remove suporte para Python 3.8`
*   Ou no corpo do commit:
    ```text
    feat: muda estrutura do banco de dados

    BREAKING CHANGE: A tabela 'users' foi renomeada para 'profiles'.
    ```
