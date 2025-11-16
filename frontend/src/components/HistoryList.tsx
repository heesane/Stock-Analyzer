'use client';

import { HistoryEntry } from '../lib/api';

interface HistoryListProps {
  history: HistoryEntry[];
  onSelect: (entry: HistoryEntry) => void;
}

export function HistoryList({ history, onSelect }: HistoryListProps) {
  if (!history.length) {
    return (
      <div className="card p-4 text-sm text-slate-400">
        최근 분석한 기록이 없습니다.
      </div>
    );
  }
  return (
    <div className="card p-4">
      <h3 className="font-semibold mb-3">최근 분석</h3>
      <ul className="space-y-2">
        {history.map((entry) => (
          <li key={`${entry.ticker}-${entry.created_at}`}>
            <button
              onClick={() => onSelect(entry)}
              className="w-full rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-left hover:border-brand-400"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold">{entry.ticker}</span>
                <span className="text-xs text-slate-500">
                  {entry.created_at ? new Date(entry.created_at).toLocaleString() : ''}
                </span>
              </div>
              {entry.benchmark && (
                <p className="text-xs text-slate-500">vs {entry.benchmark}</p>
              )}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
