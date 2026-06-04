create extension if not exists pg_cron;

-- Agenda a exclusão semanal de registros antigos (logs, sessões e reports) com mais de 12 meses
select cron.schedule(
  'descarte-logs-12-meses',
  '0 0 * * 0', -- Executa todo domingo às 00:00 UTC
  $$
  -- 1. Remover referências na tabela pivot de base de conhecimento (chat_logs_kb)
  delete from public.chat_logs_kb
  where chat_id in (
    select chat_id from public.chat_logs where created_at < now() - interval '12 months'
  );

  -- 2. Remover logs de chat
  delete from public.chat_logs where created_at < now() - interval '12 months';

  -- 3. Remover logs de erro
  delete from public.error_logs where created_at < now() - interval '12 months';

  -- 4. Remover denúncias/relatórios de usuários
  delete from public.user_reports where created_at < now() - interval '12 months';

  -- 5. Remover sessões
  delete from public.sessions where created_at < now() - interval '12 months';
  $$
);
