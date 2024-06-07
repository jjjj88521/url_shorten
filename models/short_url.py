from typing import TYPE_CHECKING, List
from db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, func, text
from sqlalchemy.orm import mapped_column, Mapped, relationship


class ShortUrl(Base):
    __tablename__ = "short_urls"

    short_code: Mapped[str] = mapped_column(
        String(10), primary_key=True, unique=True, index=True
    )
    origin_url: Mapped[str] = mapped_column(Text)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    last_click_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    expired_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # Relationship to AccessLog
    access_logs: Mapped[List["AccessLog"]] = relationship(
        "AccessLog", back_populates="short_url"
    )


if TYPE_CHECKING:
    from models.access_log import AccessLog
