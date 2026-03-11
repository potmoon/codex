"""Deterministic offline-safe mock market data provider."""

from __future__ import annotations

import hashlib

from backend.app.services.market_data.base import MarketDataProvider
from backend.app.services.market_data.types import NormalizedCandle


class MockMarketDataProvider(MarketDataProvider):
    def _seed(self, ticker: str, timeframe: str) -> int:
        digest = hashlib.sha256(f"{ticker}:{timeframe}".encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def fetch_candles(self, ticker: str, timeframe: str, limit: int) -> list[NormalizedCandle]:
        if timeframe not in {"1d", "4h", "1h"}:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        if limit <= 0:
            raise ValueError("limit must be > 0")

        seed = self._seed(ticker, timeframe)
        base = 5.0 + (seed % 5000) / 200
        step = 0.02 + ((seed >> 3) % 25) / 1000

        candles: list[NormalizedCandle] = []
        for i in range(limit):
            drift = (i - (limit // 2)) * step
            open_px = base + drift
            close_px = open_px + ((seed + i) % 7 - 3) * 0.01
            high_px = max(open_px, close_px) + 0.03
            low_px = min(open_px, close_px) - 0.03
            volume = float(50_000 + ((seed + i * 13) % 90_000))
            candles.append(
                {
                    "timestamp": f"{timeframe}_{i+1}",
                    "open": round(open_px, 4),
                    "high": round(high_px, 4),
                    "low": round(low_px, 4),
                    "close": round(close_px, 4),
                    "volume": volume,
                }
            )
        return candles
