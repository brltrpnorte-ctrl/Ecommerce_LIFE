from __future__ import annotations

from typing import Annotated

import logging

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.core.settings import get_settings
from app.models.schemas import (
    AdminContentResponse,
    AdminContentUpdateRequest,
    AuditLogListResponse,
    BrandListResponse,
    CategoryListResponse,
    CheckoutValidationRequest,
    CheckoutValidationResponse,
    ContactListResponse,
    CrmDashboardResponse,
    FollowUpAutomationResponse,
    InteractionCreateRequest,
    InteractionListResponse,
    InteractionRecord,
    LeadCaptureRequest,
    LeadCaptureResponse,
    LeadListResponse,
    LeadRecord,
    LeadUpdateRequest,
    Product,
    ProductListResponse,
    SiteContent,
    ShippingOption,
    ShippingQuoteRequest,
    ShippingQuoteResponse,
    TaskCreateRequest,
    TaskListResponse,
    TaskRecord,
    TaskUpdateRequest,
)
from app.services import CRMStore, SiteStore
from app.services.crm_store import PIPELINE_STAGES

router = APIRouter()
settings = get_settings()
crm_store = CRMStore(settings.database_path, settings.backup_dir)
site_store = SiteStore(settings.database_path, settings.backup_dir)


def normalize_role(value: str | None) -> str:
    return (value or '').strip().lower()


def require_admin_token(token: str | None) -> None:
    # If the server is running with an obvious default token, refuse admin operations
    default_tokens = ('change-this-token-in-production', 'troque-este-token-em-producao')
    if settings.auth_token in default_tokens:
        # In non-development environment, fail fast and require proper configuration
        if getattr(settings, 'environment', 'development') not in ('development', 'dev', 'local'):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Admin token is not configured on server')
        else:
            logging.getLogger('ecommerce').warning('Using default admin token in non-production environment')

    if token != settings.auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token admin invalido')


def authorize_crm(
    x_user_role: str | None,
    x_admin_token: str | None,
    *,
    write: bool = False,
) -> str:
    if x_admin_token == settings.auth_token:
        return 'admin'
    role = normalize_role(x_user_role)
    allowed = settings.crm_write_roles if write else settings.crm_roles
    if role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Perfil sem permissao para CRM')
    return role


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.app_name}


@router.get('/site/content', response_model=SiteContent)
def get_site_content() -> SiteContent:
    return SiteContent(**site_store.get_site_content())


@router.get('/categories', response_model=CategoryListResponse)
def list_categories() -> CategoryListResponse:
    categories = site_store.list_categories()
    return CategoryListResponse(
        items=[item['slug'] for item in categories],
        labels={item['slug']: item['label'] for item in categories},
    )


@router.get('/brands', response_model=BrandListResponse)
def list_brands() -> BrandListResponse:
    return BrandListResponse(items=site_store.list_brands())


@router.get('/products', response_model=ProductListResponse)
def list_products(
    category: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    q: str | None = Query(default=None, min_length=2),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    featured: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=48),
) -> ProductListResponse:
    items = site_store.list_products()

    if category:
        items = [item for item in items if item.category == category]
    if brand:
        items = [item for item in items if item.brand == brand]
    if q:
        term = q.strip().lower()
        items = [
            item
            for item in items
            if term in item.name.lower()
            or term in item.description.lower()
            or term in item.category.lower()
            or term in item.brand.lower()
        ]
    if min_price is not None:
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price <= max_price]
    if featured is not None:
        items = [item for item in items if item.featured is featured]

    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return ProductListResponse(items=items[start:end], total=total, page=page, page_size=page_size)


@router.get('/products/{slug}', response_model=Product)
def get_product(slug: str) -> Product:
    if not slug or len(slug) > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Slug invalido')
    for item in site_store.list_products():
        if item.slug == slug:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Produto nao encontrado')


@router.post('/shipping/quote', response_model=ShippingQuoteResponse)
def calculate_shipping(payload: ShippingQuoteRequest) -> ShippingQuoteResponse:
    if payload.weight_kg <= 0 or payload.weight_kg > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Peso invalido')
    if payload.subtotal <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Subtotal invalido')
    
    zip_numeric = ''.join(char for char in payload.zip_code if char.isdigit())
    if len(zip_numeric) != 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='CEP invalido')
    
    regional_factor = 1.1 if zip_numeric.startswith(('0', '1', '2', '3')) else 1.0
    volume_factor = min(2.5, 1 + (payload.weight_kg / 4))

    express_price = round((27 + payload.weight_kg * 5) * regional_factor, 2)
    standard_price = round((16 + payload.weight_kg * 3.5) * regional_factor, 2)
    economy_price = round((12 + payload.weight_kg * 2.8) * regional_factor * volume_factor, 2)

    options = [
        ShippingOption(name='Express', days=2, price=express_price),
        ShippingOption(name='Padrao', days=5, price=standard_price),
        ShippingOption(name='Economico', days=9, price=economy_price),
    ]
    return ShippingQuoteResponse(options=options)


@router.post('/checkout/validate', response_model=CheckoutValidationResponse)
def validate_checkout(payload: CheckoutValidationRequest) -> CheckoutValidationResponse:
    if payload.cart_total <= 0 or payload.cart_total > 50000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Valor do carrinho invalido')
    if payload.installments < 1 or payload.installments > 12:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Numero de parcelas invalido')
    if '@' not in payload.customer_email or len(payload.customer_email) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email invalido')
    
    risk_score = 12
    if payload.cart_total > 1800:
        risk_score += 24
    if payload.installments >= 8:
        risk_score += 18
    if payload.method.lower() == 'boleto':
        risk_score += 8

    approved = risk_score <= 55
    action = 'Aprovado' if approved else 'Revisao manual antifraude'
    return CheckoutValidationResponse(approved=approved, risk_score=risk_score, recommended_action=action)


@router.get('/admin/overview')
def admin_overview(
    x_admin_token: Annotated[str | None, Header()] = None,
) -> dict[str, int | float]:
    require_admin_token(x_admin_token)

    products = site_store.list_products()
    low_stock = [item for item in products if item.stock <= 12]
    featured = [item for item in products if item.featured]
    crm_snapshot = crm_store.dashboard()

    return {
        'total_products': len(products),
        'low_stock_alerts': len(low_stock),
        'featured_products': len(featured),
        'estimated_month_revenue': 189430.0,
        'open_orders': 37,
        'crm_total_leads': crm_snapshot['total_leads'],
        'crm_conversion_rate': crm_snapshot['conversion_rate'],
    }


@router.get('/admin/content', response_model=AdminContentResponse)
def admin_content(
    x_admin_token: Annotated[str | None, Header()] = None,
) -> AdminContentResponse:
    require_admin_token(x_admin_token)
    return AdminContentResponse(**site_store.get_admin_content())


@router.put('/admin/content', response_model=AdminContentResponse)
def admin_update_content(
    payload: AdminContentUpdateRequest,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> AdminContentResponse:
    require_admin_token(x_admin_token)
    try:
        updated = site_store.update_admin_content(payload.model_dump(), by='admin')
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AdminContentResponse(**updated)


@router.get('/crm/stages')
def crm_stages() -> dict[str, list[str]]:
    return {'items': list(PIPELINE_STAGES)}


@router.post('/crm/leads/capture', response_model=LeadCaptureResponse, status_code=status.HTTP_201_CREATED)
def crm_capture_lead(payload: LeadCaptureRequest) -> LeadCaptureResponse:
    result = crm_store.capture_lead(payload.model_dump())
    return LeadCaptureResponse(**result)


@router.get('/crm/contacts', response_model=ContactListResponse)
def crm_list_contacts(
    status_filter: str | None = Query(default=None, alias='status'),
    tag: str | None = Query(default=None),
    search: str | None = Query(default=None),
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> ContactListResponse:
    authorize_crm(x_user_role, x_admin_token, write=False)
    items = crm_store.list_contacts(status=status_filter, tag=tag, search=search)
    return ContactListResponse(items=items, total=len(items))


@router.get('/crm/leads', response_model=LeadListResponse)
def crm_list_leads(
    stage: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    search: str | None = Query(default=None),
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> LeadListResponse:
    authorize_crm(x_user_role, x_admin_token, write=False)
    items = crm_store.list_leads(stage=stage, owner=owner, active_only=active_only, search=search)
    return LeadListResponse(items=items, total=len(items))


@router.patch('/crm/leads/{lead_id}', response_model=LeadRecord)
def crm_update_lead(
    lead_id: int,
    payload: LeadUpdateRequest,
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> LeadRecord:
    role = authorize_crm(x_user_role, x_admin_token, write=True)
    try:
        result = crm_store.update_lead(lead_id, payload.model_dump(), by=role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LeadRecord(**result)


@router.post('/crm/interactions', response_model=InteractionRecord, status_code=status.HTTP_201_CREATED)
def crm_create_interaction(
    payload: InteractionCreateRequest,
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> InteractionRecord:
    role = authorize_crm(x_user_role, x_admin_token, write=True)
    try:
        result = crm_store.create_interaction(payload.model_dump(), by=role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return InteractionRecord(**result)


@router.get('/crm/interactions', response_model=InteractionListResponse)
def crm_list_interactions(
    contact_id: int | None = Query(default=None, ge=1),
    lead_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=100, ge=1, le=300),
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> InteractionListResponse:
    authorize_crm(x_user_role, x_admin_token, write=False)
    items = crm_store.list_interactions(contact_id=contact_id, lead_id=lead_id, limit=limit)
    return InteractionListResponse(items=items, total=len(items))


@router.post('/crm/tasks', response_model=TaskRecord, status_code=status.HTTP_201_CREATED)
def crm_create_task(
    payload: TaskCreateRequest,
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> TaskRecord:
    role = authorize_crm(x_user_role, x_admin_token, write=True)
    try:
        result = crm_store.create_task(payload.model_dump(), by=role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskRecord(**result)


@router.patch('/crm/tasks/{task_id}', response_model=TaskRecord)
def crm_update_task(
    task_id: int,
    payload: TaskUpdateRequest,
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> TaskRecord:
    role = authorize_crm(x_user_role, x_admin_token, write=True)
    try:
        result = crm_store.update_task(task_id, done=payload.done, by=role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskRecord(**result)


@router.get('/crm/tasks', response_model=TaskListResponse)
def crm_list_tasks(
    lead_id: int | None = Query(default=None, ge=1),
    owner: str | None = Query(default=None),
    done: bool | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> TaskListResponse:
    authorize_crm(x_user_role, x_admin_token, write=False)
    items = crm_store.list_tasks(lead_id=lead_id, owner=owner, done=done, limit=limit)
    return TaskListResponse(items=items, total=len(items))


@router.post('/crm/automation/follow-ups', response_model=FollowUpAutomationResponse)
def crm_automation_followups(
    stale_days: int = Query(default=7, ge=1, le=90),
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> FollowUpAutomationResponse:
    role = authorize_crm(x_user_role, x_admin_token, write=True)
    result = crm_store.run_stalled_lead_automation(stale_days=stale_days, by=role)
    return FollowUpAutomationResponse(**result)


@router.get('/crm/dashboard', response_model=CrmDashboardResponse)
def crm_dashboard(
    stale_days: int = Query(default=7, ge=1, le=90),
    x_user_role: Annotated[str | None, Header()] = None,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> CrmDashboardResponse:
    authorize_crm(x_user_role, x_admin_token, write=False)
    return CrmDashboardResponse(**crm_store.dashboard(stale_days=stale_days))


@router.get('/crm/audit', response_model=AuditLogListResponse)
def crm_audit_logs(
    limit: int = Query(default=200, ge=1, le=1000),
    x_admin_token: Annotated[str | None, Header()] = None,
) -> AuditLogListResponse:
    require_admin_token(x_admin_token)
    items = crm_store.list_audit(limit=limit)
    return AuditLogListResponse(items=items, total=len(items))


@router.post('/crm/backup')
def crm_backup(
    x_admin_token: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    require_admin_token(x_admin_token)
    path = crm_store.backup_now()
    return {'backup_path': path}
