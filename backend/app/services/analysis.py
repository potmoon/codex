"""Deterministic analysis service."""

from __future__ import annotations

from typing import Any


def analyze_ticker(analysis_input: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic analysis result from candle input.

    This service intentionally stays deterministic and does not call any LLM.
    """

    ticker = analysis_input.get("ticker", "")
    candles = analysis_input.get("candles", {}) or {}

    has_daily = bool(candles.get("daily"))
    has_h4 = bool(candles.get("h4"))
    has_h1 = bool(candles.get("h1"))

    daily_allows_long = has_daily
    h4_setup_active = has_h4 and has_daily
    h1_late_after_ignition = has_h1 and h4_setup_active

    if daily_allows_long and h4_setup_active and not h1_late_after_ignition:
        action = "prepare"
        entry_stage = "ready"
        conflict_level = "low"
    elif daily_allows_long and not h4_setup_active:
        action = "wait"
        entry_stage = "setup"
        conflict_level = "medium"
    else:
        action = "wait"
        entry_stage = "late"
        conflict_level = "medium"

    return {
        "ticker": ticker,
        "mtf_view": {
            "daily": "available" if has_daily else "missing",
            "h4": "available" if has_h4 else "missing",
            "h1": "available" if has_h1 else "missing",
        },
        "signals": {
            "daily_allows_long": daily_allows_long,
            "h4_setup_active": h4_setup_active,
            "h1_late_after_ignition": h1_late_after_ignition,
        },
        "decision_context": {
            "action": action,
            "entry_stage": entry_stage,
            "conflict_level": conflict_level,
        },
    }
