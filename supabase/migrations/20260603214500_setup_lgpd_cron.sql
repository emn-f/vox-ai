create extension if not exists pg_cron;

-- Agenda a exclusão semanal de registros antigos (logs, sessões e reports) com mais de 12 meses
select cron.schedule(
  'descarte-logs-12-meses',
  '0 0 * * 0', -- Executa todo domingo às 00:00 UTC
  $$
  delete from public.chat_logs where created_at < now() - interval '12 months';
  delete from public.sessions where created_at < now() - interval '12 months';
  delete from public.user_reports where created_at < now() - interval '12 months';
  $$
);
