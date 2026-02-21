from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


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
    media: list[str]


class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    page: int
    page_size: int


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
