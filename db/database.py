from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.config import settings
from typing import AsyncGenerator
from sqlalchemy.engine import URL
import ssl

ssl_path = settings.SSL_PEM_PATH
ssl_context = ssl.create_default_context(cafile=ssl_path)

DATABASE_URL = URL(
    drivername="mysql+aiomysql",
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
    database=settings.DATABASE_NAME,
    query={"ssl": ssl_context},
)

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
