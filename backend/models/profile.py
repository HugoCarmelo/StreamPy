from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(100), nullable=True)  # emoji ou chemin icône
    pin_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)   # SHA-256 + sel
    pin_salt: Mapped[str | None] = mapped_column(String(64), nullable=True)   # sel aléatoire 32 bytes hex
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    credentials: Mapped[list["XtreamCredentials"]] = relationship(
        "XtreamCredentials", back_populates="profile", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="profile", cascade="all, delete-orphan"
    )
    watch_history: Mapped[list["WatchHistory"]] = relationship(
        "WatchHistory", back_populates="profile", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="profile", cascade="all, delete-orphan"
    )
    catalog_cache: Mapped[list["CatalogCache"]] = relationship(
        "CatalogCache", back_populates="profile", cascade="all, delete-orphan"
    )


class XtreamCredentials(Base):
    __tablename__ = "xtream_credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    server_url_enc: Mapped[str] = mapped_column(String, nullable=False)   # AES-256-GCM chiffré
    username_enc: Mapped[str] = mapped_column(String, nullable=False)     # AES-256-GCM chiffré
    password_enc: Mapped[str] = mapped_column(String, nullable=False)     # AES-256-GCM chiffré
    last_verified: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="credentials")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)  # SHA-256 du refresh token
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="refresh_tokens")
