"""
Models para CMS (Conteúdo, Mídia, Banners, etc.)
Segurança: Auditoria integrada, validações, permissões
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, Text, JSON, ForeignKey, ARRAY, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class MediaType(str, Enum):
    """Tipos de mídia suportados"""
    IMAGE = "image"
    VIDEO = "video"


class MediaStatus(str, Enum):
    """Status de processamento de mídia"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class BannerType(str, Enum):
    """Tipos de banner"""
    IMAGE = "image"
    VIDEO = "video"


class DeviceType(str, Enum):
    """Tipos de dispositivo"""
    ALL = "all"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class PublishStatus(str, Enum):
    """Status de publicação"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserRole(str, Enum):
    """Papéis de usuário admin"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    EDITOR = "editor"
    WAREHOUSE = "warehouse"
    SUPPORT = "support"


class Media(Base):
    """
    Biblioteca de mídia (imagens e vídeos)
    Suporta: JPG, PNG, WebP, AVIF (imagens); MP4, WebM (vídeos)
    """
    __tablename__ = "cms_media"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(SQLEnum(MediaType), nullable=False)  # image | video
    url = Column(String(500), nullable=False, unique=True)
    thumbnail_url = Column(String(500), nullable=True)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)  # em bytes
    width = Column(Integer, nullable=True)  # px
    height = Column(Integer, nullable=True)  # px
    duration = Column(Float, nullable=True)  # segundos (para vídeos)
    
    # SEO e contexto
    alt_text = Column(String(255), nullable=True, default="")
    tags = Column(ARRAY(String), default=[])  # ['banner-home', 'holograma', etc.]
    folder = Column(String(255), default="root")  # organização
    
    # Otimizações
    optimized = Column(JSON, default={
        "webp": None,
        "avif": None,
        "thumb": None
    })
    cdn_url = Column(String(500), nullable=True)
    
    # Status e auditoria
    status = Column(SQLEnum(MediaStatus), default=MediaStatus.UPLOADING)
    uploaded_by = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Controle
    is_public = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Media {self.id} - {self.filename}>"


class Banner(Base):
    """
    Banners (herói, carrossel, campanhas)
    Suporta: imagem ou vídeo, agendamento, segmentação por dispositivo
    """
    __tablename__ = "cms_banners"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)  # nome interno
    
    # Conteúdo
    type = Column(SQLEnum(BannerType), default=BannerType.IMAGE)
    media_id = Column(String(36), ForeignKey("cms_media.id"), nullable=False)
    poster_id = Column(String(36), ForeignKey("cms_media.id"), nullable=True)  # capa para vídeo
    
    # Texto e CTA
    title = Column(String(255), nullable=True)
    subtitle = Column(String(255), nullable=True)
    cta_text = Column(String(100), nullable=True)  # "Comprar agora"
    cta_link = Column(String(500), nullable=True)  # /products, /collections/carnaval
    
    # Ordenação e segmentação
    order_position = Column(Integer, default=0)
    device_type = Column(SQLEnum(DeviceType), default=DeviceType.ALL)
    
    # Agendamento
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    
    # Status e publicação
    publish_status = Column(SQLEnum(PublishStatus), default=PublishStatus.DRAFT)
    is_active = Column(Boolean, default=True)
    
    # A/B Testing
    ab_variant = Column(String(1), nullable=True)  # 'A' ou 'B'
    
    # Analytics
    analytics = Column(JSON, default={
        "views": 0,
        "clicks": 0,
        "ctr": 0.0
    })
    
    # Auditoria
    created_by = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Banner {self.id} - {self.name}>"


class PageSection(Base):
    """
    Seções da página (Home, Coleção, etc.)
    Suporta: Hero, Holograma, Galeria, Destaques, etc.
    """
    __tablename__ = "cms_page_sections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tipo de página e seção
    page_type = Column(String(100), default="home")  # home, collection, product, etc.
    section_type = Column(String(100), nullable=False)  # hero, holograma, gallery, etc.
    title = Column(String(255), nullable=True)
    
    # Conteúdo (JSON dinâmico)
    props = Column(JSON, nullable=False, default={})
    
    # Visibilidade e ordem
    is_visible = Column(Boolean, default=True)
    order_position = Column(Integer, default=0)
    
    # Auditoria
    created_by = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PageSection {self.id} - {self.section_type}>"


class ContentGlobal(Base):
    """
    Conteúdo global do site (textos fixos, frases, FAQ, etc.)
    """
    __tablename__ = "cms_content_global"

    key = Column(String(100), primary_key=True)  # 'slogan', 'footer_about', etc.
    value = Column(JSON, nullable=False, default={})
    description = Column(String(255), nullable=True)
    
    # Auditoria
    updated_by = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ContentGlobal {self.key}>"


class HologramaConfig(Base):
    """
    Configuração do holograma 3D (Trevo)
    Controle total de mídia, intensidade, velocidade, cor
    """
    __tablename__ = "cms_holograma_config"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), default="default")
    enabled = Column(Boolean, default=True)
    
    # Visual
    intensity = Column(String(20), default="médio")  # suave, médio, forte
    rotation_speed = Column(Float, default=1.5)
    glow_color = Column(String(7), default="#00FF00")  # hex color
    glow_intensity = Column(Float, default=0.8)
    
    # Performance
    performance_mode = Column(JSON, default={
        "mobile": True,
        "max_fps": 30
    })
    
    # Fallback 2D
    fallback_media_id = Column(String(36), ForeignKey("cms_media.id"), nullable=True)
    
    # Auditoria
    updated_by = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<HologramaConfig {self.id}>"


class HologramaMedia(Base):
    """
    Mídia do holograma (imagem ou vídeo)
    """
    __tablename__ = "cms_holograma_media"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_id = Column(String(36), ForeignKey("cms_holograma_config.id"), nullable=False)
    media_id = Column(String(36), ForeignKey("cms_media.id"), nullable=False)
    
    duration_seconds = Column(Integer, default=5)
    order_position = Column(Integer, default=0)
    
    added_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HologramaMedia {self.id}>"


class PolaroidItem(Base):
    """
    Itens de galeria (Polaroid) com história
    """
    __tablename__ = "cms_polaroid_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id = Column(String(36), ForeignKey("cms_media.id"), nullable=False)
    
    # Conteúdo
    caption = Column(String(255), nullable=True)
    story = Column(Text, nullable=True)
    collection = Column(String(100), nullable=True)
    
    # Ordenação e destaque
    order_position = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    show_modal = Column(Boolean, default=True)
    
    # Data
    date = Column(DateTime, default=datetime.utcnow)
    
    # Auditoria
    created_by = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PolaroidItem {self.id}>"


class AdminUser(Base):
    """
    Usuário administrativo com roles e permissões
    Segurança: Senhas hasheadas, 2FA, logs de acesso
    """
    __tablename__ = "cms_admin_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Roles e permissões
    role = Column(SQLEnum(UserRole), default=UserRole.EDITOR)
    permissions = Column(ARRAY(String), default=[])
    
    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AdminUser {self.id} - {self.email}>"


class AuditLog(Base):
    """
    Log de auditoria: quem fez o quê, quando e de onde
    Segurança: Rastreamento completo de mudanças
    """
    __tablename__ = "cms_audit_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Usuário e ação
    user_id = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # 'create', 'update', 'delete', etc.
    resource_type = Column(String(50), nullable=False)  # 'banner', 'media', etc.
    resource_id = Column(String(100), nullable=False)
    
    # Mudanças (old vs new)
    changes = Column(JSON, nullable=True)
    
    # Contexto (IP, User-Agent)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.id} - {self.action}>"


class Approval(Base):
    """
    Workflow de aprovação para mudanças críticas
    Segurança: Separação de criação e publicação
    """
    __tablename__ = "cms_approvals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Recurso
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)  # 'publish', 'delete', etc.
    
    # Status e usuários
    status = Column(String(20), default="pending")  # pending, approved, rejected
    requester_id = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=False)
    approved_by = Column(String(36), ForeignKey("cms_admin_users.id"), nullable=True)
    
    # Conteúdo pendente (snapshot antes de aprovação)
    pending_changes = Column(JSON, nullable=False)
    
    # Timeline
    requested_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Approval {self.id} - {self.status}>"
