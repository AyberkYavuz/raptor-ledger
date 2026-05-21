# backend/check_users.py
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Force environment loading first
env_path = Path(__file__).resolve().parent.parent / "env" / "backend-local.env"
load_dotenv(dotenv_path=env_path)

from backend.db.base import AsyncSessionLocal
from backend.models.models import User
from sqlalchemy import select


async def check():
    print(f"Checking records using connection: {os.getenv('DATABASE_URL')}")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"📊 Total user records found in database: {len(users)}")
        for u in users:
            print(f" -> ID: {u.id} | Email: {u.email}")

if __name__ == "__main__":
    asyncio.run(check())
