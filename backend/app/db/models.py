"""Session persistence models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SessionRecord:
    id: str
    created_at: str
    session_type: str
    label: str | None
    ticker: str | None
    request_payload: dict[str, Any]
    facts_payload: dict[str, Any]
    llm_payload: dict[str, Any]
    interpretation_payload: dict[str, Any]
    ranking_payload: dict[str, Any] | None
    metadata: dict[str, Any]
