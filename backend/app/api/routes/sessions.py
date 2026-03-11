"""Session persistence and comparison routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.app.db.session_store import SessionStore
from backend.app.schemas.interpreter import (
    SaveBatchSessionRequest,
    SaveSingleSessionRequest,
    SessionCompareResponse,
    SessionDetail,
    SessionSaveResponse,
    SessionsListResponse,
    SessionSummary,
)
from backend.app.services.session_compare import compare_sessions

router = APIRouter(prefix="/sessions", tags=["sessions"])
store = SessionStore()


@router.post("/save-single", response_model=SessionSaveResponse)
def save_single_session(request: SaveSingleSessionRequest) -> SessionSaveResponse:
    payload = request.payload.model_dump()
    session_id = store.save(
        {
            "session_type": "single_ticker_analysis",
            "label": request.label,
            "ticker": payload.get("ticker"),
            "request_payload": {},
            "facts_payload": payload.get("facts", {}),
            "llm_payload": payload.get("llm_payload", {}),
            "interpretation_payload": payload.get("interpretation", {}),
            "ranking_payload": None,
            "metadata": {"source": "save-single"},
        }
    )
    return SessionSaveResponse(id=session_id)


@router.post("/save-batch", response_model=SessionSaveResponse)
def save_batch_session(request: SaveBatchSessionRequest) -> SessionSaveResponse:
    payload = request.payload.model_dump()
    session_id = store.save(
        {
            "session_type": "watchlist_batch_analysis",
            "label": request.label,
            "ticker": None,
            "request_payload": {},
            "facts_payload": {},
            "llm_payload": {},
            "interpretation_payload": {},
            "ranking_payload": {},
            "metadata": {"source": "save-batch", "items": payload.get("items", [])},
        }
    )
    return SessionSaveResponse(id=session_id)


@router.get("", response_model=SessionsListResponse)
def list_sessions(limit: int = Query(default=50, ge=1, le=200)) -> SessionsListResponse:
    records = store.list(limit=limit)
    return SessionsListResponse(
        items=[
            SessionSummary(
                id=r.id,
                created_at=r.created_at,
                session_type=r.session_type,
                label=r.label,
                ticker=r.ticker,
            )
            for r in records
        ]
    )


@router.get("/compare", response_model=SessionCompareResponse)
def compare_saved_sessions(left_id: str, right_id: str) -> SessionCompareResponse:
    left = store.get(left_id)
    right = store.get(right_id)
    if not left or not right:
        raise HTTPException(status_code=404, detail="One or both sessions not found")

    diff = compare_sessions(left.__dict__, right.__dict__)
    return SessionCompareResponse(**diff)


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(session_id: str) -> SessionDetail:
    record = store.get(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionDetail(
        id=record.id,
        created_at=record.created_at,
        session_type=record.session_type,
        label=record.label,
        ticker=record.ticker,
        request_payload=record.request_payload,
        facts_payload=record.facts_payload,
        llm_payload=record.llm_payload,
        interpretation_payload=record.interpretation_payload,
        ranking_payload=record.ranking_payload,
        metadata=record.metadata,
    )
