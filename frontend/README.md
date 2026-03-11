# Frontend Dashboard (Next.js)

Internal operator dashboard for the Chart Analyzer backend.

## Required environment variable

- `NEXT_PUBLIC_API_BASE_URL` (example: `http://localhost:8000`)

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:3000`

## Pages

- `/` Home dashboard links
- `/single` Single Ticker Analyzer
  - Analyze (`POST /analyze`)
  - Interpret (`POST /analyze/interpret`)
  - Interpret with Images (`POST /analyze/interpret-with-images`)
- `/watchlist` Watchlist Analyzer
  - Batch ranking (`POST /analyze/batch-interpret`)
  - Ticker enrichment batch ranking (`POST /watchlist/enrich-and-batch-interpret`)
  - Two input modes:
    - **Paste JSON** (existing direct-candle flow)
    - **Upload CSV** (ticker-first flow)

## CSV upload flow

- Upload a `.csv` file (or paste CSV text) with at least a `ticker` column.
- CSV rows are parsed client-side and previewed before submit.
- Then choose one of two execution paths:
  1. **Use placeholder candles** (frontend mock candles, current developer convenience path)
  2. **Enrich from backend by ticker** (backend fetches candles via mock/provider market-data mode)

### Supported columns (minimum)

- `ticker` (required)

### Current limitations

- Real provider-backed candle enrichment depends on backend market-data provider mode/config.
- Placeholder candle mode remains for development/testing and is not real market data.

## Notes

- UI intentionally minimal and operator-focused.
- No auth, no persistence, no chart rendering yet.
- Frontend consumes backend contracts as-is.
