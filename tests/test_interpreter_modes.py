from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("pydantic")

from backend.app.schemas.interpreter import InterpretationResult
from backend.app.services.interpreter import interpret_from_facts


def _payload_base() -> dict[str, Any]:
    return {
        "ticker": "ABC",
        "mtf_view": {"daily": "available", "h4": "available", "h1": "available"},
        "levels": {
            "daily": {"invalidation_level": 9.5},
            "h4": {"invalidation_level": 9.8},
            "h1": {"invalidation_level": 10.0},
        },
        "signals": {
            "daily_allows_long": True,
            "h4_setup_active": True,
            "h1_late_after_ignition": False,
        },
        "reason_flags": {
            "daily_allows_long": True,
            "h4_setup_active": True,
            "h1_late_after_ignition": False,
            "prior_entry_likely_happened": False,
            "local_climax_present": False,
            "major_bc_risk": False,
            "extended_from_break": False,
        },
        "decision_context": {
            "action": "buy",
            "entry_stage": "best",
            "conflict_level": "low",
        },
    }


def test_mock_mode_still_works() -> None:
    result = interpret_from_facts(_payload_base(), mode="mock")
    assert isinstance(result, InterpretationResult)
    assert result.action == "buy"
    assert result.entry_stage == "best"


class _FakeOpenAIClient:
    def interpret(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "ticker": payload["ticker"],
            "action": "wait",
            "setup_type": "llm_interpretation",
            "entry_stage": "early",
            "confidence": 0.66,
            "summary": "Synthetic OpenAI client result",
            "mtf_view": payload["mtf_view"],
            "invalidation": {"type": "price_level", "value": 10.0},
        }


def test_openai_mode_with_injected_fake_client() -> None:
    result = interpret_from_facts(_payload_base(), mode="openai", client=_FakeOpenAIClient())
    assert result.action == "wait"
    assert result.entry_stage == "early"
    assert result.setup_type == "llm_interpretation"


class _FailingOpenAIClient:
    def interpret(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("boom")


def test_openai_failure_falls_back_to_mock() -> None:
    result = interpret_from_facts(_payload_base(), mode="openai", client=_FailingOpenAIClient())
    assert result.action == "buy"
    assert result.setup_type == "confirmed_bullish_setup"


def test_interpretation_schema_valid_after_fallback() -> None:
    result = interpret_from_facts(_payload_base(), mode="openai", client=_FailingOpenAIClient())
    data = result.model_dump()
    validated = InterpretationResult.model_validate(data)
    assert validated.summary
