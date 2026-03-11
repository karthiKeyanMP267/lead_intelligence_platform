import { RefreshCw } from 'lucide-react';

function fmt(d) {
  if (!d) return '—';
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function Navbar({ lastUpdated, onRefresh, loading }) {
  return (
    <header className="fixed top-0 left-60 right-0 h-14 bg-white border-b border-slate-200 flex items-center justify-between px-6 z-10">
      <div>
        <h1 className="text-sm font-semibold text-slate-800">Lead Intelligence Platform</h1>
        <p className="text-[11px] text-slate-400">AI-powered scoring and analytics</p>
      </div>
      <div className="flex items-center gap-4">
        {lastUpdated && (
          <span className="text-xs text-slate-400">Updated {fmt(lastUpdated)}</span>
        )}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 transition-colors disabled:opacity-40"
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
        <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[11px] font-medium text-emerald-700">Live</span>
        </div>
      </div>
    </header>
  );
}
