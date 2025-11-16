'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { TickerForm, TickerFormValues } from '../components/TickerForm';
import { HistoryList } from '../components/HistoryList';
import { ResultPanel } from '../components/ResultPanel';
import { analyzeTicker, AnalyzePayload, AnalyzeResponse, fetchHistory, HistoryEntry } from '../lib/api';

export default function Home() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [result, setResult] = useState<AnalyzeResponse | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [historyError, setHistoryError] = useState<string | undefined>();

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const data = await fetchHistory(10);
        setHistory(data);
      } catch (err: any) {
        setHistoryError(err?.message || '히스토리를 불러오지 못했습니다.');
      }
    };
    loadHistory();
  }, []);

  const handleSubmit = useCallback(async (values: TickerFormValues) => {
    setLoading(true);
    setError(undefined);
    try {
      const payload: AnalyzePayload = {
        ticker: values.ticker,
        benchmark: values.benchmark,
        backtest_days: values.backtest_days,
      };
      const response = await analyzeTicker(payload);
      setResult(response);
      const refreshed = await fetchHistory(10);
      setHistory(refreshed);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || '분석 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleHistorySelect = useCallback((entry: HistoryEntry) => {
    if (entry.payload) {
      setResult(entry.payload);
    } else {
      handleSubmit({ ticker: entry.ticker });
    }
  }, [handleSubmit]);

  const summary = useMemo(() => result, [result]);

  return (
    <main className="space-y-8">
      <header className="text-center space-y-2">
        <p className="text-xs tracking-widest text-brand-300">Stock Analyzer</p>
        <h1 className="text-4xl font-bold">대시보드</h1>
        <p className="text-slate-400">
          티커와 벤치마크를 입력하면 즉시 분석 결과를 확인할 수 있습니다.
        </p>
      </header>
      <section className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <TickerForm loading={loading} onSubmit={handleSubmit} />
          <ResultPanel data={summary} loading={loading} error={error} />
        </div>
        <div className="space-y-4">
          <HistoryList history={history} onSelect={handleHistorySelect} />
          {historyError && <div className="text-sm text-red-400">{historyError}</div>}
        </div>
      </section>
    </main>
  );
}
