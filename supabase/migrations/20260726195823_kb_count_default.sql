alter table "public"."knowledge_base" alter column "kb_count" set default '0'::numeric;

update "public"."knowledge_base"
set kb_count = 0
where kb_count is null