"""Prepare compact LLM-ready facts payloads from deterministic analysis."""

from __future__ import annotations

from typing import Any


LEVEL_KEYS = (
    "base_high",
    "base_low",
    "break_level",
    "invalidation_level",
    "distance_from_break_pct",
)

REASON_FLAG_KEYS = (
    "daily_allows_long",
    "h4_setup_active",
    "h1_late_after_ignition",
    "prior_entry_likely_happened",
    "local_climax_present",
    "major_bc_risk",
    "extended_from_break",
)


def _as_bool(value: Any) -> bool:
    return bool(value)


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


def _extract_levels(levels: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for tf in ("daily", "h4", "h1"):
        src = levels.get(tf, {}) or {}
        out[tf] = {k: src.get(k) for k in LEVEL_KEYS}
    return out


def _extract_reason_flags(reason_flags: dict[str, Any], signals: dict[str, Any]) -> dict[str, bool]:
    out = {k: _as_bool(reason_flags.get(k)) for k in REASON_FLAG_KEYS}
    out["daily_allows_long"] = _as_bool(signals.get("daily_allows_long", out["daily_allows_long"]))
    out["h4_setup_active"] = _as_bool(signals.get("h4_setup_active", out["h4_setup_active"]))
    out["h1_late_after_ignition"] = _as_bool(
        signals.get("h1_late_after_ignition", out["h1_late_after_ignition"])
    )
    return out


def build_llm_facts_payload(analysis_result: dict) -> dict:
    """Convert deterministic analysis output to a compact LLM-ready facts object."""

    mtf_view = analysis_result.get("mtf_view", {}) or {}
    signals = analysis_result.get("signals", {}) or {}
    decision_context = analysis_result.get("decision_context", {}) or {}
    levels = analysis_result.get("levels", {}) or {}
    reason_flags = analysis_result.get("reason_flags", {}) or {}

    return {
        "ticker": _as_str(analysis_result.get("ticker")),
        "mtf_view": {
            "daily": _as_str(mtf_view.get("daily")),
            "h4": _as_str(mtf_view.get("h4")),
            "h1": _as_str(mtf_view.get("h1")),
        },
        "levels": _extract_levels(levels),
        "signals": {
            "daily_allows_long": _as_bool(signals.get("daily_allows_long")),
            "h4_setup_active": _as_bool(signals.get("h4_setup_active")),
            "h1_late_after_ignition": _as_bool(signals.get("h1_late_after_ignition")),
        },
        "reason_flags": _extract_reason_flags(reason_flags, signals),
        "decision_context": {
            "action": _as_str(decision_context.get("action")),
            "entry_stage": _as_str(decision_context.get("entry_stage")),
            "conflict_level": _as_str(decision_context.get("conflict_level")),
        },
    }
