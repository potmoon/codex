# Codex Backend (Deterministic Facts + Interpreters)

This backend keeps deterministic analysis as the source of truth and adds interpretation and watchlist ranking layers on top.

## Endpoints

### `POST /analyze`
Returns full deterministic analysis facts from candle input.

### `POST /analyze/llm-payload`
Runs deterministic analysis, then returns a compact LLM-ready facts payload.

### `POST /analyze/interpret`
Runs the full single-ticker pipeline:
1. deterministic analyzer (`analyze_ticker`) to build facts
2. compact payload builder (`build_llm_facts_payload`)
3. interpreter (`interpret_from_facts`) in either `mock` or `openai` mode

Response shape is stable:
```json
{
  "ticker": "...",
  "facts": {"...": "full deterministic analysis"},
  "llm_payload": {"...": "compact deterministic facts"},
  "interpretation": {"...": "InterpretationResult"}
}
```

### `POST /analyze/interpret-with-images`
Image-aware single-ticker interpretation. Uses **multipart/form-data** so candles and images can be uploaded together.

Required form fields:
- `ticker` (string)
- `daily` (JSON array string of candles)
- `h4` (JSON array string of candles)
- `h1` (JSON array string of candles)
- `images` (one or more files)

Accepted image types:
- `image/png`
- `image/jpeg`
- `image/jpg`

Validation:
- at least one image required
- empty files rejected
- max image size: 5MB each

Behavior:
- always computes deterministic facts first
- `mock` mode: ignores images and uses deterministic interpreter
- `openai` mode: sends deterministic facts + images to OpenAI adapter
- OpenAI failures fallback automatically to deterministic mock

Wrapper shape extends `/analyze/interpret` with metadata:
```json
{
  "ticker": "...",
  "facts": {},
  "llm_payload": {},
  "interpretation": {},
  "interpreter_context": {
    "mode": "mock|openai|fallback_mock",
    "used_images": true,
    "image_count": 2
  }
}
```

### `POST /analyze/batch-interpret`
Runs the same analyze→payload→interpret pipeline for multiple watchlist items and adds deterministic ranking.

Request shape:
```json
{
  "items": [
    {
      "ticker": "WIMI",
      "daily": [{"timestamp": "...", "open": 0, "high": 0, "low": 0, "close": 0}],
      "h4": [{"timestamp": "...", "open": 0, "high": 0, "low": 0, "close": 0}],
      "h1": [{"timestamp": "...", "open": 0, "high": 0, "low": 0, "close": 0}]
    }
  ]
}
```

Response shape:
```json
{
  "count": 1,
  "items": [
    {
      "ticker": "WIMI",
      "status": "ok",
      "facts": {},
      "llm_payload": {},
      "interpretation": {},
      "ranking": {
        "score": 87.0,
        "priority": "high",
        "reason": "Best buy alignment across daily and H4"
      }
    }
  ],
  "sorted_by": "ranking.score"
}
```

## Interpreter modes

Set mode with environment variable:

- `INTERPRETER_MODE=mock` (default)
- `INTERPRETER_MODE=openai`

Additional OpenAI settings:

- `OPENAI_API_KEY` (required when `INTERPRETER_MODE=openai`)
- `OPENAI_MODEL` (optional, default: `gpt-5.4`)

### Fallback behavior

If `INTERPRETER_MODE=openai` and any OpenAI call fails (API error, malformed output, schema mismatch), the service automatically falls back to the deterministic mock interpreter.

Deterministic facts remain the source of truth in all modes. The model only interprets structured facts. For image-aware interpretation, screenshots are additive context and must not override deterministic signals.

## Ranking logic summary (MVP)

Batch ranking is deterministic and starts from `interpretation.confidence * 100`, then applies fixed adjustments:

- `+10` if action is `buy`
- `+8` if entry stage is `best`
- `+4` if entry stage is `early`
- `-8` if entry stage is `late`
- `-12` if `reason_flags.major_bc_risk`
- `-10` if `reason_flags.local_climax_present`
- `-8` if `conflict_level == high`
- `+5` for daily/H4 alignment without late H1 ignition

Score is clamped to `0..100` and mapped to priority:

- `high >= 75`
- `medium >= 55`
- `low < 55`

## Partial-failure behavior in batch mode

If one ticker fails internally, the batch still succeeds:

- failed item gets `status: "error"`
- interpretation becomes deterministic error payload:
  - `action: "wait"`
  - `setup_type: "analysis_error"`
  - `confidence: 0.0`
- ranking becomes low-priority zero score
- other items are processed normally

## Installation

```bash
pip install -r requirements.txt
```
