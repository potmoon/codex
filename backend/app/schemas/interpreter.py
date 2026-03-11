"""Schemas for structured interpretation output."""

from __future__ import annotations

from pydantic import BaseModel


class MTFView(BaseModel):
    daily: str
    h4: str
    h1: str


class Invalidation(BaseModel):
    type: str
    value: float | None


class InterpretationResult(BaseModel):
    ticker: str
    action: str
    setup_type: str
    entry_stage: str
    confidence: float
    summary: str
    mtf_view: MTFView
    invalidation: Invalidation


class AnalyzeInterpretResponse(BaseModel):
    ticker: str
    facts: dict
    llm_payload: dict
    interpretation: InterpretationResult
