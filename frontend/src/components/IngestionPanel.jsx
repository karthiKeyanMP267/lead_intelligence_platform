import { useEffect, useState } from 'react';
import { Upload, PlusCircle } from 'lucide-react';

const initialLead = {
  industry: 'SaaS',
  company_size: 100,
  annual_revenue: 1000000,
  country: 'US',
  lead_stage: 'MQL',
  previous_interactions: 1,
  website_visits: 5,
  pages_viewed: 10,
  email_clicks: 1,
  calls_made: 0,
  meetings_scheduled: 0,
  demo_requested: 0,
  time_spent_minutes: 15,
  days_since_last_activity: 2,
  source: 'website',
  ads_clicked: 0,
  campaign_engagement_score: 50,
  converted: 0,
};

const fields = [
  { name: 'industry', label: 'Industry', type: 'text' },
  { name: 'country', label: 'Country', type: 'text' },
  { name: 'source', label: 'Source', type: 'text' },
  { name: 'lead_stage', label: 'Lead Stage', type: 'text' },
  { name: 'company_size', label: 'Company Size', type: 'number', numeric: true },
  { name: 'annual_revenue', label: 'Annual Revenue', type: 'number', numeric: true },
  { name: 'previous_interactions', label: 'Previous Interactions', type: 'number', numeric: true },
  { name: 'website_visits', label: 'Website Visits', type: 'number', numeric: true },
  { name: 'pages_viewed', label: 'Pages Viewed', type: 'number', numeric: true },
  { name: 'email_clicks', label: 'Email Clicks', type: 'number', numeric: true },
  { name: 'calls_made', label: 'Calls Made', type: 'number', numeric: true },
  { name: 'meetings_scheduled', label: 'Meetings Scheduled', type: 'number', numeric: true },
  { name: 'demo_requested', label: 'Demo Requested', type: 'number', numeric: true },
  { name: 'time_spent_minutes', label: 'Time Spent (Minutes)', type: 'number', numeric: true },
  { name: 'days_since_last_activity', label: 'Days Since Last Activity', type: 'number', numeric: true },
  { name: 'ads_clicked', label: 'Ads Clicked', type: 'number', numeric: true },
  { name: 'campaign_engagement_score', label: 'Campaign Engagement Score', type: 'number', numeric: true, step: '0.01' },
  { name: 'converted', label: 'Converted (0/1)', type: 'number', numeric: true, min: 0, max: 1 },
];

export default function IngestionPanel({ onSubmitLead, onUpdateLead, onPredictLead, onUploadCsv, loading, ingestStatus, predictedScore, editingLead, onCancelEdit }) {
  const [lead, setLead] = useState(initialLead);
  const [file, setFile] = useState(null);

  useEffect(() => {
    if (editingLead) {
      setLead((prev) => ({ ...prev, ...editingLead }));
    }
  }, [editingLead]);

  function updateLead(name, value, isNumeric = false) {
    setLead((prev) => ({
      ...prev,
      [name]: isNumeric ? Number(value) : value,
    }));
  }

  async function handleLeadSubmit(e) {
    e.preventDefault();
    if (editingLead?.lead_id) {
      await onUpdateLead(editingLead.lead_id, lead);
    } else {
      await onSubmitLead(lead);
    }
  }

  async function handlePredict(e) {
    e.preventDefault();
    await onPredictLead(lead);
  }

  async function handleCsvSubmit(e) {
    e.preventDefault();
    if (!file) return;
    await onUploadCsv(file);
    setFile(null);
    e.target.reset();
  }

  return (
    <section className="bg-white rounded-xl border border-slate-200 p-4 space-y-4 shadow-sm">
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div>
          <h3 className="text-sm font-semibold text-slate-800">Data Ingestion</h3>
          <p className="text-xs text-slate-500">Add one lead or upload a CSV to hit real-time endpoints</p>
        </div>
        {ingestStatus && (
          <div className="text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1.5">
            Auto-retrain threshold: <span className="font-semibold text-slate-700">{ingestStatus.retrain_threshold}</span> lead(s) · Remaining: <span className="font-semibold text-slate-700">{ingestStatus.leads_until_next_retrain}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <form onSubmit={handleLeadSubmit} className="border border-slate-200 rounded-lg p-3 space-y-3">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              {editingLead?.lead_id ? `Edit Lead #${editingLead.lead_id}` : 'Single Lead'}
            </h4>
            {editingLead?.lead_id && (
              <button
                type="button"
                onClick={onCancelEdit}
                className="text-[11px] text-slate-500 hover:text-slate-700"
              >
                Cancel Edit
              </button>
            )}
          </div>
          <div className="grid grid-cols-2 gap-2">
            {fields.map((field) => (
              <label key={field.name} className="space-y-1">
                <span className="text-[11px] font-medium text-slate-500">{field.label}</span>
                <input
                  type={field.type}
                  step={field.step}
                  min={field.min}
                  max={field.max}
                  className="w-full px-2.5 py-2 text-sm border border-slate-200 rounded-md"
                  value={lead[field.name]}
                  onChange={(e) => updateLead(field.name, e.target.value, !!field.numeric)}
                  required
                />
              </label>
            ))}
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button
              type="button"
              onClick={handlePredict}
              disabled={loading === 'predict'}
              className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-md disabled:opacity-60"
            >
              {loading === 'predict' ? (
                <span className="w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
              ) : (
                <PlusCircle size={14} />
              )}
              {loading === 'predict' ? 'Predicting…' : 'Predict Score'}
            </button>
            <button
              type="submit"
              disabled={loading === 'lead'}
              className="inline-flex items-center gap-2 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md disabled:opacity-60"
            >
              {loading === 'lead' ? (
                <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              ) : (
                <PlusCircle size={14} />
              )}
              {loading === 'lead' ? (editingLead?.lead_id ? 'Updating…' : 'Adding…') : (editingLead?.lead_id ? 'Update Lead' : 'Add Single Lead')}
            </button>
          </div>
          {typeof predictedScore === 'number' && (
            <div className="text-sm bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-md px-3 py-2">
              Predicted Lead Score: <span className="font-semibold">{predictedScore.toFixed(4)}</span>
            </div>
          )}
        </form>

        <form onSubmit={handleCsvSubmit} className="border border-slate-200 rounded-lg p-3 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">CSV Upload</h4>
          <p className="text-xs text-slate-500">Upload a .csv file with the same columns as backend ingest endpoint.</p>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-slate-600 file:mr-3 file:px-3 file:py-2 file:border-0 file:rounded-md file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200"
            required
          />
          <button
            type="submit"
            disabled={loading === 'csv' || !file}
            className="inline-flex items-center gap-2 px-3 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-md disabled:opacity-60"
          >
            {loading === 'csv' ? (
              <span className="w-4 h-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
            ) : (
              <Upload size={14} />
            )}
            {loading === 'csv' ? 'Uploading…' : 'Upload CSV'}
          </button>
        </form>
      </div>
    </section>
  );
}
