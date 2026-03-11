from backend.app.services.market_data.mock_provider import MockMarketDataProvider


def test_mock_provider_is_deterministic() -> None:
    provider = MockMarketDataProvider()
    first = provider.fetch_candles("WIMI", "1d", 5)
    second = provider.fetch_candles("WIMI", "1d", 5)
    assert first == second


def test_mock_provider_supported_timeframes() -> None:
    provider = MockMarketDataProvider()
    for tf in ("1d", "4h", "1h"):
        candles = provider.fetch_candles("FSCO", tf, 3)
        assert len(candles) == 3
        assert set(candles[0].keys()) == {"timestamp", "open", "high", "low", "close", "volume"}
