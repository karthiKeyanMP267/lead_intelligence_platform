export default function KPICard({ icon, label, value, sub, accent, trend, delay = 0 }) {
  const accents = {
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    red:    'bg-red-50    text-red-600    border-red-100',
    amber:  'bg-amber-50  text-amber-600  border-amber-100',
    emerald:'bg-emerald-50 text-emerald-600 border-emerald-100',
  };
  const colors = {
    indigo: 'from-indigo-500 to-indigo-600',
    red:    'from-red-500 to-red-600',
    amber:  'from-amber-500 to-amber-600',
    emerald:'from-emerald-500 to-emerald-600',
  };
  const cls = accents[accent] || accents.indigo;
  const gradient = colors[accent] || colors.indigo;

  return (
    <div
      className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 animate-fade-up relative overflow-hidden"
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Decorative gradient bar */}
      <div className={`absolute top-0 left-0 right-0 h-0.5 bg-linear-to-r ${gradient}`} />

      <div className="flex items-start justify-between mb-3">
        <div className={`w-9 h-9 rounded-lg border flex items-center justify-center text-lg ${cls}`}>
          {icon}
        </div>
        {trend != null && (
          <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${
            trend >= 0
              ? 'text-emerald-700 bg-emerald-50'
              : 'text-red-700 bg-red-50'
          }`}>
            {trend >= 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>

      <p className="text-2xl font-bold text-slate-900 tracking-tight">{value}</p>
      <p className="text-sm font-medium text-slate-600 mt-0.5">{label}</p>
      {sub && <p className="text-[11px] text-slate-400 mt-1">{sub}</p>}
    </div>
  );
}
