set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.increment_kb_count()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
begin
  UPDATE knowledge_base
  set kb_count = kb_count + 1
  where kb_id = new.kb_id;
  return new;
end
$function$
;

CREATE OR REPLACE FUNCTION public.match_knowledge_base(query_embedding public.vector, match_threshold double precision, match_count integer, filter_topic text DEFAULT NULL::text)
 RETURNS TABLE(id text, topico text, eixo_tematico text, descricao text, similarity double precision)
 LANGUAGE plpgsql
AS $function$
  BEGIN
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
    order by knowledge_base.embedding <=> query_embedding
    limit match_count;
  END;
  $function$
;

CREATE TRIGGER tg_update_kb_usage AFTER INSERT ON public.chat_logs_kb FOR EACH ROW EXECUTE FUNCTION public.increment_kb_count();


