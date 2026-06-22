from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from services.xtream import (
    get_live_categories, get_live_streams,
    get_vod_categories, get_vod_streams,
    get_series_categories, get_series,
    get_series_info, get_vod_info, get_stream_url,
)
from services.auth import get_current_profile_id

router = APIRouter(prefix="/catalog", tags=["catalog"])


# ---------------------------------------------------------------------------
# Live TV
# ---------------------------------------------------------------------------

@router.get("/live/categories")
async def live_categories(
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_live_categories(profile_id, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/live/streams")
async def live_streams(
    category_id: Optional[str] = Query(None),
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_live_streams(profile_id, db, category_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------------------------------------------------------------------------
# VOD
# ---------------------------------------------------------------------------

@router.get("/vod/categories")
async def vod_categories(
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_vod_categories(profile_id, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/vod/streams")
async def vod_streams(
    category_id: Optional[str] = Query(None),
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_vod_streams(profile_id, db, category_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/vod/{vod_id}/info")
async def vod_info(
    vod_id: int,
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_vod_info(profile_id, vod_id, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------------------------------------------------------------------------
# Series
# ---------------------------------------------------------------------------

@router.get("/series/categories")
async def series_categories(
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_series_categories(profile_id, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/series")
async def series_list(
    category_id: Optional[str] = Query(None),
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_series(profile_id, db, category_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/series/{series_id}/info")
async def series_info(
    series_id: int,
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await get_series_info(profile_id, series_id, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ---------------------------------------------------------------------------
# Stream URL (pour le player)
# ---------------------------------------------------------------------------

@router.get("/stream-url")
async def stream_url(
    stream_type: str = Query(..., pattern="^(live|vod|series)$"),
    stream_id: int = Query(...),
    profile_id: int = Depends(get_current_profile_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        url = await get_stream_url(profile_id, stream_type, stream_id, db)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
