from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Profile schemas
# ---------------------------------------------------------------------------

class ProfileCreate(BaseModel):
    name: str
    avatar: Optional[str] = None
    pin: Optional[str] = None          # PIN en clair, haché côté serveur
    server_url: str
    username: str
    password: str

    @field_validator("pin")
    @classmethod
    def pin_must_be_digits(cls, v):
        if v is not None and (not v.isdigit() or len(v) not in (4, 6)):
            raise ValueError("PIN must be 4 or 6 digits")
        return v


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    pin: Optional[str] = None
    server_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @field_validator("pin")
    @classmethod
    def pin_must_be_digits(cls, v):
        if v is not None and (not v.isdigit() or len(v) not in (4, 6)):
            raise ValueError("PIN must be 4 or 6 digits")
        return v


class ProfileResponse(BaseModel):
    id: int
    name: str
    avatar: Optional[str]
    has_pin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileListItem(BaseModel):
    id: int
    name: str
    avatar: Optional[str]
    has_pin: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class ProfileAuthRequest(BaseModel):
    pin: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    profile_id: int


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
