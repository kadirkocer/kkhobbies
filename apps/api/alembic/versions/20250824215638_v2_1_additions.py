"""v2.1 additions: hobby extras and EntryTag table

Revision ID: v2_1_additions
Revises: e57a1c1a5dbf
Create Date: 2025-08-24 21:56:38
"""


from alembic import op

# revision identifiers, used by Alembic.
revision = "v2_1_additions"
down_revision = "e57a1c1a5dbf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.exec_driver_sql("PRAGMA foreign_keys=ON;")

    # Hobby extra columns and indexes
    conn.exec_driver_sql("ALTER TABLE hobby ADD COLUMN slug TEXT;")
    conn.exec_driver_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_hobby_slug ON hobby(slug);"
    )
    conn.exec_driver_sql("ALTER TABLE hobby ADD COLUMN description TEXT;")
    conn.exec_driver_sql("ALTER TABLE hobby ADD COLUMN sort_order INTEGER DEFAULT 0;")
    conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_hobby_parent ON hobby(parent_id);"
    )

    # EntryTag table
    conn.exec_driver_sql(
        """
        CREATE TABLE IF NOT EXISTS entrytag (
            id INTEGER PRIMARY KEY,
            entry_id INTEGER NOT NULL REFERENCES entry(id) ON DELETE CASCADE,
            tag TEXT NOT NULL
        );
        """
    )
    conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_entrytag_entry ON entrytag(entry_id);"
    )
    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_entrytag_tag ON entrytag(tag);")


def downgrade() -> None:
    conn = op.get_bind()
    # SQLite doesn't support dropping columns; leave columns as-is.
    # Optionally drop indexes and entrytag table.
    conn.exec_driver_sql("DROP TABLE IF EXISTS entrytag;")
    conn.exec_driver_sql("DROP INDEX IF EXISTS ux_hobby_slug;")
    conn.exec_driver_sql("DROP INDEX IF EXISTS ix_hobby_parent;")
