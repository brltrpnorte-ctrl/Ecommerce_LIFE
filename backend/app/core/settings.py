from functools import lru_cache
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'LIFE STYLE API'
    environment: str = 'development'
    api_prefix: str = '/api/v1'
    allowed_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    allowed_origin_regex: str | None = None
    allowed_hosts: str = 'localhost,127.0.0.1'
    auth_token: str = 'change-this-token-in-production'
    auth_token_previous: str | None = None
    database_path: str = 'data/ecommerce_life.db'
    database_url: str | None = None
    database_url_runtime: str | None = None
    database_url_migrations: str | None = None
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    backup_dir: str = 'data/backups'
    request_rate_limit_per_minute: int = 180
    sensitive_rate_limit_per_minute: int = 60
    crm_allowed_roles: str = 'admin,gerente,vendedor'
    crm_editor_roles: str = 'admin,gerente'

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]

    @property
    def cors_origin_regex(self) -> str | None:
        value = (self.allowed_origin_regex or '').strip()
        return value or None

    @property
    def host_whitelist(self) -> list[str]:
        hosts = [host.strip() for host in self.allowed_hosts.split(',') if host.strip()]

        # Vercel injects the deployment host in VERCEL_URL (without scheme).
        # Auto-allowing only the current deployment host avoids broad wildcards.
        vercel_host = (os.getenv('VERCEL_URL') or '').strip()
        if vercel_host:
            vercel_host = vercel_host.replace('https://', '').replace('http://', '').strip('/')
            if vercel_host and vercel_host not in hosts:
                hosts.append(vercel_host)

        return hosts

    @property
    def active_database_url(self) -> str | None:
        for value in (self.database_url_runtime, self.database_url, self.database_url_migrations):
            if value and value.strip():
                return value.strip()
        return None

    @property
    def runtime_database_url(self) -> str | None:
        for value in (self.database_url_runtime, self.database_url):
            if value and value.strip():
                return value.strip()
        return None

    @property
    def migrations_database_url(self) -> str | None:
        for value in (self.database_url_migrations, self.database_url):
            if value and value.strip():
                return value.strip()
        return None

    @property
    def crm_roles(self) -> set[str]:
        return {role.strip().lower() for role in self.crm_allowed_roles.split(',') if role.strip()}

    @property
    def crm_write_roles(self) -> set[str]:
        return {role.strip().lower() for role in self.crm_editor_roles.split(',') if role.strip()}

    @property
    def admin_tokens(self) -> set[str]:
        tokens = {self.auth_token.strip()} if self.auth_token and self.auth_token.strip() else set()
        if self.auth_token_previous:
            tokens.update(token.strip() for token in self.auth_token_previous.split(',') if token.strip())
        return tokens


@lru_cache
def get_settings() -> Settings:
    return Settings()
