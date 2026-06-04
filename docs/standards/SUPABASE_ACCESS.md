# 🗄️ Guia de Acesso ao Supabase

> Último modificação em 21/05/2026

Bem-vindo(a)! Este guia explica como funciona nossa infraestrutura de banco de dados, quais ambientes existem, o que cada colaborador pode acessar e como configurar tudo localmente.

> **Leia antes de pedir credenciais.** A maioria das contribuições não exige acesso ao banco. Verifique a seção [Preciso realmente de acesso?](#-preciso-realmente-de-acesso) antes de prosseguir.



## 📚 Índice

1. [Arquitetura de Ambientes](#-arquitetura-de-ambientes)
2. [Princípio do Menor Privilégio](#-princípio-do-menor-privilégio)
3. [Preciso realmente de acesso?](#-preciso-realmente-de-acesso)
4. [Solicitando Acesso](#-solicitando-acesso)
5. [Configurando o Ambiente Local](#-configurando-o-ambiente-local)
6. [O que você pode fazer com a anon key](#-o-que-você-pode-fazer-com-a-anon-key)
7. [Trabalhando com Migrations](#-trabalhando-com-migrations)
8. [O que NUNCA fazer](#-o-que-nunca-fazer)
9. [Dúvidas Frequentes](#-dúvidas-frequentes)


## 🏗️ Arquitetura de Ambientes

O Vox AI possui **dois projetos Supabase** dentro da organização `vox`:

| Projeto | Finalidade | Quem acessa |
| :--- | :--- | :--- |
| `vox-ai` | **Produção.** Banco real, com dados reais de usuários. | Apenas o CI/CD (GitHub Actions). Nenhum colaborador acessa manualmente. |
| `vox-ai-dev` | **Desenvolvimento.** Ambiente seguro para testar features e migrations. | Colaboradores com necessidade comprovada. |

```
Organização Supabase: vox
├── vox-ai        → produção  (CI/CD only — GitHub Secrets)
└── vox-ai-dev    → dev/testes (colaboradores com acesso aprovado)
```

**Por que essa separação existe?** Produção nunca é tocada manualmente. Qualquer alteração de schema vai primeiro para `vox-ai-dev`, é validada, e só chega à produção via migration automática pelo pipeline `deploy_db.yml`. Isso protege os dados da comunidade que usa o Vox.


## 🔒 Princípio do Menor Privilégio

Cada colaborador recebe o mínimo de acesso necessário para fazer seu trabalho. Na prática:

| Credencial | O que permite | Quem recebe |
| :--- | :--- | :--- |
| Convite na org (role `Developer`) | Visualizar o banco no Studio, rodar queries, ver logs | Colaboradores com necessidade comprovada |
| `URL` + `anon key` do `vox-ai-dev` | Conectar a aplicação ao banco de dev localmente | Todos com acesso aprovado |
| `service_role_key` do `vox-ai-dev` | Operações de escrita fora do fluxo normal da aplicação | Apenas quando a feature exige, **temporariamente** |
| Qualquer credencial de `vox-ai` (prod) | — | **Ninguém.** Fica exclusivamente no GitHub Secrets. |


## 🤔 Preciso realmente de acesso?

Antes de solicitar, verifique:

- **Estou corrigindo um bug de UI, lógica de frontend ou prompt?**
  → Não precisa. O projeto roda sem credenciais do Supabase (apenas sem conexão com o banco). Você verá avisos no terminal, o que é esperado.

- **Estou adicionando ou corrigindo conteúdo da base de conhecimento?**
  → Use o [Formulário de Sugestão de Conteúdo](https://forms.gle/Bwb3NEurV7YoZFXG8). A curadoria gerencia a KB internamente.

- **Estou desenvolvendo uma feature que lê ou escreve no banco (logs, reports, sessões, RAG)?**
  → Sim, você precisa de acesso. Siga para a próxima seção.


## 📩 Solicitando Acesso

Envie um e-mail para **assistentedeapoiolgbtvox@gmail.com** com o assunto `[SUPABASE ACCESS] - Seu Nome` e inclua:

- Seu usuário do GitHub
- O e-mail da sua conta Supabase (ou informe que não tem uma — criaremos o convite pelo e-mail que você preferir)
- Uma linha descrevendo a feature ou tarefa que exige o acesso

A equipe vai:
1. Enviar o convite para você entrar na organização `vox` no Supabase com role `Developer` no projeto `vox-ai-dev`
2. Passar a `URL` e a `anon key` do `vox-ai-dev` por canal seguro (nunca por issue ou PR)

> **Tempo de resposta:** até 48 horas úteis.


## ⚙️ Configurando o Ambiente Local

Depois de receber as credenciais, configure o arquivo de segredos local:

**1. Crie o arquivo `.streamlit/secrets.toml` na raiz do projeto** (se ainda não existir):

```toml
GEMINI_API_KEY = "SUA_CHAVE_GEMINI_AQUI"

[supabase]
url = "URL_DO_VOX_AI_DEV"
key = "ANON_KEY_DO_VOX_AI_DEV"
```

> 💡 A `GEMINI_API_KEY` é **sua própria chave**, obtida gratuitamente em [Google AI Studio](https://aistudio.google.com/app/apikey). Não compartilhamos essa chave — cada colaborador usa a sua.

**2. Confirme que o arquivo está no `.gitignore`:**

```bash
git check-ignore -v .streamlit/secrets.toml
```

Se não retornar nada, o arquivo **não está** ignorado — pare imediatamente e avise a equipe antes de continuar.

**3. Execute o projeto:**

```bash
uv run streamlit run vox_ai.py
```

Se a conexão estiver correta, os avisos de banco desaparecem do terminal e o RAG passa a funcionar normalmente.


## 🔍 O que você pode fazer com a anon key

A `anon key` representa o role `anon` do PostgreSQL. O que ela pode ou não fazer é estritamente controlado pelas nossas políticas de RLS (Row Level Security) em conformidade com a LGPD. Resumindo:

| Tabela | Leitura (`anon`) | Escrita (`anon`) | Finalidade da RLS |
| :--- | :---: | :---: | :--- |
| `sessions` | ❌ | ❌ | Protegido. Gravado via `service_role` pelo backend. |
| `chat_logs` | ❌ | ❌ | Protegido. Gravado via `service_role` pelo backend. |
| `chat_logs_kb` | ❌ | ❌ | Protegido. Gravado via `service_role` pelo backend. |
| `error_logs` | ❌ | ❌ | Protegido. Gravado via `service_role` pelo backend. |
| `user_reports` | ❌ | ❌ | Protegido. Gravado via `service_role` pelo backend. |
| `knowledge_base` | ✅ | ❌ | Leitura pública liberada para estatísticas e metadados no Dashboard. |
| `knowledge_base_etl` | ❌ | ❌ | Tabela de controle de ETL. Totalmente protegida. |
| `report_categories` | ✅ | ❌ | Leitura pública para listar as categorias de denúncia no app e Dashboard. |

Toda escrita e leitura de logs e dados sensíveis que a aplicação faz usa a `service_role` do Supabase internamente do lado do servidor (backend Python/Streamlit). Isso blinda o banco de dados contra qualquer tentativa de leitura ou inserção pública vinda de agentes externos maliciosos usando a `anon_key` pública.


## 🗃️ Trabalhando com Migrations

Se sua feature alterar o schema do banco (nova tabela, nova coluna, alteração de tipo), siga este fluxo:

**1. Gere a migration usando o CLI do Supabase:**

```bash
# Autentique com sua conta pessoal do Supabase (token pessoal, não compartilhado)
supabase login

# Vincule ao projeto de dev
supabase link --project-ref <ref-do-vox-ai-dev>

# Faça as alterações no banco de dev pelo Studio
# Depois gere o diff automaticamente:
supabase db diff -f nome_descritivo_da_migration
```

**2. Nomeie a migration seguindo a convenção do projeto:**

```
<timestamp>_<verbo>_<objeto>_<contexto>.sql
```

Exemplos corretos:
```
20260510120000_add_column_feedback_to_chat_logs.sql
20260510130000_create_table_user_preferences.sql
```

Consulte [CONVENTIONAL_MIGRATIONS.md](../docs/standards/CONVENTIONAL_MIGRATIONS.md) para a lista completa de verbos e exemplos.

**3. Inclua o arquivo `.sql` no mesmo commit que o código:**

```bash
git add supabase/migrations/seu_arquivo.sql src/core/database.py
git commit -m "feat(db): adiciona coluna de feedback nos logs de chat"
```

> ⚠️ Nossos Git Hooks verificam isso. Um commit que altera código de banco sem a migration correspondente será bloqueado.

**4. O deploy para produção é automático:**

Quando seu PR for mergeado em `main`, o workflow `deploy_db.yml` aplica a migration no `vox-ai` de produção automaticamente. Você não precisa fazer nada.

---

## 🚫 O que NUNCA fazer

```
❌ Commitar o arquivo .streamlit/secrets.toml
❌ Colar credenciais em issues, PRs, comentários, Discord ou qualquer local de acesso público.
❌ Compartilhar sua anon key com outras pessoas
❌ Usar a service_role_key sem autorização da equipe
❌ Tentar acessar ou solicitar credenciais do banco de produção (vox-ai)
❌ Rodar supabase db push apontando para produção manualmente
❌ Alterar dados da knowledge_base de produção diretamente pelo Studio
```

Qualquer uma dessas situações deve ser reportada para `assistentedeapoiolgbtvox@gmail.com` imediatamente, sem julgamentos — acidentes acontecem e o importante é corrigir rápido.


## ❓ Dúvidas Frequentes

**O projeto travou com erro de conexão ao Supabase. O que faço?**
Verifique se o `.streamlit/secrets.toml` existe e se a `url` e `key` estão corretas. O projeto roda sem o banco, mas com avisos — se o erro for bloqueante, fale com a equipe.

**Posso ver os dados reais de usuários no banco de dev?**
O `vox-ai-dev` é um ambiente de desenvolvimento e não contém dados reais de produção. Dados de produção nunca são copiados para o dev.

**Minha feature precisa da `service_role_key`. Como peço?**
Descreva no e-mail de solicitação qual operação específica exige esse nível de acesso. Passamos a chave de forma temporária e por canal seguro.

**Saí do projeto. O que acontece com meu acesso?**
Avise a equipe por e-mail. Removeremos seu convite da organização Supabase e rotacionaremos as chaves se necessário.

**Posso usar o Supabase Studio para explorar o schema do banco?**
Sim! O Studio é ótimo para isso. Só tome cuidado para não modificar dados ou schema diretamente — sempre via migration.

---

<div align="center">
    <p>🤖 Vox AI: conversas que importam 🏳️‍🌈</p>
</div>
