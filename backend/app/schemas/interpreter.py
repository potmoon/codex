"""Schemas for structured interpretation and batch watchlist output."""

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
