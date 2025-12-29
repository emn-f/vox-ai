
  create policy "Permitir leitura pública da KB"
  on "public"."knowledge_base"
  as permissive
  for select
  to anon
using (true);



