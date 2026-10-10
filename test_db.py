import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.database import Base
from src.models import User, GVP, Payout

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Connecting to:", DATABASE_URL)

async def test():
    engine = create_async_engine(DATABASE_URL, echo=True)
    try:
        async with engine.begin() as conn:
            print("Executing CREATE EXTENSION...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            print("Dropping tables with CASCADE...")
            await conn.execute(text("DROP TABLE IF EXISTS payouts CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS gvps CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("Inserting dummy user...")
            await conn.execute(text("INSERT INTO users (id, name, upi_id, phone_number, wallet_balance, created_at) VALUES ('00000000-0000-0000-0000-000000000000', 'Dummy Reporter', 'dummy@ybl', '0000000000', 0, NOW()) ON CONFLICT (id) DO NOTHING;"))
            print("Success!")
    except Exception as e:
        print("ERROR:", str(e))
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())
