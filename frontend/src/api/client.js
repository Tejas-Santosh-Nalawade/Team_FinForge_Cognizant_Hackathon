import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

apiClient.interceptors.request.use((config) => {
  const token = window.sessionStorage.getItem('finforge_access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/** Convert local-storage report paths into a URL served by FastAPI, not Vite. */
export const artifactUrl = (url) => {
  if (!url || url === '#') return null;
  if (/^https?:\/\//i.test(url)) return url;
  return `${API_ORIGIN}${url.startsWith('/') ? url : `/${url}`}`;
};

export const openArtifact = (url) => {
  const resolved = artifactUrl(url);
  if (resolved) window.open(resolved, '_blank', 'noopener,noreferrer');
};

export const uploadStatementFile = async (file, clientName, periodEnding, framework) => {
  const formData = new FormData();
  formData.append('file', file);
  if (clientName) formData.append('client_name', clientName);
  if (periodEnding) formData.append('period_ending', periodEnding);
  if (framework) formData.append('framework', framework);

  const response = await apiClient.post('/ingest/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const loginToWorkspace = async (email, password) => {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
};

export const resolveDiscrepancies = async (payload) => {
  const response = await apiClient.post('/audit/resolve-discrepancies', payload);
  return response.data;
};

export const explainFindingWithRAG = async (findingPayload) => {
  const response = await apiClient.post('/rag/explain-finding', findingPayload);
  return response.data;
};

export const runScenarioSimulation = async (driverPayload) => {
  const response = await apiClient.post('/simulator/stress-test', driverPayload);
  return response.data;
};

export const buildReportDeliverables = async (payload) => {
  const response = await apiClient.post('/reports/build-deliverables', payload);
  return response.data;
};

export const fetchEngagements = async () => {
  const response = await apiClient.get('/audit/engagements');
  return response.data;
};

export const fetchEngagement = async (engagementId) => {
  const response = await apiClient.get(`/audit/engagement/${engagementId}`);
  return response.data;
};

export const fetchDashboardSummary = async (engagementId) => {
  const url = engagementId ? `/audit/dashboard-summary?engagement_id=${encodeURIComponent(engagementId)}` : '/audit/dashboard-summary';
  const response = await apiClient.get(url);
  return response.data;
};

export const fetchRagStatus = async () => {
  const response = await apiClient.get('/rag/status');
  return response.data;
};
