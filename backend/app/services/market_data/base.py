"""Market data provider abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.app.services.market_data.types import NormalizedCandle


class MarketDataProvider(ABC):
    @abstractmethod
    def fetch_candles(self, ticker: str, timeframe: str, limit: int) -> list[NormalizedCandle]:
        """Fetch normalized candles for ticker/timeframe."""
