from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Lifestyle Store API'
    environment: str = 'development'
    api_prefix: str = '/api/v1'
    allowed_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    allowed_hosts: str = 'localhost,127.0.0.1'
    auth_token: str = 'change-this-token-in-production'
    database_path: str = 'data/ecommerce_life.db'
    backup_dir: str = 'data/backups'
    request_rate_limit_per_minute: int = 180
    sensitive_rate_limit_per_minute: int = 60
    crm_allowed_roles: str = 'admin,gerente,vendedor'
    crm_editor_roles: str = 'admin,gerente'

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]

    @property
    def host_whitelist(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(',') if host.strip()]

    @property
    def crm_roles(self) -> set[str]:
        return {role.strip().lower() for role in self.crm_allowed_roles.split(',') if role.strip()}

    @property
    def crm_write_roles(self) -> set[str]:
        return {role.strip().lower() for role in self.crm_editor_roles.split(',') if role.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
