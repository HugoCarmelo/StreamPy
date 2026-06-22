from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.history import WatchHistory
from services.auth import get_current_profile_id

router = APIRouter(prefix="/history", tags=["history"])


class HistoryUpsert(BaseModel):
    item_type: str        # 'live', 'vod', 'series'
    item_id: int
    series_id: Optional[int] = None
    episode_id: Optional[int] = None
    progress_sec: int = 0
    duration_sec: Optional[int] = None
    completed: bool = False


@router.get("")
async def list_history(
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WatchHistory)
        .where(WatchHistory.profile_id == profile_id)
        .order_by(WatchHistory.watched_at.desc())
        .limit(100)
    )
    items = result.scalars().all()
    return [
        {
            "id": h.id,
            "item_type": h.item_type,
            "item_id": h.item_id,
            "series_id": h.series_id,
            "episode_id": h.episode_id,
            "progress_sec": h.progress_sec,
            "duration_sec": h.duration_sec,
            "completed": h.completed,
            "watched_at": h.watched_at,
        }
        for h in items
    ]


@router.put("", status_code=200)
async def upsert_history(
    body: HistoryUpsert,
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    """Create or update a watch history entry (upsert by profile+type+item)."""
    existing = await db.execute(
        select(WatchHistory).where(
            WatchHistory.profile_id == profile_id,
            WatchHistory.item_type == body.item_type,
            WatchHistory.item_id == body.item_id,
        )
    )
    entry = existing.scalar_one_or_none()

    if entry:
        entry.progress_sec = body.progress_sec
        entry.duration_sec = body.duration_sec
        entry.completed = body.completed
        if body.series_id is not None:
            entry.series_id = body.series_id
        if body.episode_id is not None:
            entry.episode_id = body.episode_id
    else:
        entry = WatchHistory(
            profile_id=profile_id,
            item_type=body.item_type,
            item_id=body.item_id,
            series_id=body.series_id,
            episode_id=body.episode_id,
            progress_sec=body.progress_sec,
            duration_sec=body.duration_sec,
            completed=body.completed,
        )
        db.add(entry)

    await db.flush()
    return {"item_id": entry.item_id, "progress_sec": entry.progress_sec}
