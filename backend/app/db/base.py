"""SQLite database bootstrap for session persistence."""

from __future__ import annotations

import os
import sqlite3

DB_PATH = os.getenv("SESSION_DB_PATH", "backend/app/db/sessions.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                session_type TEXT NOT NULL,
                label TEXT,
                ticker TEXT,
                request_payload TEXT NOT NULL,
                facts_payload TEXT NOT NULL,
                llm_payload TEXT NOT NULL,
                interpretation_payload TEXT NOT NULL,
                ranking_payload TEXT,
                metadata_payload TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
