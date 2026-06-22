from sqlalchemy import Integer, String, DateTime, UniqueConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'live', 'vod', 'series'
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)       # stream_id Xtream
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_logo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="favorites")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("profile_id", "item_type", "item_id", name="uq_favorite"),
    )
