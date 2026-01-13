import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "contacts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        company TEXT,
        position TEXT,
        linkedin TEXT,
        tags TEXT, -- comma separated
        notes TEXT,
        last_contact_date TEXT,
        relationship_status TEXT DEFAULT 'active'
    )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
