"""
Schemas Pydantic para validação de dados CMS
Segurança: Validação rigorosa de entrada, tipos e limites
"""
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class MediaTypeEnum(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class MediaStatusEnum(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class BannerTypeEnum(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class DeviceTypeEnum(str, Enum):
    ALL = "all"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class PublishStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    EDITOR = "editor"
    WAREHOUSE = "warehouse"
    SUPPORT = "support"


# ============================================================================
# MEDIA (BIBLIOTECA DE MÍDIA)
# ============================================================================

class MediaCreate(BaseModel):
    """Schema para criação de mídia (upload)"""
    type: MediaTypeEnum
    filename: str = Field(..., min_length=1, max_length=255)
    size: int = Field(..., gt=0, le=104857600)  # max 100MB
    width: Optional[int] = Field(None, gt=0)
    height: Optional[int] = Field(None, gt=0)
    duration: Optional[float] = Field(None, gt=0)  # para vídeos
    alt_text: Optional[str] = Field("", max_length=255)
    tags: Optional[List[str]] = Field(default_factory=list)
    folder: str = Field(default="root", max_length=255)

    @validator("tags")
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Máximo 10 tags")
        return [tag[:50] for tag in v]  # max 50 chars por tag


class MediaUpdate(BaseModel):
    """Schema para atualização de mídia"""
    alt_text: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = Field(None)
    folder: Optional[str] = Field(None, max_length=255)


class MediaResponse(BaseModel):
    """Schema para resposta de mídia"""
    id: str
    type: MediaTypeEnum
    url: str
    thumbnail_url: Optional[str]
    filename: str
    size: int
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    alt_text: str
    tags: List[str]
    folder: str
    status: MediaStatusEnum
    cdn_url: Optional[str]
    uploaded_at: datetime
    uploaded_by: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# BANNERS
# ============================================================================

class BannerCreate(BaseModel):
    """Schema para criação de banner"""
    name: str = Field(..., min_length=1, max_length=255)
    type: BannerTypeEnum = BannerTypeEnum.IMAGE
    media_id: str = Field(..., min_length=1)
    poster_id: Optional[str] = None
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    cta_text: Optional[str] = Field(None, max_length=100)
    cta_link: Optional[str] = Field(None, max_length=500)
    order_position: int = Field(default=0, ge=0)
    device_type: DeviceTypeEnum = DeviceTypeEnum.ALL
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    publish_status: PublishStatusEnum = PublishStatusEnum.DRAFT
    ab_variant: Optional[str] = Field(None, regex="^[AB]$")

    @validator("scheduled_end")
    def validate_schedule(cls, v, values):
        if v and "scheduled_start" in values and values["scheduled_start"]:
            if v <= values["scheduled_start"]:
                raise ValueError("Data fim deve ser após data início")
        return v


class BannerUpdate(BaseModel):
    """Schema para atualização de banner"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    media_id: Optional[str] = None
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    cta_text: Optional[str] = Field(None, max_length=100)
    cta_link: Optional[str] = Field(None, max_length=500)
    order_position: Optional[int] = Field(None, ge=0)
    publish_status: Optional[PublishStatusEnum] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


class BannerResponse(BaseModel):
    """Schema para resposta de banner"""
    id: str
    name: str
    type: BannerTypeEnum
    media_id: str
    title: Optional[str]
    subtitle: Optional[str]
    cta_text: Optional[str]
    cta_link: Optional[str]
    order_position: int
    device_type: DeviceTypeEnum
    publish_status: PublishStatusEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PAGE SECTIONS & CONTENT
# ============================================================================

class PageSectionCreate(BaseModel):
    """Schema para criação de seção"""
    page_type: str = Field(default="home", max_length=100)
    section_type: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=255)
    props: Dict[str, Any] = Field(default_factory=dict)
    order_position: int = Field(default=0, ge=0)
    is_visible: bool = Field(default=True)


class PageSectionUpdate(BaseModel):
    """Schema para atualização de seção"""
    title: Optional[str] = Field(None, max_length=255)
    props: Optional[Dict[str, Any]] = None
    order_position: Optional[int] = Field(None, ge=0)
    is_visible: Optional[bool] = None


class PageSectionResponse(BaseModel):
    """Schema para resposta de seção"""
    id: str
    page_type: str
    section_type: str
    title: Optional[str]
    props: Dict[str, Any]
    is_visible: bool
    order_position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentGlobalUpdate(BaseModel):
    """Schema para atualização de conteúdo global"""
    value: Dict[str, Any] = Field(...)
    description: Optional[str] = Field(None, max_length=255)


class ContentGlobalResponse(BaseModel):
    """Schema para resposta de conteúdo global"""
    key: str
    value: Dict[str, Any]
    description: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# HOLOGRAMA
# ============================================================================

class HologramaConfigCreate(BaseModel):
    """Schema para criação de config holograma"""
    name: str = Field(default="default", max_length=255)
    enabled: bool = Field(default=True)
    intensity: str = Field(default="médio", regex="^(suave|médio|forte)$")
    rotation_speed: float = Field(default=1.5, gt=0)
    glow_color: str = Field(default="#00FF00", regex="^#[0-9A-Fa-f]{6}$")
    glow_intensity: float = Field(default=0.8, ge=0, le=1)
    fallback_media_id: Optional[str] = None


class HologramaConfigUpdate(BaseModel):
    """Schema para atualização de config holograma"""
    name: Optional[str] = None
    enabled: Optional[bool] = None
    intensity: Optional[str] = Field(None, regex="^(suave|médio|forte)$")
    rotation_speed: Optional[float] = Field(None, gt=0)
    glow_color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    glow_intensity: Optional[float] = Field(None, ge=0, le=1)
    fallback_media_id: Optional[str] = None


class HologramaConfigResponse(BaseModel):
    """Schema para resposta de config holograma"""
    id: str
    name: str
    enabled: bool
    intensity: str
    rotation_speed: float
    glow_color: str
    glow_intensity: float
    fallback_media_id: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# POLAROID
# ============================================================================

class PolaroidItemCreate(BaseModel):
    """Schema para criação de item polaroid"""
    media_id: str = Field(..., min_length=1)
    caption: Optional[str] = Field(None, max_length=255)
    story: Optional[str] = None
    collection: Optional[str] = Field(None, max_length=100)
    order_position: int = Field(default=0, ge=0)
    is_featured: bool = Field(default=False)
    show_modal: bool = Field(default=True)


class PolaroidItemUpdate(BaseModel):
    """Schema para atualização de polaroid"""
    media_id: Optional[str] = None
    caption: Optional[str] = Field(None, max_length=255)
    story: Optional[str] = None
    collection: Optional[str] = Field(None, max_length=100)
    order_position: Optional[int] = Field(None, ge=0)
    is_featured: Optional[bool] = None
    show_modal: Optional[bool] = None


class PolaroidItemResponse(BaseModel):
    """Schema para resposta de polaroid"""
    id: str
    media_id: str
    caption: Optional[str]
    story: Optional[str]
    collection: Optional[str]
    order_position: int
    is_featured: bool
    show_modal: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# USUARIOS ADMIN
# ============================================================================

class AdminUserCreate(BaseModel):
    """Schema para criação de usuário admin"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRoleEnum = UserRoleEnum.EDITOR
    permissions: Optional[List[str]] = Field(default_factory=list)

    @validator("password")
    def validate_password(cls, v):
        """Validar força de senha"""
        if not any(c.isupper() for c in v):
            raise ValueError("Deve conter letra maiúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Deve conter dígito")
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError("Deve conter caractere especial")
        return v


class AdminUserUpdate(BaseModel):
    """Schema para atualização de usuário admin"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[UserRoleEnum] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None


class AdminUserResponse(BaseModel):
    """Schema para resposta de usuário admin"""
    id: str
    name: str
    email: str
    role: UserRoleEnum
    permissions: List[str]
    two_factor_enabled: bool
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str = Field(..., min_length=1)
    totp_code: Optional[str] = Field(None, regex="^[0-9]{6}$")


class TokenResponse(BaseModel):
    """Schema para resposta de token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AdminUserResponse


# ============================================================================
# AUDITORIA
# ============================================================================

class AuditLogResponse(BaseModel):
    """Schema para resposta de log de auditoria"""
    id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: str
    changes: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RESPOSTAS GENÉRICAS
# ============================================================================

class SuccessResponse(BaseModel):
    """Resposta genérica de sucesso"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Resposta genérica de erro"""
    success: bool = False
    error: str
    details: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """Resposta paginada"""
    data: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
