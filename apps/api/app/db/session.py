import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from ..models.base import Base


DATABASE_URL = f"sqlite:///{os.getenv('DB_PATH', '../../data/app.db')}"

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


def init_db():
    """Initialize database with tables and FTS5 virtual table"""
    Base.metadata.create_all(bind=engine)
    
    # Create FTS5 virtual table and triggers
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS entry_fts USING fts5(
                title, description, tags, content='entry', content_rowid='id'
            )
        """))
        
        # FTS5 triggers for automatic indexing
        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS entry_ai AFTER INSERT ON entry BEGIN
                INSERT INTO entry_fts(rowid, title, description, tags)
                VALUES (new.id, new.title, new.description, new.tags);
            END
        """))
        
        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS entry_ad AFTER DELETE ON entry BEGIN
                INSERT INTO entry_fts(entry_fts, rowid, title, description, tags)
                VALUES ('delete', old.id, old.title, old.description, old.tags);
            END
        """))
        
        connection.execute(text("""
            CREATE TRIGGER IF NOT EXISTS entry_au AFTER UPDATE ON entry BEGIN
                INSERT INTO entry_fts(entry_fts, rowid, title, description, tags)
                VALUES ('delete', old.id, old.title, old.description, old.tags);
                INSERT INTO entry_fts(rowid, title, description, tags)
                VALUES (new.id, new.title, new.description, new.tags);
            END
        """))
        
        connection.commit()


def get_session() -> Session:
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()