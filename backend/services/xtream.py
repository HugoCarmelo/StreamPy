"""
Xtream Codes API client.
Fetches data from the IPTV provider and caches results in SQLite.
"""
import json
import httpx
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.profile import Profile, XtreamCredentials
from models.cache import CatalogCache
from services.crypto import decrypt

# Cache TTL
CACHE_TTL_CATEGORIES = timedelta(hours=6)
CACHE_TTL_STREAMS = timedelta(hours=2)


async def _get_credentials(profile_id: int, db: AsyncSession) -> dict:
    """Decrypt and return Xtream credentials for a profile."""
    result = await db.execute(
        select(XtreamCredentials).where(XtreamCredentials.profile_id == profile_id)
    )
    creds = result.scalar_one_or_none()
    if not creds:
        raise ValueError("No credentials found for this profile")
    return {
        "server_url": decrypt(creds.server_url_enc).rstrip("/"),
        "username": decrypt(creds.username_enc),
        "password": decrypt(creds.password_enc),
    }


def _xtream_url(server_url: str, username: str, password: str, action: str) -> str:
    return f"{server_url}/player_api.php?username={username}&password={password}&action={action}"


async def _fetch_from_cache(profile_id: int, cache_type: str, db: AsyncSession):
    """Return cached data if still valid, else None."""
    now = datetime.utcnow()
    result = await db.execute(
        select(CatalogCache).where(
            CatalogCache.profile_id == profile_id,
            CatalogCache.cache_type == cache_type,
            CatalogCache.expires_at > now,
        )
    )
    entry = result.scalar_one_or_none()
    if entry:
        return json.loads(entry.data)
    return None


async def _save_to_cache(
    profile_id: int, cache_type: str, data: list | dict, ttl: timedelta, db: AsyncSession
):
    """Upsert cache entry."""
    # Delete old entry
    await db.execute(
        delete(CatalogCache).where(
            CatalogCache.profile_id == profile_id,
            CatalogCache.cache_type == cache_type,
        )
    )
    now = datetime.utcnow()
    entry = CatalogCache(
        profile_id=profile_id,
        cache_type=cache_type,
        data=json.dumps(data),
        fetched_at=now,
        expires_at=now + ttl,
    )
    db.add(entry)


async def _xtream_get(url: str) -> list | dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_live_categories(profile_id: int, db: AsyncSession) -> list:
    cache_type = "live_categories"
    cached = await _fetch_from_cache(profile_id, cache_type, db)
    if cached is not None:
        return cached

    creds = await _get_credentials(profile_id, db)
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], "get_live_categories")
    data = await _xtream_get(url)
    await _save_to_cache(profile_id, cache_type, data, CACHE_TTL_CATEGORIES, db)
    return data


async def get_live_streams(profile_id: int, db: AsyncSession, category_id: str | None = None) -> list:
    cache_type = f"live_streams_{category_id or 'all'}"
    cached = await _fetch_from_cache(profile_id, cache_type, db)
    if cached is not None:
        return cached

    creds = await _get_credentials(profile_id, db)
    action = "get_live_streams"
    if category_id:
        action += f"&category_id={category_id}"
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], action)
    data = await _xtream_get(url)
    await _save_to_cache(profile_id, cache_type, data, CACHE_TTL_STREAMS, db)
    return data


async def get_vod_categories(profile_id: int, db: AsyncSession) -> list:
    cache_type = "vod_categories"
    cached = await _fetch_from_cache(profile_id, cache_type, db)
    if cached is not None:
        return cached

    creds = await _get_credentials(profile_id, db)
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], "get_vod_categories")
    data = await _xtream_get(url)
    await _save_to_cache(profile_id, cache_type, data, CACHE_TTL_CATEGORIES, db)
    return data


async def get_vod_streams(profile_id: int, db: AsyncSession, category_id: str | None = None) -> list:
    cache_type = f"vod_streams_{category_id or 'all'}"
    cached = await _fetch_from_cache(profile_id, cache_type, db)
    if cached is not None:
        return cached

    creds = await _get_credentials(profile_id, db)
    action = "get_vod_streams"
    if category_id:
        action += f"&category_id={category_id}"
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], action)
    data = await _xtream_get(url)
    await _save_to_cache(profile_id, cache_type, data, CACHE_TTL_STREAMS, db)
    return data


async def get_series_categories(profile_id: int, db: AsyncSession) -> list:
    cache_type = "series_categories"
    cached = await _fetch_from_cache(profile_id, cache_type, db)
    if cached is not None:
        return cached

    creds = await _get_credentials(profile_id, db)
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], "get_series_categories")
    data = await _xtream_get(url)
    await _save_to_cache(profile_id, cache_type, data, CACHE_TTL_CATEGORIES, db)
    return data


async def get_series(profile_id: int, db: AsyncSession, category_id: str | None = None) -> list:
    cache_type = f"series_{category_id or 'all'}"
    cached = await _fetch_from_cache(profile_id, cache_type, db)
    if cached is not None:
        return cached

    creds = await _get_credentials(profile_id, db)
    action = "get_series"
    if category_id:
        action += f"&category_id={category_id}"
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], action)
    data = await _xtream_get(url)
    await _save_to_cache(profile_id, cache_type, data, CACHE_TTL_STREAMS, db)
    return data


async def get_series_info(profile_id: int, series_id: int, db: AsyncSession) -> dict:
    cache_type = f"series_info_{series_id}"
    cached = await _fetch_from_cache(profile_id, cache_type, db)
    if cached is not None:
        return cached

    creds = await _get_credentials(profile_id, db)
    action = f"get_series_info&series_id={series_id}"
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], action)
    data = await _xtream_get(url)
    await _save_to_cache(profile_id, cache_type, data, CACHE_TTL_STREAMS, db)
    return data


async def get_vod_info(profile_id: int, vod_id: int, db: AsyncSession) -> dict:
    creds = await _get_credentials(profile_id, db)
    action = f"get_vod_info&vod_id={vod_id}"
    url = _xtream_url(creds["server_url"], creds["username"], creds["password"], action)
    return await _xtream_get(url)


async def get_stream_url(
    profile_id: int,
    stream_type: str,
    stream_id: int,
    db: AsyncSession,
    container_extension: str | None = None,
) -> str:
    """Build the direct stream URL for live/vod/series."""
    creds = await _get_credentials(profile_id, db)
    base = creds["server_url"]
    u = creds["username"]
    p = creds["password"]

    if stream_type == "live":
        return f"{base}/live/{u}/{p}/{stream_id}.m3u8"

    elif stream_type == "vod":
        # Récupérer l'extension réelle depuis l'info VOD
        ext = container_extension
        if not ext:
            try:
                info = await get_vod_info(profile_id, stream_id, db)
                ext = info.get("movie_data", {}).get("container_extension", "mp4")
            except Exception:
                ext = "mp4"
        return f"{base}/movie/{u}/{p}/{stream_id}.{ext}"

    elif stream_type == "series":
        # stream_id est l'episode_id ; container_extension vient de l'épisode
        ext = container_extension or "mp4"
        return f"{base}/series/{u}/{p}/{stream_id}.{ext}"

    else:
        raise ValueError(f"Unknown stream type: {stream_type}")
