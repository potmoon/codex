"""Deterministic ranking service for watchlist batch interpretation."""

from __future__ import annotations

from typing import Any


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _priority(score: float) -> str:
    if score >= 75:
        return "high"
    if score >= 55:
        return "medium"
    return "low"


def _reason(
    score: float,
    action: str,
    entry_stage: str,
    reason_flags: dict[str, Any],
    conflict_level: str,
) -> str:
    if reason_flags.get("major_bc_risk"):
        return "Major BC risk despite strong prior move"
    if conflict_level == "high":
        return "High conflict across timeframes"
    if action == "buy" and entry_stage == "best":
        return "Best buy alignment across daily and H4"
    if entry_stage == "late":
        return "Bullish but extended after ignition"
    if score >= 75:
        return "Constructive multi-timeframe setup with good timing"
    return "Mixed signals; watchlist candidate but not prime"


def rank_interpretation(
    facts: dict[str, Any],
    llm_payload: dict[str, Any],
    interpretation: dict[str, Any],
) -> dict[str, Any]:
    """Rank interpreted setups with deterministic watchlist scoring."""

    reason_flags = llm_payload.get("reason_flags", {}) or {}
    decision_context = facts.get("decision_context", {}) or {}

    score = float(interpretation.get("confidence", 0.0)) * 100.0

    action = str(interpretation.get("action", ""))
    entry_stage = str(interpretation.get("entry_stage", ""))

    if action == "buy":
        score += 10.0

    if entry_stage == "best":
        score += 8.0
    elif entry_stage == "early":
        score += 4.0
    elif entry_stage == "late":
        score -= 8.0

    if reason_flags.get("major_bc_risk"):
        score -= 12.0
    if reason_flags.get("local_climax_present"):
        score -= 10.0
    if decision_context.get("conflict_level") == "high":
        score -= 8.0

    if (
        reason_flags.get("daily_allows_long")
        and reason_flags.get("h4_setup_active")
        and not reason_flags.get("h1_late_after_ignition")
    ):
        score += 5.0

    score = _clamp(score)
    priority = _priority(score)
    reason = _reason(
        score=score,
        action=action,
        entry_stage=entry_stage,
        reason_flags=reason_flags,
        conflict_level=str(decision_context.get("conflict_level", "")),
    )
    return {
        "score": round(score, 2),
        "priority": priority,
        "reason": reason,
    }
