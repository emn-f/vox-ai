create or replace view "public"."knowledge_base_public_stats" as  SELECT topico AS tema,
    count(*) AS quantidade,
    max(modificado_em) AS modificado_em
   FROM public.knowledge_base
  WHERE (ativo IS TRUE)
  GROUP BY topico;



