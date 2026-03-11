import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _item(ticker: str, daily_close: float, h4_close: float, h1_close: float) -> dict:
    return {
        "ticker": ticker,
        "daily": [
            {"timestamp": "1", "open": 10.0, "high": 10.3, "low": 9.8, "close": 10.1},
            {"timestamp": "2", "open": 10.1, "high": 10.5, "low": 10.0, "close": daily_close},
        ],
        "h4": [
            {"timestamp": "1", "open": 10.2, "high": 10.4, "low": 10.1, "close": 10.3},
            {"timestamp": "2", "open": 10.3, "high": 10.45, "low": 10.2, "close": h4_close},
        ],
        "h1": [
            {"timestamp": "1", "open": 10.38, "high": 10.42, "low": 10.3, "close": 10.4},
            {"timestamp": "2", "open": 10.4, "high": 10.8, "low": 10.35, "close": h1_close},
        ],
    }


def test_batch_endpoint_returns_sorted_results() -> None:
    payload = {
        "items": [
            _item("BEST", 10.45, 10.44, 10.47),
            _item("LATE", 10.45, 10.44, 10.79),
        ]
    }
    response = client.post("/analyze/batch-interpret", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["count"] == 2
    assert data["sorted_by"] == "ranking.score"
    assert data["items"][0]["ranking"]["score"] >= data["items"][1]["ranking"]["score"]


def test_best_buy_ranks_above_late_chase() -> None:
    payload = {
        "items": [
            _item("BEST", 10.45, 10.44, 10.47),
            _item("LATE", 10.45, 10.44, 10.79),
        ]
    }
    response = client.post("/analyze/batch-interpret", json=payload)
    data = response.json()
    assert data["items"][0]["ticker"] == "BEST"
    assert data["items"][1]["ticker"] == "LATE"


def test_error_item_does_not_break_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.api.routes import analyze as analyze_route

    original = analyze_route.analyze_ticker

    def _patched(input_data: dict) -> dict:
        if input_data.get("ticker") == "BROKEN":
            raise RuntimeError("simulated failure")
        return original(input_data)

    monkeypatch.setattr(analyze_route, "analyze_ticker", _patched)

    payload = {
        "items": [
            _item("BEST", 10.45, 10.44, 10.47),
            _item("BROKEN", 10.45, 10.44, 10.47),
        ]
    }
    response = client.post("/analyze/batch-interpret", json=payload)
    assert response.status_code == 200
    data = response.json()

    by_ticker = {i["ticker"]: i for i in data["items"]}
    assert by_ticker["BROKEN"]["status"] == "error"
    assert by_ticker["BROKEN"]["interpretation"]["setup_type"] == "analysis_error"
    assert by_ticker["BROKEN"]["ranking"]["score"] == 0.0


def test_batch_response_shape_and_ranking_present() -> None:
    payload = {"items": [_item("ONE", 10.45, 10.44, 10.47)]}
    response = client.post("/analyze/batch-interpret", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {"count", "items", "sorted_by"}
    item = data["items"][0]
    assert {"ticker", "status", "facts", "llm_payload", "interpretation", "ranking"}.issubset(item.keys())
    assert {"score", "priority", "reason"}.issubset(item["ranking"].keys())
