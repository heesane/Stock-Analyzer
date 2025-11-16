'use client';

import { useState } from 'react';

export interface TickerFormValues {
  ticker: string;
  benchmark?: string;
  backtest_days?: number;
}

interface Props {
  loading: boolean;
  onSubmit: (values: TickerFormValues) => void;
}

export function TickerForm({ loading, onSubmit }: Props) {
  const [ticker, setTicker] = useState('');
  const [benchmark, setBenchmark] = useState('');
  const [backtestDays, setBacktestDays] = useState<number | ''>('');

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!ticker.trim()) return;
    onSubmit({
      ticker: ticker.trim().toUpperCase(),
      benchmark: benchmark.trim() || undefined,
      backtest_days: typeof backtestDays === 'number' ? backtestDays : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="card p-6 space-y-4">
      <div>
        <label className="text-sm text-slate-400">Ticker</label>
        <input
          className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-lg focus:border-brand-400 focus:outline-none"
          placeholder="예: AAPL, TSLA"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          disabled={loading}
        />
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="text-sm text-slate-400">Benchmark (선택)</label>
          <input
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            placeholder="예: QQQ"
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value.toUpperCase())}
            disabled={loading}
          />
        </div>
        <div>
          <label className="text-sm text-slate-400">Backtest Days (선택)</label>
          <input
            type="number"
            min={1}
            className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
            placeholder="예: 120"
            value={backtestDays}
            onChange={(e) => {
              const value = e.target.value;
              setBacktestDays(value ? Number(value) : '');
            }}
            disabled={loading}
          />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-brand-500 px-4 py-2 font-semibold text-white hover:bg-brand-400 disabled:opacity-70"
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </form>
  );
}
