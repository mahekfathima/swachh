import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/swachhconnect")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create an async session factory
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """FastAPI dependency for database sessions."""
    async with async_session() as session:
        yield session
