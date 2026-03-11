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
