import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

try:
    from backend.app.config import settings
    from backend.db.models import Base
except ModuleNotFoundError:
    from app.config import settings
    from db.models import Base

# Database engine initialization
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables in the database if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
