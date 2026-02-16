"""
Application settings loaded from environment variables.
Configuracoes da aplicacao carregadas de variaveis de ambiente.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings.
    Configuracoes da aplicacao usando Pydantic BaseSettings.
    """

    # Application / Aplicacao
    APP_NAME: str = "TeamPrincipal"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Server / Servidor
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database / Banco de Dados
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "team_principal"
    POSTGRES_PASSWORD: str = "changeme"
    POSTGRES_DB: str = "team_principal"

    @property
    def DATABASE_URL(self) -> str:
        """Async database URL / URL assincrona do banco de dados."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Sync database URL for Alembic / URL sincrona do banco para Alembic."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Auth / Autenticacao
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
