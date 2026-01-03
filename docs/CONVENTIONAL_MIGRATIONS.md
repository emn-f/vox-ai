# Convenção de Nomes para Migrations (Supabase/SQL)

Assim como seguimos o *Conventional Commits* para nossas mensagens de git, adotamos um padrão semântico para os arquivos de migração de banco de dados.

O objetivo é que qualquer desenvolvedor saiba o que uma migration faz apenas lendo seu nome, sem precisar abrir o código SQL.

## 📐 Formato Padrão

O Supabase adiciona automaticamente o timestamp. Você deve fornecer o **sufixo descritivo**.

Formato: `<verbo>_<objeto>_<contexto>`

Exemplo: `20240101123000_add_category_to_user_reports.sql`

## 📚 Glossário de Verbos

Use estes verbos no início do nome para categorizar o tipo de mudança:

| Verbo | Quando usar | Exemplo |
| :--- | :--- | :--- |
| **create** | Criação de uma tabela inteiramente nova. | `create_table_profiles` |
| **add** | Adição de colunas, funções ou policies em algo existente. | `add_email_to_users` |
| **update** | Alteração de tipo de coluna, defaults ou lógica de função. | `update_function_calculate_total` |
| **alter** | Mudanças estruturais em tabelas existentes (renomear, constraints). | `alter_users_set_email_unique` |
| **drop** | Remoção de tabelas, colunas ou funções. | `drop_table_legacy_logs` |
| **fix** | Correções de lógica ou dados (migrations de manutenção). | `fix_rls_policy_on_profiles` |
| **seed** | Inserção de dados iniciais ou de teste. | `seed_initial_categories` |
| **normalize** | Refatoração para separar dados em novas tabelas (normalização). | `normalize_report_categories` |

## ❌ Anti-Patterns (O que NÃO fazer)

*   ⛔ **Nomes Genéricos**: `update_db`, `migration_1`, `changes`.
*   ⛔ **Contexto Implícito**: `new_column` (Qual coluna? Onde?).
*   ⛔ **Verbos Fracos**: `change_table` (Use `alter`, `add` ou `drop` para ser específico).
*   ⛔ **Mistura de Idiomas**: `adicionar_user_table` (Mantenha tudo em inglês para consistência com o SQL).

## 💡 Exemplos Práticos

**Cenário 1: O usuário pediu para adicionar categorias no report**
*   *Ruim*: `update_reports`
*   *Bom*: `add_category_id_to_reports`
*   *Ótimo*: `normalize_report_categories` (se envolveu criar tabela nova e chave estrangeira)

**Cenário 2: Corrigir um bug na policy de segurança**
*   *Ruim*: `fix_security`
*   *Bom*: `fix_rls_policy_select_reports`

---
> **Dica**: No Supabase CLI, o comando fica:
> `supabase db diff --use-migra -f <nome_padrao>`


<div align="center">
<p>🤖 Vox AI: conversas que importam 🏳️‍🌈</p>
</div>