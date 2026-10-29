import {
  DashboardSummary,
  RecoveryAnalysisData,
  ServiceHealth,
  Experiment,
  ExperimentType,
  TargetService
} from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  getDashboardSummary: (): Promise<DashboardSummary> =>
    request<DashboardSummary>('/api/dashboard/summary'),

  getRecoveryAnalysis: (): Promise<RecoveryAnalysisData> =>
    request<RecoveryAnalysisData>('/api/dashboard/analysis'),

  getServices: (): Promise<ServiceHealth[]> =>
    request<ServiceHealth[]>('/api/services'),

  verifyService: (serviceId: string): Promise<any> =>
    request<any>(`/api/services/${serviceId}/verify`, { method: 'POST' }),

  triggerExperiment: (payload: {
    type: ExperimentType;
    target_service: TargetService;
    duration_seconds: number;
    load_percent?: number;
    memory_mb?: number;
    delay_ms?: number;
    confirm_destruction: boolean;
  }): Promise<Experiment> =>
    request<Experiment>('/api/experiments', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getExperiments: (params?: {
    type?: string;
    target_service?: string;
    status?: string;
    limit?: number;
  }): Promise<Experiment[]> => {
    const query = new URLSearchParams();
    if (params?.type) query.append('type', params.type);
    if (params?.target_service) query.append('target_service', params.target_service);
    if (params?.status) query.append('status', params.status);
    if (params?.limit) query.append('limit', params.limit.toString());
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<Experiment[]>(`/api/experiments${qs}`);
  },

  getExperiment: (id: string): Promise<Experiment> =>
    request<Experiment>(`/api/experiments/${id}`),

  cancelExperiment: (id: string): Promise<any> =>
    request<any>(`/api/experiments/${id}/cancel`, { method: 'POST' }),
};
