"""Analysis API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.services.analysis import analyze_ticker
from backend.app.services.llm_payload import build_llm_facts_payload

router = APIRouter(prefix="/analyze", tags=["analyze"])


class Candle(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    candles: dict[str, list[Candle]]
    context: dict[str, Any] | None = None


@router.post("")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    return analyze_ticker(request.model_dump())


@router.post("/llm-payload")
def analyze_llm_payload(request: AnalyzeRequest) -> dict[str, Any]:
    analysis_result = analyze_ticker(request.model_dump())
    return build_llm_facts_payload(analysis_result)
