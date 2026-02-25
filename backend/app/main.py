from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
import logging
import os
import threading
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.settings import get_settings

settings = get_settings()
logger = logging.getLogger('ecommerce')

rate_lock = threading.Lock()
rate_buckets: dict[str, list[float]] = {}
sensitive_buckets: dict[str, list[float]] = {}
DEFAULT_ADMIN_TOKENS = {'change-this-token-in-production', 'troque-este-token-em-producao'}


async def startup_configuration_checks() -> None:
    env = (settings.environment or 'development').strip().lower()

    if env == 'production' and settings.auth_token in DEFAULT_ADMIN_TOKENS:
        raise RuntimeError('AUTH_TOKEN inseguro em producao. Configure um token admin forte via variavel de ambiente.')

    if env == 'production':
        localhost_origins = [origin for origin in settings.cors_origins if 'localhost' in origin or '127.0.0.1' in origin]
        if localhost_origins:
            logger.warning('CORS em producao ainda inclui localhost: %s', ', '.join(localhost_origins))

    if settings.runtime_database_url:
        logger.info('Runtime DB configurado via DATABASE_URL_RUNTIME/DATABASE_URL (dialeto resolvido na inicializacao dos stores).')
    elif os.getenv('VERCEL') and env == 'production':
        logger.warning(
            'Deploy em Vercel detectado sem DATABASE_URL_RUNTIME/DATABASE_URL. '
            'O backend caira em SQLite local (efemero em serverless).'
        )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await startup_configuration_checks()
    yield


app = FastAPI(
    title=settings.app_name,
    version='0.1.0',
    docs_url=None if settings.environment == 'production' else '/docs',
    redoc_url=None if settings.environment == 'production' else '/redoc',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type', 'X-Admin-Token', 'X-User-Role'],
    max_age=3600,
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.host_whitelist or ['localhost', '127.0.0.1'],
)


def is_sensitive_path(path: str) -> bool:
    return path.startswith(f'{settings.api_prefix}/admin') or path.startswith(f'{settings.api_prefix}/crm')


def exceeds_rate_limit(bucket: dict[str, list[float]], key: str, limit: int, window: int = 60) -> bool:
    now = time.time()
    min_time = now - window
    with rate_lock:
        history = bucket.setdefault(key, [])
        history[:] = [hit for hit in history if hit >= min_time]
        if len(history) >= limit:
            return True
        history.append(now)
    return False


@app.middleware('http')
async def security_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get('X-Request-Id', str(uuid.uuid4()))
    request.state.request_id = request_id

    ip = request.client.host if request.client else 'unknown'
    path = request.url.path
    sensitive = is_sensitive_path(path)
    bucket = sensitive_buckets if sensitive else rate_buckets
    limit = settings.sensitive_rate_limit_per_minute if sensitive else settings.request_rate_limit_per_minute
    key = f'{ip}:{path}'

    if exceeds_rate_limit(bucket, key, limit):
        return JSONResponse(
            status_code=429,
            content={'detail': 'Limite de requisicoes excedido. Tente novamente em instantes.', 'request_id': request_id},
            headers={'X-Request-Id': request_id},
        )

    start = time.perf_counter()
    response: Response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    response.headers['X-Request-Id'] = request_id
    response.headers['X-Response-Time-Ms'] = f'{elapsed_ms:.2f}'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' https: data:; media-src 'self' https:; frame-ancestors 'none';"
    )

    if sensitive:
        response.headers['Cache-Control'] = 'no-store'
    if settings.environment.lower() == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    logger.exception('Unhandled exception (request_id=%s): %s', request_id, exc)
    return JSONResponse(status_code=500, content={'detail': 'Erro interno inesperado', 'request_id': request_id})


app.include_router(router, prefix=settings.api_prefix)
