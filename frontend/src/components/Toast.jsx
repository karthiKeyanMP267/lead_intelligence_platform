import { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

export default function Toast({ toast, onDismiss }) {
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(onDismiss, 4000);
    return () => clearTimeout(t);
  }, [toast, onDismiss]);

  if (!toast) return null;
  const isOk = toast.type === 'success';

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-fade-up">
      <div className={[
        'flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl border text-sm font-medium min-w-72 max-w-sm',
        isOk
          ? 'bg-white border-emerald-200 text-slate-800'
          : 'bg-white border-red-200 text-slate-800',
      ].join(' ')}>
        {isOk
          ? <CheckCircle size={16} className="text-emerald-500 flex-shrink-0" />
          : <XCircle    size={16} className="text-red-500 flex-shrink-0" />
        }
        <span className="flex-1">{toast.message}</span>
        <button onClick={onDismiss} className="text-slate-400 hover:text-slate-600 transition-colors">
          <X size={14} />
        </button>
      </div>
    </div>
  );
}
