'use client';

import { ScoreIndicator } from '../lib/api';

interface Props {
  data?: {
    ticker: string;
    latest_date: string;
    latest_close: number;
    decision: { action: string; rationale: string };
    scorecard: {
      total_score: number;
      rating_label_key: string;
      indicators: ScoreIndicator[];
    };
  };
  loading: boolean;
  error?: string;
}

const ratingMap: Record<string, string> = {
  rating_strong_buy: '강력 매수',
  rating_buy: '매수',
  rating_neutral: '중립',
  rating_sell: '매도',
};

export function ResultPanel({ data, loading, error }: Props) {
  if (loading) {
    return <div className="card p-6 text-brand-200">분석 중입니다...</div>;
  }
  if (error) {
    return <div className="card p-6 text-red-400">{error}</div>;
  }
  if (!data) {
    return <div className="card p-6 text-slate-400">분석 결과가 여기에 표시됩니다.</div>;
  }

  const rating = ratingMap[data.scorecard.rating_label_key] || data.scorecard.rating_label_key;

  return (
    <div className="card space-y-4 p-6">
      <div>
        <p className="text-sm text-slate-400">{data.latest_date}</p>
        <h2 className="text-2xl font-bold">
          {data.ticker} <span className="text-lg text-slate-400">${data.latest_close.toFixed(2)}</span>
        </h2>
      </div>
      <div className="rounded-lg bg-slate-950/60 p-4">
        <p className="text-sm text-slate-400">판단</p>
        <p className="text-lg font-semibold">{data.decision.action}</p>
        <p className="text-slate-300">{data.decision.rationale}</p>
      </div>
      <div className="rounded-lg bg-slate-950/60 p-4">
        <p className="text-sm text-slate-400">종합 점수</p>
        <p className="text-3xl font-bold text-brand-300">{data.scorecard.total_score.toFixed(1)} / 100</p>
        <p className="text-slate-300">등급: {rating}</p>
      </div>
      <div>
        <h3 className="mb-2 font-semibold">지표 요약</h3>
        <div className="grid gap-3 md:grid-cols-2">
          {data.scorecard.indicators.slice(0, 6).map((indicator) => (
            <div key={indicator.key} className="rounded-lg border border-slate-800 p-3">
              <p className="text-sm text-slate-400">{indicator.label_key}</p>
              <p className="text-lg font-semibold">{indicator.score.toFixed(1)}</p>
              <p className="text-xs text-slate-500">weight {indicator.weight.toFixed(1)}%</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
