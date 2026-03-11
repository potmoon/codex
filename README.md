# Codex Backend (Deterministic Analysis + Mock Interpretation)

This backend provides a deterministic analysis pipeline for ticker candles and a compact payload suitable for later LLM use.

## Endpoints

### `POST /analyze`
Returns full deterministic analysis facts from candle input.

### `POST /analyze/llm-payload`
Runs deterministic analysis, then returns a compact LLM-ready facts payload.

### `POST /analyze/interpret`
Runs a two-phase interpretation flow:
1. deterministic analyzer (`analyze_ticker`) to build facts
2. compact payload builder (`build_llm_facts_payload`)
3. **mock deterministic interpreter** (`interpret_from_facts`)

This interpretation layer is intentionally mock logic and is designed to be replaced later by a real LLM-backed implementation (see `OpenAIInterpreterClient` scaffold).

## Example `/analyze/interpret`

### Request
```json
{
  "ticker": "WIMI",
  "candles": {
    "daily": [
      {"timestamp": "1", "open": 9.6, "high": 10.0, "low": 9.3, "close": 9.8},
      {"timestamp": "2", "open": 9.9, "high": 10.3, "low": 9.7, "close": 10.2}
    ],
    "h4": [
      {"timestamp": "1", "open": 10.0, "high": 10.2, "low": 9.8, "close": 10.0},
      {"timestamp": "2", "open": 10.0, "high": 10.25, "low": 9.95, "close": 10.22}
    ],
    "h1": [
      {"timestamp": "1", "open": 10.15, "high": 10.21, "low": 10.12, "close": 10.19},
      {"timestamp": "2", "open": 10.18, "high": 10.23, "low": 10.14, "close": 10.22}
    ]
  }
}
```

### Response (shape)
```json
{
  "ticker": "WIMI",
  "facts": {"...": "full deterministic analysis"},
  "llm_payload": {"...": "compact LLM-ready payload"},
  "interpretation": {
    "ticker": "WIMI",
    "action": "buy",
    "setup_type": "confirmed_bullish_setup",
    "entry_stage": "best",
    "confidence": 0.82,
    "summary": "...",
    "mtf_view": {
      "daily": "available",
      "h4": "available",
      "h1": "available"
    },
    "invalidation": {
      "type": "price_level",
      "value": 10.12
    }
  }
}
```

## Assumptions
- No real OpenAI API calls are made yet.
- No environment variables are required yet.
- Interpretation confidence is deterministic placeholder logic for now.
