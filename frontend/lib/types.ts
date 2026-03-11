export type Candle = {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
};

export type AnalyzeRequest = {
  ticker: string;
  candles: {
    daily: Candle[];
    h4: Candle[];
    h1: Candle[];
  };
};

export type MtfView = {
  daily: string;
  h4: string;
  h1: string;
};

export type Levels = {
  daily: Record<string, number | null>;
  h4: Record<string, number | null>;
  h1: Record<string, number | null>;
};

export type Signals = {
  daily_allows_long: boolean;
  h4_setup_active: boolean;
  h1_late_after_ignition: boolean;
};

export type ReasonFlags = {
  daily_allows_long: boolean;
  h4_setup_active: boolean;
  h1_late_after_ignition: boolean;
  prior_entry_likely_happened: boolean;
  local_climax_present: boolean;
  major_bc_risk: boolean;
  extended_from_break: boolean;
};

export type DecisionContext = {
  action: string;
  entry_stage: string;
  conflict_level: string;
};

export type AnalyzeResponse = {
  ticker: string;
  mtf_view: MtfView;
  levels: Levels;
  signals: Signals;
  reason_flags: ReasonFlags;
  decision_context: DecisionContext;
};

export type LlmPayload = {
  ticker: string;
  mtf_view: MtfView;
  levels: Levels;
  signals: Signals;
  reason_flags: ReasonFlags;
  decision_context: DecisionContext;
};

export type Interpretation = {
  ticker: string;
  action: "buy" | "wait" | "sell";
  setup_type: string;
  entry_stage: "best" | "early" | "late" | "no_trade";
  confidence: number;
  summary: string;
  mtf_view: MtfView;
  invalidation: {
    type: string;
    value: number | null;
  };
};

export type InterpreterContext = {
  mode: "mock" | "openai" | "fallback_mock";
  used_images: boolean;
  image_count: number;
};

export type InterpretWrapper = {
  ticker: string;
  facts: AnalyzeResponse;
  llm_payload: LlmPayload;
  interpretation: Interpretation;
};

export type InterpretWithImagesWrapper = InterpretWrapper & {
  interpreter_context: InterpreterContext;
};

export type BatchItemInput = {
  ticker: string;
  daily: Candle[];
  h4: Candle[];
  h1: Candle[];
};

export type BatchInterpretRequest = {
  items: BatchItemInput[];
};

export type BatchInterpretItem = {
  ticker: string;
  status: "ok" | "error";
  facts: AnalyzeResponse;
  llm_payload: LlmPayload;
  interpretation: Interpretation;
  ranking: {
    score: number;
    priority: "high" | "medium" | "low";
    reason: string;
  };
};

export type BatchInterpretResponse = {
  count: number;
  items: BatchInterpretItem[];
  sorted_by: string;
};


export type CsvTickerRow = {
  ticker: string;
};
