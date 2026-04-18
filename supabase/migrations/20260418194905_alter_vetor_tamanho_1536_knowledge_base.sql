update knowledge_base set embedding = null where embedding is not null;

alter table "public"."knowledge_base" alter column "embedding" set data type public.vector(1536) using "embedding"::public.vector(1536);


