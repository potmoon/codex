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
  - Two input modes:
    - **Paste JSON** (existing flow)
    - **Upload CSV** (frontend-only conversion to existing batch JSON payload)

## CSV upload flow

- Upload a `.csv` file (or paste CSV text) with at least a `ticker` column.
- CSV rows are parsed client-side.
- A preview table of parsed rows is shown before submission.
- Parsed rows are converted into the existing batch request shape expected by `POST /analyze/batch-interpret`.

### Supported columns (minimum)

- `ticker` (required)

### Current limitation

Real candle/market-data enrichment from tickers is **not automated yet**.

For development/testing, CSV rows are mapped to temporary mock candles using configurable placeholder settings (base price + per-row step). This will be replaced later by real data enrichment.

## Notes

- UI intentionally minimal and operator-focused.
- No auth, no persistence, no chart rendering yet.
- Frontend consumes backend contracts as-is.
