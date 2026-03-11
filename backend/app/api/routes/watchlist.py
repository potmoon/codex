"""Watchlist enrichment API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.app.core.config import get_settings
from backend.app.schemas.interpreter import (
    BatchInterpretItem,
    EnrichAndBatchInterpretRequest,
    EnrichAndBatchInterpretResponse,
    InterpretationResult,
    Invalidation,
    MTFView,
    RankingResult,
)
from backend.app.services.analysis import analyze_ticker
from backend.app.services.interpreter import interpret_from_facts
from backend.app.services.llm_payload import build_llm_facts_payload
from backend.app.services.market_data.provider_router import get_market_data_provider
from backend.app.services.ranking import rank_interpretation

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def _error_item(ticker: str, setup_type: str, message: str) -> BatchInterpretItem:
    interpretation = InterpretationResult(
        ticker=ticker,
        action="wait",
        setup_type=setup_type,
        entry_stage="no_trade",
        confidence=0.0,
        summary=message,
        mtf_view=MTFView(daily="unknown", h4="unknown", h1="unknown"),
        invalidation=Invalidation(type="price_level", value=None),
    )
    return BatchInterpretItem(
        ticker=ticker,
        status="error",
        facts={"ticker": ticker},
        llm_payload={"ticker": ticker},
        interpretation=interpretation,
        ranking=RankingResult(score=0.0, priority="low", reason="Market data unavailable for this ticker"),
    )


@router.post("/enrich-and-batch-interpret", response_model=EnrichAndBatchInterpretResponse)
def enrich_and_batch_interpret(request: EnrichAndBatchInterpretRequest) -> EnrichAndBatchInterpretResponse:
    provider, data_source = get_market_data_provider()
    items: list[BatchInterpretItem] = []

    for raw_ticker in request.tickers:
        ticker = raw_ticker.strip().upper()
        if not ticker:
            items.append(_error_item(ticker="", setup_type="market_data_error", message="Ticker value is empty"))
            continue

        try:
            candles = {
                "daily": provider.fetch_candles(ticker, "1d", request.limits.daily),
                "h4": provider.fetch_candles(ticker, "4h", request.limits.h4),
                "h1": provider.fetch_candles(ticker, "1h", request.limits.h1),
            }
            facts = analyze_ticker({"ticker": ticker, "candles": candles})
            llm_payload = build_llm_facts_payload(facts)
            interpretation = interpret_from_facts(llm_payload, mode=get_settings().interpreter_mode)
            ranking = rank_interpretation(
                facts=facts,
                llm_payload=llm_payload,
                interpretation=interpretation.model_dump(),
            )
            items.append(
                BatchInterpretItem(
                    ticker=ticker,
                    status="ok",
                    facts=facts,
                    llm_payload=llm_payload,
                    interpretation=interpretation,
                    ranking=RankingResult.model_validate(ranking),
                )
            )
        except Exception as exc:  # noqa: BLE001
            items.append(
                _error_item(
                    ticker=ticker,
                    setup_type="market_data_error",
                    message=f"Market data fetch failed for {ticker}: {exc.__class__.__name__}",
                )
            )

    sorted_items = sorted(items, key=lambda x: x.ranking.score, reverse=True)
    return EnrichAndBatchInterpretResponse(
        count=len(sorted_items),
        items=sorted_items,
        sorted_by="ranking.score",
        data_source=data_source,
    )
