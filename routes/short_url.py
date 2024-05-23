import csv
import io
from io import StringIO
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.logger import logger
from sqlalchemy.exc import IntegrityError
from db.database import get_db_session
from models.short_url import ShortUrl
from schemas.short_url import (
    ShortUrlCreate,
    ShortUrl as ShortUrlSchema,
    ShortUrlUpdate,
)
from schemas.general import ListResponse, MyResponse
from services.short_url import ShortUrlService
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Dict

from utils.snowflake import simple_snowflake_generator, generate_short_url

app = APIRouter()


# 生成短網址 short_code
def generate_short_code() -> str:
    # 生成一個ID
    unique_id = simple_snowflake_generator.generate_id()
    # 生成6碼Base62短網址
    short_code = generate_short_url(unique_id)
    return short_code


@app.post("/shorten", response_model=MyResponse[ShortUrlSchema], summary="縮短網址")
async def create_short_url(
    short_url_create: ShortUrlCreate, db: Session = Depends(get_db_session)
):
    short_url = await ShortUrlService.get_short_url(
        db, origin_url=str(short_url_create.origin_url)
    )
    if short_url:
        return MyResponse(data=short_url)
    short_code = generate_short_code()
    result = await ShortUrlService.create_short_url(
        db, short_code=short_code, origin_url=short_url_create.origin_url
    )
    return MyResponse(data=result)


@app.get(
    "/short_url/list",
    response_model=MyResponse[ListResponse[ShortUrlSchema]],
    summary="獲取短網址列表",
)
async def get_short_urls(
    page: int = Query(1), limit: int = Query(20), db: Session = Depends(get_db_session)
):

    result = await ShortUrlService.get_short_url_list(db, page, limit)
    return MyResponse(
        data=ListResponse(list=result, total=len(result), page=page, limit=limit)
    )


@app.get(
    "/short_url/{short_code}",
    response_model=MyResponse[ShortUrlSchema],
    summary="獲取單一短網址",
)
async def get_short_url(short_code: str, db: Session = Depends(get_db_session)):
    short_url = await ShortUrlService.get_short_url(db, short_code=short_code)
    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return MyResponse(data=short_url)


@app.put(
    "/short_url/{short_code}",
    response_model=MyResponse[ShortUrlSchema],
    summary="更新短網址",
    description="只能更新 origin_url",
)
async def update_short_url(
    short_code: str,
    short_url_update: ShortUrlUpdate,
    db: Session = Depends(get_db_session),
):
    updates = short_url_update.model_dump(exclude_unset=True)
    updated_url = await ShortUrlService.update_short_url(db, short_code, **updates)
    if not updated_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return MyResponse(data=updated_url)


@app.delete("/short_url/{short_code}", response_model=MyResponse, summary="刪除短網址")
async def delete_short_url(short_code: str, db: Session = Depends(get_db_session)):
    deleted_url = await ShortUrlService.delete_short_url(db, short_code)
    if not deleted_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return MyResponse


@app.post("/shorten/batch", response_class=StreamingResponse, summary="批量縮短網址")
async def shorten_batch(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db_session)
):
    content = await file.read()
    csv_reader = csv.DictReader(io.StringIO(content.decode("utf-8")))

    # 檢查 CSV 文件是否包含必要的列
    if "origin_url" not in csv_reader.fieldnames:
        raise HTTPException(
            status_code=400, detail="CSV file must contain 'origin_url' column"
        )

    origin_urls = [row["origin_url"] for row in csv_reader]

    # 批量查詢現有的短網址
    existing_short_urls = await ShortUrlService.get_short_url_list(
        db, page=-1, origin_url=origin_urls
    )
    existing_origin_urls = {url.origin_url: url for url in existing_short_urls}

    new_mappings = []
    new_short_urls = []
    existing_short_codes = set(url.short_code for url in existing_short_urls)

    for origin_url in origin_urls:
        if origin_url in existing_origin_urls:
            short_url = existing_origin_urls[origin_url]
        else:
            while True:
                short_code = generate_short_code()
                if short_code not in existing_short_codes:
                    break
            short_url = ShortUrl(origin_url=origin_url, short_code=short_code)
            new_short_urls.append(short_url)
            existing_origin_urls[origin_url] = short_url
            existing_short_codes.add(short_code)

        new_mappings.append(short_url)

    # 批量創建新的短網址，分批次處理以避免過多數據
    if new_short_urls:
        while new_short_urls:
            batch = new_short_urls[:1000]
            successful = False
            while not successful:
                try:
                    await ShortUrlService.create_batch_short_url(db, batch)
                    await db.commit()
                    new_short_urls = new_short_urls[1000:]
                    successful = True
                except IntegrityError as e:
                    await db.rollback()
                    # 處理重複的短碼
                    for url in batch:

                        while True:
                            short_code = generate_short_code()
                            if short_code not in existing_short_codes:
                                url.short_code = short_code
                                existing_short_codes.add(short_code)

                                new_mappings.append(url)
                                break

    # 創建結果的 CSV 文件
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["short_code", "origin_url"])
    writer.writeheader()
    writer.writerows(
        {"short_code": url.short_code, "origin_url": url.origin_url}
        for url in new_mappings
    )
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=result.csv"},
    )
