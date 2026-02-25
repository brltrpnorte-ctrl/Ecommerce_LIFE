from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


PIPELINE_STAGE_LITERAL = Literal['lead', 'qualificado', 'proposta', 'negociacao', 'fechado-ganho', 'fechado-perdido']


class Product(BaseModel):
    id: int
    slug: str
    name: str
    category: str
    brand: str
    description: str
    price: float
    sizes: list[str]
    colors: list[str]
    stock: int
    rating: float = Field(ge=0, le=5)
    featured: bool = False
    promo_tag: str | None = Field(default=None, max_length=80)
    media: list[str]

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r'[a-z0-9-]{3,120}', normalized):
            raise ValueError('Slug invalido')
        return normalized

    @field_validator('media')
    @classmethod
    def validate_media(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError('Produto precisa de pelo menos 1 midia')
        normalized_items: list[str] = []
        for item in value:
            url = item.strip()
            if not url.startswith(('http://', 'https://')):
                raise ValueError('URL de midia invalida')
            normalized_items.append(url)
        return normalized_items


class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    page: int
    page_size: int


class CategoryRecord(BaseModel):
    slug: str = Field(min_length=2, max_length=80)
    label: str = Field(min_length=2, max_length=80)

    @field_validator('slug')
    @classmethod
    def validate_category_slug(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r'[a-z0-9-]{2,80}', normalized):
            raise ValueError('Slug de categoria invalido')
        return normalized

    @field_validator('label')
    @classmethod
    def validate_label(cls, value: str) -> str:
        return value.strip()


class CategoryListResponse(BaseModel):
    items: list[str]
    labels: dict[str, str]


class BrandListResponse(BaseModel):
    items: list[str]


HeroMediaType = Literal['image', 'video']
StoryMediaType = Literal['image', 'video']


class HeroSlideRecord(BaseModel):
    id: int = Field(ge=1)
    title: str = Field(min_length=4, max_length=180)
    subtitle: str = Field(min_length=4, max_length=280)
    cta: str = Field(min_length=2, max_length=80)
    media_type: HeroMediaType = 'image'
    media_url: str = Field(min_length=8, max_length=600)

    @field_validator('media_url')
    @classmethod
    def validate_media_url(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.startswith(('http://', 'https://')):
            raise ValueError('URL de midia invalida')
        return normalized


class StoryItemRecord(BaseModel):
    id: int = Field(ge=1)
    title: str = Field(min_length=2, max_length=180)
    type: StoryMediaType = 'image'
    src: str = Field(min_length=8, max_length=600)
    text: str = Field(min_length=2, max_length=420)

    @field_validator('src')
    @classmethod
    def validate_story_src(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.startswith(('http://', 'https://')):
            raise ValueError('URL de midia invalida')
        return normalized


class SiteTextContent(BaseModel):
    hero_eyebrow: str = Field(min_length=2, max_length=120)
    presentation_title: str = Field(min_length=4, max_length=180)
    presentation_body: str = Field(min_length=8, max_length=420)
    featured_title: str = Field(min_length=3, max_length=120)
    featured_link_label: str = Field(min_length=2, max_length=60)
    hologram_eyebrow: str = Field(min_length=2, max_length=120)
    hologram_title: str = Field(min_length=4, max_length=180)
    hologram_body: str = Field(min_length=8, max_length=420)
    story_eyebrow: str = Field(min_length=2, max_length=120)
    story_title: str = Field(min_length=4, max_length=180)


MediaAssetType = Literal['image', 'video']


class MediaAsset(BaseModel):
    id: int = Field(ge=1)
    type: MediaAssetType
    url: str = Field(min_length=8, max_length=600)
    thumbnail_url: str | None = Field(default=None, min_length=8, max_length=600)
    alt: str | None = Field(default=None, max_length=180)
    folder: str | None = Field(default=None, max_length=120)
    tags: list[str] = Field(default_factory=list, max_length=50)
    created_at: str | None = None

    @field_validator('url')
    @classmethod
    def validate_url(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.startswith(('http://', 'https://')):
            raise ValueError('URL de midia invalida')
        return normalized

    @field_validator('thumbnail_url')
    @classmethod
    def validate_thumbnail_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized.startswith(('http://', 'https://')):
            raise ValueError('URL de thumbnail invalida')
        return normalized

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        clean: list[str] = []
        seen: set[str] = set()
        for item in value:
            tag = item.strip().lower()
            if not tag or tag in seen:
                continue
            if not re.fullmatch(r'[a-z0-9-]{2,40}', tag):
                continue
            seen.add(tag)
            clean.append(tag)
        return clean


BannerSegment = Literal['all', 'desktop', 'mobile']
BannerStatus = Literal['draft', 'published']


class BannerRecord(BaseModel):
    id: int = Field(ge=1)
    type: MediaAssetType
    media_id: int = Field(ge=1)
    poster_media_id: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=2, max_length=180)
    subtitle: str = Field(min_length=2, max_length=280)
    phrase: str | None = Field(default=None, max_length=240)
    cta_text: str | None = Field(default=None, max_length=80)
    cta_link: str | None = Field(default=None, max_length=420)
    order: int = Field(default=1, ge=1, le=1000)
    segment: BannerSegment = 'all'
    start_at: str | None = Field(default=None, max_length=40)
    end_at: str | None = Field(default=None, max_length=40)
    status: BannerStatus = 'published'


HologramIntensity = Literal['suave', 'medio', 'forte']
HologramSpeed = Literal['lento', 'normal', 'rapido']


class HologramConfig(BaseModel):
    enabled: bool = True
    items: list[int] = Field(default_factory=list, description='media ids')
    intensity: HologramIntensity = 'medio'
    rotation_speed: HologramSpeed = 'normal'
    glow_color: str = Field(default='#2aff6d', max_length=20)
    performance_mode: bool = True
    fallback_media_id: int | None = Field(default=None, ge=1)


class PolaroidRecord(BaseModel):
    id: int = Field(ge=1)
    media_id: int = Field(ge=1)
    caption: str = Field(min_length=2, max_length=140)
    story: str = Field(min_length=2, max_length=2000)
    collection_tag: str | None = Field(default=None, max_length=120)
    date: str | None = Field(default=None, max_length=40)
    order: int = Field(default=1, ge=1, le=5000)
    featured: bool = False
    modal_enabled: bool = True


class GlobalContent(BaseModel):
    main_slogan: str = Field(default='LIFE STYLE', max_length=180)
    footer_text: str = Field(default='LIFE STYLE', max_length=280)
    whatsapp_link: str | None = Field(default=None, max_length=420)
    instagram_link: str | None = Field(default=None, max_length=420)
    terms: str = Field(default='', max_length=12000)
    privacy: str = Field(default='', max_length=12000)
    lgpd: str = Field(default='', max_length=12000)
    faq: list[dict[str, str]] = Field(default_factory=list)


HomeSectionType = Literal['hero', 'presentation', 'featured', 'hologram', 'story']


class HomeSection(BaseModel):
    id: str = Field(min_length=2, max_length=60)
    type: HomeSectionType
    enabled: bool = True
    order: int = Field(default=1, ge=1, le=1000)
    props: dict[str, Any] = Field(default_factory=dict)


class SiteContent(BaseModel):
    hero_slides: list[HeroSlideRecord] = Field(min_length=1, max_length=12)
    story_gallery: list[StoryItemRecord] = Field(min_length=1, max_length=24)
    texts: SiteTextContent

    media_library: list[MediaAsset] = Field(default_factory=list, max_length=500)
    banners: list[BannerRecord] = Field(default_factory=list, max_length=40)
    home_sections: list[HomeSection] = Field(default_factory=list, max_length=40)
    hologram: HologramConfig = Field(default_factory=HologramConfig)
    polaroids: list[PolaroidRecord] = Field(default_factory=list, max_length=80)
    global_content: GlobalContent = Field(default_factory=GlobalContent)

    @model_validator(mode='after')
    def ensure_unique_ids(self) -> 'SiteContent':
        hero_ids = [item.id for item in self.hero_slides]
        story_ids = [item.id for item in self.story_gallery]
        if len(hero_ids) != len(set(hero_ids)):
            raise ValueError('IDs duplicados em hero_slides')
        if len(story_ids) != len(set(story_ids)):
            raise ValueError('IDs duplicados em story_gallery')

        media_ids = [item.id for item in self.media_library]
        if len(media_ids) != len(set(media_ids)):
            raise ValueError('IDs duplicados em media_library')

        banner_ids = [item.id for item in self.banners]
        if len(banner_ids) != len(set(banner_ids)):
            raise ValueError('IDs duplicados em banners')

        polaroid_ids = [item.id for item in self.polaroids]
        if len(polaroid_ids) != len(set(polaroid_ids)):
            raise ValueError('IDs duplicados em polaroids')

        section_ids = [item.id for item in self.home_sections]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError('IDs duplicados em home_sections')

        media_id_set = set(media_ids)
        for banner in self.banners:
            if media_id_set and banner.media_id not in media_id_set:
                raise ValueError(f'Banner {banner.id} referencia media_id inexistente')
            if banner.type == 'video' and banner.poster_media_id is not None and media_id_set and banner.poster_media_id not in media_id_set:
                raise ValueError(f'Banner {banner.id} referencia poster_media_id inexistente')

        for polaroid in self.polaroids:
            if media_id_set and polaroid.media_id not in media_id_set:
                raise ValueError(f'Polaroid {polaroid.id} referencia media_id inexistente')

        return self


class CatalogContent(BaseModel):
    categories: list[CategoryRecord] = Field(min_length=1, max_length=80)
    brands: list[str] = Field(min_length=1, max_length=120)
    products: list[Product] = Field(min_length=1, max_length=600)

    @field_validator('brands')
    @classmethod
    def validate_brands(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        clean: list[str] = []
        for item in values:
            value = item.strip()
            if not value:
                continue
            lowered = value.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            clean.append(value)
        if not clean:
            raise ValueError('Informe ao menos uma marca valida')
        return clean

    @model_validator(mode='after')
    def validate_cross_references(self) -> 'CatalogContent':
        category_slugs = [item.slug for item in self.categories]
        if len(category_slugs) != len(set(category_slugs)):
            raise ValueError('Categorias duplicadas por slug')

        brand_names = {item.lower() for item in self.brands}
        product_ids = [item.id for item in self.products]
        product_slugs = [item.slug for item in self.products]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError('Produtos com id duplicado')
        if len(product_slugs) != len(set(product_slugs)):
            raise ValueError('Produtos com slug duplicado')

        allowed_categories = set(category_slugs)
        for product in self.products:
            if product.category not in allowed_categories:
                raise ValueError(f'Produto "{product.slug}" usa categoria inexistente: {product.category}')
            if product.brand.lower() not in brand_names:
                raise ValueError(f'Produto "{product.slug}" usa marca inexistente: {product.brand}')
        return self


class AdminContentUpdateRequest(BaseModel):
    site_content: SiteContent
    catalog: CatalogContent


class AdminContentResponse(BaseModel):
    site_content: SiteContent
    catalog: CatalogContent
    updated_at: str


class ShippingQuoteRequest(BaseModel):
    zip_code: str = Field(min_length=8, max_length=9)
    subtotal: float = Field(gt=0)
    weight_kg: float = Field(gt=0)


class ShippingOption(BaseModel):
    name: str
    days: int
    price: float


class ShippingQuoteResponse(BaseModel):
    options: list[ShippingOption]


class CheckoutValidationRequest(BaseModel):
    cart_total: float = Field(gt=0)
    method: str
    installments: int = Field(ge=1, le=12)
    customer_email: str

    @field_validator('customer_email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if '@' not in normalized or '.' not in normalized.split('@')[-1]:
            raise ValueError('E-mail invalido')
        return normalized


class CheckoutValidationResponse(BaseModel):
    approved: bool
    risk_score: int
    recommended_action: str


class ContactRecord(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None = None
    company: str | None = None
    job_title: str | None = None
    status: str
    source: str
    tags: list[str] = Field(default_factory=list)
    consent: bool
    created_at: str
    updated_at: str


class LeadRecord(BaseModel):
    id: int
    contact_id: int
    contact_name: str
    contact_email: str
    contact_phone: str | None = None
    company: str | None = None
    job_title: str | None = None
    source: str
    tags: list[str] = Field(default_factory=list)
    stage: PIPELINE_STAGE_LITERAL
    owner: str | None = None
    estimated_value: float = Field(ge=0)
    close_probability: int = Field(ge=0, le=100)
    notes: str = ''
    is_active: bool
    last_activity_at: str
    created_at: str
    updated_at: str


class LeadCaptureRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=160)
    phone: str | None = Field(default=None, min_length=8, max_length=25)
    company: str | None = Field(default=None, max_length=120)
    job_title: str | None = Field(default=None, max_length=80)
    source: str = Field(default='site', max_length=80)
    status: str = Field(default='lead', max_length=40)
    tags: list[str] = Field(default_factory=list)
    consent: bool = True
    stage: PIPELINE_STAGE_LITERAL = 'lead'
    owner: str | None = Field(default=None, max_length=80)
    estimated_value: float = Field(default=0, ge=0)
    close_probability: int = Field(default=10, ge=0, le=100)
    notes: str | None = Field(default=None, max_length=1200)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if '@' not in normalized or '.' not in normalized.split('@')[-1]:
            raise ValueError('E-mail invalido')
        return normalized

    @field_validator('tags')
    @classmethod
    def clean_tags(cls, value: list[str]) -> list[str]:
        clean = []
        seen = set()
        for tag in value:
            normalized = tag.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            clean.append(normalized)
        return clean


class LeadCaptureResponse(BaseModel):
    deduplicated_contact: bool
    reopened_lead: bool
    lead: LeadRecord


class LeadUpdateRequest(BaseModel):
    stage: PIPELINE_STAGE_LITERAL | None = None
    owner: str | None = Field(default=None, max_length=80)
    estimated_value: float | None = Field(default=None, ge=0)
    close_probability: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = Field(default=None, max_length=1200)
    is_active: bool | None = None
    touchpoint: bool = False


class ContactListResponse(BaseModel):
    items: list[ContactRecord]
    total: int


class LeadListResponse(BaseModel):
    items: list[LeadRecord]
    total: int


class InteractionCreateRequest(BaseModel):
    contact_id: int = Field(ge=1)
    lead_id: int | None = Field(default=None, ge=1)
    channel: str = Field(min_length=2, max_length=40)
    summary: str = Field(min_length=4, max_length=1200)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InteractionRecord(BaseModel):
    id: int
    contact_id: int
    lead_id: int | None = None
    contact_name: str
    contact_email: str
    channel: str
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class InteractionListResponse(BaseModel):
    items: list[InteractionRecord]
    total: int


class TaskCreateRequest(BaseModel):
    lead_id: int = Field(ge=1)
    title: str = Field(min_length=3, max_length=220)
    due_date: str | None = Field(default=None, max_length=60)
    done: bool = False
    auto_generated: bool = False


class TaskUpdateRequest(BaseModel):
    done: bool


class TaskRecord(BaseModel):
    id: int
    lead_id: int
    title: str
    due_date: str | None = None
    done: bool
    auto_generated: bool
    lead_stage: str
    owner: str | None = None
    contact_name: str
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    items: list[TaskRecord]
    total: int


class StageCount(BaseModel):
    stage: str
    total: int


class SourceCount(BaseModel):
    source: str
    total: int


class CrmDashboardResponse(BaseModel):
    total_contacts: int
    total_leads: int
    open_leads: int
    qualified_leads: int
    won_deals: int
    lost_deals: int
    stalled_leads: int
    estimated_revenue: float
    conversion_rate: float
    by_stage: list[StageCount]
    by_source: list[SourceCount]


class FollowUpAutomationResponse(BaseModel):
    threshold_days: int
    stalled_leads: int
    tasks_created: int
    tasks: list[TaskRecord]


class AuditLogRecord(BaseModel):
    id: int
    entity: str
    entity_id: int | None = None
    action: str
    performed_by: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class AuditLogListResponse(BaseModel):
    items: list[AuditLogRecord]
    total: int
