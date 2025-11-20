"""Lightweight in-repo HITL review queue using SQLite.

Provides simple enqueue / list / approve / reject operations. The DB path
can be overridden via the `HITL_DB_PATH` environment variable. By default
the DB file will be created at the current working directory as
`.hitl_reviews.db` to keep the repo self-contained for local testing.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _get_conn(db_path: Optional[Path] = None) -> sqlite3.Connection:
    # Resolve DB path at call time so tests can monkeypatch `HITL_DB_PATH`
    env_path = os.environ.get("HITL_DB_PATH")
    if db_path is not None:
        path = Path(db_path)
    elif env_path:
        path = Path(env_path)
    else:
        # Use a repository-local default path (stable across CWD changes)
        path = Path(__file__).resolve().parents[3] / ".hitl_reviews.db"

    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state_json TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            reviewed_at TEXT,
            reviewer TEXT,
            notes TEXT,
            result_json TEXT
        )
        """
    )
    conn.commit()


def enqueue_review(state: Dict[str, Any]) -> int:
    """Enqueue a review and return its id."""
    conn = _get_conn()
    cur = conn.cursor()
    # Use timezone-aware UTC timestamps to avoid deprecation warnings and
    # be explicit about timezone information when storing datetimes.
    now = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO reviews (state_json, status, created_at) VALUES (?, ?, ?)",
        (json.dumps(state), "pending", now),
    )
    conn.commit()
    return cur.lastrowid


def list_pending() -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.execute("SELECT * FROM reviews WHERE status = 'pending' ORDER BY created_at ASC")
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["state"] = json.loads(r.pop("state_json"))
    return rows


def get_review(review_id: int) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
    row = cur.fetchone()
    if not row:
        return None
    out = dict(row)
    out["state"] = json.loads(out.pop("state_json"))
    return out


def approve_review(review_id: int, reviewer: str, notes: Optional[str] = None, result: Optional[Dict[str, Any]] = None) -> bool:
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE reviews SET status = ?, reviewed_at = ?, reviewer = ?, notes = ?, result_json = ? WHERE id = ?",
        ("approved", now, reviewer, notes, json.dumps(result) if result is not None else None, review_id),
    )
    conn.commit()
    return True


def reject_review(review_id: int, reviewer: str, notes: Optional[str] = None) -> bool:
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE reviews SET status = ?, reviewed_at = ?, reviewer = ?, notes = ? WHERE id = ?",
        ("rejected", now, reviewer, notes, review_id),
    )
    conn.commit()
    return True
