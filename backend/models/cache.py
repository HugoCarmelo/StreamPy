from sqlalchemy import Integer, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime


class CatalogCache(Base):
    __tablename__ = "catalog_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    cache_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'live_categories', 'vod_categories', 'series_categories', 'live_streams', 'vod_streams', 'series'
    data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON sérialisé
    fetched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="catalog_cache")  # noqa: F821

    __table_args__ = (
        Index("idx_cache_lookup", "profile_id", "cache_type", "expires_at"),
    )
