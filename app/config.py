"""Configuración del servicio."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Auth interna — servicio a servicio, nunca JWT de usuario final
    internal_api_key: str = ""

    # Límites (ver plan: arrancar en 20-30 MB)
    max_file_size_mb: int = 25

    host: str = "0.0.0.0"
    port: int = 8100
    debug: bool = False
    enable_docs: bool = False

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()
