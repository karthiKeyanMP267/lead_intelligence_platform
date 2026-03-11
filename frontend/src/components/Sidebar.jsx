import { LayoutDashboard, Users, BarChart2, Brain, Settings, Zap, ChevronRight } from 'lucide-react';

const NAV = [
  { icon: LayoutDashboard, label: 'Dashboard',     id: 'dashboard',  active: true },
  { icon: Users,           label: 'Leads',         id: 'leads' },
  // { icon: BarChart2,       label: 'Analytics',     id: 'analytics' },
  { icon: Brain,           label: 'Model Insights', id: 'insights' },
  // { icon: Settings,        label: 'Settings',      id: 'settings' },
];

export default function Sidebar({ active, onChange }) {
  return (
    <aside className="fixed inset-y-0 left-0 w-60 bg-slate-900 flex flex-col z-20 select-none">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0">
          <Zap size={16} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white leading-tight">Lead Intelligence</p>
          <p className="text-[10px] text-slate-500 leading-tight">AI-Powered Platform</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto scrollbar-thin">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-600 px-2 mb-3">Navigation</p>
        {NAV.map(({ icon: Icon, label, id }) => {
          const isActive = active === id;
          return (
            <button
              key={id}
              onClick={() => onChange?.(id)}
              className={[
                'w-full flex items-center justify-between gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group',
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/40'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800',
              ].join(' ')}
            >
              <span className="flex items-center gap-3">
                <Icon size={16} />
                {label}
              </span>
              {isActive && <ChevronRight size={14} className="opacity-60" />}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center text-xs font-semibold text-slate-300">A</div>
          <div>
            <p className="text-xs font-medium text-slate-300">Admin</p>
            <p className="text-[10px] text-slate-600">v1.0.0</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
