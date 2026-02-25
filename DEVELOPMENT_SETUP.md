# Desenvolvimento no Windows (Docker + Local)

## Setup: Postgres em Docker, Backend/Frontend Local

### Pré-requisitos
- Docker Desktop instalado e rodando
- Python 3.11+ (venv)
- Node.js 18+

---

## 1. Iniciar Postgres em Docker (seguro, 127.0.0.1 apenas)

```powershell
# Na raiz do projeto
docker compose up -d postgres

# Verificar se está rodando
docker compose ps
docker compose logs -f postgres
```

Postgres estará **apenas** em `127.0.0.1:5432` (não exposto na rede).
- **Usuário:** ecommerce_user
- **Senha:** ecommerce_secure_password
- **Banco:** ecommerce_life

---

## 2. Iniciar Backend (local em venv)

```powershell
cd backend

# Criar venv (primeira vez)
python -m venv .venv

# Ativar venv
.venv\Scripts\Activate.ps1

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Rodar servidor
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend estará em `http://127.0.0.1:8000/api/v1`

---

## 3. Iniciar Frontend (local em dev)

Em outro terminal PowerShell:

```powershell
cd frontend

# Instalar dependências (primeira vez)
npm install

# Rodar dev server (com hot reload)
npm run dev
```

Frontend estará em `http://localhost:5173`

---

## 4. Acessar Painel Admin

1. Abra http://localhost:5173/admin
2. Cole o token admin: `REDACTED_ADMIN_TOKEN`
3. Clique "Carregar painel"

---

## Checklist de Configuração

- [x] Docker compose define Postgres em 127.0.0.1:5432
- [x] backend/.env com DATABASE_URL apontando para localhost:5432
- [x] backend/requirements.txt usando psycopg[binary] (sem erros de pg_config)
- [x] ALLOWED_ORIGINS configurado para localhost:5173 (frontend)
- [x] AUTH_TOKEN configurado com valor de teste

---

## Troubleshooting

### Postgres não conecta
```powershell
# Verificar logs do container
docker compose logs postgres

# Reiniciar
docker compose down postgres
docker compose up -d postgres
```

### Backend não conecta ao Postgres
- Verificar `.env` tem DATABASE_URL correto
- Verificar Postgres está rodando: `docker compose ps`
- Testar conexão manual:
  ```powershell
  pip install psycopg2
  python -c "import psycopg2; conn = psycopg2.connect('postgresql://ecommerce_user:ecommerce_secure_password@127.0.0.1:5432/ecommerce_life'); print('OK')"
  ```

### Frontend não conecta ao backend
- Verificar se backend está rodando: `http://127.0.0.1:8000/health`
- Verificar `frontend/src/lib/api.js` - `VITE_API_URL` default é `http://localhost:8000/api/v1`
- Se houver erro CORS: verificar `backend/app/main.py` - `allow_origins` incluir `http://localhost:5173`

---

## Parar Tudo

```powershell
# Parar containers Docker
docker compose down

# Parar backend/frontend: Ctrl+C nos terminais
```

---

## Estrutura de Pastas

```
ecommerce_life/
├── backend/
│   ├── .venv/               # Ambiente Python (local)
│   ├── .env                 # Variáveis (DATABASE_URL, AUTH_TOKEN, etc)
│   ├── requirements.txt
│   └── app/
├── frontend/
│   ├── node_modules/        # (local)
│   ├── src/
│   └── package.json
├── docker-compose.yml       # Postgres apenas
└── README.md
```

---

## Próximos Passos

1. **Rodas Alembic** para criar schema do banco:
   ```powershell
   cd backend
   alembic upgrade head
   ```

2. **Testes** (pytest) — rodar testes backend:
   ```powershell
   pytest -v
   ```

3. **Seed inicial** (se tiver) — popular dados fictícios para dev.

