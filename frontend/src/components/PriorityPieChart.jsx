import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = { HOT: '#ef4444', WARM: '#f59e0b', COLD: '#38bdf8' };

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg px-3 py-2 text-xs">
      <p className="font-semibold text-slate-800">{d.name}</p>
      <p className="text-slate-500">{d.value} leads ({d.payload.pct}%)</p>
    </div>
  );
};

export default function PriorityPieChart({ leads }) {
  const counts = leads.reduce((acc, l) => {
    const p = (l.priority || 'COLD').toUpperCase();
    acc[p] = (acc[p] || 0) + 1;
    return acc;
  }, {});
  const total = leads.length || 1;
  const data = Object.entries(counts).map(([name, value]) => ({
    name, value, pct: ((value / total) * 100).toFixed(1),
  }));

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 animate-fade-up" style={{ animationDelay: '150ms' }}>
      <h3 className="text-sm font-semibold text-slate-800 mb-1">Priority Distribution</h3>
      <p className="text-[11px] text-slate-400 mb-4">{leads.length} total leads</p>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name] || '#94a3b8'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(v) => <span className="text-xs text-slate-600">{v}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
