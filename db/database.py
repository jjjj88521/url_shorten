from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.config import DATABASE_URL
from typing import AsyncGenerator

async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)  # 創建引擎
Base = declarative_base()  # 創建基底
SessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)  # 創建 SessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_session = None
    try:
        db_session = SessionLocal()
        yield db_session
    finally:
        if db_session:
            await db_session.close()
