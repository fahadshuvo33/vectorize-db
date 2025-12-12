# backend/app/database.py
"""
Database configuration using SQLModel (not raw SQLAlchemy).
SQLModel is a wrapper around SQLAlchemy that works with Pydantic.
"""

from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.SUPABASE_DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Test connections before using
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300,
)


def init_db() -> None:
    """
    Initialize database tables.
    Call this on application startup if you want auto-migration.
    Note: For production, use Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()