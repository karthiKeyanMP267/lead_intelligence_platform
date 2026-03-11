import { Zap, RefreshCw } from 'lucide-react';

export default function ControlsPanel({ onBatchScore, onRetrain, loading }) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      <button
        onClick={onBatchScore}
        disabled={!!loading}
        className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white text-sm font-medium rounded-lg shadow-sm shadow-indigo-200 hover:shadow-md hover:shadow-indigo-200 hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none transition-all duration-150"
      >
        {loading === 'batch' ? (
          <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
        ) : (
          <Zap size={15} />
        )}
        {loading === 'batch' ? 'Scoring…' : 'Batch Score'}
      </button>
      <button
        onClick={onRetrain}
        disabled={!!loading}
        className="inline-flex items-center gap-2 px-4 py-2.5 bg-white hover:bg-slate-50 active:bg-slate-100 text-slate-700 text-sm font-medium rounded-lg border border-slate-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none transition-all duration-150"
      >
        {loading === 'retrain' ? (
          <span className="w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
        ) : (
          <RefreshCw size={15} />
        )}
        {loading === 'retrain' ? 'Retraining…' : 'Retrain Model'}
      </button>
    </div>
  );
}
