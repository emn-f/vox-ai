drop view if exists "public"."knowledge_base_public_stats";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_knowledge_base(query_embedding public.vector, match_threshold double precision, match_count integer, filter_topic text DEFAULT NULL::text)
 RETURNS TABLE(id text, topico text, eixo_tematico text, descricao text, similarity double precision)
 LANGUAGE plpgsql
AS $function$BEGIN
    return query
    select
      knowledge_base.kb_id,
      knowledge_base.topico,
      knowledge_base.eixo_tematico,
      knowledge_base.descricao,
      1 - (knowledge_base.embedding <=> query_embedding) as similarity
    from knowledge_base
    where 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
    and (filter_topic is null or knowledge_base.topico = filter_topic)
    and knowledge_base.ativo is true
    order by knowledge_base.embedding <=> query_embedding
    limit match_count;
  END;$function$
;


