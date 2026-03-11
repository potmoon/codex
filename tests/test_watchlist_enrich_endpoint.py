import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_enrich_and_batch_interpret_response_shape_sorted() -> None:
    response = client.post(
        "/watchlist/enrich-and-batch-interpret",
        json={
            "tickers": ["WIMI", "FSCO", "BATL"],
            "limits": {"daily": 10, "h4": 10, "h1": 10},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"count", "items", "sorted_by", "data_source"}
    assert data["count"] == 3
    assert data["sorted_by"] == "ranking.score"
    assert data["data_source"] in {"mock", "provider"}
    assert data["items"][0]["ranking"]["score"] >= data["items"][1]["ranking"]["score"]


def test_partial_failure_isolated(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.api.routes import watchlist as watchlist_route

    class FailOneProvider:
        def fetch_candles(self, ticker: str, timeframe: str, limit: int):
            if ticker == "BROKEN":
                raise RuntimeError("market down")
            return [
                {
                    "timestamp": f"{timeframe}_1",
                    "open": 10.0,
                    "high": 10.5,
                    "low": 9.8,
                    "close": 10.2,
                    "volume": 1000.0,
                }
                for _ in range(limit)
            ]

    monkeypatch.setattr(watchlist_route, "get_market_data_provider", lambda: (FailOneProvider(), "mock"))

    response = client.post(
        "/watchlist/enrich-and-batch-interpret",
        json={"tickers": ["GOOD", "BROKEN"], "limits": {"daily": 5, "h4": 5, "h1": 5}},
    )
    assert response.status_code == 200
    data = response.json()
    by_ticker = {item["ticker"]: item for item in data["items"]}
    assert by_ticker["BROKEN"]["status"] == "error"
    assert by_ticker["BROKEN"]["interpretation"]["setup_type"] == "market_data_error"
    assert by_ticker["BROKEN"]["ranking"]["score"] == 0.0
    assert by_ticker["GOOD"]["status"] == "ok"
