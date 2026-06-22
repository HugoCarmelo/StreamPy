from sqlalchemy import Integer, String, DateTime, Boolean, UniqueConstraint, Index, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime


class WatchHistory(Base):
    __tablename__ = "watch_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(10), nullable=False)   # 'live', 'vod', 'series'
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)        # stream_id ou episode id Xtream
    series_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    episode_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    progress_sec: Mapped[int] = mapped_column(Integer, default=0)        # timestamp en secondes
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    watched_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="watch_history")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("profile_id", "item_type", "item_id", name="uq_history"),
        Index("idx_history_recent", "profile_id", "watched_at"),
    )
