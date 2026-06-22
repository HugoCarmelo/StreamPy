from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.profile import Profile, XtreamCredentials
from schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse, ProfileListItem
from services.crypto import encrypt
from services.auth import hash_pin

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _profile_to_response(p: Profile) -> ProfileResponse:
    return ProfileResponse(
        id=p.id,
        name=p.name,
        avatar=p.avatar,
        has_pin=p.pin_hash is not None,
        created_at=p.created_at,
    )


@router.get("", response_model=list[ProfileListItem])
async def list_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).order_by(Profile.id))
    profiles = result.scalars().all()
    return [
        ProfileListItem(
            id=p.id,
            name=p.name,
            avatar=p.avatar,
            has_pin=p.pin_hash is not None,
        )
        for p in profiles
    ]


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(body: ProfileCreate, db: AsyncSession = Depends(get_db)):
    # Hash PIN if provided
    pin_hash, pin_salt = (None, None)
    if body.pin:
        pin_hash, pin_salt = hash_pin(body.pin)

    profile = Profile(
        name=body.name,
        avatar=body.avatar,
        pin_hash=pin_hash,
        pin_salt=pin_salt,
    )
    db.add(profile)
    await db.flush()  # Get profile.id

    creds = XtreamCredentials(
        profile_id=profile.id,
        server_url_enc=encrypt(body.server_url),
        username_enc=encrypt(body.username),
        password_enc=encrypt(body.password),
    )
    db.add(creds)
    return _profile_to_response(profile)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _profile_to_response(profile)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int, body: ProfileUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if body.name is not None:
        profile.name = body.name
    if body.avatar is not None:
        profile.avatar = body.avatar
    if body.pin is not None:
        profile.pin_hash, profile.pin_salt = hash_pin(body.pin)

    # Update credentials if any field provided
    if any(v is not None for v in [body.server_url, body.username, body.password]):
        creds_result = await db.execute(
            select(XtreamCredentials).where(XtreamCredentials.profile_id == profile_id)
        )
        creds = creds_result.scalar_one_or_none()
        if creds:
            if body.server_url:
                creds.server_url_enc = encrypt(body.server_url)
            if body.username:
                creds.username_enc = encrypt(body.username)
            if body.password:
                creds.password_enc = encrypt(body.password)

    return _profile_to_response(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    await db.delete(profile)
