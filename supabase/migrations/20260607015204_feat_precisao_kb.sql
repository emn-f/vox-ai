
  create table "public"."system_settings" (
    "key" text not null,
    "value" text not null
      );


alter table "public"."system_settings" enable row level security;

alter table "public"."knowledge_base" add column "ativo" boolean default true;

alter table "public"."knowledge_base" add column "validated" smallint not null default '0'::smallint;

CREATE UNIQUE INDEX system_settings_pkey ON public.system_settings USING btree (key);

alter table "public"."system_settings" add constraint "system_settings_pkey" PRIMARY KEY using index "system_settings_pkey";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.is_dev_environment()
 RETURNS boolean
 LANGUAGE sql
 STABLE SECURITY DEFINER
AS $function$
  SELECT COALESCE(
    (SELECT value = 'development'
     FROM public.system_settings
     WHERE key = 'environment'),
    false
  );
$function$
;


grant select on table "public"."system_settings" to "anon";


grant select on table "public"."system_settings" to "authenticated";

grant delete on table "public"."system_settings" to "service_role";

grant insert on table "public"."system_settings" to "service_role";

grant references on table "public"."system_settings" to "service_role";

grant select on table "public"."system_settings" to "service_role";

grant trigger on table "public"."system_settings" to "service_role";

grant truncate on table "public"."system_settings" to "service_role";

grant update on table "public"."system_settings" to "service_role";


  create policy "Permitir leitura pública da base de conhecimento"
  on "public"."knowledge_base"
  as permissive
  for select
  to anon
using (true);



  create policy "Permitir leitura pública de categorias de relatório"
  on "public"."report_categories"
  as permissive
  for select
  to anon
using (true);



