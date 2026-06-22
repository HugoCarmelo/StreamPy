"""
JWT access/refresh tokens + PIN hashing (SHA-256 + salt).
"""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from config import get_settings
from models.profile import RefreshToken

settings = get_settings()


# ---------------------------------------------------------------------------
# PIN helpers
# ---------------------------------------------------------------------------

def hash_pin(pin: str) -> tuple[str, str]:
    """Return (pin_hash, pin_salt) for storage."""
    salt = secrets.token_hex(32)
    pin_hash = hashlib.sha256(f"{salt}{pin}".encode()).hexdigest()
    return pin_hash, salt


def verify_pin(pin: str, pin_hash: str, pin_salt: str) -> bool:
    """Verify a PIN against stored hash+salt."""
    computed = hashlib.sha256(f"{pin_salt}{pin}".encode()).hexdigest()
    return secrets.compare_digest(computed, pin_hash)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(profile_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_expire_minutes)
    payload = {
        "sub": str(profile_id),
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token() -> str:
    """Generate a random refresh token (opaque)."""
    return secrets.token_hex(48)


def hash_token(token: str) -> str:
    """SHA-256 hash of a token for DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def decode_access_token(token: str) -> int | None:
    """Decode JWT and return profile_id, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            return None
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Refresh token DB helpers
# ---------------------------------------------------------------------------

async def store_refresh_token(db: AsyncSession, profile_id: int, token: str) -> None:
    expires = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    rt = RefreshToken(
        profile_id=profile_id,
        token_hash=hash_token(token),
        expires_at=expires,
    )
    db.add(rt)
    await db.flush()


async def validate_refresh_token(db: AsyncSession, token: str) -> int | None:
    """Return profile_id if token is valid and not expired, else None."""
    token_hash = hash_token(token)
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expires_at > now,
        )
    )
    rt = result.scalar_one_or_none()
    return rt.profile_id if rt else None


async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    """Delete a refresh token from DB (logout)."""
    token_hash = hash_token(token)
    await db.execute(
        delete(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
