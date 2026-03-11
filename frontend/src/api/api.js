import axios from 'axios';

const api = axios.create({ baseURL: 'http://127.0.0.1:8001' });

export const getLeads            = ()         => api.get('/leads');
export const getLeadById         = (leadId)   => api.get(`/leads/${leadId}`);
export const updateLeadById      = (leadId, payload) => api.put(`/leads/${leadId}`, payload);
export const getMetrics          = ()         => api.get('/metrics');
export const getFeatureImportance = ()        => api.get('/feature-importance');
export const batchScore          = ()         => api.post('/batch-score');
export const retrainModel        = ()         => api.post('/retrain');
export const ingestLead          = (payload)  => api.post('/ingest/lead', payload);
export const predictLead         = (payload)  => api.post('/predict/lead', payload);
export const getIngestStatus     = ()         => api.get('/ingest/status');
export const addConversation     = (leadId, text) => api.post(`/leads/${leadId}/conversation`, { text });
export const ingestCsv           = (file)     => {
	const formData = new FormData();
	formData.append('file', file);
	return api.post('/ingest/csv', formData, {
		headers: { 'Content-Type': 'multipart/form-data' },
	});
};
