import { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import KPICard from '../components/KPICard';
import MetricsCard from '../components/MetricsCard';
import PriorityPieChart from '../components/PriorityPieChart';
import ScoreLineChart from '../components/ScoreLineChart';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import LeadTable from '../components/LeadTable';
import ControlsPanel from '../components/ControlsPanel';
import IngestionPanel from '../components/IngestionPanel';
import Toast from '../components/Toast';
import { SkeletonCard, SkeletonTable, SkeletonChart } from '../components/Skeleton';
import {
  getLeads,
  getLeadById,
  updateLeadById,
  getMetrics,
  getFeatureImportance,
  batchScore,
  retrainModel,
  ingestLead,
  predictLead,
  ingestCsv,
  getIngestStatus,
  addConversation,
} from '../api/api';

export default function Dashboard() {
  const [activeNav, setActiveNav]   = useState('dashboard');
  const [leads, setLeads]           = useState([]);
  const [metrics, setMetrics]       = useState(null);
  const [featureData, setFeatureData] = useState([]);
  const [loading, setLoading]       = useState(false);
  const [dataLoading, setDataLoading] = useState(true);
  const [toast, setToast]           = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [ingestLoading, setIngestLoading] = useState(null);
  const [ingestStatus, setIngestStatus] = useState(null);
  const [predictedScore, setPredictedScore] = useState(null);
  const [editingLead, setEditingLead] = useState(null);
  const [conversationLoadingId, setConversationLoadingId] = useState(null);
  const editPanelRef = useRef(null);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
  }, []);

  const fetchAll = useCallback(async () => {
    setDataLoading(true);
    try {
      const [leadsRes, metricsRes, fiRes] = await Promise.all([
        getLeads(),
        getMetrics(),
        getFeatureImportance(),
      ]);
      setLeads(leadsRes.data?.leads || leadsRes.data || []);
      setMetrics(metricsRes.data);
      const fi = fiRes.data;
      const arr = Array.isArray(fi)
        ? fi
        : Object.entries(fi).map(([name, value]) => ({ name, value }));
      setFeatureData(arr);
      setLastUpdated(new Date());
    } catch (e) {
      showToast('Failed to load data. Is the backend running?', 'error');
    } finally {
      setDataLoading(false);
    }
  }, [showToast]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const fetchIngestStatus = useCallback(async () => {
    try {
      const res = await getIngestStatus();
      setIngestStatus(res.data);
    } catch {
      setIngestStatus(null);
    }
  }, []);

  useEffect(() => { fetchIngestStatus(); }, [fetchIngestStatus]);

  async function handleBatchScore() {
    setLoading('batch');
    try {
      await batchScore();
      await fetchAll();
      showToast('Batch scoring completed successfully');
    } catch {
      showToast('Batch scoring failed', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function handleRetrain() {
    setLoading('retrain');
    try {
      await retrainModel();
      await fetchAll();
      showToast('Model retrained successfully');
    } catch {
      showToast('Retraining failed', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function handleAddConversation(leadId) {
    const text = window.prompt('Paste the latest conversation transcript or notes');
    if (!text || !text.trim()) return;
    setConversationLoadingId(leadId);
    try {
      await addConversation(leadId, text.trim());
      await fetchAll();
      showToast(`Conversation added and lead #${leadId} re-scored`);
    } catch {
      showToast('Adding conversation failed', 'error');
    } finally {
      setConversationLoadingId(null);
    }
  }

  async function handleIngestLead(payload) {
    setIngestLoading('lead');
    try {
      const res = await ingestLead(payload);
      await Promise.all([fetchAll(), fetchIngestStatus()]);
      const leadId = res?.data?.lead_id;
      showToast(leadId ? `Lead #${leadId} added and scored` : 'Lead added and scored');
    } catch {
      showToast('Single lead ingestion failed', 'error');
    } finally {
      setIngestLoading(null);
    }
  }

  async function handleEditLead(leadId) {
    setIngestLoading('edit-load');
    try {
      setActiveNav('leads');
      const res = await getLeadById(leadId);
      setEditingLead(res.data);
      setTimeout(() => {
        editPanelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 50);
    } catch {
      showToast('Failed to load lead for editing', 'error');
    } finally {
      setIngestLoading(null);
    }
  }

  async function handleUpdateLead(leadId, payload) {
    setIngestLoading('lead');
    try {
      await updateLeadById(leadId, payload);
      await Promise.all([fetchAll(), fetchIngestStatus()]);
      setEditingLead(null);
      showToast(`Lead #${leadId} updated and re-scored`);
    } catch {
      showToast('Lead update failed', 'error');
    } finally {
      setIngestLoading(null);
    }
  }

  async function handlePredictLead(payload) {
    setIngestLoading('predict');
    try {
      const res = await predictLead(payload);
      const score = res?.data?.predicted_score;
      if (typeof score === 'number') {
        setPredictedScore(score);
        showToast(`Predicted score: ${score.toFixed(4)}`);
      } else {
        showToast('Prediction returned no score', 'error');
      }
    } catch {
      showToast('Prediction failed', 'error');
    } finally {
      setIngestLoading(null);
    }
  }

  async function handleIngestCsv(file) {
    setIngestLoading('csv');
    try {
      const res = await ingestCsv(file);
      await Promise.all([fetchAll(), fetchIngestStatus()]);
      const count = res?.data?.count;
      showToast(count ? `${count} leads uploaded successfully` : 'CSV uploaded successfully');
    } catch {
      showToast('CSV upload failed', 'error');
    } finally {
      setIngestLoading(null);
    }
  }

  /* ── derived stats ── */
  const hotLeads  = leads.filter((l) => (l.priority || '').toUpperCase() === 'HOT').length;
  const warmLeads = leads.filter((l) => (l.priority || '').toUpperCase() === 'WARM').length;
  const coldLeads = leads.filter((l) => (l.priority || '').toUpperCase() === 'COLD').length;
  const avgScore  = leads.length ? (leads.reduce((s, l) => s + (l.score || 0), 0) / leads.length) : 0;

  let topAUC = 0, topModel = '—';
  if (metrics) {
    Object.entries(metrics).forEach(([k, v]) => {
      if ((v.auc || 0) > topAUC) { topAUC = v.auc; topModel = k; }
    });
  }

  const navMeta = {
    dashboard: {
      title: 'Overview',
      subtitle: 'System summary and KPI snapshot',
    },
    leads: {
      title: 'Leads',
      subtitle: 'Ingest, predict, and manage lead records',
    },
    analytics: {
      title: 'Analytics',
      subtitle: 'Priority and scoring trends',
    },
    insights: {
      title: 'Model Insights',
      subtitle: 'Model metrics and feature importance',
    },
    settings: {
      title: 'Settings',
      subtitle: 'Operational actions for scoring and retraining',
    },
  };

  const current = navMeta[activeNav] || navMeta.dashboard;

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar active={activeNav} onChange={setActiveNav} />

      {/* Main */}
      <div className="flex-1 ml-60 flex flex-col min-h-screen">
        <Navbar lastUpdated={lastUpdated} onRefresh={fetchAll} loading={dataLoading} />

        <main className="flex-1 px-6 py-6 mt-14 space-y-6 max-w-screen-2xl w-full mx-auto">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-up">
            <div>
              <h2 className="text-base font-semibold text-slate-800">{current.title}</h2>
              <p className="text-xs text-slate-400">{current.subtitle}</p>
            </div>
            {(activeNav === 'dashboard' || activeNav === 'settings') && (
              <ControlsPanel onBatchScore={handleBatchScore} onRetrain={handleRetrain} loading={loading} />
            )}
          </div>

          {activeNav === 'dashboard' && (
            <>
              {dataLoading ? (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
                </div>
              ) : (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <KPICard icon="👥" label="Total Leads" value={leads.length.toLocaleString()} sub="In database" accent="indigo" delay={0} />
                  <KPICard icon="🔥" label="HOT Leads" value={hotLeads} sub={`${warmLeads} Warm · ${coldLeads} Cold`} accent="red" delay={80} />
                  <KPICard icon="🎯" label="Avg Lead Score" value={avgScore.toFixed(3)} sub="Across all leads" accent="amber" delay={160} />
                  <KPICard icon="🏆" label="Best AUC" value={topAUC.toFixed(3)} sub={topModel} accent="emerald" delay={240} />
                </div>
              )}
              {dataLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <SkeletonChart /><SkeletonChart />
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <PriorityPieChart leads={leads} />
                  <ScoreLineChart leads={leads} />
                </div>
              )}
            </>
          )}

          {activeNav === 'leads' && (
            <>
              <div ref={editPanelRef}>
                <IngestionPanel
                  onSubmitLead={handleIngestLead}
                  onUpdateLead={handleUpdateLead}
                  onPredictLead={handlePredictLead}
                  onUploadCsv={handleIngestCsv}
                  loading={ingestLoading}
                  ingestStatus={ingestStatus}
                  predictedScore={predictedScore}
                  editingLead={editingLead}
                  onCancelEdit={() => setEditingLead(null)}
                />
              </div>
              {dataLoading ? <SkeletonTable /> : (
                <LeadTable
                  leads={leads}
                  conversationLoadingId={conversationLoadingId}
                  onEdit={handleEditLead}
                  onAddConversation={handleAddConversation}
                />
              )}
            </>
          )}

          {activeNav === 'analytics' && (
            <>
              {dataLoading ? (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
                </div>
              ) : (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <KPICard icon="👥" label="Total Leads" value={leads.length.toLocaleString()} sub="In database" accent="indigo" delay={0} />
                  <KPICard icon="🔥" label="HOT Leads" value={hotLeads} sub={`${warmLeads} Warm · ${coldLeads} Cold`} accent="red" delay={80} />
                  <KPICard icon="🎯" label="Avg Lead Score" value={avgScore.toFixed(3)} sub="Across all leads" accent="amber" delay={160} />
                  <KPICard icon="🏆" label="Best AUC" value={topAUC.toFixed(3)} sub={topModel} accent="emerald" delay={240} />
                </div>
              )}
              {dataLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <SkeletonChart /><SkeletonChart />
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <PriorityPieChart leads={leads} />
                  <ScoreLineChart leads={leads} />
                </div>
              )}
            </>
          )}

          {activeNav === 'insights' && (
            <>
              {dataLoading ? <SkeletonChart /> : <MetricsCard metrics={metrics} />}
              {dataLoading ? <SkeletonChart /> : <FeatureImportanceChart data={featureData} />}
            </>
          )}

          {activeNav === 'settings' && (
            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <p className="text-sm text-slate-600">Use the actions above to run batch scoring or retrain the model.</p>
            </div>
          )}
        </main>
      </div>

      <Toast toast={toast} onDismiss={() => setToast(null)} />
    </div>
  );
}
