"""Prepare compact LLM-ready facts payloads from deterministic analysis."""

from __future__ import annotations

from typing import Any


def _as_bool(value: Any) -> bool:
    return bool(value)


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


def build_llm_facts_payload(analysis_result: dict) -> dict:
    """Convert deterministic analysis output to a compact LLM-ready facts object."""

    mtf_view = analysis_result.get("mtf_view", {}) or {}
    signals = analysis_result.get("signals", {}) or {}
    decision_context = analysis_result.get("decision_context", {}) or {}

    return {
        "ticker": _as_str(analysis_result.get("ticker")),
        "mtf_view": {
            "daily": _as_str(mtf_view.get("daily")),
            "h4": _as_str(mtf_view.get("h4")),
            "h1": _as_str(mtf_view.get("h1")),
        },
        "signals": {
            "daily_allows_long": _as_bool(signals.get("daily_allows_long")),
            "h4_setup_active": _as_bool(signals.get("h4_setup_active")),
            "h1_late_after_ignition": _as_bool(signals.get("h1_late_after_ignition")),
        },
        "decision_context": {
            "action": _as_str(decision_context.get("action")),
            "entry_stage": _as_str(decision_context.get("entry_stage")),
            "conflict_level": _as_str(decision_context.get("conflict_level")),
        },
    }
