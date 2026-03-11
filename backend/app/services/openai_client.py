<<<<<<< codex/add-llm-payload-preparation-module-7e5a2e
"""OpenAI Responses API adapter for structured interpretation."""

from __future__ import annotations

import base64
import json
from typing import Any

from openai import OpenAI

INTERPRETATION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "ticker": {"type": "string"},
        "action": {"type": "string", "enum": ["buy", "wait", "sell"]},
        "setup_type": {"type": "string"},
        "entry_stage": {
            "type": "string",
            "enum": ["best", "early", "late", "no_trade"],
        },
        "confidence": {"type": "number"},
        "summary": {"type": "string"},
        "mtf_view": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "daily": {"type": "string"},
                "h4": {"type": "string"},
                "h1": {"type": "string"},
            },
            "required": ["daily", "h4", "h1"],
        },
        "invalidation": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {"type": "string"},
                "value": {"type": ["number", "null"]},
            },
            "required": ["type", "value"],
        },
    },
    "required": [
        "ticker",
        "action",
        "setup_type",
        "entry_stage",
        "confidence",
        "summary",
        "mtf_view",
        "invalidation",
    ],
}


def build_interpretation_prompt(payload: dict[str, Any], with_images: bool = False) -> str:
    """Build concise deterministic-facts interpretation instructions."""

    image_guidance = ""
    if with_images:
        image_guidance = (
            "Images are optional visual context only. "
            "Treat deterministic facts as source of truth. "
            "Mention image observations only when consistent with deterministic facts. "
            "Do not invent indicators from screenshots. "
        )

    return (
        "Interpret the deterministic chart facts. "
        "Do not invent missing signals. "
        "Prefer 'wait' over overconfident buy/sell. "
        "Summarize multi-timeframe state in plain English. "
        "Preserve deterministic entry_stage unless there is a strong reason not to. "
        f"{image_guidance}"
        "Return concise output that strictly matches the provided JSON schema.\n\n"
        f"FACTS_PAYLOAD:\n{json.dumps(payload, separators=(',', ':'))}"
    )


def _parse_json_output(response: Any) -> dict[str, Any]:
    content = getattr(response, "output_text", None)
    if not content:
        raise RuntimeError("OpenAI response did not include output_text")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI response was not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("OpenAI response JSON must be an object")
    return parsed


class OpenAIInterpreterClient:
    """Adapter for OpenAI-backed interpretation with structured outputs."""

    def __init__(self, api_key: str, model: str = "gpt-5.4") -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when INTERPRETER_MODE=openai")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def interpret(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = build_interpretation_prompt(payload, with_images=False)
        try:
            response = self._client.responses.create(
                model=self._model,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "interpretation_result",
                        "strict": True,
                        "schema": INTERPRETATION_JSON_SCHEMA,
                    }
                },
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"OpenAI Responses API call failed: {exc}") from exc

        return _parse_json_output(response)

    def interpret_with_images(self, payload: dict[str, Any], images: list[dict[str, Any]]) -> dict[str, Any]:
        prompt = build_interpretation_prompt(payload, with_images=True)
        content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt}]

        for image in images:
            image_bytes = image.get("bytes", b"")
            mime_type = image.get("mime_type", "image/png")
            encoded = base64.b64encode(image_bytes).decode("utf-8")
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{mime_type};base64,{encoded}",
                }
            )

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[{"role": "user", "content": content}],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "interpretation_result",
                        "strict": True,
                        "schema": INTERPRETATION_JSON_SCHEMA,
                    }
                },
            )
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"OpenAI image interpretation call failed: {exc}") from exc

        return _parse_json_output(response)
=======
"""Placeholder OpenAI adapter for future interpreter integration."""

from __future__ import annotations


class OpenAIInterpreterClient:
    """Scaffold adapter to later swap in a real OpenAI-backed interpreter."""

    def interpret(self, payload: dict) -> dict:
        raise NotImplementedError(
            "OpenAI interpreter client is not implemented yet. "
            "Use the deterministic mock interpreter service for now."
        )
>>>>>>> main
