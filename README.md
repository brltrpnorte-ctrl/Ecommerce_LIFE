# Lifestyle Store

Loja de roupas premium com storytelling visual, animações avançadas e foco em conversão.

## 🚀 Início Rápido

```powershell
# Setup automático
.\start.bat

# Iniciar tudo
.\run.ps1

# Testar
cd scripts
.\smoke-tests.ps1
```

**URLs:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Docs: http://localhost:8000/docs

**Token Admin:** configurar via `backend/.env` (`AUTH_TOKEN`)

## Stack implementada

- Frontend: React + Vite + CSS + GSAP + ScrollTrigger
- Backend: FastAPI (Python)
- Operacao: Docker Compose (frontend + backend)

## Escopo inicial entregue

- Home como pagina de apresentacao da loja com:
  - banner/carrossel
  - secao holografica do trevo de 4 folhas
  - galeria polaroid com modal
- Catalogo de produtos com filtros de marca/categoria/preco/busca
- Pagina de detalhe do produto com variacoes e add no carrinho
- Carrinho e checkout com:
  - calculo de frete (mock estruturado)
  - validacao antifraude basica (mock estruturado)
  - opcoes Pix/cartao/boleto + parcelas
- Paginas de conta, login, rastreamento, wishlist e admin
- Backend com endpoints para catalogo, frete, checkout e dashboard admin
- Seguranca inicial:
  - CORS por ambiente
  - security headers
  - token para endpoint administrativo

## Rodar em desenvolvimento

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

Frontend: `http://localhost:5173`
API: `http://localhost:8000/api/v1`

## Rodar em producao local (Docker)

```bash
copy backend\.env.example backend\.env
docker compose up --build -d
```

Frontend: `http://localhost:3000`
API: `http://localhost:8000/api/v1`

## Token admin para teste

Use o valor de `AUTH_TOKEN` em `backend/.env` na pagina `/admin`.

## Proximas etapas criticas

1. Persistencia real (PostgreSQL + ORM + migracoes).
2. Autenticacao real (JWT + refresh + OAuth Google/Apple).
3. Integracao real de pagamento (Pix/cartao/boleto) e frete.
4. Painel CMS completo para banners/galerias/promocoes.
5. Observabilidade, testes E2E e hardening OWASP para go-live.


## 📋 Roadmap - Painel CMS Completo

### Objetivo
100% do conteúdo editável pelo admin (banners, fotos, vídeos, textos, layout)

### Documentação Completa
- **[ADMIN_CMS_SPEC.md](ADMIN_CMS_SPEC.md)** - Especificação técnica completa
- **[ROADMAP_CMS.md](ROADMAP_CMS.md)** - Timeline e fases de implementação
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - Índice de toda documentação

### Stack Recomendado
- Commerce: Saleor (Django + GraphQL)
- CMS: Strapi v4 (Node.js + PostgreSQL)
- Admin UI: Next.js + shadcn/ui
- Mídia: Cloudflare R2 + CDN

### Timeline: 5-6 meses (10 fases)

**Fase 1-2:** Biblioteca de mídia + banners editáveis (4-6 semanas)
**Fase 3-4:** Commerce + promoções (4-5 semanas)
**Fase 5-6:** Vendas + financeiro (5 semanas)
**Fase 7-8:** CRM + segurança (4-5 semanas)
**Fase 9-10:** Otimização + go-live (3 semanas)

### Funcionalidades do Painel CMS

✅ Biblioteca de mídia (upload, organização, otimização)
✅ Banners com foto/vídeo editáveis
✅ Page builder (drag & drop seções)
✅ Config holograma (mídias, intensidade, cores)
✅ Galeria polaroid gerenciável
✅ Textos globais editáveis
✅ Categorias com extensões CMS
✅ Promoções programáveis
✅ Pipeline de pedidos visual
✅ Gestão de frete e rastreio
✅ Trocas e devoluções
✅ Financeiro com relatórios
✅ CRM e segmentação
✅ Carrinho abandonado
✅ Cupons e descontos
✅ Permissões e auditoria
✅ Exportações (CSV/Excel/PDF)
