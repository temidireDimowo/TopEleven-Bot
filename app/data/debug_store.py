"""SQLite-backed debug event store."""

import sqlite3
import zipfile
import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class DetectionEvent:
    id: int
    timestamp: str
    class_name: str
    confidence: float
    found: bool
    point_x: Optional[int]
    point_y: Optional[int]
    detection_method: str
    duration_ms: float
    screenshot_path: Optional[str]


class DebugStore:

    def __init__(self, db_path: str = "logs/debug.db"):
        self._db = Path(db_path)
        self._db.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS detection_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    confidence REAL DEFAULT 0,
                    found INTEGER DEFAULT 0,
                    point_x INTEGER,
                    point_y INTEGER,
                    detection_method TEXT DEFAULT 'unknown',
                    duration_ms REAL DEFAULT 0,
                    screenshot_path TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON detection_events(timestamp)
            """)
            conn.commit()

    def record(
        self,
        class_name: str,
        confidence: float,
        found: bool,
        point=None,
        detection_method: str = "unknown",
        duration_ms: float = 0.0,
        screenshot_path: Optional[str] = None,
    ) -> None:
        px, py = (int(point[0]), int(point[1])) if point else (None, None)
        with sqlite3.connect(self._db) as conn:
            conn.execute(
                "INSERT INTO detection_events "
                "(timestamp, class_name, confidence, found, point_x, point_y, "
                "detection_method, duration_ms, screenshot_path) VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    datetime.datetime.now().isoformat(),
                    class_name, confidence, int(found), px, py,
                    detection_method, duration_ms, screenshot_path,
                )
            )
            conn.commit()

    def get_recent(self, limit: int = 100) -> List[DetectionEvent]:
        with sqlite3.connect(self._db) as conn:
            rows = conn.execute(
                "SELECT id, timestamp, class_name, confidence, found, point_x, point_y, "
                "detection_method, duration_ms, screenshot_path "
                "FROM detection_events ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [DetectionEvent(*r) for r in rows]

    def get_stats(self) -> dict:
        with sqlite3.connect(self._db) as conn:
            total = conn.execute("SELECT COUNT(*) FROM detection_events").fetchone()[0]
            found = conn.execute(
                "SELECT COUNT(*) FROM detection_events WHERE found=1"
            ).fetchone()[0]
            avg_ms = conn.execute(
                "SELECT AVG(duration_ms) FROM detection_events"
            ).fetchone()[0] or 0.0
        return {
            "total": total,
            "found": found,
            "not_found": total - found,
            "success_rate": round(found / total * 100, 1) if total else 0.0,
            "avg_latency_ms": round(avg_ms, 1),
        }

    def clear(self) -> None:
        with sqlite3.connect(self._db) as conn:
            conn.execute("DELETE FROM detection_events")
            conn.commit()

    def export_bundle(self, out_dir: str = "logs") -> str:
        today = datetime.date.today().isoformat()
        bundle = Path(out_dir) / f"debug_export_{today}.zip"
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as zf:
            # db
            if self._db.exists():
                zf.write(self._db, self._db.name)
            # text logs
            for log_file in Path("logs/text").glob("*.log"):
                zf.write(log_file, f"logs/{log_file.name}")
            # screenshots
            for img in Path("logs/screenshots").glob("*.png"):
                zf.write(img, f"screenshots/{img.name}")
            # config
            if Path("config.json").exists():
                zf.write("config.json", "config.json")
        return str(bundle)
