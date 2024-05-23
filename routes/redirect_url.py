from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from db.database import get_db_session as get_db
from schemas.short_url import ShortUrl as ShortUrlSchema
from services.short_url import ShortUrlService
from fastapi.responses import RedirectResponse

app = APIRouter()


@app.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=302,
    summary="短網址轉址",
)
async def redirect_url(short_code: str, db: Session = Depends(get_db)):
    # 根據短網址獲取原始網址
    short_url = await ShortUrlService.get_short_url(db, short_code=short_code)
    # 如果短網址不存在，則返回404
    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # 短網址存在，click_count 加 1
    await ShortUrlService.update_short_url(
        db,
        short_url.short_code,
        click_count=short_url.click_count + 1,
        last_click_at=func.now(),
    )
    return short_url.origin_url
