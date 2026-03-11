import json
from pathlib import Path

import pytest

from backend.app.services.analysis import analyze_ticker
from backend.app.services.llm_payload import build_llm_facts_payload


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_case(name: str) -> dict:
    with (FIXTURE_DIR / f"{name}.json").open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("case_name", ["WIMI_like", "FSCO_like", "BATL_like", "SMX_like"])
def test_analysis_cases(case_name: str) -> None:
    case = _load_case(case_name)
    result = analyze_ticker(case["input"])

    assert result["decision_context"]["action"] == case["expected"]["action"]
    assert result["decision_context"]["entry_stage"] == case["expected"]["entry_stage"]

    for flag_name, expected_value in case["expected"]["reason_flags"].items():
        assert result["reason_flags"][flag_name] is expected_value

    for timeframe in ("daily", "h4", "h1"):
        levels = result["levels"][timeframe]
        for key in (
            "base_high",
            "base_low",
            "break_level",
            "invalidation_level",
            "distance_from_break_pct",
        ):
            assert key in levels


def test_llm_payload_includes_levels_and_reason_flags() -> None:
    case = _load_case("WIMI_like")
    result = analyze_ticker(case["input"])
    payload = build_llm_facts_payload(result)

    assert "levels" in payload
    assert "reason_flags" in payload
    assert payload["reason_flags"]["daily_allows_long"] is True
    assert payload["levels"]["daily"]["break_level"] is not None
