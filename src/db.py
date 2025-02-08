from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from conf import settings


class Base(DeclarativeBase):
    pass

DB_URL = settings.DB_URL
async_engine = create_async_engine(url= DB_URL)
async_session = async_sessionmaker(async_engine)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

