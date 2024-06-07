from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from datetime import datetime


# 基礎的短網址模型
class ShortUrlBase(BaseModel):
    origin_url: HttpUrl

    @field_validator("origin_url")
    def convert_httpurl_to_str(cls, v):
        return str(v)


# 建立短網址的模型
class ShortUrlCreate(ShortUrlBase):
    pass


# 更新短網址的模型
class ShortUrlUpdate(BaseModel):
    origin_url: Optional[HttpUrl] = None
    expired_at: Optional[datetime] = None

    @field_validator("origin_url")
    def convert_httpurl_to_str(cls, v):
        return str(v)


# 完整的短網址模型
class ShortUrl(ShortUrlBase):
    short_code: str
    click_count: int
    last_click_at: Optional[datetime]
    expired_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),  # 日期時間格式化
        }
