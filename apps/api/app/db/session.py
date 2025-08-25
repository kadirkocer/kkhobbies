import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def _database_url() -> str:
    # Default to repo-local data path when DB_PATH not provided
    db_path = os.getenv("DB_PATH", "data/app.db")
    if not os.path.isabs(db_path):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        db_path = os.path.abspath(os.path.join(base, db_path))
    return f"sqlite:///{db_path}"

DATABASE_URL = _database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=os.getenv("APP_ENV") == "development",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()




def get_session():
    """Get database session dependency"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
