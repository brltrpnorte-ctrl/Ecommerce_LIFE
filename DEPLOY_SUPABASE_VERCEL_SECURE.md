# Deploy Seguro: Supabase + Vercel + Docker (Local)

## Regras de segurança (obrigatórias)

- Nunca comitar credenciais (`.env`, chaves, connection strings com senha).
- Nunca usar `VITE_` para segredos (frontend torna isso público).
- `SUPABASE_SERVICE_ROLE_KEY` é somente backend.
- Runtime serverless (Vercel) usa pooler (`:6543`); migrations usam conexão direta (`:5432`).
- Se qualquer segredo foi colado em chat, issue ou commit, rotacione antes do deploy.

## 1) Desenvolvimento local seguro (Windows) com Docker Postgres

1. Defina uma senha local forte em uma variável de ambiente (PowerShell):
   `setx POSTGRES_PASSWORD "SUA_SENHA_FORTE_LOCAL"`
2. Reinicie o terminal.
3. Suba o banco local (porta exposta apenas em `127.0.0.1`):
   `docker compose -f docker-compose.postgres-local.yml up -d`
4. Verifique se está saudável:
   `docker compose -f docker-compose.postgres-local.yml ps`
5. Configure `backend/.env` usando `DATABASE_URL` local.

## 2) Supabase (produção) - chaves e URLs

1. No painel do Supabase:
   - `Settings > API`: copie `Project URL`, `anon/publishable key`, `service_role key`.
   - `Connect > Connection string`: copie:
     - `Direct connection` (`:5432`) para migrations
     - `Transaction pooler` (`:6543`) para runtime Vercel
2. `Database Settings`: habilite `SSL enforcement`.
3. Se `Network Restrictions / allow_list` estiver ativo, libere:
   - IP(s) de saida do backend (Vercel/host)
   - seu IP atual apenas para tarefas administrativas/migracao (temporariamente, se necessario)
4. Se o host direto `db.<ref>.supabase.co:5432` falhar no Windows por IPv6, use `Session Pooler` para executar a migracao a partir da sua maquina local (ou execute a migracao em CI/host com IPv6).
5. Execute os scripts SQL:
   - `backend/sql/supabase_roles_setup.sql`
   - `backend/sql/supabase_default_privileges.sql` (como `app_owner`)
   - `backend/sql/supabase_verify.sql`
6. Migre os dados atuais do SQLite para o Supabase (usa `DATABASE_URL_MIGRATIONS`):
   - Dry run: `python backend/scripts/migrate_sqlite_to_postgres.py --dry-run`
   - Executar: `python backend/scripts/migrate_sqlite_to_postgres.py --yes`

## 3) Vercel (2 projetos recomendados)

### Frontend (pasta `frontend`)

- Root Directory: `frontend`
- `frontend/vercel.json` ja inclui rewrite SPA para rotas (`/admin`, `/promocoes`, etc.)
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variables:
  - `VITE_API_URL`
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`

### Backend (pasta `backend`)

- Use `backend/vercel.json` e `backend/api/index.py`
- Environment Variables:
  - `ENVIRONMENT=production`
  - `ALLOWED_ORIGINS=https://SEU_FRONTEND.vercel.app`
  - `ALLOWED_ORIGIN_REGEX=https://.*\\.vercel\\.app` (opcional para previews)
  - `ALLOWED_HOSTS=localhost,127.0.0.1,SEU_BACKEND.vercel.app`
  - `AUTH_TOKEN`
  - `DATABASE_URL_RUNTIME` (pooler `:6543`)
  - `DATABASE_URL_MIGRATIONS` (direct `:5432`, se usar migrations fora da Vercel)
  - `SUPABASE_URL` (se backend usar APIs Supabase)
  - `SUPABASE_SERVICE_ROLE_KEY` (somente backend)

## 4) Antes do deploy (checklist)

- `.env` local existe e nao esta versionado.
- Use `frontend/.env.vercel.example` e `backend/.env.vercel.example` como base para cadastro manual na Vercel.
- Backend agora suporta Postgres/Supabase via `DATABASE_URL_RUNTIME` (runtime) e `DATABASE_URL_MIGRATIONS` (migracao/admin).
- Nenhum segredo em `README`, docs ou scripts.
- Frontend usa somente chaves publicas (`VITE_*`).
- Backend usa segredos fora de `VITE_*`.
- Credenciais rotacionadas se foram expostas anteriormente.
