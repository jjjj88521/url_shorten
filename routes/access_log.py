import csv
import io
from io import StringIO
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.logger import logger
from sqlalchemy.exc import IntegrityError
from db.database import get_db_session
from models.short_url import ShortUrl
from schemas.access_log import AccessLog
from schemas.general import ListResponse, MyResponse
from sqlalchemy.orm import Session

from services.access_log import AccessLogService


app = APIRouter()


@app.get(
    "/access_log/list",
    response_model=MyResponse[ListResponse[AccessLog]],
    summary="獲取訪問紀錄列表",
)
async def get_short_urls(
    page: int = Query(1), limit: int = Query(20), db: Session = Depends(get_db_session)
):

    result = await AccessLogService.get_access_log_list(db, page, limit)
    return MyResponse(
        data=ListResponse(
            list=result["list"], total=result["total"], page=page, limit=limit
        )
    )
