from typing import TYPE_CHECKING
from db.database import Base
from sqlalchemy import ForeignKey, Integer, String, DateTime, Text, func, text
from sqlalchemy.orm import mapped_column, Mapped, relationship


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    short_code: Mapped[str] = mapped_column(
        String(10), ForeignKey("short_urls.short_code"), index=True
    )
    ip_address: Mapped[str] = mapped_column(Text, nullable=False)
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)
    accessed_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    # Relationship to ShortURL
    short_url: Mapped["ShortUrl"] = relationship(
        "ShortUrl", back_populates="access_logs"
    )


# 避免循環導入
if TYPE_CHECKING:
    from models.short_url import ShortUrl
else:
    ShortUrl = "ShortUrl"
