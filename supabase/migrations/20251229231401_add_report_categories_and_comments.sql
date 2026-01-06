create sequence "public"."report_categories_id_seq";


  create table "public"."report_categories" (
    "id" integer not null default nextval('public.report_categories_id_seq'::regclass),
    "label" text,
    "description" text,
    "created_at" timestamp with time zone default now()
      );


alter table "public"."report_categories" enable row level security;

alter table "public"."user_reports" add column "category_id" bigint;

alter table "public"."user_reports" add column "comment" text;

alter sequence "public"."report_categories_id_seq" owned by "public"."report_categories"."id";

CREATE UNIQUE INDEX report_categories_pkey ON public.report_categories USING btree (id);

alter table "public"."report_categories" add constraint "report_categories_pkey" PRIMARY KEY using index "report_categories_pkey";

alter table "public"."user_reports" add constraint "user_reports_category_id_fkey" FOREIGN KEY (category_id) REFERENCES public.report_categories(id) ON UPDATE CASCADE not valid;

alter table "public"."user_reports" validate constraint "user_reports_category_id_fkey";

grant delete on table "public"."report_categories" to "anon";

grant insert on table "public"."report_categories" to "anon";

grant references on table "public"."report_categories" to "anon";

grant select on table "public"."report_categories" to "anon";

grant trigger on table "public"."report_categories" to "anon";

grant truncate on table "public"."report_categories" to "anon";

grant update on table "public"."report_categories" to "anon";

grant delete on table "public"."report_categories" to "authenticated";

grant insert on table "public"."report_categories" to "authenticated";

grant references on table "public"."report_categories" to "authenticated";

grant select on table "public"."report_categories" to "authenticated";

grant trigger on table "public"."report_categories" to "authenticated";

grant truncate on table "public"."report_categories" to "authenticated";

grant update on table "public"."report_categories" to "authenticated";

grant delete on table "public"."report_categories" to "service_role";

grant insert on table "public"."report_categories" to "service_role";

grant references on table "public"."report_categories" to "service_role";

grant select on table "public"."report_categories" to "service_role";

grant trigger on table "public"."report_categories" to "service_role";

grant truncate on table "public"."report_categories" to "service_role";

grant update on table "public"."report_categories" to "service_role";


