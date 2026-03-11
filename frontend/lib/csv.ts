import type { BatchInterpretRequest, BatchItemInput, Candle, CsvTickerRow } from "@/lib/types";

export type CsvParseResult = {
  rows: CsvTickerRow[];
  errors: string[];
};

function parseCsvLine(line: string): string[] {
  return line.split(",").map((part) => part.trim());
}

export function parseTickerCsv(rawCsv: string): CsvParseResult {
  const lines = rawCsv
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  if (lines.length === 0) {
    return { rows: [], errors: ["CSV is empty"] };
  }

  const headers = parseCsvLine(lines[0]).map((h) => h.toLowerCase());
  const tickerIndex = headers.indexOf("ticker");

  if (tickerIndex < 0) {
    return { rows: [], errors: ["CSV must include a 'ticker' column"] };
  }

  const rows: CsvTickerRow[] = [];
  const errors: string[] = [];

  lines.slice(1).forEach((line, i) => {
    const columns = parseCsvLine(line);
    const ticker = (columns[tickerIndex] ?? "").trim();
    const rowNumber = i + 2;

    if (!ticker) {
      errors.push(`Row ${rowNumber}: missing ticker value`);
      return;
    }

    rows.push({ ticker });
  });

  if (rows.length === 0 && errors.length === 0) {
    errors.push("No data rows found");
  }

  return { rows, errors };
}

function mockCandle(price: number, timestamp: string): Candle {
  return {
    timestamp,
    open: Number(price.toFixed(2)),
    high: Number((price * 1.03).toFixed(2)),
    low: Number((price * 0.97).toFixed(2)),
    close: Number((price * 1.01).toFixed(2)),
    volume: 100000,
  };
}

export function csvRowsToBatchRequest(rows: CsvTickerRow[], basePrice: number, step: number): BatchInterpretRequest {
  const items: BatchItemInput[] = rows.map((row, idx) => {
    const price = basePrice + idx * step;
    return {
      ticker: row.ticker,
      daily: [mockCandle(price, `csv_daily_${idx + 1}`)],
      h4: [mockCandle(price, `csv_h4_${idx + 1}`)],
      h1: [mockCandle(price, `csv_h1_${idx + 1}`)],
    };
  });

  return { items };
}
