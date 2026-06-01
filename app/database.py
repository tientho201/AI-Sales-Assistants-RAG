"""
Database connection setup.
Supports both PostgreSQL and SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

db_url = settings.DATABASE_URL
# Supabase connection strings often start with postgres:// which SQLAlchemy 1.4+ deprecated.
# We map it to postgresql:// to ensure standard compatibility.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# If using SQLite, we need connect_args check_same_thread
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True  # Detect and recover from database restarts
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    Database session generator to be used as a FastAPI dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
