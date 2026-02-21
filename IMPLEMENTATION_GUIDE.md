# 🔐 Implementação do CMS com Segurança — Guia de Integração

## Status de Implementação

✅ **Completado:**
- Modelos SQLAlchemy para todas as entidades (Media, Banner, PageSection, HologramaConfig, etc.)
- Schemas Pydantic para validação de entrada
- Middleware de segurança (JWT, RBAC, Rate Limiting, Auditoria)
- Rotas de API estruturadas com docstrings

⏳ **Próximos Passos:**
1. Integrar no FastAPI `main.py`
2. Implementar as funções CRUD (database operations)
3. Testes unitários e de integração
4. Deploy com segurança (HTTPS, secrets, etc.)

---

## 🏗️ Arquitetura de Segurança

### Camadas de Segurança

```
┌──────────────────────────────────────┐
│     Cliente (Frontend / Admin)        │
└────────────────┬─────────────────────┘
                 │ HTTPS + JWT Token
┌────────────────▼─────────────────────┐
│   Rate Limiting & CORS Check          │
│   (middleware global)                 │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│   Authentication (JWT Decode)         │
│   (get_current_user dependency)       │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│   Authorization (RBAC + Permissions)  │
│   (@require_permission decorator)     │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│   Input Validation (Pydantic)         │
│   Type checking + business rules      │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│   Database Operations                 │
│   (ORM com prepared statements)       │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│   Audit Logging                       │
│   (quem fez o quê, quando, de onde)   │
└──────────────────────────────────────┘
```

---

## 📦 Estrutura de Arquivos Criados

```
backend/
├── app/
│   ├── models/
│   │   ├── cms_models.py          ✅ SQLAlchemy models
│   │   └── cms_schemas.py         ✅ Pydantic schemas
│   ├── api/
│   │   └── cms_routes.py          ✅ Rotas da API
│   └── core/
│       └── cms_security.py        ✅ Middleware de segurança
├── main.py                        📝 Precisa integrar
├── requirements.txt               📝 Adicionar deps
└── logs/
    └── cms_security.log          📝 Será criado em runtime
```

---

## 🔧 Passo 1: Integrar no FastAPI

### Adicionar ao `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Importar router CMS
from app.api.cms_routes import cms_router

# Importar segurança
from app.core.cms_security import setup_security_logging

# Criar app
app = FastAPI(
    title="Ecommerce LIFE API",
    description="Backend com CMS seguro",
    version="1.0.0"
)

# ========================
# MIDDLEWARES DE SEGURANÇA
# ========================

# 1. Hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.trevorte.com"]
)

# 2. CORS (restritivo em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # dev frontend
        "https://trevorte.com",       # produção
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Logging de segurança
security_logger = setup_security_logging()

# ========================
# REGISTRAR ROTAS CMS
# ========================

app.include_router(cms_router)

# Exemplo: outras rotas existentes
# app.include_router(commerce_routes, prefix="/api")
# app.include_router(user_routes, prefix="/api")

# ========================
# ROTAS DE HEALTH
# ========================

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
```

---

## 📋 Passo 2: Adicionar Dependências

### Atualizar `backend/requirements.txt`

```
# JWT e Segurança
PyJWT==2.8.1
bcrypt==4.1.1
cryptography==41.0.7
python-multipart==0.0.6

# Validação
pydantic==2.5.0
pydantic[email]==2.5.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9  # PostgreSQL driver

# FastAPI + ASGI
fastapi==0.104.1
uvicorn==0.24.0
python-jose==3.3.0

# Rate Limiting (opcional, recomendado)
slowapi==0.1.9

# Armazenamento de mídia (optional, para integração com S3/cloud)
boto3==1.34.14
python-multipart==0.0.6

# Utilitários
python-dotenv==1.0.0
loguru==0.7.2
```

### Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

---

## 🗄️ Passo 3: Configurar Banco de Dados

### Criar tabelas CMS

```python
# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.cms_models import Base

# Conexão (usar Supabase ou PostgreSQL local)
DATABASE_URL = "postgresql://user:password@localhost/ecommerce_life"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # True para debug
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def init_db():
    """Criar todas as tabelas"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency para pegar sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Na inicialização da app:
# init_db()
```

### Exemplo: RodupySQL Alembic para migrations

```bash
# Inicializar alembic
alembic init migrations

# Criar migração automática
alembic revision --autogenerate -m "Add CMS models"

# Aplicar migração
alembic upgrade head
```

---

## 🔑 Passo 4: Configurar Variáveis de Ambiente

### Criar `.env` no backend

```bash
# Banco de dados
DATABASE_URL=postgresql://user:password@localhost/ecommerce_life

# JWT e Segurança
CMS_SECRET_KEY=sua-chave-secreta-super-longa-aqui-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Armazenamento de mídia
CDN_URL=https://cdn.trevorte.com
UPLOAD_FOLDER=/tmp/uploads

# Email (para notificações de segurança)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Carregar no main.py

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("CMS_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## 🧪 Passo 5: Implementar Funções CRUD

### Exemplo: Criar função para listar banners

```python
# backend/app/services/banner_service.py
from sqlalchemy.orm import Session
from app.models.cms_models import Banner
from app.models.cms_schemas import BannerResponse
from typing import List, Optional

class BannerService:
    
    @staticmethod
    def get_banners(
        db: Session,
        page: int = 1,
        per_page: int = 20,
        publish_status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[BannerResponse], int]:
        """Listar banners com paginação e filtros"""
        
        query = db.query(Banner)
        
        # Filtros
        if publish_status:
            query = query.filter(Banner.publish_status == publish_status)
        if is_active is not None:
            query = query.filter(Banner.is_active == is_active)
        
        # Contar total
        total = query.count()
        
        # Paginação
        banners = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return [BannerResponse.model_validate(b) for b in banners], total
    
    @staticmethod
    def create_banner(db: Session, banner_data: BannerCreate, user_id: str) -> BannerResponse:
        """Criar novo banner"""
        
        banner = Banner(
            name=banner_data.name,
            type=banner_data.type,
            media_id=banner_data.media_id,
            title=banner_data.title,
            subtitle=banner_data.subtitle,
            cta_text=banner_data.cta_text,
            cta_link=banner_data.cta_link,
            order_position=banner_data.order_position,
            device_type=banner_data.device_type,
            scheduled_start=banner_data.scheduled_start,
            scheduled_end=banner_data.scheduled_end,
            publish_status=banner_data.publish_status,
            created_by=user_id,
        )
        
        db.add(banner)
        db.commit()
        db.refresh(banner)
        
        return BannerResponse.model_validate(banner)
    
    @staticmethod
    def update_banner(db: Session, banner_id: str, banner_data: BannerUpdate) -> BannerResponse:
        """Atualizar banner"""
        
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            raise ValueError(f"Banner {banner_id} não encontrado")
        
        # Atualizar campos
        for field, value in banner_data.model_dump(exclude_unset=True).items():
            setattr(banner, field, value)
        
        banner.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(banner)
        
        return BannerResponse.model_validate(banner)
```

### Integrar na rota

```python
# backend/app/api/cms_routes.py (atualizar)
from app.services.banner_service import BannerService
from app.database import get_db

@cms_router.get("/banners")
async def list_banners(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    publish_status: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Listar banners com filtros"""
    
    banners, total = BannerService.get_banners(
        db, page, per_page, publish_status, is_active
    )
    
    return {
        "data": banners,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }
```

---

## 🧪 Passo 6: Testar as Rotas

### 1. Rodar o servidor

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Acessar Swagger UI

```
http://localhost:8000/docs
```

### 3. Testar login

```bash
curl -X POST "http://localhost:8000/api/admin/cms/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!"
  }'
```

Resposta esperada:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-here",
    "name": "Admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### 4. Testar rota protegida

```bash
# Usar token obtido acima
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X GET "http://localhost:8000/api/admin/cms/banners" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🛡️ Passo 7: Deploy com Segurança

### Checklist pre-production

- [ ] Mudar `SECRET_KEY` para valor aleatório forte (32+ chars)
- [ ] Habilitar HTTPS/TLS
- [ ] Configurar CORS restritivo (apenas domínios permitidos)
- [ ] Usar variáveis de ambiente para secrets
- [ ] Implementar CSRF protection nos forms
- [ ] Rate limiting em produção
- [ ] Logging de auditoria persistente
- [ ] Backups automáticos do banco
- [ ] Monitoramento de intrusões (opcional)
- [ ] 2FA para admins (implementado, precisa testar)

### Docker Seguro

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY ./app ./app
COPY ./main.py .

# Rodar como user não-root
RUN useradd -m appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Rodar app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 Próximas Implementações (Fase 2)

- [ ] Upload de mídia com otimização automática
- [ ] Integração com CDN (CloudFlare / AWS CloudFront)
- [ ] Page Builder visual (drag & drop)
- [ ] Integração com Saleor (produtos/estoque)
- [ ] Dashboard financeiro (vendas, conversão, etc.)
- [ ] CRM (clientes, segmentação)
- [ ] Automação (carrinho abandonado, etc.)
- [ ] Analytics avançado (Google Analytics 4)

---

## 📞 Suporte e Referências

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **JWT.io**: https://jwt.io/
- **OWASP Cheat Sheet**: https://cheatsheetseries.owasp.org/

---

## ✅ Checklist de Conclusão

- [ ] Models criados e testados
- [ ] Schemas Pydantic validando entrada
- [ ] Middleware de segurança implementado
- [ ] Rotas CMS estruturadas
- [ ] Integração no main.py concluída
- [ ] Banco de dados configurado
- [ ] Funções CRUD implementadas
- [ ] Testes unitários passando
- [ ] Deploy seguro realizado
- [ ] Documentação atualizada

---

Próximo passo: **Implementar as funções CRUD** (database operations) para cada module.
