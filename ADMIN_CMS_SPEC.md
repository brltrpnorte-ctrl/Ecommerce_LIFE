# Painel Administrativo CMS - Especificação Completa

## Arquitetura Recomendada

```
┌─────────────────────────────────────────────────────────┐
│                   Admin Central (Next.js)                │
│              Interface Unificada do Painel               │
└────────────────┬────────────────────────┬────────────────┘
                 │                        │
        ┌────────▼────────┐      ┌───────▼────────┐
        │  Saleor/Medusa  │      │  CMS Headless  │
        │   (Commerce)    │      │   (Conteúdo)   │
        │                 │      │                │
        │ • Produtos      │      │ • Banners      │
        │ • Estoque       │      │ • Mídia        │
        │ • Pedidos       │      │ • Textos       │
        │ • Clientes      │      │ • Layout       │
        │ • Cupons        │      │ • Promoções    │
        └─────────────────┘      └────────────────┘
```

## 1. Módulo de Conteúdo (CMS)

### A) Biblioteca de Mídia

**Schema: `Media`**
```typescript
{
  id: string
  type: 'image' | 'video'
  url: string
  thumbnail: string
  filename: string
  size: number
  width?: number
  height?: number
  duration?: number // vídeo
  alt: string
  tags: string[]
  folder: string
  optimized: {
    webp: string
    avif: string
    thumb: string
  }
  cdn_url: string
  uploaded_by: string
  uploaded_at: datetime
  status: 'processing' | 'ready' | 'error'
}
```

**Funcionalidades:**
- Upload drag & drop (múltiplos arquivos)
- Organização por pastas/tags
- Busca e filtros
- Otimização automática (sharp/imagemin)
- Preview e edição básica (crop, resize)
- Integração CDN (Cloudflare/AWS)
- Limites: imagem max 10MB, vídeo max 100MB

### B) Gerenciador de Banners

**Schema: `Banner`**
```typescript
{
  id: string
  name: string // interno
  type: 'image' | 'video'
  media_id: string // FK Media
  poster_id?: string // FK Media (se vídeo)
  title: string
  subtitle: string
  cta_text: string
  cta_link: string
  order: number
  device: 'all' | 'desktop' | 'mobile'
  schedule: {
    start: datetime
    end: datetime
  }
  status: 'draft' | 'published' | 'archived'
  ab_variant?: string
  analytics: {
    views: number
    clicks: number
    ctr: number
  }
}
```

**Interface Admin:**
- Lista com preview, ordem drag & drop
- Editor com preview ao vivo
- Agendamento visual (calendário)
- Duplicar banner
- Estatísticas (views/clicks)

### C) Editor da Home (Page Builder)

**Schema: `PageSection`**
```typescript
{
  id: string
  page: 'home' | 'about' | 'custom'
  section_type: 'hero' | 'hologram' | 'polaroid' | 'featured' | 'categories' | 'brands' | 'custom'
  order: number
  visible: boolean
  config: {
    title?: string
    subtitle?: string
    items?: any[]
    layout?: string
    background?: string
    // props específicas por tipo
  }
  responsive: {
    desktop: object
    tablet: object
    mobile: object
  }
  status: 'draft' | 'published'
}
```

**Tipos de Seção:**
1. **Hero** - Carrossel de banners
2. **Hologram** - Seção 3D do símbolo
3. **Polaroid** - Galeria de histórias
4. **Featured** - Produtos em destaque
5. **Categories** - Grid de categorias
6. **Brands** - Marcas
7. **Custom** - HTML/React customizado

**Interface:**
- Drag & drop para reordenar seções
- Toggle visibilidade
- Preview desktop/tablet/mobile
- Publicar/agendar mudanças

### D) Config Holograma

**Schema: `HologramConfig`**
```typescript
{
  id: string
  media_items: string[] // FK Media[]
  transition_speed: 'slow' | 'medium' | 'fast'
  rotation_speed: number
  glow_color: string
  glow_intensity: 'low' | 'medium' | 'high'
  performance_mode: boolean
  fallback_media_id: string // FK Media
  scanlines: boolean
  noise_intensity: number
  auto_play: boolean
  loop: boolean
}
```

**Interface:**
- Seletor de mídias (múltiplas)
- Sliders para intensidade/velocidade
- Color picker para glow
- Preview 3D ao vivo
- Presets (suave/médio/intenso)

### E) Galeria Polaroid

**Schema: `PolaroidItem`**
```typescript
{
  id: string
  media_id: string // FK Media
  caption: string
  story: string // texto longo
  collection: string
  date: datetime
  order: number
  featured: boolean
  modal_enabled: boolean
  status: 'draft' | 'published'
}
```

**Interface:**
- Grid com preview polaroid
- Editor WYSIWYG para história
- Drag & drop para ordem
- Toggle destaque/modal

### F) Textos Globais

**Schema: `GlobalContent`**
```typescript
{
  key: string // unique
  type: 'text' | 'html' | 'markdown'
  value: string
  category: 'header' | 'footer' | 'legal' | 'faq' | 'contact'
  label: string
  description: string
  updated_at: datetime
  updated_by: string
}
```

**Exemplos de keys:**
- `site.slogan`
- `footer.copyright`
- `legal.terms`
- `legal.privacy`
- `legal.lgpd`
- `contact.whatsapp`
- `contact.instagram`
- `faq.shipping`
- `faq.returns`

## 2. Módulo de Produtos (Commerce)

### Extensões CMS para Categorias

**Schema: `CategoryCMS`**
```typescript
{
  category_id: string // FK do commerce
  banner_id?: string // FK Media
  description: string
  manifesto: string
  cover_media_id?: string // FK Media
  featured_order?: number
  seo: {
    title: string
    description: string
    keywords: string[]
    og_image_id: string
  }
}
```

### Extensões CMS para Produtos

**Schema: `ProductCMS`**
```typescript
{
  product_id: string // FK do commerce
  video_id?: string // FK Media
  lifestyle_images: string[] // FK Media[]
  story: string
  care_instructions: string
  size_guide_id?: string // FK Media
}
```

## 3. Módulo de Promoções

**Schema: `Promotion`**
```typescript
{
  id: string
  name: string
  type: 'discount' | 'free_shipping' | 'bundle' | 'bogo'
  badge_text: string // "-20%", "FRETE GRÁTIS"
  badge_color: string
  rules: {
    min_value?: number
    categories?: string[]
    brands?: string[]
    products?: string[]
  }
  discount: {
    type: 'percentage' | 'fixed'
    value: number
  }
  schedule: {
    start: datetime
    end: datetime
  }
  banner_id?: string // FK Banner
  priority: number
  status: 'active' | 'scheduled' | 'expired'
}
```

## 4. Módulo de Vendas

### Pipeline de Pedidos

**Status Flow:**
```
created → paid → processing → shipped → delivered
                    ↓
                cancelled / returned
```

**Schema: `OrderStatus`**
```typescript
{
  order_id: string
  status: OrderStatusEnum
  tracking_code?: string
  carrier?: string
  estimated_delivery?: datetime
  notes: string
  updated_by: string
  updated_at: datetime
}
```

**Interface:**
- Kanban board (drag status)
- Filtros avançados
- Ações em lote
- Impressão de etiquetas
- Envio automático de e-mail/WhatsApp

### Gestão de Frete

**Schema: `ShippingConfig`**
```typescript
{
  id: string
  carrier: string
  enabled: boolean
  api_key: string
  rules: {
    free_shipping_threshold?: number
    regions: {
      cep_range: string
      multiplier: number
    }[]
  }
  label_template: string
}
```

### Trocas e Devoluções

**Schema: `Return`**
```typescript
{
  id: string
  order_id: string
  items: {
    product_id: string
    quantity: number
    reason: string
  }[]
  status: 'requested' | 'approved' | 'rejected' | 'received' | 'refunded'
  reverse_tracking?: string
  refund_amount: number
  notes: string
  created_at: datetime
}
```

## 5. Módulo Financeiro

**Dashboard Widgets:**
- Faturamento (dia/semana/mês/ano)
- Ticket médio
- Taxa de conversão
- Produtos mais vendidos
- Margem por categoria
- Gateway fees
- Net revenue

**Schema: `FinancialReport`**
```typescript
{
  period: string
  gross_revenue: number
  gateway_fees: number
  shipping_revenue: number
  discounts: number
  net_revenue: number
  orders_count: number
  avg_ticket: number
  conversion_rate: number
  top_products: {
    product_id: string
    quantity: number
    revenue: number
  }[]
}
```

**Exportações:**
- CSV/Excel
- PDF (relatório formatado)
- Integração contábil (API)

## 6. CRM e Marketing

### Segmentação de Clientes

**Schema: `CustomerSegment`**
```typescript
{
  id: string
  name: string
  rules: {
    orders_count?: { min: number, max: number }
    total_spent?: { min: number, max: number }
    last_order?: { days: number }
    categories?: string[]
    tags?: string[]
  }
  auto_update: boolean
  customers_count: number
}
```

**Segmentos Padrão:**
- Novos (primeira compra < 30 dias)
- Recorrentes (2+ pedidos)
- VIP (> R$ 5000 total)
- Inativos (sem compra > 90 dias)

### Carrinho Abandonado

**Schema: `AbandonedCart`**
```typescript
{
  id: string
  customer_id: string
  items: CartItem[]
  total: number
  abandoned_at: datetime
  recovery_sent: boolean
  recovery_sent_at?: datetime
  recovered: boolean
  recovered_at?: datetime
}
```

**Automação:**
- E-mail 1h após abandono
- E-mail 24h com cupom 10%
- WhatsApp 48h (opcional)

### Cupons

**Schema: `Coupon`**
```typescript
{
  code: string
  type: 'percentage' | 'fixed' | 'free_shipping'
  value: number
  min_value?: number
  max_uses?: number
  uses_count: number
  per_customer_limit?: number
  categories?: string[]
  products?: string[]
  valid_from: datetime
  valid_until: datetime
  status: 'active' | 'expired' | 'disabled'
}
```

## 7. Controle e Segurança

### Usuários e Permissões

**Roles:**
- `admin` - Acesso total
- `editor` - Conteúdo e produtos
- `stock` - Estoque e pedidos
- `support` - Pedidos e clientes (read-only)
- `marketing` - Promoções e cupons

**Schema: `AdminUser`**
```typescript
{
  id: string
  email: string
  name: string
  role: RoleEnum
  permissions: string[]
  two_factor_enabled: boolean
  last_login: datetime
  status: 'active' | 'suspended'
}
```

### Auditoria

**Schema: `AuditLog`**
```typescript
{
  id: string
  user_id: string
  action: string // 'create', 'update', 'delete'
  entity: string // 'banner', 'product', 'order'
  entity_id: string
  changes: object // diff
  ip: string
  user_agent: string
  created_at: datetime
}
```

## Implementação Recomendada

### Stack Sugerido

**Opção A: Tudo Integrado**
```
- Payload CMS (Node.js) - CMS + Commerce
- PostgreSQL - Banco
- S3/Cloudflare R2 - Mídia
- Next.js - Admin UI customizado
```

**Opção B: Separado (Recomendado)**
```
- Saleor (Django/GraphQL) - Commerce
- Strapi/Directus - CMS
- PostgreSQL - Banco
- Cloudflare R2 - Mídia + CDN
- Next.js - Admin Central unificado
```

### Priorização (MVP → Full)

**Sprint 1-2 (MVP):**
- ✅ Biblioteca de mídia básica
- ✅ Banners editáveis
- ✅ Textos globais
- ✅ Produtos do commerce

**Sprint 3-4:**
- ✅ Page builder (seções)
- ✅ Config holograma
- ✅ Galeria polaroid
- ✅ Promoções

**Sprint 5-6:**
- ✅ Pipeline de pedidos
- ✅ Frete e rastreio
- ✅ Financeiro básico

**Sprint 7-8:**
- ✅ CRM e segmentação
- ✅ Carrinho abandonado
- ✅ Auditoria e permissões

## Checklist Final

✅ Banners com foto/vídeo editáveis
✅ Biblioteca de mídia completa
✅ Todas seções da home editáveis
✅ Config holograma no admin
✅ Galeria polaroid gerenciável
✅ Textos e frases editáveis
✅ Categorias com CMS
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

**Resultado:** Painel administrativo completo onde 100% do conteúdo é editável sem tocar em código.
