"""
SQLite storage for PyCal events. DB at ~/.pycal/events.db; create table on first use.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

from events import Event

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL
);
"""


def _db_path() -> Path:
    """Path to the events database; ensure directory exists."""
    base = Path.home() / ".pycal"
    base.mkdir(parents=True, exist_ok=True)
    return base / "events.db"


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M")


def _parse_iso(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M")


def add_event(event: Event) -> None:
    """Insert a single event into the database."""
    path = _db_path()
    conn = sqlite3.connect(path)
    try:
        _ensure_schema(conn)
        conn.execute(
            "INSERT INTO events (description, category, start, end) VALUES (?, ?, ?, ?)",
            (event.description, event.category, _iso(event.start), _iso(event.end)),
        )
        conn.commit()
    finally:
        conn.close()


def events_in_range(start: datetime, end: datetime) -> list[Event]:
    """Return events that overlap [start, end], sorted by start. Overlap: event.start < end AND event.end > start."""
    path = _db_path()
    conn = sqlite3.connect(path)
    try:
        _ensure_schema(conn)
        start_s = _iso(start)
        end_s = _iso(end)
        rows = conn.execute(
            "SELECT description, category, start, end FROM events WHERE start < ? AND end > ? ORDER BY start",
            (end_s, start_s),
        ).fetchall()
        return [
            Event(description=row[0], category=row[1], start=_parse_iso(row[2]), end=_parse_iso(row[3]))
            for row in rows
        ]
    finally:
        conn.close()
