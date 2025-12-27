alter table "public"."knowledge_base" add column "modificado_em" timestamp with time zone default now();

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.update_modificado_em()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.modificado_em = now();
    RETURN NEW;
END;
$function$
;

CREATE TRIGGER update_kb_modificado_em BEFORE UPDATE ON public.knowledge_base FOR EACH ROW EXECUTE FUNCTION public.update_modificado_em();


