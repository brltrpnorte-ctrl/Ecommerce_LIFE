"""
Middleware de segurança para painel administrativo CMS
Inclui: Autenticação JWT, Autorização, Rate Limiting, Auditoria, CSRF Protection
"""
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, List, Callable
import jwt
import os
import logging
from sqlalchemy.orm import Session

# Não importar models ainda (será feito na integração)


logger = logging.getLogger("cms.security")


# ============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================================================

class SecurityConfig:
    """Configurações de segurança centralizadas"""
    SECRET_KEY = os.getenv("CMS_SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 60
    
    # Senhas
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True


# ============================================================================
# MODELOS DE TOKEN E USUÁRIO (será importado do contexto real)
# ============================================================================

class TokenData:
    """Dados do token JWT"""
    def __init__(self, user_id: str, email: str, role: str, permissions: List[str]):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.permissions = permissions
        self.issued_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(
            minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES
        )


# ============================================================================
# AUTENTICAÇÃO JWT
# ============================================================================

class JWTAuthentication:
    """Gerenciar tokens JWT com segurança"""
    
    @staticmethod
    def create_token(user_id: str, email: str, role: str, permissions: List[str]) -> str:
        """
        Criar token JWT com dados do usuário
        
        Args:
            user_id: ID único do usuário
            email: Email do usuário
            role: Papel do usuário (super_admin, admin, editor, etc.)
            permissions: Lista de permissões
            
        Returns:
            Token JWT assinado
        """
        token_data = TokenData(user_id, email, role, permissions)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "permissions": permissions,
            "iat": int(token_data.issued_at.timestamp()),
            "exp": int(token_data.expires_at.timestamp()),
        }
        
        try:
            token = jwt.encode(
                payload,
                SecurityConfig.SECRET_KEY,
                algorithm=SecurityConfig.ALGORITHM
            )
            logger.info(f"Token criado para usuário: {email}")
            return token
        except Exception as e:
            logger.error(f"Erro ao criar token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao gerar token"
            )
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        Verificar e decodificar token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            TokenData com dados do usuário
            
        Raises:
            HTTPException se token inválido ou expirado
        """
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.SECRET_KEY,
                algorithms=[SecurityConfig.ALGORITHM]
            )
            
            user_id = payload.get("sub")
            email = payload.get("email")
            role = payload.get("role")
            permissions = payload.get("permissions", [])
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            return TokenData(user_id, email, role, permissions)
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Token expirado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token inválido: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )


# ============================================================================
# DEPENDÊNCIAS DE AUTENTICAÇÃO (para usar em rotas FastAPI)
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(HTTPBearer()),
) -> TokenData:
    """
    Dependência para extrair e validar token JWT
    Uso em rota:
        @router.get("/protected")
        async def protected_route(current_user: TokenData = Depends(get_current_user)):
            pass
    """
    token = credentials.credentials
    return JWTAuthentication.verify_token(token)


async def get_optional_user(
    request: Request,
) -> Optional[TokenData]:
    """
    Dependência para usuário opcional (retorna None se não autenticado)
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
        return JWTAuthentication.verify_token(token)
    except Exception:
        return None


# ============================================================================
# AUTORIZAÇÃO (ROLES E PERMISSÕES)
# ============================================================================

class RoleBasedAuthorization:
    """Autorização baseada em roles e permissões"""
    
    # Definiçãodeacessos por role
    ROLE_PERMISSIONS = {
        "super_admin": ["*"],  # acesso total
        "admin": [
            "cms.media.create",
            "cms.media.read",
            "cms.media.update",
            "cms.media.delete",
            "cms.banners.create",
            "cms.banners.read",
            "cms.banners.update",
            "cms.banners.delete",
            "cms.content.manage",
            "cms.users.manage",
            "cms.audit.read",
        ],
        "editor": [
            "cms.media.create",
            "cms.media.read",
            "cms.media.update",
            "cms.banners.create",
            "cms.banners.read",
            "cms.banners.update",
            "cms.content.update",
        ],
        "warehouse": [
            "cms.media.read",
            "cms.banners.read",
            "cms.audit.read",
        ],
        "support": [
            "cms.audit.read",
        ],
    }
    
    @staticmethod
    def check_permission(user: TokenData, required_permission: str) -> bool:
        """Verificar se usuário tem permissão"""
        if user.role not in RoleBasedAuthorization.ROLE_PERMISSIONS:
            return False
        
        permissions = RoleBasedAuthorization.ROLE_PERMISSIONS[user.role]
        
        # Super admin tem tudo
        if "*" in permissions:
            return True
        
        # Verificar permissão específica ou permissão customizada
        return required_permission in permissions or required_permission in user.permissions
    
    @staticmethod
    def require_permission(required_permission: str):
        """
        Decorator para exigir permissão em rota
        Uso:
            @router.delete("/banners/{id}")
            @require_permission("cms.banners.delete")
            async def delete_banner(id: str, current_user: TokenData = Depends(get_current_user)):
                pass
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, current_user: TokenData = None, **kwargs):
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Autenticação necessária"
                    )
                
                if not RoleBasedAuthorization.check_permission(current_user, required_permission):
                    logger.warning(
                        f"Acesso negado para {current_user.email}: "
                        f"permissão '{required_permission}' não encontrada"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Permissão insuficiente"
                    )
                
                return await func(*args, current_user=current_user, **kwargs)
            
            return wrapper
        return decorator


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Rate limiter simples baseado em memória"""
    
    def __init__(self):
        self.requests = {}
    
    def is_rate_limited(self, identifier: str) -> bool:
        """
        Verificar se identifícador atingiu limite
        
        Args:
            identifier: Cliente IP, User ID, etc.
            
        Returns:
            True se rate limited, False caso contrário
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=SecurityConfig.RATE_LIMIT_WINDOW_SECONDS)
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Limpar requisições antigas
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Verificar se atingiu limite
        if len(self.requests[identifier]) >= SecurityConfig.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit atingido para: {identifier}")
            return True
        
        self.requests[identifier].append(now)
        return False


rate_limiter = RateLimiter()


async def check_rate_limit(request: Request) -> None:
    """
    Dependência para verificar rate limit
    Uso em rota:
        @router.post("/banners")
        async def create_banner(
            ...,
            _: None = Depends(check_rate_limit)
        ):
            pass
    """
    client_ip = request.client.host
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições. Tente novamente em alguns minutos."
        )


# ============================================================================
# VALIDAÇÃO DE ENTRADA
# ============================================================================

class InputValidation:
    """Validação de dados de entrada"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitizar string: remover caracteres perigosos"""
        if not isinstance(value, str):
            return ""
        
        # Remover caracteres de controle
        value = "".join(char for char in value if ord(char) >= 32)
        
        # Limitar tamanho
        return value[:max_length].strip()
    
    @staticmethod
    def validate_hex_color(value: str) -> bool:
        """Validar cor em formato hex"""
        import re
        return bool(re.match(r"^#[0-9A-Fa-f]{6}$", value))
    
    @staticmethod
    def validate_email(value: str) -> bool:
        """Validar email"""
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, value))
    
    @staticmethod
    def validate_url(value: str) -> bool:
        """Validar URL"""
        import re
        pattern = r"^https?://[^\s/$.?#].[^\s]*$|^/[^\s]*$"
        return bool(re.match(pattern, value))


# ============================================================================
# AUDITORIA
# ============================================================================

class AuditLogger:
    """Registrar ações para auditoria"""
    
    @staticmethod
    async def log_action(
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        db: Session = None,
    ):
        """
        Registrar ação de usuário em log
        
        Args:
            user_id: ID do usuário
            action: 'create', 'update', 'delete', 'read', etc.
            resource_type: 'banner', 'media', 'content', etc.
            resource_id: ID do recurso
            changes: Mudanças (before/after)
            ip_address: IP do cliente
            user_agent: User agent string
            db: Session do banco (para salvar)
        """
        logger.info(
            f"[AUDIT] {action} | Resource: {resource_type}/{resource_id} | "
            f"User: {user_id} | IP: {ip_address}"
        )
        
        # Se tiver banco de dados, salvar log (será implementado na integração)
        # if db:
        #     audit_log = AuditLog(
        #         user_id=user_id,
        #         action=action,
        #         resource_type=resource_type,
        #         resource_id=resource_id,
        #         changes=changes,
        #         ip_address=ip_address,
        #         user_agent=user_agent,
        #     )
        #     db.add(audit_log)
        #     db.commit()


# ============================================================================
# CSRF PROTECTION
# ============================================================================

class CSRFProtection:
    """Proteção contra CSRF"""
    
    @staticmethod
    async def get_csrf_token(request: Request) -> str:
        """
        Gerar token CSRF
        Uso:
            @router.get("/csrf-token")
            async def get_csrf_token(token: str = Depends(CSRFProtection.get_csrf_token)):
                return {"token": token}
        """
        # Gerar token aleatório
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Salvar na sessão (será implementado com cookies seguros)
        return token
    
    @staticmethod
    async def verify_csrf_token(
        request: Request,
        x_csrf_token: str = Header(None),
    ) -> bool:
        """
        Verificar token CSRF em requisições POST/PUT/DELETE
        """
        if x_csrf_token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token CSRF ausente"
            )
        
        # Verificar token contra sessão (será implementado com cookies seguros)
        return True


# ============================================================================
# SEGURANÇA DE SENHA
# ============================================================================

class PasswordSecurity:
    """Gerenciar segurança de senhas"""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validar força de senha
        
        Returns:
            (válido, mensagem)
        """
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            return False, f"Mínimo {SecurityConfig.PASSWORD_MIN_LENGTH} caracteres"
        
        if SecurityConfig.PASSWORD_REQUIRE_UPPER and not any(c.isupper() for c in password):
            return False, "Deve conter letra maiúscula"
        
        if SecurityConfig.PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Deve conter dígito"
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*_-+=[]{}|;:'" for c in password):
            return False, "Deve conter caractere especial (!@#$%^&*)"
        
        return True, "Senha válida"
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash de senha com bcrypt"""
        try:
            import bcrypt
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        except ImportError:
            logger.error("bcrypt não instalado")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar senha"
            )
    
    @staticmethod
    def verify_password(password: str, hash_password: str) -> bool:
        """Verificar senha contra hash"""
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), hash_password.encode())
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False


# ============================================================================
# LOGGING SEGURO
# ============================================================================

def setup_security_logging():
    """Configurar logging de segurança"""
    security_logger = logging.getLogger("cms.security")
    security_logger.setLevel(logging.INFO)
    
    # Handler para arquivo
    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler(
        "logs/cms_security.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
    )
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)
    
    return security_logger
