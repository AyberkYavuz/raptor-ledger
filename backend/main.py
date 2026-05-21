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

# --- IMPORT FASTAPI CORE AND ROUTES ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.api.auth import router as auth_router

app = FastAPI(
    title="Raptor Ledger API",
    description="High-Performance Asynchronous Agentic Trading Bot Engine Core Layer",
    version="1.0.0"
)

# --- CONFIGURE CROSS-ORIGIN RESOURCE SHARING (CORS) ---
# Allows your React frontend running on port 3000/5173 to talk securely to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific local ports in production if necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTER COMPONENT ROUTERS ---
app.include_router(auth_router)


@app.get("/health", tags=["System"])
async def health_check():
    """System heartbeat verification boundary endpoint."""
    return {"status": "operational", "engine": "Raptor Ledger Matrix Core V1"}

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
        log_config=None  # Strips out uvicorn default formatting so structlog controls everything
    )
