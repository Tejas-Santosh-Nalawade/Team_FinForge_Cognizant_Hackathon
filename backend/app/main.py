import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.app.api.v1.router import api_v1_router
    from backend.app.config import settings
    from backend.db.session import init_db
except ModuleNotFoundError:
    from app.api.v1.router import api_v1_router
    from app.config import settings
    from db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite/Postgres DB tables
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cognizant NPN • Enterprise FP&A & Financial Statement Audit Assurance Suite (ARCH-SPEC-WP514)",
    lifespan=lifespan
)

# CORS configuration for local frontend development and Vercel deployments.
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if not allowed_origins:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API endpoints
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health")
def healthcheck():
    return {"status": "healthy", "database": "connected"}