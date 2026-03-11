# Codex Backend

Deterministic analysis is the source of truth. Interpretation, ranking, market-data enrichment, and session persistence are additive layers.

## Core endpoints (unchanged contracts)

- `POST /analyze`
- `POST /analyze/llm-payload`
- `POST /analyze/interpret`
- `POST /analyze/interpret-with-images`
- `POST /analyze/batch-interpret`
- `POST /watchlist/enrich-and-batch-interpret`

## New session endpoints

- `POST /sessions/save-single`
- `POST /sessions/save-batch`
- `GET /sessions`
- `GET /sessions/{session_id}`
- `GET /sessions/compare?left_id=...&right_id=...`

### Save single example
```json
{
  "label": "WIMI morning run",
  "payload": {
    "ticker": "WIMI",
    "facts": {},
    "llm_payload": {},
    "interpretation": {}
  }
}
```

### Save batch example
```json
{
  "label": "watchlist close",
  "payload": {
    "count": 2,
    "items": [],
    "sorted_by": "ranking.score"
  }
}
```

### List response example
```json
{
  "items": [
    {
      "id": "...",
      "created_at": "2026-03-11T00:00:00+00:00",
      "session_type": "single_ticker_analysis",
      "label": "WIMI morning run",
      "ticker": "WIMI"
    }
  ]
}
```

### Compare response example
```json
{
  "left_id": "...",
  "right_id": "...",
  "ticker": "WIMI",
  "changes": {
    "action_changed": true,
    "entry_stage_changed": true,
    "confidence_delta": -0.12,
    "ranking_score_delta": null,
    "reason_flag_changes": {},
    "level_changes": {},
    "summary": "Moved from best to late."
  }
}
```

## Storage design (SQLite MVP)

- SQLite-backed local persistence via `backend/app/db/sessions.db` by default.
- Single table `sessions` stores full JSON blobs (`request/facts/llm/interpretation/ranking/metadata`).
- For watchlist sessions, per-item rows are stored in `metadata.items` JSON blob (simple schema-first MVP).

## Environment

- `INTERPRETER_MODE=mock|openai` (default `mock`)
- `OPENAI_API_KEY` (required for openai mode)
- `OPENAI_MODEL` (default `gpt-5.4`)
- `MARKET_DATA_MODE=mock|provider` (default `mock`)
- `MARKET_DATA_API_KEY` (provider scaffold placeholder)
- `MARKET_DATA_PROVIDER_NAME` (provider scaffold placeholder)
- `SESSION_DB_PATH` (optional, default `backend/app/db/sessions.db`)

## Notes

- No auth, no multi-user support, no background jobs.
- Provider mode remains scaffolded if external vendor is not configured.
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
