from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func


class ShortUrl(Base):
    __tablename__ = "short_url"
    short_code = Column(String(10), nullable=False, primary_key=True, unique=True)
    origin_url = Column(String, nullable=False, index=True)
    click_count = Column(Integer, default=0)
    non_repeat_click_count = Column(Integer, default=0)
    created_at = Column(DateTime(), default=func.now())
    updated_at = Column(DateTime(), default=func.now(), onupdate=func.now())
