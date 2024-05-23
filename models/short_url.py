from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func, text
from sqlalchemy.orm import mapped_column, Mapped


class ShortUrl(Base):
    __tablename__ = "short_url"

    short_code: Mapped[str] = mapped_column(
        String(10), primary_key=True, unique=True, index=True
    )
    origin_url: Mapped[str] = mapped_column(String, index=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    last_click_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
