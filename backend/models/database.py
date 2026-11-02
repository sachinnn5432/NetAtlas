"""Database engine and session management for NetAtlas."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.config.settings import DATABASE_URL
from backend.models.db_models import Base
from backend.config.logging_config import logger

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    """Initializes tables and indexes in the database."""
    logger.info("Initializing database schema at: %s", DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema successfully created.")

def get_db():
    """Context-managed or generator session provider."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

