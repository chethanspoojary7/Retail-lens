const BASE = import.meta.env.VITE_API_URL || '';
export async function api(path, opts = {}) {
  const res = await fetch(BASE + path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}
export const getDashboard = () => api('/api/dashboard');
export const getSegments = () => api('/api/segments');
export const getCustomers = (p) => api('/api/customers?' + new URLSearchParams(p));
export const getModels = () => api('/api/models/compare');
export const getInsights = () => api('/api/insights');
export const getAnalytics = () => api('/api/analytics');
export const getSummary = () => api('/api/data/summary');
export const uploadDataset = (file) => {
  const body = new FormData();
  body.append('file', file);
  return api('/api/data/upload', { method: 'POST', body });
};
export const runModels = (params) => api('/api/models/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) });
export const runAnalysis = (params) => api('/api/analysis/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params) });
export const exportCsv = (type) => { window.open(BASE + '/api/reports/export?type=' + type, '_blank'); };
export const getPreprocessing = () => api('/api/preprocessing/summary');
export const getEda = () => api('/api/eda/summary');
export const getClusteringResults = () => api('/api/clustering/results');
export const getClusterCustomers = (id, p = {}) => api('/api/clusters/' + id + '/customers?' + new URLSearchParams(p));
export const exportAssignments = () => { window.open(BASE + '/api/export/assignments', '_blank'); };
export const exportProfiles = () => { window.open(BASE + '/api/export/profiles', '_blank'); };
