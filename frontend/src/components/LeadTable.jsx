import { useState, useMemo } from 'react';
import { Search, ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE = 20;

const PRIORITY_CONFIG = {
  HOT:  { bg: 'bg-red-50',    text: 'text-red-700',    border: 'border-red-200',    dot: 'bg-red-500' },
  WARM: { bg: 'bg-amber-50',  text: 'text-amber-700',  border: 'border-amber-200',  dot: 'bg-amber-500' },
  COLD: { bg: 'bg-sky-50',    text: 'text-sky-700',    border: 'border-sky-200',    dot: 'bg-sky-500' },
};

function PriorityBadge({ priority }) {
  const p = (priority || 'COLD').toUpperCase();
  const cfg = PRIORITY_CONFIG[p] || PRIORITY_CONFIG.COLD;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${cfg.bg} ${cfg.text} ${cfg.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {p}
    </span>
  );
}

function ScoreBar({ score }) {
  const pct = Math.round((score || 0) * 100);
  const color = pct >= 70 ? 'bg-red-500' : pct >= 40 ? 'bg-amber-500' : 'bg-sky-500';
  return (
    <div className="flex items-center gap-2 min-w-24">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-500 ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs tabular-nums font-medium text-slate-700 w-10 text-right">{(score || 0).toFixed(3)}</span>
    </div>
  );
}

function SortIcon({ col, sort }) {
  if (sort.col !== col) return <ChevronsUpDown size={12} className="text-slate-300" />;
  return sort.dir === 'asc'
    ? <ChevronUp size={12} className="text-indigo-500" />
    : <ChevronDown size={12} className="text-indigo-500" />;
}

const FILTERS = ['ALL', 'HOT', 'WARM', 'COLD'];

export default function LeadTable({ leads, conversationLoadingId, onEdit, onAddConversation }) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [sort, setSort] = useState({ col: 'score', dir: 'desc' });
  const [page, setPage] = useState(1);

  const filterCounts = useMemo(() => {
    const c = { ALL: leads.length };
    leads.forEach((l) => {
      const p = (l.priority || 'COLD').toUpperCase();
      c[p] = (c[p] || 0) + 1;
    });
    return c;
  }, [leads]);

  const filtered = useMemo(() => {
    let rows = leads;
    if (filter !== 'ALL') rows = rows.filter((l) => (l.priority || 'COLD').toUpperCase() === filter);
    if (search.trim()) {
      const q = search.toLowerCase();
      rows = rows.filter((l) =>
        String(l.lead_id || '').toLowerCase().includes(q) ||
        String(l.industry || '').toLowerCase().includes(q) ||
        String(l.country || '').toLowerCase().includes(q)
      );
    }
    rows = [...rows].sort((a, b) => {
      let av = a[sort.col] ?? 0, bv = b[sort.col] ?? 0;
      if (typeof av === 'string') av = av.toLowerCase();
      if (typeof bv === 'string') bv = bv.toLowerCase();
      if (av < bv) return sort.dir === 'asc' ? -1 : 1;
      if (av > bv) return sort.dir === 'asc' ? 1 : -1;
      return 0;
    });
    return rows;
  }, [leads, filter, search, sort]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageData = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function toggleSort(col) {
    setSort((s) => s.col === col ? { col, dir: s.dir === 'asc' ? 'desc' : 'asc' } : { col, dir: 'desc' });
    setPage(1);
  }

  const TH = ({ label, col, className = '' }) => (
    <th
      className={`px-4 py-3 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wider cursor-pointer select-none hover:text-slate-700 transition-colors ${className}`}
      onClick={() => col && toggleSort(col)}
    >
      <span className="flex items-center gap-1">
        {label}
        {col && <SortIcon col={col} sort={sort} />}
      </span>
    </th>
  );

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm animate-fade-up" style={{ animationDelay: '300ms' }}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-100">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-800">All Leads</h3>
            <p className="text-[11px] text-slate-400">{filtered.length} of {leads.length} leads</p>
          </div>
          <div className="relative">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search by ID, industry, country…"
              className="pl-8 pr-3 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 w-64 transition-all placeholder:text-slate-400"
            />
          </div>
        </div>
        {/* Filter chips */}
        <div className="flex gap-2 mt-3">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => { setFilter(f); setPage(1); }}
              className={[
                'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all',
                filter === f
                  ? f === 'HOT'  ? 'bg-red-600    text-white border-red-600'
                  : f === 'WARM' ? 'bg-amber-500  text-white border-amber-500'
                  : f === 'COLD' ? 'bg-sky-500    text-white border-sky-500'
                  : 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300',
              ].join(' ')}
            >
              {f !== 'ALL' && (
                <span className={`w-1.5 h-1.5 rounded-full ${
                  filter === f ? 'bg-white' :
                  f === 'HOT' ? 'bg-red-500' : f === 'WARM' ? 'bg-amber-500' : 'bg-sky-500'
                }`} />
              )}
              {f}
              <span className={`text-[10px] px-1 py-0 rounded ${filter === f ? 'bg-white/20' : 'bg-slate-100'}`}>
                {filterCounts[f] || 0}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50/50">
            <tr>
              <TH label="Lead ID"   col="lead_id"  />
              <TH label="Industry"  col="industry" />
              <TH label="Country"   col="country"  />
              <TH label="Revenue"   col="annual_revenue" />
              <TH label="Score"     col="score"    className="w-44" />
              <TH label="Priority"  col="priority" />
              <TH label=""          col={null}     />
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {pageData.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-sm text-slate-400">
                  No leads match your filters
                </td>
              </tr>
            ) : pageData.map((l) => (
              <tr key={l.lead_id} className="hover:bg-slate-50/60 transition-colors group">
                <td className="px-4 py-3 text-xs font-medium text-slate-800">#{l.lead_id}</td>
                <td className="px-4 py-3 text-xs text-slate-600">{l.industry || '—'}</td>
                <td className="px-4 py-3 text-xs text-slate-600">{l.country || '—'}</td>
                <td className="px-4 py-3 text-xs text-slate-600">
                  {l.annual_revenue ? `$${(l.annual_revenue / 1e6).toFixed(1)}M` : '—'}
                </td>
                <td className="px-4 py-3"><ScoreBar score={l.score} /></td>
                <td className="px-4 py-3"><PriorityBadge priority={l.priority} /></td>
                <td className="px-4 py-3">
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity inline-flex items-center gap-1">
                    <button
                      onClick={() => onEdit?.(l.lead_id)}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium bg-white text-slate-700 rounded-lg border border-slate-200 hover:bg-slate-50"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onAddConversation?.(l.lead_id)}
                      disabled={conversationLoadingId === l.lead_id}
                      className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-200 hover:bg-emerald-100 disabled:opacity-50 disabled:cursor-wait"
                    >
                      {conversationLoadingId === l.lead_id
                        ? <span className="w-3 h-3 border border-emerald-500 border-t-transparent rounded-full animate-spin" />
                        : <span className="text-[10px] font-semibold">+</span>
                      }
                      Conversation
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-5 py-3 border-t border-slate-100 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            Page {page} of {totalPages} · {filtered.length} results
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <ChevronLeft size={13} />
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let p;
              if (totalPages <= 5) p = i + 1;
              else if (page <= 3) p = i + 1;
              else if (page >= totalPages - 2) p = totalPages - 4 + i;
              else p = page - 2 + i;
              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={[
                    'w-7 h-7 rounded-lg text-xs font-medium transition-all',
                    page === p
                      ? 'bg-indigo-600 text-white'
                      : 'border border-slate-200 text-slate-600 hover:bg-slate-50',
                  ].join(' ')}
                >
                  {p}
                </button>
              );
            })}
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <ChevronRight size={13} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
