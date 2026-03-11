export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="w-8 h-8 rounded-lg bg-slate-100" />
        <div className="w-12 h-3 rounded bg-slate-100" />
      </div>
      <div className="w-20 h-7 rounded bg-slate-100 mb-2" />
      <div className="w-28 h-3 rounded bg-slate-100" />
    </div>
  );
}

export function SkeletonTable() {
  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 animate-pulse">
      <div className="w-40 h-4 rounded bg-slate-100 mb-6" />
      {[...Array(6)].map((_, i) => (
        <div key={i} className="flex gap-4 mb-3">
          <div className="w-24 h-3 rounded bg-slate-100" />
          <div className="flex-1 h-3 rounded bg-slate-100" />
          <div className="w-16 h-3 rounded bg-slate-100" />
          <div className="w-16 h-3 rounded bg-slate-100" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 animate-pulse">
      <div className="w-32 h-4 rounded bg-slate-100 mb-4" />
      <div className="w-full h-52 rounded-lg bg-slate-100" />
    </div>
  );
}
