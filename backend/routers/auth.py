from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.profile import Profile
from schemas.profile import ProfileAuthRequest, TokenResponse, RefreshRequest, LogoutRequest
from services.auth import (
    verify_pin,
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    validate_refresh_token,
    revoke_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login/{profile_id}", response_model=TokenResponse)
async def login(
    profile_id: int,
    body: ProfileAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check PIN if profile has one
    if profile.pin_hash is not None:
        if not body.pin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="PIN required",
            )
        if not verify_pin(body.pin, profile.pin_hash, profile.pin_salt):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN",
            )

    access_token = create_access_token(profile.id)
    refresh_token = create_refresh_token()
    await store_refresh_token(db, profile.id, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        profile_id=profile.id,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    profile_id = await validate_refresh_token(db, body.refresh_token)
    if not profile_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Rotate refresh token
    await revoke_refresh_token(db, body.refresh_token)
    new_refresh = create_refresh_token()
    await store_refresh_token(db, profile_id, new_refresh)

    return TokenResponse(
        access_token=create_access_token(profile_id),
        refresh_token=new_refresh,
        profile_id=profile_id,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    await revoke_refresh_token(db, body.refresh_token)
