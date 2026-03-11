"""Interpreter service with deterministic mock + OpenAI-backed mode."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError

from backend.app.core.config import get_settings
from backend.app.schemas.interpreter import InterpretationResult, Invalidation, MTFView
from backend.app.services.openai_client import OpenAIInterpreterClient

logger = logging.getLogger(__name__)


def _pick_invalidation_value(levels: dict[str, Any]) -> float | None:
    for timeframe in ("h1", "h4", "daily"):
        tf_levels = levels.get(timeframe, {}) or {}
        value = tf_levels.get("invalidation_level")
        if value is not None:
            return float(value)
    return None


def _normalize_entry_stage(stage: Any) -> str:
    stage_str = str(stage or "").strip().lower()
    mapping = {
        "best": "best",
        "early": "early",
        "late": "late",
        "trigger": "early",
        "setup": "early",
        "ready": "early",
        "no_trade": "no_trade",
        "": "no_trade",
    }
    return mapping.get(stage_str, "no_trade")


def _build_summary(reason_flags: dict[str, Any], decision_context: dict[str, Any]) -> str:
    parts: list[str] = []

    if reason_flags.get("major_bc_risk"):
        parts.append("Major BC risk is active")
    elif reason_flags.get("h4_setup_active"):
        parts.append("H4 setup is active")
    else:
        parts.append("No strong setup confirmation")

    if reason_flags.get("h1_late_after_ignition") or decision_context.get("entry_stage") == "late":
        parts.append("entry appears late")
    elif decision_context.get("entry_stage"):
        parts.append(f"entry stage is {decision_context.get('entry_stage')}")

    if reason_flags.get("daily_allows_long"):
        parts.append("daily bias allows long")
    else:
        parts.append("daily bias does not support long")

    return "; ".join(parts) + "."


def _mock_interpret(payload: dict[str, Any]) -> InterpretationResult:
    ticker = str(payload.get("ticker", ""))
    decision_context = payload.get("decision_context", {}) or {}
    reason_flags = payload.get("reason_flags", {}) or {}
    levels = payload.get("levels", {}) or {}
    entry_stage = _normalize_entry_stage(decision_context.get("entry_stage", ""))

    if reason_flags.get("major_bc_risk"):
        action = "wait"
        setup_type = "major_bc_risk"
        confidence = 0.80
    elif decision_context.get("action") == "buy" and entry_stage == "best":
        action = "buy"
        setup_type = "confirmed_bullish_setup"
        confidence = 0.82
    elif entry_stage == "late":
        action = "wait"
        setup_type = "bullish_but_extended"
        confidence = 0.74
    else:
        action = "wait"
        setup_type = "unclear_or_no_trade"
        confidence = 0.60

    summary = _build_summary(reason_flags, decision_context)

    return InterpretationResult(
        ticker=ticker,
        action=action,
        setup_type=setup_type,
        entry_stage=entry_stage,
        confidence=confidence,
        summary=summary,
        mtf_view=MTFView(
            daily=str((payload.get("mtf_view", {}) or {}).get("daily", "")),
            h4=str((payload.get("mtf_view", {}) or {}).get("h4", "")),
            h1=str((payload.get("mtf_view", {}) or {}).get("h1", "")),
        ),
        invalidation=Invalidation(
            type="price_level",
            value=_pick_invalidation_value(levels),
        ),
    )


def _openai_client(client: OpenAIInterpreterClient | Any | None = None) -> OpenAIInterpreterClient | Any:
    if client is not None:
        return client
    settings = get_settings()
    return OpenAIInterpreterClient(
        api_key=settings.openai_api_key or "",
        model=settings.openai_model,
    )


def _openai_interpret(
    payload: dict[str, Any],
    client: OpenAIInterpreterClient | Any | None = None,
    images: list[dict[str, Any]] | None = None,
) -> InterpretationResult:
    use_client = _openai_client(client)
    if images:
        result = use_client.interpret_with_images(payload, images)
    else:
        result = use_client.interpret(payload)
    return InterpretationResult.model_validate(result)


def interpret_from_facts(
    payload: dict[str, Any],
    mode: str = "mock",
    client: OpenAIInterpreterClient | Any | None = None,
) -> InterpretationResult:
    result, _ = interpret_from_facts_with_context(
        payload,
        mode=mode,
        client=client,
        images=None,
    )
    return result


def interpret_from_facts_with_context(
    payload: dict[str, Any],
    mode: str = "mock",
    client: OpenAIInterpreterClient | Any | None = None,
    images: list[dict[str, Any]] | None = None,
) -> tuple[InterpretationResult, dict[str, Any]]:
    """Interpret facts with optional images and return context metadata."""

    selected_mode = (mode or "mock").lower()

    if selected_mode == "openai":
        try:
            interpretation = _openai_interpret(payload, client=client, images=images)
            used_images = bool(images)
            logger.info(
                "interpretation_source=openai used_images=%s image_count=%d",
                used_images,
                len(images or []),
            )
            return interpretation, {
                "mode": "openai",
                "used_images": used_images,
                "image_count": len(images or []),
            }
        except (RuntimeError, ValueError, ValidationError) as exc:
            logger.warning("interpretation_source=fallback_mock error=%s", exc)
            fallback = _mock_interpret(payload)
            return fallback, {
                "mode": "fallback_mock",
                "used_images": False,
                "image_count": len(images or []),
            }

    interpretation = _mock_interpret(payload)
    logger.info("interpretation_source=mock")
    return interpretation, {
        "mode": "mock",
        "used_images": False,
        "image_count": len(images or []),
    }