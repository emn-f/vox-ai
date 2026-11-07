# Manutenção do Supabase e Estratégia de Backup (Vox AI)

Este documento descreve os procedimentos de sustentabilidade da infraestrutura do Supabase no projeto Vox AI, detalhando a rotina de prevenção contra auto-pause e os procedimentos de backup e restauração.

---

## 1. Política de Inatividade (Keep-Alive)

No plano gratuito do Supabase, projetos sem atividade direta no banco de dados por **7 dias** são suspensos (estado `PAUSED`), resultando na remoção do registro de DNS (`<ref>.supabase.co`) e interrupção do serviço.

### Solução Implementada
O workflow [`.github/workflows/supabase_keepalive.yml`](../.github/workflows/supabase_keepalive.yml) executa a cada 3 dias às 06:00 UTC uma query PostgREST leve autenticada:
```bash
curl -X GET "https://<ref>.supabase.co/rest/v1/report_categories?select=id&limit=1" \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>"
```
Isso gera atividade real no PostgreSQL e zera o contador de inatividade sem onerar limites de cota.

---

## 2. Rotina de Backup Automatizado

Para mitigar riscos de perda de dados e garantir a preservação contínua da Knowledge Base e dos logs de auditoria (Issue #276):

### 2.1 Workflow Automatizado
O workflow [`.github/workflows/supabase_backup.yml`](../.github/workflows/supabase_backup.yml) roda semanalmente aos domingos às 03:00 UTC e também aceita disparo manual (`workflow_dispatch`).
Ele armazena os dados das tabelas em arquivos JSON compactados com gzip (`.json.gz`) com retenção de 30 dias no GitHub Artifacts.

### 2.2 Execução Local
Você pode rodar o backup a qualquer momento localmente através do script:
```bash
# Executar backup compactado
uv run python scripts/backup_supabase.py --output-dir backups/

# Executar backup em JSON puro (sem gzip)
uv run python scripts/backup_supabase.py --output-dir backups/ --no-compress
```

Tabelas incluídas no backup:
* `knowledge_base`
* `report_categories`
* `sessions`
* `error_logs`
* `user_reports`
