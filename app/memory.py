import sqlite3
import threading
from datetime import datetime
from .config import DB_PATH

class Memory:
    def __init__(self, path=DB_PATH):
        self.path = str(path)
        self.lock = threading.Lock()
        self._init()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init(self):
        with self._connect() as db:
            db.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)
            db.execute("""
            CREATE TABLE IF NOT EXISTS memories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """)
            db.commit()

    def add_message(self, role, content):
        with self.lock, self._connect() as db:
            db.execute(
                "INSERT INTO messages(role,content,created_at) VALUES(?,?,?)",
                (role, content, datetime.now().isoformat(timespec="seconds"))
            )
            db.commit()

    def recent_messages(self, limit=20):
        with self._connect() as db:
            rows = db.execute(
                "SELECT role,content FROM messages ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return list(reversed(rows))

    def set_memory(self, key, value):
        now = datetime.now().isoformat(timespec="seconds")
        with self.lock, self._connect() as db:
            db.execute("""
            INSERT INTO memories(key,value,created_at,updated_at)
            VALUES(?,?,?,?)
            ON CONFLICT(key) DO UPDATE SET
                value=excluded.value,
                updated_at=excluded.updated_at
            """, (key, value, now, now))
            db.commit()

    def get_memories(self, limit=50):
        with self._connect() as db:
            return db.execute(
                "SELECT key,value FROM memories ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            ).fetchall()

    def clear_messages(self):
        with self.lock, self._connect() as db:
            db.execute("DELETE FROM messages")
            db.commit()
