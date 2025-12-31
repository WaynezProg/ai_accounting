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

export default api;
