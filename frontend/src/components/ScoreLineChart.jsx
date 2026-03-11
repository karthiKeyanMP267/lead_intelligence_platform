import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg px-3 py-2 text-xs">
      <p className="text-slate-500">Score range: <span className="font-medium text-slate-800">{payload[0].payload.range}</span></p>
      <p className="text-slate-500">Leads: <span className="font-medium text-slate-800">{payload[0].value}</span></p>
    </div>
  );
};

export default function ScoreLineChart({ leads }) {
  const buckets = Array.from({ length: 10 }, (_, i) => ({
    range: `${i * 10}–${i * 10 + 10}%`,
    count: 0,
  }));
  leads.forEach((l) => {
    const score = (l.score ?? l.lead_score ?? 0);
    const idx = Math.min(Math.floor(score * 10), 9);
    buckets[idx].count++;
  });
  const data = buckets.map((b) => ({ range: b.range, count: b.count }));

  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5 animate-fade-up" style={{ animationDelay: '200ms' }}>
      <h3 className="text-sm font-semibold text-slate-800 mb-1">Score Distribution</h3>
      <p className="text-[11px] text-slate-400 mb-4">Lead count per score bucket</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} barSize={18} margin={{ top: 4, right: 8, bottom: 0, left: -10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis dataKey="range" tick={{ fontSize: 9, fill: '#94a3b8' }} tickLine={false} axisLine={false} interval={1} />
          <YAxis tick={{ fontSize: 9, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" fill="#6366f1" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
