-- Esquema inicial do banco (Supabase / PostgreSQL), baseado no MER do projeto.
-- Como usar: Supabase → SQL Editor → cole este arquivo inteiro → Run.

-- =====================================================================
-- CONTA → especialização administrador / usuario
-- O login e a senha ficam no Supabase Auth (auth.users). Aqui guardamos
-- só nome e papel. Uma linha é criada automaticamente a cada cadastro.
-- =====================================================================
create table public.perfil (
  id    uuid primary key references auth.users (id) on delete cascade,
  nome  text not null default '',
  papel text not null default 'usuario' check (papel in ('administrador', 'usuario'))
);

create function public.criar_perfil() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.perfil (id, nome)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'nome', split_part(new.email, '@', 1)));
  return new;
end $$;

create trigger ao_criar_usuario
  after insert on auth.users
  for each row execute function public.criar_perfil();

create function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.perfil where id = auth.uid() and papel = 'administrador');
$$;

-- =====================================================================
-- PRATOS
-- =====================================================================
create table public.pratos (
  id        bigint generated always as identity primary key,
  nome      text not null,
  classe    text not null default '',
  tipo      text not null check (tipo in ('prato_principal_1', 'prato_principal_2', 'guarnicao', 'sobremesa_1')),
  descricao text not null default '',
  unique (nome, tipo)
);

-- =====================================================================
-- AREA
-- =====================================================================
create table public.areas (
  area            text primary key,
  numero_usuarios integer not null default 0 check (numero_usuarios >= 0)
);

-- =====================================================================
-- DATA (calendário). Os campos derivados (vespera_feriado, dias_ate_ferias…)
-- podem ser calculados numa view ou no backend Python, a partir destes.
-- =====================================================================
create table public.calendario (
  data    date primary key,
  letivo  boolean not null default true,
  feriado boolean not null default false,
  ferias  boolean not null default false
);

-- =====================================================================
-- CARDAPIO: uma linha por data + horário + área, com um prato por slot.
-- Responde à dúvida do MER: cada slot guarda o ID do prato; o "tipo"
-- é um atributo do prato, não do cardápio.
-- =====================================================================
create table public.cardapios (
  data              date not null references public.calendario (data),
  horario           text not null check (horario in ('almoco', 'jantar')),
  area              text not null references public.areas (area) on update cascade,
  prato_principal_1 bigint references public.pratos (id),
  prato_principal_2 bigint references public.pratos (id),
  guarnicao         bigint references public.pratos (id),
  sobremesa_1       bigint references public.pratos (id),
  primary key (data, horario, area)
);

-- Para o histórico usado no treino do previsor (demanda real observada).
create table public.demanda_real (
  data      date not null references public.calendario (data),
  horario   text not null check (horario in ('almoco', 'jantar')),
  area      text not null references public.areas (area) on update cascade,
  refeicoes integer not null check (refeicoes >= 0),
  primary key (data, horario, area)
);

-- =====================================================================
-- SEGURANÇA (Row Level Security)
-- Qualquer usuário logado lê; só administradores escrevem.
-- =====================================================================
alter table public.perfil       enable row level security;
alter table public.pratos       enable row level security;
alter table public.areas        enable row level security;
alter table public.calendario   enable row level security;
alter table public.cardapios    enable row level security;
alter table public.demanda_real enable row level security;

create policy "ver o próprio perfil" on public.perfil
  for select to authenticated using (id = auth.uid() or public.is_admin());
create policy "admin altera perfis" on public.perfil
  for update to authenticated using (public.is_admin());

do $$
declare t text;
begin
  foreach t in array array['pratos', 'areas', 'calendario', 'cardapios', 'demanda_real'] loop
    execute format('create policy "logado lê" on public.%I for select to authenticated using (true)', t);
    execute format('create policy "admin insere" on public.%I for insert to authenticated with check (public.is_admin())', t);
    execute format('create policy "admin atualiza" on public.%I for update to authenticated using (public.is_admin())', t);
    execute format('create policy "admin remove" on public.%I for delete to authenticated using (public.is_admin())', t);
  end loop;
end $$;

-- =====================================================================
-- DADOS INICIAIS (opcional)
-- =====================================================================
insert into public.areas (area, numero_usuarios) values ('Área 1', 0), ('Área 2', 0);

-- Depois de criar sua conta pelo painel (Authentication → Users → Add user),
-- torne-a administradora:
--   update public.perfil set papel = 'administrador' where id = (select id from auth.users where email = 'seu@usp.br');
