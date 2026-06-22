from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.favorites import Favorite
from services.auth import get_current_profile_id

router = APIRouter(prefix="/favorites", tags=["favorites"])


class FavoriteIn(BaseModel):
    item_type: str   # 'live', 'vod', 'series'
    item_id: int
    item_name: str
    item_logo: Optional[str] = None


@router.get("")
async def list_favorites(
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(Favorite.profile_id == profile_id)
    )
    favs = result.scalars().all()
    return [
        {
            "id": f.id,
            "item_type": f.item_type,
            "item_id": f.item_id,
            "item_name": f.item_name,
            "item_logo": f.item_logo,
            "added_at": f.added_at,
        }
        for f in favs
    ]


@router.post("", status_code=201)
async def add_favorite(
    body: FavoriteIn,
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    if body.item_type not in ("live", "vod", "series"):
        raise HTTPException(status_code=422, detail="item_type must be live, vod or series")

    # Check duplicate
    existing = await db.execute(
        select(Favorite).where(
            Favorite.profile_id == profile_id,
            Favorite.item_type == body.item_type,
            Favorite.item_id == body.item_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already in favorites")

    fav = Favorite(
        profile_id=profile_id,
        item_type=body.item_type,
        item_id=body.item_id,
        item_name=body.item_name,
        item_logo=body.item_logo,
    )
    db.add(fav)
    await db.flush()
    return {"id": fav.id, "item_id": fav.item_id}


@router.delete("/{item_type}/{item_id}", status_code=204)
async def remove_favorite(
    item_type: str,
    item_id: int,
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(Favorite).where(
            Favorite.profile_id == profile_id,
            Favorite.item_type == item_type,
            Favorite.item_id == item_id,
        )
    )
