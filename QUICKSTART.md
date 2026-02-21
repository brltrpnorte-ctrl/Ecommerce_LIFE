# 🚀 Início Rápido

## Opção 1: Automático (Recomendado)

```powershell
# Instalar tudo
.\start.bat

# Iniciar backend + frontend
.\run.ps1

# Testar
cd scripts
.\smoke-tests.ps1
```

## Opção 2: Manual

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testes
```bash
cd scripts
.\smoke-tests.ps1
```

## URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (dev only)

## Token Admin

```
REDACTED_ADMIN_TOKEN
```

Use no header: `X-Admin-Token`

## Estrutura

```
Ecommerce_LIFE/
├── backend/          # FastAPI + Python
├── frontend/         # React + Vite
├── scripts/          # Testes
├── start.bat         # Setup automático
├── run.ps1           # Inicia tudo
└── QUICKSTART.md     # Este arquivo
```

## Categorias de Produtos

Camisas, Sneakers, Lupa (óculos), Shorts, Bermudas, Cuecas, Moletom, Conjuntos, Meias

## Marcas

Life Originals, North Pulse, Urban Luck, Rare Thread

## Segurança Implementada

✅ Rate limiting (180/60 req/min)
✅ Headers de segurança (HSTS, CSP, XSS)
✅ Validações de entrada
✅ Token seguro
✅ CORS configurado

## Documentação Completa

- `README.md` - Visão geral
- `SECURITY.md` - Segurança
- `VALIDATION.md` - Validação completa
