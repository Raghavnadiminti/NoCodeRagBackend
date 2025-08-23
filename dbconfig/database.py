import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")


if "command_timeout" not in DATABASE_URL:
    connector = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL += f"{connector}command_timeout=15"

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create async SQLAlchemy engine with connection health checks
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Ensures connections are alive
)

# Create async session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI routes with retry logic
async def get_db(retries: int = 2):
    attempt = 0
    while attempt <= retries:
        try:
            async with SessionLocal() as session:
                yield session
            break  # success
        except OperationalError as e:
            logger.warning(f"Database connection failed: {e}")
            attempt += 1
            if attempt > retries:
                logger.error("Exceeded retry limit. Raising HTTP 500.")
                raise HTTPException(status_code=500, detail="Database temporarily unavailable.")
            await asyncio.sleep(0.5)  # wait before retry
