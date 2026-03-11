"""Placeholder OpenAI adapter for future interpreter integration."""

from __future__ import annotations


class OpenAIInterpreterClient:
    """Scaffold adapter to later swap in a real OpenAI-backed interpreter."""

    def interpret(self, payload: dict) -> dict:
        raise NotImplementedError(
            "OpenAI interpreter client is not implemented yet. "
            "Use the deterministic mock interpreter service for now."
        )
