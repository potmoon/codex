"""Normalized market data types."""

from __future__ import annotations

from typing import TypedDict


class NormalizedCandle(TypedDict):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
