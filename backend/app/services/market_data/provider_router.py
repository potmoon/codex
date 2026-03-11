"""Market data provider routing by environment mode."""

from __future__ import annotations

from backend.app.core.config import get_settings
from backend.app.services.market_data.base import MarketDataProvider
from backend.app.services.market_data.mock_provider import MockMarketDataProvider


class ProviderScaffold(MarketDataProvider):
    def __init__(self, provider_name: str | None, api_key: str | None) -> None:
        self._provider_name = provider_name
        self._api_key = api_key

    def fetch_candles(self, ticker: str, timeframe: str, limit: int):
        if not self._provider_name or not self._api_key:
            raise RuntimeError(
                "MARKET_DATA_PROVIDER_NAME and MARKET_DATA_API_KEY are required for provider mode"
            )
        raise NotImplementedError(
            f"Provider adapter scaffold for '{self._provider_name}' is not implemented in this environment"
        )


def get_market_data_provider() -> tuple[MarketDataProvider, str]:
    settings = get_settings()
    if settings.market_data_mode == "provider":
        return (
            ProviderScaffold(settings.market_data_provider_name, settings.market_data_api_key),
            "provider",
        )
    return MockMarketDataProvider(), "mock"
