import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList } from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg px-3 py-2 text-xs">
      <p className="font-medium text-slate-800">{payload[0].payload.name}</p>
      <p className="text-slate-500">Importance: <span className="font-medium text-indigo-600">{(payload[0].value * 100).toFixed(1)}%</span></p>
    </div>
  );
};

export default function FeatureImportanceChart({ data }) {
  const [showAll, setShowAll] = useState(false);

  const sorted = [...(data || [])].sort((a, b) => b.value - a.value);
  const display = showAll ? sorted : sorted.slice(0, 10);

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 animate-fade-up" style={{ animationDelay: '250ms' }}>
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-sm font-semibold text-slate-800">Feature Importance</h3>
        <div className="flex rounded-lg border border-slate-200 overflow-hidden">
          {['Top 10', 'All'].map((label) => {
            const active = (label === 'All') === showAll;
            return (
              <button
                key={label}
                onClick={() => setShowAll(label === 'All')}
                className={[
                  'px-3 py-1 text-xs font-medium transition-colors',
                  active ? 'bg-indigo-600 text-white' : 'text-slate-500 hover:text-slate-700 bg-white',
                ].join(' ')}
              >
                {label}
              </button>
            );
          })}
        </div>
      </div>
      <p className="text-[11px] text-slate-400 mb-4">LightGBM relative feature contributions</p>
      <ResponsiveContainer width="100%" height={Math.max(240, display.length * 28)}>
        <BarChart layout="vertical" data={display} margin={{ top: 0, right: 80, bottom: 0, left: 160 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
          <XAxis type="number" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 9, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} axisLine={false} width={155} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" fill="#6366f1" radius={[0, 3, 3, 0]} maxBarSize={14}>
            <LabelList dataKey="value" position="right" formatter={(v) => `${(v * 100).toFixed(1)}%`} style={{ fontSize: 10, fill: '#64748b' }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
