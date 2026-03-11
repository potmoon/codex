"""Deterministic analysis service."""

from __future__ import annotations

from typing import Any


EMPTY_LEVELS = {
    "base_high": None,
    "base_low": None,
    "break_level": None,
    "invalidation_level": None,
    "distance_from_break_pct": None,
}


def _round_or_none(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 4)


def _build_timeframe_levels(candles: list[dict[str, Any]]) -> dict[str, float | None]:
    if not candles:
        return dict(EMPTY_LEVELS)

    if len(candles) == 1:
        only = candles[0]
        high = float(only["high"])
        low = float(only["low"])
        return {
            "base_high": _round_or_none(high),
            "base_low": _round_or_none(low),
            "break_level": _round_or_none(high),
            "invalidation_level": _round_or_none(low),
            "distance_from_break_pct": 0.0,
        }

    setup = candles[:-1]
    trigger = candles[-1]

    base_high = max(float(c["high"]) for c in setup)
    base_low = min(float(c["low"]) for c in setup)
    break_level = base_high
    invalidation_level = base_low
    close = float(trigger["close"])

    distance_from_break_pct = 0.0
    if break_level:
        distance_from_break_pct = ((close - break_level) / break_level) * 100

    return {
        "base_high": _round_or_none(base_high),
        "base_low": _round_or_none(base_low),
        "break_level": _round_or_none(break_level),
        "invalidation_level": _round_or_none(invalidation_level),
        "distance_from_break_pct": _round_or_none(distance_from_break_pct),
    }


def _safe_pct(levels: dict[str, float | None]) -> float:
    return float(levels.get("distance_from_break_pct") or 0.0)


def analyze_ticker(analysis_input: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic analysis result from candle input.

    This service intentionally stays deterministic and does not call any LLM.
    """

    ticker = analysis_input.get("ticker", "")
    candles = analysis_input.get("candles", {}) or {}

    daily_levels = _build_timeframe_levels(candles.get("daily") or [])
    h4_levels = _build_timeframe_levels(candles.get("h4") or [])
    h1_levels = _build_timeframe_levels(candles.get("h1") or [])

    has_daily = bool(candles.get("daily"))
    has_h4 = bool(candles.get("h4"))
    has_h1 = bool(candles.get("h1"))

    daily_dist = _safe_pct(daily_levels)
    h4_dist = _safe_pct(h4_levels)
    h1_dist = _safe_pct(h1_levels)

    daily_allows_long = has_daily and daily_dist >= 0
    h4_setup_active = has_h4 and daily_allows_long and -2.0 <= h4_dist <= 4.0
    h1_late_after_ignition = has_h1 and h4_setup_active and h1_dist >= 3.0

    prior_entry_likely_happened = h1_late_after_ignition or h1_dist >= 5.0
    local_climax_present = h1_dist >= 8.0
    major_bc_risk = local_climax_present or h4_dist >= 6.0
    extended_from_break = h1_dist >= 10.0 or h4_dist >= 10.0 or daily_dist >= 12.0

    reason_flags = {
        "daily_allows_long": daily_allows_long,
        "h4_setup_active": h4_setup_active,
        "h1_late_after_ignition": h1_late_after_ignition,
        "prior_entry_likely_happened": prior_entry_likely_happened,
        "local_climax_present": local_climax_present,
        "major_bc_risk": major_bc_risk,
        "extended_from_break": extended_from_break,
    }

    if not daily_allows_long:
        action = "wait"
        entry_stage = "late"
        conflict_level = "high"
    elif h4_setup_active and not prior_entry_likely_happened and not major_bc_risk and 0.0 <= h1_dist <= 2.5:
        action = "buy"
        entry_stage = "best"
        conflict_level = "low"
    elif h4_setup_active and not prior_entry_likely_happened and not major_bc_risk:
        action = "watch"
        entry_stage = "trigger"
        conflict_level = "low"
    elif h4_setup_active:
        action = "wait"
        entry_stage = "late"
        conflict_level = "medium"
    else:
        action = "wait"
        entry_stage = "setup"
        conflict_level = "medium"

    return {
        "ticker": ticker,
        "mtf_view": {
            "daily": "available" if has_daily else "missing",
            "h4": "available" if has_h4 else "missing",
            "h1": "available" if has_h1 else "missing",
        },
        "levels": {
            "daily": daily_levels,
            "h4": h4_levels,
            "h1": h1_levels,
        },
        "signals": {
            "daily_allows_long": daily_allows_long,
            "h4_setup_active": h4_setup_active,
            "h1_late_after_ignition": h1_late_after_ignition,
        },
        "reason_flags": reason_flags,
        "decision_context": {
            "action": action,
            "entry_stage": entry_stage,
            "conflict_level": conflict_level,
        },
    }
