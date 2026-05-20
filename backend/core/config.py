import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core Application Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://ayberkmacmini@localhost:5432/postgres"

    # Security Configurations
    JWT_SECRET_KEY: str = "9a1f26e2eefb40889c25f4b5a329d01b10a2f4581c81e3a6a1122a27bfae6f42"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 Hours

    # Third Party Exchange Credentials
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    BINANCE_TESTNET_API_KEY: str = ""
    BINANCE_TESTNET_SECRET_KEY: str = ""

    # LLM Settings
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    # Engine Settings
    TRADING_ENABLED: bool = False
    LIVE_TRADING_ENABLED: bool = False
    LOG_LEVEL: str = "INFO"
    USE_MOCK_BINANCE: bool = True
    USE_FAKE_LLM: bool = True

    # Risk Guardrails
    MAX_DAILY_LOSS: float = 20.0
    MAX_POSITION_SIZE_USD: float = 50.0
    MAX_DAILY_TRADES: int = 10

    # Auto-load custom environment overrides
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / "env" / "backend-local.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
