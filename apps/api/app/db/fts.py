from sqlalchemy import text
from sqlalchemy.orm import Session


def ensure_fts(session: Session) -> None:
    """Ensure FTS5 virtual table and triggers exist for Entry search"""
    # Create FTS5 virtual table
    session.execute(text("""
        CREATE VIRTUAL TABLE IF NOT EXISTS entry_fts USING fts5(
            title, description, tags, content='entry', content_rowid='id'
        )
    """))

    # Create triggers for automatic indexing
    session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS entry_ai AFTER INSERT ON entry BEGIN
            INSERT INTO entry_fts(rowid, title, description, tags)
            VALUES (new.id, new.title, new.description, new.tags);
        END
    """))

    session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS entry_ad AFTER DELETE ON entry BEGIN
            INSERT INTO entry_fts(entry_fts, rowid, title, description, tags)
            VALUES ('delete', old.id, old.title, old.description, old.tags);
        END
    """))

    session.execute(text("""
        CREATE TRIGGER IF NOT EXISTS entry_au AFTER UPDATE ON entry BEGIN
            INSERT INTO entry_fts(entry_fts, rowid, title, description, tags)
            VALUES ('delete', old.id, old.title, old.description, old.tags);
            INSERT INTO entry_fts(rowid, title, description, tags)
            VALUES (new.id, new.title, new.description, new.tags);
        END
    """))

    session.commit()
