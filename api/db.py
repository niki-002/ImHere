from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .core.config import settings


DATABASE_URL = settings.database_url

db_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

db_session = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=db_engine,
)

session = db_session()

def get_db() -> Generator[Session, None, None]:
    db = session
    try:
        yield db
    finally:
        db.close()
