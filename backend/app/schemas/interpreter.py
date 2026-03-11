"""Schemas for structured interpretation, watchlist, and session persistence."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class MTFView(BaseModel):
    daily: str
    h4: str
    h1: str


class Invalidation(BaseModel):
    type: str
    value: float | None


class InterpretationResult(BaseModel):
    ticker: str
    action: Literal["buy", "wait", "sell"]
    setup_type: str
    entry_stage: Literal["best", "early", "late", "no_trade"]
    confidence: float
    summary: str
    mtf_view: MTFView
    invalidation: Invalidation


class AnalyzeInterpretResponse(BaseModel):
    ticker: str
    facts: dict[str, Any]
    llm_payload: dict[str, Any]
    interpretation: InterpretationResult


class InterpreterContext(BaseModel):
    mode: Literal["mock", "openai", "fallback_mock"]
    used_images: bool
    image_count: int


class AnalyzeInterpretWithImagesResponse(BaseModel):
    ticker: str
    facts: dict[str, Any]
    llm_payload: dict[str, Any]
    interpretation: InterpretationResult
    interpreter_context: InterpreterContext


class RankingResult(BaseModel):
    score: float
    priority: Literal["high", "medium", "low"]
    reason: str


class BatchInterpretItem(BaseModel):
    ticker: str
    status: Literal["ok", "error"]
    facts: dict[str, Any]
    llm_payload: dict[str, Any]
    interpretation: InterpretationResult
    ranking: RankingResult


class BatchInterpretResponse(BaseModel):
    count: int
    items: list[BatchInterpretItem]
    sorted_by: str = "ranking.score"


class CandleInput(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class BatchInterpretRequestItem(BaseModel):
    ticker: str = Field(..., min_length=1)
    daily: list[CandleInput]
    h4: list[CandleInput]
    h1: list[CandleInput]


class BatchInterpretRequest(BaseModel):
    items: list[BatchInterpretRequestItem]


class WatchlistLimits(BaseModel):
    daily: int = 120
    h4: int = 120
    h1: int = 120


class EnrichAndBatchInterpretRequest(BaseModel):
    tickers: list[str]
    limits: WatchlistLimits = WatchlistLimits()


class EnrichAndBatchInterpretResponse(BatchInterpretResponse):
    data_source: Literal["mock", "provider"]


class SaveSingleSessionRequest(BaseModel):
    label: str | None = None
    payload: AnalyzeInterpretResponse


class SaveBatchSessionRequest(BaseModel):
    label: str | None = None
    payload: BatchInterpretResponse


class SessionSummary(BaseModel):
    id: str
    created_at: str
    session_type: Literal["single_ticker_analysis", "watchlist_batch_analysis"]
    label: str | None
    ticker: str | None


class SessionDetail(BaseModel):
    id: str
    created_at: str
    session_type: Literal["single_ticker_analysis", "watchlist_batch_analysis"]
    label: str | None
    ticker: str | None
    request_payload: dict[str, Any]
    facts_payload: dict[str, Any]
    llm_payload: dict[str, Any]
    interpretation_payload: dict[str, Any]
    ranking_payload: dict[str, Any] | None
    metadata: dict[str, Any]


class SessionSaveResponse(BaseModel):
    id: str


class SessionsListResponse(BaseModel):
    items: list[SessionSummary]


class SessionCompareResponse(BaseModel):
    left_id: str
    right_id: str
    ticker: str | None = None
    changes: dict[str, Any]