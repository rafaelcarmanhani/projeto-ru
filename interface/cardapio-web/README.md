# RU São Carlos · Plataforma de Apoio à Decisão (front-end)

Interface web do TCC: login, previsão de demanda, geração de cardápio,
manutenção da base e retreino do modelo.

**Stack:** React 19 + Vite + TypeScript · Tailwind CSS 4 · React Router 7 · Recharts · Supabase (auth e banco)

## Rodando pela primeira vez

```bash
npm install
npm run dev
```

Abra http://localhost:5173. Sem configurar nada, o app roda em **modo demonstração**:
qualquer e-mail entra, você escolhe se é administrador ou usuário, e os dados são fictícios
(ficam em `src/lib/mock.ts`). Assim dá para desenvolver a interface antes do backend ficar pronto.

## Conectando ao Supabase

1. Crie um projeto em https://supabase.com.
2. Em **SQL Editor**, rode `supabase/schema.sql` (cria as tabelas do MER e as regras de acesso).
3. Em **Authentication → Users → Add user**, crie sua conta e rode no SQL Editor:
   ```sql
   update public.perfil set papel = 'administrador'
   where id = (select id from auth.users where email = 'seu@usp.br');
   ```
4. Copie `.env.example` para `.env.local` e preencha `VITE_SUPABASE_URL` e
   `VITE_SUPABASE_ANON_KEY` (em **Project Settings → API**).

Dá para ligar o Supabase e continuar com a API em modo demonstração, ou o contrário.
Cada parte é independente.

## Conectando à API FastAPI

Preencha `VITE_API_URL` (ex.: `http://localhost:8000`). O front espera estes endpoints:

| Método | Rota | Corpo / resposta |
|---|---|---|
| POST | `/previsao` | `{data_inicio, data_fim, area}` → `[{data, area, horario, demanda_prevista}]` |
| POST | `/cardapio/gerar` | `{data_inicio, data_fim, area, horario}` → `[{data, horario, area, prato_principal_1, prato_principal_2, guarnicao, sobremesa_1}]` (ids dos pratos) |
| GET | `/modelo/status` | → `{ultimo_treino, metricas: {mae, mape}}` |
| POST | `/modelo/retreino` | → `{job_id, status}` (deve responder na hora e treinar em segundo plano) |
| GET | `/modelo/retreino/{job_id}` | → `{job_id, status, progresso, mensagem}` |

Toda chamada envia `Authorization: Bearer <token do Supabase>`. Na FastAPI, valide o token
com o *JWT secret* do projeto (Project Settings → API) e consulte `perfil.papel` para
liberar as rotas de administrador. Lembre de habilitar CORS para a origem do front.

Os tipos de cada resposta estão em `src/types.ts`.

## Estrutura

```
src/
  main.tsx, App.tsx       rotas e provedores
  types.ts                tipos do domínio (espelham o MER)
  auth/                   login (Supabase Auth) e proteção de rotas por papel
  components/             Layout (menu lateral) e componentes de UI
  lib/
    supabase.ts           cliente Supabase
    api.ts                cliente da FastAPI (previsão, cardápio, retreino)
    db.ts                 CRUD das tabelas no Supabase
    mock.ts               dados do modo demonstração
    datas.ts              utilitários de datas
  pages/
    Login, Dashboard, Previsao, GerarCardapio, BaseDados, Modelo
supabase/schema.sql       tabelas, gatilho de perfil e regras RLS
```

## Permissões

| Tela | Usuário | Administrador |
|---|:-:|:-:|
| Início (dashboard) | ✔ | ✔ |
| Previsão de demanda | ✔ | ✔ |
| Gerar cardápio | | ✔ |
| Base de dados | | ✔ |
| Modelo e retreino | | ✔ |

O menu esconde o que o usuário não pode ver, as rotas bloqueiam o acesso direto, e o
Supabase (RLS) recusa escritas de quem não é administrador, mesmo que alguém chame a API à mão.

## Publicação

- Front: Vercel ou Netlify (build `npm run build`, pasta `dist`). Configure as variáveis
  `VITE_*` no painel e uma regra de *rewrite* de todas as rotas para `/index.html`.
- API: Render, Railway ou Fly.io.
