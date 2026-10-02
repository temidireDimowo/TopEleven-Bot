"""SQLite-backed session history store."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional


@dataclass
class FarmingSession:
    id: int
    started_at: str
    ended_at: Optional[str]
    mode: str
    greens_earned: int
    cycles_completed: int
    errors: int


class SessionStore:

    def __init__(self, db_path: str = "logs/sessions.db"):
        self._db = Path(db_path)
        self._db.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    mode TEXT NOT NULL DEFAULT 'farm_greens',
                    greens_earned INTEGER DEFAULT 0,
                    cycles_completed INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def start_session(self, mode: str) -> int:
        with sqlite3.connect(self._db) as conn:
            cur = conn.execute(
                "INSERT INTO sessions (started_at, mode) VALUES (?, ?)",
                (datetime.now().isoformat(), mode)
            )
            conn.commit()
            return cur.lastrowid

    def end_session(self, session_id: int, greens: int, cycles: int, errors: int) -> None:
        with sqlite3.connect(self._db) as conn:
            conn.execute(
                "UPDATE sessions SET ended_at=?, greens_earned=?, cycles_completed=?, errors=? WHERE id=?",
                (datetime.now().isoformat(), greens, cycles, errors, session_id)
            )
            conn.commit()

    def get_today_greens(self) -> int:
        today = date.today().isoformat()
        with sqlite3.connect(self._db) as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(greens_earned), 0) FROM sessions WHERE started_at LIKE ?",
                (f"{today}%",)
            ).fetchone()
            return row[0] if row else 0

    def get_recent_sessions(self, limit: int = 10) -> List[FarmingSession]:
        with sqlite3.connect(self._db) as conn:
            rows = conn.execute(
                "SELECT id, started_at, ended_at, mode, greens_earned, cycles_completed, errors "
                "FROM sessions ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [FarmingSession(*r) for r in rows]

    def get_total_greens(self) -> int:
        with sqlite3.connect(self._db) as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(greens_earned), 0) FROM sessions"
            ).fetchone()
            return row[0] if row else 0
