const MODEL_STYLES = [
  { light: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  { light: 'bg-violet-50 text-violet-700 border-violet-200' },
  { light: 'bg-teal-50 text-teal-700 border-teal-200' },
  { light: 'bg-amber-50 text-amber-700 border-amber-200' },
  { light: 'bg-sky-50 text-sky-700 border-sky-200' },
];

const METRICS = [
  { key: 'precision', label: 'Precision', color: 'bg-indigo-400' },
  { key: 'recall',    label: 'Recall',    color: 'bg-sky-400' },
  { key: 'f1',        label: 'F1 Score',  color: 'bg-violet-400' },
  { key: 'auc',       label: 'AUC-ROC',   color: 'bg-amber-400' },
];

function Bar({ value, color }) {
  const pct = Math.round((value || 0) * 100);
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-medium text-slate-700 w-12 text-right tabular-nums">
        {(value || 0).toFixed(3)}
      </span>
    </div>
  );
}

export default function MetricsCard({ metrics }) {
  if (!metrics) return null;

  const modelEntries = Object.entries(metrics).filter(([, modelMetrics]) =>
    modelMetrics && typeof modelMetrics === 'object'
  );

  const formatModelLabel = (name) =>
    String(name)
      .replace(/_/g, ' ')
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      .replace(/\s+/g, ' ')
      .trim();

  if (modelEntries.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 animate-fade-up" style={{ animationDelay: '100ms' }}>
      <h3 className="text-sm font-semibold text-slate-800 mb-1">Model Performance</h3>
      <p className="text-[11px] text-slate-400 mb-5">Comparison across {modelEntries.length} trained models</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {modelEntries.map(([key, m], index) => {
          const style = MODEL_STYLES[index % MODEL_STYLES.length];
          return (
            <div key={key} className="rounded-lg border border-slate-100 p-4">
              <span className={`inline-block text-[10px] font-semibold px-2.5 py-0.5 rounded-full border mb-4 ${style.light}`}>{formatModelLabel(key)}</span>
              <div className="space-y-3">
                {METRICS.map(({ key: mk, label: ml, color: mc }) => (
                  <div key={mk}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] text-slate-500">{ml}</span>
                    </div>
                    <Bar value={m[mk]} color={mc} />
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
