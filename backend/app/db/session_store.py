"""Session store for saving/loading analysis sessions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from backend.app.db.base import get_connection, init_db
from backend.app.db.models import SessionRecord


class SessionStore:
    def __init__(self) -> None:
        init_db()

    def save(self, data: dict[str, Any]) -> str:
        session_id = data.get("id") or str(uuid.uuid4())
        created_at = data.get("created_at") or datetime.now(timezone.utc).isoformat()

        conn = get_connection()
        try:
            conn.execute(
                """
                INSERT INTO sessions (
                    id, created_at, session_type, label, ticker,
                    request_payload, facts_payload, llm_payload,
                    interpretation_payload, ranking_payload, metadata_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    created_at,
                    data["session_type"],
                    data.get("label"),
                    data.get("ticker"),
                    json.dumps(data.get("request_payload", {})),
                    json.dumps(data.get("facts_payload", {})),
                    json.dumps(data.get("llm_payload", {})),
                    json.dumps(data.get("interpretation_payload", {})),
                    json.dumps(data.get("ranking_payload")) if data.get("ranking_payload") is not None else None,
                    json.dumps(data.get("metadata", {})),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return session_id

    def _row_to_record(self, row: Any) -> SessionRecord:
        return SessionRecord(
            id=row["id"],
            created_at=row["created_at"],
            session_type=row["session_type"],
            label=row["label"],
            ticker=row["ticker"],
            request_payload=json.loads(row["request_payload"]),
            facts_payload=json.loads(row["facts_payload"]),
            llm_payload=json.loads(row["llm_payload"]),
            interpretation_payload=json.loads(row["interpretation_payload"]),
            ranking_payload=json.loads(row["ranking_payload"]) if row["ranking_payload"] else None,
            metadata=json.loads(row["metadata_payload"]),
        )

    def list(self, limit: int = 50) -> list[SessionRecord]:
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM sessions ORDER BY datetime(created_at) DESC LIMIT ?", (limit,)
            ).fetchall()
            return [self._row_to_record(r) for r in rows]
        finally:
            conn.close()

    def get(self, session_id: str) -> SessionRecord | None:
        conn = get_connection()
        try:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            return self._row_to_record(row) if row else None
        finally:
            conn.close()
