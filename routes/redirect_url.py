from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from db.database import get_db_session as get_db
from schemas.short_url import ShortUrl
from services.access_log import AccessLogService
from services.short_url import ShortUrlService
from fastapi.responses import RedirectResponse
from fastapi.requests import Request

app = APIRouter()


# 異步記錄訪問紀錄
async def log_access(
    db: Session, short_code: str, ip_address: str, user_agent_str: str
):
    await AccessLogService.create_access_log(
        async_session=db,
        short_code=short_code,
        ip_address=ip_address,
        user_agent=user_agent_str,
    )


@app.get(
    "/{short_code}",
    summary="短網址轉址",
)
async def redirect_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # 根據短網址獲取原始網址
    short_url = await ShortUrlService.get_short_url(db, short_code=short_code)
    # 如果短網址不存在，則返回404
    if not short_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # 如果 expired_at 過期，則返回 404
    if short_url.expired_at and short_url.expired_at < func.now():
        raise HTTPException(status_code=404, detail="Short URL expired")

    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")

    # 異步記錄訪問紀錄
    background_tasks.add_task(log_access, db, short_code, ip_address, user_agent)

    # 設置Cache-Control頭來防止瀏覽器緩存重定向
    headers = {"Cache-Control": "no-store"}

    # 短網址存在，click_count 加 1
    await ShortUrlService.update_short_url(
        db,
        short_url.short_code,
        click_count=short_url.click_count + 1,
        last_click_at=func.now(),
    )
    return RedirectResponse(url=short_url.origin_url, status_code=302, headers=headers)
