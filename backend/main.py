from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db
from routers import profiles, auth

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown — nothing to do for SQLite


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/api/docs" if settings.environment == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# CORS — restricted to local network / VPN origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Routers
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.app_version}
