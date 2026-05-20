# backend/init_db.py
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Calculate path to your custom environment file (raptor-ledger/env/backend-local.env)
env_path = Path(__file__).resolve().parent.parent / "env" / "backend-local.env"

# Load the environment variables before importing anything from the db layer
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Environment loaded cleanly using python-dotenv from: {env_path}")
else:
    print(f"⚠️ Warning: Environment file not found at {env_path}. Falling back to defaults.")

# Now we safely import database components because os.environ['DATABASE_URL'] is primed!
from backend.db.base import engine, Base
from backend.models.models import User, Trade, AgentDecision, LLMLog, PortfolioSnapshot


async def run_db_initialization():
    current_url = os.getenv("DATABASE_URL")
    print(f"Connecting to database endpoint: {current_url}")

    try:
        async with engine.begin() as conn:
            print("Syncing relational metadata parameters...")
            await conn.run_sync(Base.metadata.create_all)
        print("🎉 Success! Database schemas mapped seamlessly without Alembic conflicts.")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(run_db_initialization())
