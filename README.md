# Codex Backend (Deterministic Facts + Interpreters)

This backend keeps deterministic analysis as the source of truth and adds interpretation, market-data enrichment, and watchlist ranking layers.

## Endpoints

### `POST /analyze`
Returns full deterministic analysis facts from candle input.

### `POST /analyze/llm-payload`
Runs deterministic analysis, then returns a compact LLM-ready facts payload.

### `POST /analyze/interpret`
Runs single-ticker deterministic analyze → payload → interpret.

### `POST /analyze/interpret-with-images`
Image-aware single-ticker interpretation (multipart upload) where images are additive context only.

### `POST /analyze/batch-interpret`
Runs analyze/payload/interpret/ranking for explicitly provided candles per ticker.

### `POST /watchlist/enrich-and-batch-interpret`
Fetches candles by ticker (mock/provider), then runs analyze/payload/interpret/ranking.

Request:
```json
{
  "tickers": ["WIMI", "FSCO", "BATL", "SMX"],
  "limits": {
    "daily": 120,
    "h4": 120,
    "h1": 120
  }
}
```

Response:
```json
{
  "count": 4,
  "items": [
    {
      "ticker": "WIMI",
      "status": "ok",
      "facts": {},
      "llm_payload": {},
      "interpretation": {},
      "ranking": {
        "score": 82.0,
        "priority": "high",
        "reason": "Best buy alignment across daily and H4"
      }
    }
  ],
  "sorted_by": "ranking.score",
  "data_source": "mock"
}
```

If one ticker fetch fails, the batch still succeeds and that ticker becomes:
- `status: "error"`
- `interpretation.setup_type: "market_data_error"`
- `interpretation.confidence: 0.0`
- `ranking.score: 0.0`

## Interpreter configuration

- `INTERPRETER_MODE=mock|openai` (default `mock`)
- `OPENAI_API_KEY` (required for `openai`)
- `OPENAI_MODEL` (default `gpt-5.4`)

OpenAI failures fallback to deterministic mock interpretation.

## Market data configuration

- `MARKET_DATA_MODE=mock|provider` (default `mock`)
- `MARKET_DATA_API_KEY` (optional scaffold placeholder)
- `MARKET_DATA_PROVIDER_NAME` (optional scaffold placeholder)

### Mock vs provider behavior

- **mock mode (default, offline-safe):** deterministic candle generation seeded by ticker/timeframe for repeatable tests.
- **provider mode:** routes through a provider abstraction scaffold. If provider config or adapter is incomplete, per-ticker errors are isolated and do not break whole-batch responses.

## Installation

```bash
pip install -r requirements.txt
```
