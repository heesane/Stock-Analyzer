import axios from 'axios';

export interface AnalyzePayload {
  ticker: string;
  lang?: string;
  benchmark?: string | null;
  backtest_days?: number | null;
  relative_window?: number | null;
}

export interface ScoreIndicator {
  key: string;
  label_key: string;
  value?: string | number | null;
  display?: string | null;
  score: number;
  weight: number;
  category: string;
}

export interface Scorecard {
  indicators: ScoreIndicator[];
  total_score: number;
  rating_label_key: string;
  category_scores: { category: string; label_key: string; score: number }[];
}

export interface AnalyzeResponse {
  ticker: string;
  latest_date: string;
  latest_close: number;
  decision: { action: string; rationale: string };
  scorecard: Scorecard;
  probability?: {
    bullish: number;
    bearish: number;
    confidence_key: string;
  };
  risk?: Record<string, unknown>;
  relative_performance?: Record<string, unknown>;
  backtest?: Record<string, unknown>;
}

export interface HistoryEntry {
  ticker: string;
  benchmark?: string | null;
  lang: string;
  created_at?: string;
  payload?: AnalyzeResponse | null;
}

const DEFAULT_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function analyzeTicker(payload: AnalyzePayload): Promise<AnalyzeResponse> {
  const baseURL = DEFAULT_BASE.replace(/\/$/, '');
  const { data } = await axios.post<AnalyzeResponse>(`${baseURL}/analyze`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  return data;
}

export async function fetchHistory(limit = 10): Promise<HistoryEntry[]> {
  const baseURL = DEFAULT_BASE.replace(/\/$/, '');
  const { data } = await axios.get<HistoryEntry[]>(`${baseURL}/history`, {
    params: { limit },
  });
  return data;
}
