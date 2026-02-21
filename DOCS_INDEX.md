# Documentação - Ecommerce LIFE

## 📚 Índice de Documentos

### Início Rápido
- **[README.md](README.md)** - Visão geral e comandos básicos
- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido

### Segurança
- **[SECURITY.md](SECURITY.md)** - Implementações de segurança e checklist OWASP
- **[VALIDATION.md](VALIDATION.md)** - Validação completa do projeto

### Painel Administrativo CMS
- **[ADMIN_CMS_SPEC.md](ADMIN_CMS_SPEC.md)** - Especificação completa do painel CMS
- **[ROADMAP_CMS.md](ROADMAP_CMS.md)** - Roadmap de implementação (10 fases)

### Scripts
- **[start.bat](start.bat)** - Instalação automática de dependências
- **[run.ps1](run.ps1)** - Iniciar backend + frontend simultaneamente
- **[setup.ps1](setup.ps1)** - Setup com geração de token seguro
- **[scripts/smoke-tests.ps1](scripts/smoke-tests.ps1)** - Testes de fumaça da API

## 🎯 Por Onde Começar

### 1. Desenvolvimento Local
```bash
# Instalar tudo
.\start.bat

# Iniciar serviços
.\run.ps1
```

### 2. Entender o Projeto
- Leia [README.md](README.md) para visão geral
- Veja [QUICKSTART.md](QUICKSTART.md) para comandos rápidos
- Consulte [SECURITY.md](SECURITY.md) para entender segurança

### 3. Planejar Próximas Fases
- Leia [ADMIN_CMS_SPEC.md](ADMIN_CMS_SPEC.md) para entender o painel completo
- Consulte [ROADMAP_CMS.md](ROADMAP_CMS.md) para timeline e fases

## 📊 Status do Projeto

### ✅ Implementado (MVP)
- Frontend React + GSAP + ScrollTrigger
- Backend FastAPI + Python
- Catálogo de produtos com filtros
- Carrinho e checkout
- CRM básico
- Segurança (rate limiting, validações, headers)
- Testes automatizados

### 🚧 Em Planejamento (Próximas Fases)
- Painel CMS completo (100% editável)
- Biblioteca de mídia
- Page builder
- Promoções programáveis
- Pipeline de vendas visual
- Financeiro com relatórios
- CRM avançado com automações

### 📅 Timeline Estimado
- **Fase 1-2:** Biblioteca de mídia + banners (4-6 semanas)
- **Fase 3-4:** Commerce + promoções (4-5 semanas)
- **Fase 5-6:** Vendas + financeiro (5 semanas)
- **Fase 7-8:** CRM + segurança (4-5 semanas)
- **Fase 9-10:** Otimização + go-live (3 semanas)
- **Total:** 20-25 semanas (~5-6 meses)

## 🛠️ Stack Tecnológico

### Atual (MVP)
```
Frontend: React 19 + Vite + GSAP
Backend: FastAPI + Python
Database: Mock (em memória)
```

### Recomendado (Produção)
```
Frontend: Next.js 16 + React 19 + TypeScript
Backend Commerce: Saleor (Django + GraphQL)
Backend CMS: Strapi v4 (Node.js)
Database: PostgreSQL
Cache: Redis
Storage: Cloudflare R2 + CDN
Monitoring: Sentry + Vercel Analytics
```

## 🔐 Segurança

Token Admin Atual: `REDACTED_ADMIN_TOKEN`

**Implementações:**
- ✅ Rate limiting (180/60 req/min)
- ✅ Headers de segurança (HSTS, CSP, XSS)
- ✅ Validações de entrada
- ✅ CORS configurado
- ✅ Docs desabilitados em produção

Ver [SECURITY.md](SECURITY.md) para detalhes completos.

## 📞 Suporte

Para dúvidas sobre:
- **Setup inicial:** Consulte [QUICKSTART.md](QUICKSTART.md)
- **Segurança:** Consulte [SECURITY.md](SECURITY.md)
- **Painel CMS:** Consulte [ADMIN_CMS_SPEC.md](ADMIN_CMS_SPEC.md)
- **Roadmap:** Consulte [ROADMAP_CMS.md](ROADMAP_CMS.md)

## 📝 Checklist de Validação

Use [VALIDATION.md](VALIDATION.md) para validar:
- ✅ Código limpo
- ✅ Segurança implementada
- ✅ Funcionalidades core
- ✅ Testes passando
- ✅ Documentação completa
