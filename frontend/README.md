# Frontend Dashboard (Next.js)

## Required env

- `NEXT_PUBLIC_API_BASE_URL` (e.g. `http://localhost:8000`)

## Run

```bash
cd frontend
npm install
npm run dev
```

## Pages

- `/` home
- `/single` single ticker analyze/interpret/image-interpret
- `/watchlist` watchlist batch analyze (JSON), CSV placeholder mode, CSV ticker-enrichment mode
- `/sessions` browse/open/compare saved sessions

## Session features

- Save single interpretation result
- Save batch/watchlist result
- Browse recent sessions
- Open session detail
- Compare two saved sessions

## CSV + enrichment

- CSV minimum column: `ticker`
- Mode 1: placeholder candles (frontend mock candles)
- Mode 2: backend enrich by ticker (`POST /watchlist/enrich-and-batch-interpret`)

## Limitations

- No auth, no persistence sync, no realtime.
- Provider enrichment quality depends on backend market-data mode/config.
