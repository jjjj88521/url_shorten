import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import async_engine, Base
from routes.short_url import app as short_url_router
from contextlib import asynccontextmanager
from routes.redirect_url import app as redirect_url_router
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from config.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan, title="短網址服務", version="0.1.0")

# 添加 CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法
    allow_headers=["*"],  # 允許所有頭
)

# 包含路由
app.include_router(redirect_url_router, tags=["短網址轉址"])  # 短網址轉址路由
app.include_router(
    short_url_router, prefix="/api/v1/admin", tags=["短網址管理"]
)  # 短網址管理路由

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


# 添加錯誤處理
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "data": None},
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"{type(exc)}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "data": None},
    )
