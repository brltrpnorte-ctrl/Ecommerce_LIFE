# 🎛️ Roadmap Painel Administrativo — Ecommerce LIFE

## Visão Geral

Painel administrativo **100% editável** separado em dois mundos:

1. **Commerce** (vendas/estoque/pedidos) → Motor de e-commerce (Saleor/WooCommerce/Native)
2. **Conteúdo** (home/banners/holograma/textos) → CMS Visual (Builder.io/Strapi/Payload)

**Resultado**: Interface unificada em Next.js que puxa dados de ambos.

---

## 1️⃣ Módulo de Conteúdo (CMS)

### 1.1 Biblioteca de Mídia (Media Library)

**O que é:**
Repositório centralizado de imagens, vídeos e assets.

**Funcionalidades:**
- ✅ Upload: JPG, PNG, WebP, AVIF (imagens); MP4, WebM (vídeos)
- ✅ Organização: Pastas/tags (`banners-home`, `holograma`, `polaroids`, etc.)
- ✅ Otimização: Geração automática de thumbnails e múltiplos tamanhos (srcset)
- ✅ CDN: CloudFlare/AWS CloudFront para servir mídia rápido
- ✅ Para vídeos: Poster customizado, compressão, limite de duração

**Stack recomendado:**
- **Backend**: Strapi/Payload/Directus (já vem com media library)
- **Alternativa leve**: Supabase Storage + Next.js API

**Banco de dados:**
```sql
CREATE TABLE media (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  type ENUM('image', 'video'),
  extension VARCHAR(10),
  size INT,
  url VARCHAR(500),
  thumbnail_url VARCHAR(500),
  cdn_url VARCHAR(500),
  tags TEXT[],
  folder VARCHAR(255),
  uploaded_at TIMESTAMP,
  updated_at TIMESTAMP,
  created_by UUID
);
```

---

### 1.2 Gerenciador de Banners (Hero/Carrossel)

**O que é:**
Banners editáveis para home, campanhas, promoções.

**Objeto Banner:**
```json
{
  "id": "uuid",
  "name": "Banner Carnaval 2026",
  "type": "image | video",
  "media_id": "uuid (ref Media)",
  "poster_id": "uuid (ref Media, optional for video)",
  "title": "Carnaval é aqui",
  "subtitle": "Pinte-se de cores",
  "cta_text": "Comprar agora",
  "cta_link": "/collections/carnaval",
  "order": 1,
  "is_active": true,
  "publish_status": "draft | published",
  "scheduled_start": "2026-02-01T00:00:00Z",
  "scheduled_end": "2026-03-15T23:59:59Z",
  "segmentation": {
    "desktop": true,
    "mobile": true,
    "tablet": true
  },
  "ab_variant": "A | B | null",
  "created_at": "2026-02-21T10:00:00Z",
  "updated_at": "2026-02-21T10:00:00Z"
}
```

**Banco de dados:**
```sql
CREATE TABLE banners (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type ENUM('image', 'video') DEFAULT 'image',
  media_id UUID NOT NULL REFERENCES media(id),
  poster_id UUID REFERENCES media(id),
  title VARCHAR(255),
  subtitle VARCHAR(255),
  cta_text VARCHAR(100),
  cta_link VARCHAR(500),
  order_position INT DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  publish_status ENUM('draft', 'published') DEFAULT 'draft',
  scheduled_start TIMESTAMP,
  scheduled_end TIMESTAMP,
  segmentation JSONB DEFAULT '{"desktop": true, "mobile": true}',
  ab_variant VARCHAR(1),
  created_by UUID,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**API Endpoints:**
```
POST   /api/banners              (criar)
GET    /api/banners              (listar)
GET    /api/banners/:id          (detalhar)
PUT    /api/banners/:id          (atualizar)
DELETE /api/banners/:id          (deletar)
GET    /api/banners/active       (listar publicados)
```

---

### 1.3 Editor da Home (Page Builder)

**O que é:**
Interface drag-and-drop para editar seções da home sem código.

**Seções padrão:**
1. **Hero** (banner principal)
2. **Holograma Trevo** (seção 3D customizável)
3. **História/Polaroids** (galeria)
4. **Destaques** (featured products)
5. **Coleções** (categorias em destaque)
6. **Marcas/Patrocinadores** (logos)
7. **Newsletter** (CTA)

**Objeto Seção:**
```json
{
  "id": "uuid",
  "type": "hero | holograma | gallery | featured | collections | brands | newsletter",
  "title": "Título da seção",
  "visible": true,
  "order": 1,
  "props": {
    // Varia por tipo
    "banners": ["uuid1", "uuid2"],  // para hero
    "items_count": 6,               // para featured
    "background_color": "#000",
    "text_color": "#fff"
  },
  "created_at": "2026-02-21T10:00:00Z"
}
```

**Banco de dados:**
```sql
CREATE TABLE page_sections (
  id UUID PRIMARY KEY,
  page_type ENUM('home', 'collection', 'product') DEFAULT 'home',
  section_type VARCHAR(100) NOT NULL,
  title VARCHAR(255),
  is_visible BOOLEAN DEFAULT true,
  order_position INT DEFAULT 0,
  props JSONB NOT NULL,
  created_by UUID,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Stack recomendado:**
- **Builder.io** (drag-and-drop com teus componentes React)
- **Alternativa**: Strapi com custom plugin de Page Builder
- **Leve**: Notion/AirTable como CMS (puxa via API)

---

### 1.4 Seção Holograma (Trevo) Controlável

**O que é:**
Configuração completa do holograma 3D sem código.

**Config Holograma:**
```json
{
  "id": "holo-config-001",
  "enabled": true,
  "media_list": [
    { "media_id": "uuid", "duration": 5 }
  ],
  "intensity": "suave | médio | forte",
  "rotation_speed": 1.5,
  "glow_color": "#00FF00",
  "glow_intensity": 0.8,
  "performance_mode": {
    "mobile": true,
    "max_fps": 30
  },
  "fallback_media_id": "uuid (imagem 2D)",
  "updated_at": "2026-02-21T10:00:00Z"
}
```

**Banco de dados:**
```sql
CREATE TABLE holograma_config (
  id VARCHAR(50) PRIMARY KEY,
  enabled BOOLEAN DEFAULT true,
  intensity ENUM('suave', 'médio', 'forte') DEFAULT 'médio',
  rotation_speed DECIMAL(3,2) DEFAULT 1.5,
  glow_color VARCHAR(7) DEFAULT '#00FF00',
  glow_intensity DECIMAL(2,2) DEFAULT 0.8,
  performance_mode JSONB DEFAULT '{"mobile": true, "max_fps": 30}',
  fallback_media_id UUID REFERENCES media(id),
  created_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE holograma_media (
  id UUID PRIMARY KEY,
  config_id VARCHAR(50) REFERENCES holograma_config(id),
  media_id UUID NOT NULL REFERENCES media(id),
  duration_seconds INT DEFAULT 5,
  order_position INT DEFAULT 0
);
```

**Frontend (React Component):**
```jsx
// Busca config do CMS e aplica em HologramProjector.tsx
const [holoConfig, setHoloConfig] = useState(null);

useEffect(() => {
  fetch('/api/holograma/config')
    .then(r => r.json())
    .then(data => setHoloConfig(data));
}, []);

return (
  <HologramProjector
    mediaList={holoConfig?.media_list}
    intensity={holoConfig?.intensity}
    rotationSpeed={holoConfig?.rotation_speed}
    glowColor={holoConfig?.glow_color}
  />
);
```

---

### 1.5 Galeria História (Polaroid) com Modais

**Objeto Polaroid:**
```json
{
  "id": "uuid",
  "media_id": "uuid (foto ou vídeo)",
  "caption": "Frase curta",
  "story": "Texto da história completa",
  "collection": "2026-carnaval",
  "date": "2026-02-21T10:00:00Z",
  "order": 1,
  "is_featured": false,
  "show_modal": true,
  "created_at": "2026-02-21T10:00:00Z"
}
```

**Banco de dados:**
```sql
CREATE TABLE polaroid_items (
  id UUID PRIMARY KEY,
  media_id UUID NOT NULL REFERENCES media(id),
  caption VARCHAR(255),
  story TEXT,
  collection VARCHAR(100),
  date TIMESTAMP,
  order_position INT DEFAULT 0,
  is_featured BOOLEAN DEFAULT false,
  show_modal BOOLEAN DEFAULT true,
  created_by UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**API:**
```
GET  /api/polaroids              (todas)
GET  /api/polaroids?featured=true
GET  /api/polaroids/:id          (detalhar com modal)
POST /api/polaroids              (criar)
PUT  /api/polaroids/:id          (editar)
```

---

### 1.6 Conteúdo Global (Textos Fixos)

**Objeto ContentGlobal:**
```json
{
  "slogan": "Trevo sorte, com arte e cor",
  "tagline": "Moda que conta histórias",
  "footer": {
    "about": "Somos uma marca de moda...",
    "contact_email": "contato@trevosorte.com",
    "whatsapp": "+55 11 99999-9999",
    "instagram": "@trevorte",
    "tiktok": "@trevorte"
  },
  "legal": {
    "terms": "Termos de Serviço...",
    "privacy": "Política de Privacidade...",
    "lgpd": "Aviso de LGPD...",
    "exchanges": "Política de Trocas..."
  },
  "faq": [
    {
      "question": "Como funciona troca?",
      "answer": "..."
    }
  ],
  "operating_hours": "Seg-Sex 9h-18h",
  "updated_at": "2026-02-21T10:00:00Z"
}
```

**Banco de dados:**
```sql
CREATE TABLE content_global (
  key VARCHAR(100) PRIMARY KEY,
  value JSONB NOT NULL,
  description TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Inserir valores padrão
INSERT INTO content_global VALUES
  ('slogan', '{"text": "..."}', 'Slogan principal'),
  ('footer_about', '{"text": "..."}', 'Texto do rodapé'),
  ('legal_terms', '{"text": "..."}', 'Termos de serviço'),
  ('faq', '[{"question": "...", "answer": "..."}]', 'FAQ'),
  ('contact_whatsapp', '{"number": "+55..."}', 'WhatsApp');
```

**API (super simples):**
```
GET  /api/content/:key           (buscar valor)
PUT  /api/content/:key           (atualizar)
GET  /api/content/all            (tudo)
```

---

## 2️⃣ Módulo de Produtos / Catálogo (Commerce)

### 2.1 Base: Integração com Saleor/WooCommerce

**Recomendação:**
- Use **Saleor GraphQL API** para produtos, categorias, atributos
- **Seu CMS** para "extras" de apresentação

**O Saleor oferece:**
- Produtos com variações (tamanho, cor, etc.)
- Categorias/Collections
- Marcas (via atributo)
- Imagens de produto
- Estoque por variação

**Você adiciona no seu CMS:**
- Banner de categoria (mídia)
- Manifesto/descrição da coleção
- SEO por produto
- Ordem de exibição na home

**Banco de dados (seus extras):**
```sql
CREATE TABLE product_extras (
  id UUID PRIMARY KEY,
  saleor_product_id VARCHAR(100) NOT NULL UNIQUE,
  category_banner_media_id UUID REFERENCES media(id),
  collection_manifest TEXT,
  seo_title VARCHAR(255),
  seo_description VARCHAR(500),
  seo_slug VARCHAR(255) UNIQUE,
  og_image_id UUID REFERENCES media(id),
  featured_on_home BOOLEAN DEFAULT false,
  home_order INT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE brands (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  logo_media_id UUID REFERENCES media(id),
  description TEXT,
  is_active BOOLEAN DEFAULT true
);

CREATE TABLE categories (
  id UUID PRIMARY KEY,
  saleor_category_id VARCHAR(100) NOT NULL,
  name VARCHAR(255),
  banner_media_id UUID REFERENCES media(id),
  description TEXT,
  order_position INT DEFAULT 0,
  is_active BOOLEAN DEFAULT true
);
```

---

## 3️⃣ Módulo de Vendas / Pedidos / Entrega

### 3.1 Pipeline de Pedidos (Status)

**Estados do pedido:**
```
CRIADO → PAGO → SEPARANDO → ENVIADO → ENTREGUE
         ↓
      CANCELADO / DEVOLVIDO / REPROVADO
```

**Banco de dados:**
```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY,
  customer_id UUID,
  status ENUM('created', 'paid', 'packing', 'shipped', 'delivered', 'cancelled', 'returned') DEFAULT 'created',
  total_price DECIMAL(10,2),
  shipping_price DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);

CREATE TABLE order_items (
  id UUID PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id),
  product_id VARCHAR(100),
  variant_id VARCHAR(100),
  quantity INT,
  unit_price DECIMAL(10,2),
  subtotal DECIMAL(10,2)
);

CREATE TABLE order_status_log (
  id UUID PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id),
  from_status VARCHAR(50),
  to_status VARCHAR(50),
  changed_by UUID,
  note TEXT,
  changed_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 Frete / Envio

**Integração com Correios / Melhor Envio:**
```sql
CREATE TABLE shipments (
  id UUID PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id),
  carrier ENUM('correios', 'sedex', 'melhor-envio', 'custom') DEFAULT 'correios',
  tracking_code VARCHAR(50) UNIQUE,
  status ENUM('waiting', 'posted', 'in_transit', 'delivered', 'returned') DEFAULT 'waiting',
  estimated_delivery DATE,
  shipped_at TIMESTAMP,
  delivered_at TIMESTAMP,
  label_url VARCHAR(500)
);
```

**API (seu backend):**
```
POST /api/shipments/:orderId/calculate    (simular preço)
POST /api/shipments/:orderId/generate     (gerar etiqueta)
GET  /api/shipments/:orderId/track        (rastrear)
POST /api/shipments/:orderId/notify       (enviar e-mail/WhatsApp)
```

### 3.3 Trocas e Devoluções (RMA)

```sql
CREATE TABLE returns (
  id UUID PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES orders(id),
  reason VARCHAR(100),
  status ENUM('requested', 'approved', 'rejected', 'refunded') DEFAULT 'requested',
  return_label_url VARCHAR(500),
  refund_amount DECIMAL(10,2),
  requested_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);
```

---

## 4️⃣ Faturamento / Financeiro

**Dashboard Financeiro:**
```sql
CREATE TABLE financial_summary (
  date DATE PRIMARY KEY,
  total_revenue DECIMAL(15,2),
  payment_method_breakdown JSONB,
  gateway_fees DECIMAL(10,2),
  net_revenue DECIMAL(15,2),
  items_sold INT,
  average_order_value DECIMAL(10,2)
);
```

**Queries úteis:**
```sql
-- Faturamento por período
SELECT DATE(created_at) as date, SUM(total_price) as revenue
FROM orders
WHERE status = 'paid'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Produtos mais vendidos
SELECT p.name, COUNT(oi.id) as qty, SUM(oi.subtotal) as revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.id
ORDER BY qty DESC
LIMIT 10;

-- Taxa de conversão
SELECT 
  COUNT(DISTINCT customer_id) as customers,
  COUNT(*) as orders,
  ROUND(100.0 * COUNT(*) / COUNT(DISTINCT customer_id), 2) as conversion_rate
FROM orders;
```

---

## 5️⃣ CRM e Marketing

```sql
CREATE TABLE customers (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(20),
  name VARCHAR(255),
  segment ENUM('new', 'recurring', 'vip', 'inactive') DEFAULT 'new',
  total_spent DECIMAL(15,2) DEFAULT 0,
  order_count INT DEFAULT 0,
  last_order_at TIMESTAMP,
  created_at TIMESTAMP
);

CREATE TABLE abandoned_carts (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES customers(id),
  items JSONB,
  total DECIMAL(10,2),
  abandoned_at TIMESTAMP,
  reminder_sent_at TIMESTAMP
);

CREATE TABLE coupons (
  id UUID PRIMARY KEY,
  code VARCHAR(50) UNIQUE NOT NULL,
  type ENUM('percentage', 'fixed') DEFAULT 'percentage',
  value DECIMAL(5,2),
  min_purchase DECIMAL(10,2),
  max_uses INT,
  current_uses INT DEFAULT 0,
  valid_from TIMESTAMP,
  valid_until TIMESTAMP,
  categories_allowed UUID[],
  is_active BOOLEAN DEFAULT true
);

CREATE TABLE promotions (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  type ENUM('banner', 'seal', 'discount') DEFAULT 'banner',
  media_id UUID REFERENCES media(id),
  text "-20%", "Frete grátis", etc.
  valid_from TIMESTAMP,
  valid_until TIMESTAMP,
  is_active BOOLEAN DEFAULT true
);
```

---

## 6️⃣ Controle e Segurança do Painel

```sql
CREATE TABLE admin_users (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  role ENUM('super_admin', 'admin', 'editor', 'warehouse', 'support') DEFAULT 'editor',
  permissions TEXT[],
  two_factor_enabled BOOLEAN DEFAULT false,
  last_login TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP
);

CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES admin_users(id),
  action VARCHAR(100),
  resource_type VARCHAR(50),
  resource_id VARCHAR(100),
  changes JSONB,
  ip_address VARCHAR(45),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE approvals (
  id UUID PRIMARY KEY,
  resource_type VARCHAR(50),
  resource_id VARCHAR(100),
  requester_id UUID REFERENCES admin_users(id),
  action VARCHAR(100),
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  approved_by UUID REFERENCES admin_users(id),
  requested_at TIMESTAMP DEFAULT NOW(),
  reviewed_at TIMESTAMP
);
```

---

## 7️⃣ Stack Recomendado (Opção A — Tudo Integrado)

| Componente | Solução | Razão |
|-----------|---------|-------|
| **Frontend** | Next.js 15 (seu frontend atual) | React, SSR, API Routes |
| **Admin CMS** | Strapi headless CMS | Bibliotec de mídia, editor visual, webhooks |
| **Commerce Engine** | Saleor (GraphQL) | Produtos, pedidos, estoque, ERP-ready |
| **CDN Mídia** | Cloudflare / AWS CloudFront | Otimização, cache, performance |
| **Banco de dados** | PostgreSQL | Para seus extras (CMS local) |
| **Cache / Sessions** | Redis | Cart, sessions, cache de queries |
| **Fila de jobs** | Bull/RabbitMQ | Envio de e-mails, notificações async |
| **Notificações** | Twilio (SMS/WhatsApp) | Tracking, carrinho abandonado |
| **Relatórios** | Charts.js / Recharts | Dashboards no painel |
| **Search** | Elasticsearch / Algolia | Busca rápida de produtos |
| **Auth** | NextAuth.js + JWT | Autenticação segura do painel |

---

## 8️⃣ Fase de Implementação

### Fase 1 (MVP - 2-3 semanas)
- [ ] Biblioteca de Mídia (upload básico)
- [ ] Gerenciador de Banners
- [ ] Conteúdo Global (textos fixos)
- [ ] Admin users + autenticação

### Fase 2 (4-6 semanas)
- [ ] Editor da Home (Page Builder simples)
- [ ] Integração Saleor (produtos/categorias)
- [ ] Gerenciador de Pedidos (básico)

### Fase 3 (6-8 semanas)
- [ ] Holograma Customizável
- [ ] Galeria Polaroids
- [ ] Faturamento / Relatórios

### Fase 4 (8-10 semanas)
- [ ] CRM / Clientes
- [ ] Cupons e Promoções
- [ ] Automação (carrinho abandonado)
- [ ] Devoluções / RMA

---

## 9️⃣ Como Unificar Tudo (Admin Central em Next.js)

Você cria um `app/admin` no seu Next.js:

```
frontend/
├── app/
│   ├── (storefront)/ → público
│   └── admin/        → painel (protegido)
│       ├── layout.tsx
│       ├── dashboard/
│       ├── media/
│       ├── banners/
│       ├── products/
│       ├── orders/
│       ├── financial/
│       └── users/
└── lib/
    ├── saleor.ts    → client GraphQL Saleor
    ├── strapi.ts    → client Strapi CMS
    └── auth.ts      → NextAuth config
```

**Exemplo de rota unificada:**
```typescript
// app/admin/products/page.tsx
export default async function AdminProducts() {
  // Busca Saleor
  const products = await fetchSaleorProducts();
  
  // Busca extras seu CMS
  const extras = await fetchProductExtras();
  
  // Merge
  const enriched = products.map(p => ({
    ...p,
    ...extras.find(e => e.saleor_product_id === p.id)
  }));

  return <ProductsTable data={enriched} />;
}
```

---

## 🔟 Checklist Final (100% Editável)

✅ **Banners com foto e vídeo** → Media Library + Banners module
✅ **Imagens/vídeos trocáveis** → Media Library com CDN
✅ **Categorias, marcas, produtos editáveis** → Saleor + Extras CMS
✅ **Promoções e cupons editáveis** → Promotions + Coupons module
✅ **Frases, textos, seções, layout da Home editáveis** → Content Global + Page Builder
✅ **Gestão completa de vendas/pedidos/frete** → Orders + Shipments module
✅ **Relatórios e faturamento com exportação** → Financial dashboard + CSV export
✅ **Controle de usuários, permissões, auditoria** → Admin Users + Audit Log

---

## 📞 Próximos Passos

1. **Escolher stack**: Strapi ou builder.io para CMS?
2. **Integração Saleor**: Já tem conta no Saleor ou começa zero?
3. **Banco de dados**: PostgreSQL local ou Supabase?
4. **CDN**: Usar Cloudflare, AWS CloudFront ou bunny.net?
5. **Timeline**: Kits realista?

**Quer que eu comece codando o boilerplate do painel?** 🚀
