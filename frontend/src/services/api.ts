import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
let authToken: string | null = localStorage.getItem('api_token');

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem('api_token', token);
  } else {
    localStorage.removeItem('api_token');
  }
};

export const getAuthToken = () => authToken;

// Request interceptor to add auth header
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

// Types
export type AccountingRequest = {
  text: string;
};

export type AccountingRecord = {
  時間: string;
  名稱: string;
  類別: string;
  花費: number;
  幣別: string;
  支付方式: string | null;
};

export type AccountingResponse = {
  success: boolean;
  message: string;
  record: AccountingRecord;
  feedback: string | null;
};

export type HealthResponse = {
  status: string;
  message: string;
  version: string;
};

export type TokenResponse = {
  token: string;
  description: string;
  created_at: string;
  expires_at: string | null;
};

// API functions
export const healthCheck = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/api/health');
  return response.data;
};

export const createEntry = async (text: string): Promise<AccountingResponse> => {
  const response = await api.post<AccountingResponse>('/api/accounting/record', {
    text,
  } as AccountingRequest);
  return response.data;
};

export const generateToken = async (description?: string): Promise<TokenResponse> => {
  const response = await api.post<TokenResponse>('/api/token/generate', {
    description: description || 'Frontend generated token',
  });
  return response.data;
};

export const validateToken = async (token: string): Promise<{ valid: boolean; description: string }> => {
  const response = await api.post<{ valid: boolean; description: string }>(
    '/api/token/validate',
    {},
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
};

// TTS Types
export type TTSVoice = 'alloy' | 'echo' | 'fable' | 'onyx' | 'nova' | 'shimmer';

export type TTSRequest = {
  text: string;
  voice?: TTSVoice;
  speed?: number;
};

export type VoiceInfo = {
  id: TTSVoice;
  name: string;
  description: string;
};

// TTS API functions
export const synthesizeSpeech = async (
  text: string,
  voice: TTSVoice = 'nova',
  speed: number = 1.0
): Promise<Blob> => {
  const response = await api.post<Blob>(
    '/api/speech/synthesize',
    { text, voice, speed } as TTSRequest,
    { responseType: 'blob' }
  );
  return response.data;
};

export const getAvailableVoices = async (): Promise<VoiceInfo[]> => {
  const response = await api.get<{ success: boolean; voices: VoiceInfo[] }>('/api/speech/voices');
  return response.data.voices;
};

// Stats Types (matches backend schema)
export type MonthlyStats = {
  month: string; // "2024-01" format
  total: number;
  record_count: number;
  by_category: Record<string, number>;
};

export type StatsResponse = {
  success: boolean;
  data: MonthlyStats;
};

// Transformed stats for frontend display
export type CategoryStat = {
  category: string;
  total: number;
  count: number;
  percentage: number;
};

export type TransformedStats = {
  month: string;
  total: number;
  record_count: number;
  categories: CategoryStat[];
  daily_average: number;
};

// Query Types
export type QueryRequest = {
  query: string;
};

export type QueryResponse = {
  success: boolean;
  response: string;
};

// Stats API functions
export const getMonthlyStats = async (year?: number, month?: number): Promise<{ success: boolean; stats: TransformedStats }> => {
  // Build month string in YYYY-MM format
  let monthParam: string | undefined;
  if (year && month) {
    monthParam = `${year}-${month.toString().padStart(2, '0')}`;
  }

  const params = new URLSearchParams();
  if (monthParam) params.append('month', monthParam);

  const response = await api.get<StatsResponse>(`/api/accounting/stats?${params.toString()}`);

  // Transform backend response to frontend format
  const data = response.data.data;
  const categories: CategoryStat[] = Object.entries(data.by_category).map(([category, total]) => ({
    category,
    total: total as number,
    count: 0, // Backend doesn't provide count per category
    percentage: data.total > 0 ? ((total as number) / data.total) * 100 : 0,
  }));

  // Calculate daily average (assuming 30 days per month)
  const daily_average = data.total / 30;

  return {
    success: response.data.success,
    stats: {
      month: data.month,
      total: data.total,
      record_count: data.record_count,
      categories,
      daily_average,
    },
  };
};

// Query API functions
export const queryAccounting = async (query: string): Promise<{ success: boolean; answer: string }> => {
  const response = await api.post<QueryResponse>('/api/accounting/query', {
    query,
  } as QueryRequest);
  return {
    success: response.data.success,
    answer: response.data.response,
  };
};

// Token management API
export type TokenInfo = {
  token: string;
  description: string;
  created_at: string;
  expires_at: string | null;
};

export type GenerateTokenResponse = {
  success: boolean;
  token: TokenInfo;
  message: string;
};

export const generateNewToken = async (description?: string): Promise<GenerateTokenResponse> => {
  const response = await api.post<GenerateTokenResponse>('/api/auth/token/generate', {
    description: description || 'Web App Token',
  });
  return response.data;
};

export const verifyToken = async (): Promise<{ success: boolean; message: string }> => {
  const response = await api.get<{ success: boolean; message: string }>('/api/auth/token/verify');
  return response.data;
};

export default api;
