# backend/main.py
import os
from pathlib import Path
from dotenv import load_dotenv

# --- FORCE ENVIRONMENT LOADING BEFORE CONFIG AND APP SETUP ---
env_path = Path(__file__).resolve().parent / "env" / "backend-local.env"
if not env_path.exists():
    # Fallback to checking root if running from a nested working directory
    env_path = Path(__file__).resolve().parent.parent / "env" / "backend-local.env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# --- INITIALIZE CORE TELEMETRY ---
from backend.core.logging import configure_logging
import structlog

configure_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
logger = structlog.get_logger("raptor_ledger.main")

logger.info("main.py begins")

# --- IMPORT FASTAPI CORE AND ROUTES ---
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uvicorn

from backend.api.auth import router as auth_router
from backend.api.websocket import router as ws_router
from backend.db.base import get_db
from backend.schemas.auth import StandardResponse
from backend.tools.mock_binance_tool import MockBinanceTool
from backend.tools.fake_llm import FakeLLM

# Instantiate mock tools for service health verification
mock_binance = MockBinanceTool()
fake_llm = FakeLLM()

app = FastAPI(
    title="Raptor Ledger API",
    description="High-Performance Asynchronous Agentic Trading Bot Engine Core Layer",
    version="1.0.0"
)

# --- CONFIGURE CROSS-ORIGIN RESOURCE SHARING (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER COMPONENT ROUTERS ---
app.include_router(auth_router)
app.include_router(ws_router)


# --- REFACTORED COMPREHENSIVE DIAGNOSTIC HEALTH CHECK ---
@app.get("/api/health", tags=["System"], response_model=StandardResponse[dict])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Checks system availability and service status across dependencies.
    Encapsulates flaws inside a success state with degraded node indicators.
    """
    logger.info("Executing operational diagnostic health checks")

    # Match the contract scheme from api_contracts.md
    health_status = {
        "backend": "healthy",
        "postgresql": "healthy",
        "binance_api": "healthy",
        "llm_api": "healthy"
    }

    # 1. Validate PostgreSQL Connectivity
    try:
        await db.execute(select(1))
    except Exception as e:
        logger.error("PostgreSQL connectivity health check failed", error=str(e))
        health_status["postgresql"] = "unhealthy"

    # 2. Validate Mock Binance Tool Connectivity
    try:
        await mock_binance.get_balance("USDT")
    except Exception as e:
        logger.error("Binance api health check failed", error=str(e))
        health_status["binance_api"] = "unhealthy"

    # 3. Validate Fake LLM Engine Connectivity
    try:
        await fake_llm.generate(prompt="healthcheck")
    except Exception as e:
        logger.error("LLM provider health check failed", error=str(e))
        health_status["llm_api"] = "unhealthy"

    # Encapsulate results inside an envelope success state per specifications
    return StandardResponse(
        success=True,
        message="System health analysis resolved successfully.",
        data=health_status
    )


# --- PYCHARM NATIVE RUN CONFIGURATION ENTRYPOINT ---
if __name__ == "__main__":
    logger.info(
        "Booting Raptor Ledger Platform API Engine inside PyCharm runtime execution environment",
        host="127.0.0.1",
        port=8000
    )

    # Run the application programmatically matching local operational metrics
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_config=None
    )
