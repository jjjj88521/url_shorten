from datetime import datetime
from pydantic import BaseModel


class AccessLogBase(BaseModel):
    short_code: str
    ip_address: str
    user_agent: str


class AccessLogCreate(AccessLogBase):
    pass


class AccessLog(AccessLogBase):
    id: int
    accessed_at: datetime

    class Config:
        orm_mode = True
