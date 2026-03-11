"""Analysis API routes."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, ValidationError

from backend.app.core.config import get_settings
from backend.app.schemas.interpreter import (
    AnalyzeInterpretResponse,
    AnalyzeInterpretWithImagesResponse,
    BatchInterpretItem,
    BatchInterpretRequest,
    BatchInterpretResponse,
    CandleInput,
    InterpretationResult,
    InterpreterContext,
    Invalidation,
    MTFView,
    RankingResult,
)
from backend.app.services.analysis import analyze_ticker
from backend.app.services.interpreter import interpret_from_facts, interpret_from_facts_with_context
from backend.app.services.llm_payload import build_llm_facts_payload
from backend.app.services.ranking import rank_interpretation

router = APIRouter(prefix="/analyze", tags=["analyze"])

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg"}


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    candles: dict[str, list[CandleInput]]
    context: dict[str, Any] | None = None


def _run_pipeline_for_ticker(ticker: str, candles: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any], dict[str, Any], InterpretationResult]:
    facts = analyze_ticker({"ticker": ticker, "candles": candles})
    llm_payload = build_llm_facts_payload(facts)
    interpretation = interpret_from_facts(llm_payload, mode=get_settings().interpreter_mode)
    return facts, llm_payload, interpretation


def _parse_candle_list(raw: str, field_name: str) -> list[dict[str, Any]]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid JSON for field '{field_name}'") from exc

    if not isinstance(parsed, list):
        raise HTTPException(status_code=422, detail=f"Field '{field_name}' must be a JSON array")

    output: list[dict[str, Any]] = []
    for idx, item in enumerate(parsed):
        try:
            candle = CandleInput.model_validate(item)
        except ValidationError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid candle in '{field_name}' at index {idx}: {exc.errors()}",
            ) from exc
        output.append(candle.model_dump())
    return output


async def _read_and_validate_images(images: list[UploadFile]) -> list[dict[str, Any]]:
    if not images:
        raise HTTPException(status_code=422, detail="At least one image is required")

    validated: list[dict[str, Any]] = []
    for file in images:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail=f"Unsupported image type: {file.content_type}")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=422, detail=f"Empty upload not allowed: {file.filename}")
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail=f"Image too large (max {MAX_IMAGE_BYTES} bytes): {file.filename}")
        validated.append({"filename": file.filename or "image", "mime_type": file.content_type, "bytes": data})
    return validated


@router.post("")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    return analyze_ticker(request.model_dump())


@router.post("/llm-payload")
def analyze_llm_payload(request: AnalyzeRequest) -> dict[str, Any]:
    analysis_result = analyze_ticker(request.model_dump())
    return build_llm_facts_payload(analysis_result)


@router.post("/interpret", response_model=AnalyzeInterpretResponse)
def analyze_interpret(request: AnalyzeRequest) -> AnalyzeInterpretResponse:
    facts, llm_payload, interpretation = _run_pipeline_for_ticker(
        ticker=request.ticker,
        candles={
            "daily": [c.model_dump() for c in request.candles.get("daily", [])],
            "h4": [c.model_dump() for c in request.candles.get("h4", [])],
            "h1": [c.model_dump() for c in request.candles.get("h1", [])],
        },
    )
    return AnalyzeInterpretResponse(
        ticker=str(facts.get("ticker", "")),
        facts=facts,
        llm_payload=llm_payload,
        interpretation=interpretation,
    )


@router.post("/interpret-with-images", response_model=AnalyzeInterpretWithImagesResponse)
async def analyze_interpret_with_images(
    ticker: str = Form(...),
    daily: str = Form(...),
    h4: str = Form(...),
    h1: str = Form(...),
    images: list[UploadFile] = File(...),
) -> AnalyzeInterpretWithImagesResponse:
    if not ticker.strip():
        raise HTTPException(status_code=422, detail="Ticker is required")

    candles = {
        "daily": _parse_candle_list(daily, "daily"),
        "h4": _parse_candle_list(h4, "h4"),
        "h1": _parse_candle_list(h1, "h1"),
    }
    validated_images = await _read_and_validate_images(images)

    facts = analyze_ticker({"ticker": ticker, "candles": candles})
    llm_payload = build_llm_facts_payload(facts)

    interpretation, context = interpret_from_facts_with_context(
        llm_payload,
        mode=get_settings().interpreter_mode,
        images=validated_images,
    )

    return AnalyzeInterpretWithImagesResponse(
        ticker=str(facts.get("ticker", "")),
        facts=facts,
        llm_payload=llm_payload,
        interpretation=interpretation,
        interpreter_context=InterpreterContext.model_validate(context),
    )


@router.post("/batch-interpret", response_model=BatchInterpretResponse)
def analyze_batch_interpret(request: BatchInterpretRequest) -> BatchInterpretResponse:
    items: list[BatchInterpretItem] = []

    for item in request.items:
        try:
            candles = {
                "daily": [c.model_dump() for c in item.daily],
                "h4": [c.model_dump() for c in item.h4],
                "h1": [c.model_dump() for c in item.h1],
            }
            facts, llm_payload, interpretation = _run_pipeline_for_ticker(item.ticker, candles)
            ranking = rank_interpretation(
                facts=facts,
                llm_payload=llm_payload,
                interpretation=interpretation.model_dump(),
            )
            items.append(
                BatchInterpretItem(
                    ticker=item.ticker,
                    status="ok",
                    facts=facts,
                    llm_payload=llm_payload,
                    interpretation=interpretation,
                    ranking=RankingResult.model_validate(ranking),
                )
            )
        except Exception as exc:  # noqa: BLE001
            error_interpretation = InterpretationResult(
                ticker=item.ticker,
                action="wait",
                setup_type="analysis_error",
                entry_stage="no_trade",
                confidence=0.0,
                summary=f"Analysis failed for {item.ticker}: {exc.__class__.__name__}",
                mtf_view=MTFView(daily="unknown", h4="unknown", h1="unknown"),
                invalidation=Invalidation(type="price_level", value=None),
            )
            items.append(
                BatchInterpretItem(
                    ticker=item.ticker,
                    status="error",
                    facts={"ticker": item.ticker},
                    llm_payload={"ticker": item.ticker},
                    interpretation=error_interpretation,
                    ranking=RankingResult(score=0.0, priority="low", reason="Analysis failed for this ticker"),
                )
            )

    sorted_items = sorted(items, key=lambda x: x.ranking.score, reverse=True)
    return BatchInterpretResponse(count=len(sorted_items), items=sorted_items, sorted_by="ranking.score")
