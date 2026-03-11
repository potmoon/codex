"""Deterministic mock interpreter built on top of compact analysis facts."""

from __future__ import annotations

from backend.app.schemas.interpreter import InterpretationResult, Invalidation, MTFView


def _pick_invalidation_value(levels: dict) -> float | None:
    for timeframe in ("h1", "h4", "daily"):
        tf_levels = levels.get(timeframe, {}) or {}
        value = tf_levels.get("invalidation_level")
        if value is not None:
            return float(value)
    return None


def _build_summary(reason_flags: dict, decision_context: dict) -> str:
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


def interpret_from_facts(payload: dict) -> InterpretationResult:
    """Return deterministic mock interpretation from compact LLM payload."""

    ticker = str(payload.get("ticker", ""))
    decision_context = payload.get("decision_context", {}) or {}
    reason_flags = payload.get("reason_flags", {}) or {}
    levels = payload.get("levels", {}) or {}
    entry_stage = str(decision_context.get("entry_stage", ""))

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
