-- Correção da view pública com dados agregados (Segurança / Portal de Transparência)
drop view if exists public.knowledge_base_public_stats;

create or replace view public.knowledge_base_public_stats as
select topico as tema, count(*) as quantidade, max(modificado_em) as modificado_em 
from public.knowledge_base
group by topico;

grant select on public.knowledge_base_public_stats to anon, authenticated;
