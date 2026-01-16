import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management - support both JWT (OAuth) and API Token
const REFRESH_TOKEN_KEY = 'refresh_token';
const AUTH_EXPIRES_AT_KEY = 'auth_expires_at';

let authToken: string | null = localStorage.getItem('auth_token') || localStorage.getItem('api_token');
let refreshToken: string | null = localStorage.getItem(REFRESH_TOKEN_KEY);
let accessTokenExpiresAt: string | null = localStorage.getItem(AUTH_EXPIRES_AT_KEY);

export const setAuthSession = (token: string, newRefreshToken: string, expiresAt: string) => {
  authToken = token;
  refreshToken = newRefreshToken;
  accessTokenExpiresAt = expiresAt;
  localStorage.setItem('auth_token', token);
  localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
  localStorage.setItem(AUTH_EXPIRES_AT_KEY, expiresAt);
};

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('api_token');
  }
  refreshToken = null;
  accessTokenExpiresAt = null;
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(AUTH_EXPIRES_AT_KEY);
};

export const getAuthToken = () => authToken;
export const getRefreshToken = () => refreshToken;
export const getAccessTokenExpiry = () => accessTokenExpiresAt;

// Check if user is authenticated
export const isAuthenticated = () => !!authToken;

// Request interceptor to add auth header
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

// Flag to prevent multiple refresh attempts
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response interceptor for auth errors with auto-refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retrying, and not the refresh endpoint itself
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/api/auth/refresh')
    ) {
      // Check if we have a refresh token
      if (refreshToken) {
        if (isRefreshing) {
          // Queue the request while refreshing
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return api(originalRequest);
            })
            .catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          // Try to refresh the token
          const response = await api.post<AuthSessionResponse>('/api/auth/refresh', {
            refresh_token: refreshToken,
          });

          const newToken = response.data.access_token;
          setAuthSession(
            response.data.access_token,
            response.data.refresh_token,
            response.data.access_token_expires_at
          );

          processQueue(null, newToken);

          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          // Refresh failed, clear tokens
          setAuthToken(null);
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      } else {
        // No refresh token, clear auth
        setAuthToken(null);
      }
    }
    return Promise.reject(error);
  }
);

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

// User types (Phase 5)
export type UserInfo = {
  id: string;
  email: string;
  name: string;
  picture: string | null;
};

export type AuthStatus = {
  success: boolean;
  authenticated: boolean;
  auth_type: 'jwt' | 'api_token' | null;
  user_id: string | null;
};

export type MeResponse = {
  success: boolean;
  user: UserInfo;
  auth_type: 'oauth' | 'api_token';
};

export type AuthSessionResponse = {
  success: boolean;
  access_token: string;
  refresh_token: string;
  access_token_expires_at: string;
  token_type: string;
  auth_type: string;
};

export type ExchangeCodeResponse = AuthSessionResponse;

export type ExchangeGoogleCodeResponse = {
  success: boolean;
  code: string;
  new_user: boolean;
};

// Sheet types (Phase 5)
export type SheetInfo = {
  sheet_id: string;
  sheet_url: string;
  sheet_name: string;
};

export type DriveSheetItem = {
  id: string;
  name: string;
  modified_time: string;
  url: string;
};

export type SheetResponse = {
  success: boolean;
  sheet: SheetInfo | null;
  message: string;
};

export type DriveSheetListResponse = {
  success: boolean;
  sheets: DriveSheetItem[];
  message: string;
};

// API Token types (Phase 5)
export type APITokenInfo = {
  id: number;
  description: string;
  created_at: string;
  expires_at: string | null;
  last_used_at: string | null;
  is_active: boolean;
};

export type APITokenListResponse = {
  success: boolean;
  tokens: APITokenInfo[];
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
export type TTSVoice = 'alloy' | 'ash' | 'ballad' | 'coral' | 'echo' | 'fable' | 'onyx' | 'nova' | 'sage' | 'shimmer' | 'verse';

export type TTSRequest = {
  text: string;
  voice?: string;
  speed?: number;
};

export type VoiceInfo = {
  id: string;
  name: string;
  description: string;
};

// TTS API functions
export const synthesizeSpeech = async (
  text: string,
  voice: string = 'nova',
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
  by_category_count: Record<string, number>;
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
    count: data.by_category_count?.[category] ?? 0,
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

// ========================================
// Query History API
// ========================================

export type QueryHistoryItem = {
  id: number;
  query: string;
  answer: string;
  created_at: string;
};

export type QueryHistoryResponse = {
  success: boolean;
  items: QueryHistoryItem[];
  next_cursor: string | null;
  total: number;
};

export type GetQueryHistoryParams = {
  limit?: number;
  cursor?: string;
  search?: string;
};

export const getQueryHistory = async (params: GetQueryHistoryParams = {}): Promise<QueryHistoryResponse> => {
  const searchParams = new URLSearchParams();
  if (params.limit) searchParams.append('limit', params.limit.toString());
  if (params.cursor) searchParams.append('cursor', params.cursor);
  if (params.search) searchParams.append('search', params.search);

  const queryString = searchParams.toString();
  const url = `/api/accounting/query/history${queryString ? `?${queryString}` : ''}`;
  
  const response = await api.get<QueryHistoryResponse>(url);
  return response.data;
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
  token: string;
  description: string;
  created_at: string;
  expires_at: string | null;
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

// ========================================
// OAuth / Auth API (Phase 5)
// ========================================

// Get Google OAuth login URL
// 生成 state 並儲存到 sessionStorage，用於 CSRF 防護
export const getGoogleLoginUrl = (): string => {
  // 生成隨機 state
  const state = crypto.randomUUID();
  // 儲存到 sessionStorage，供 callback 時驗證
  sessionStorage.setItem('oauth_state', state);
  
  return `${API_BASE_URL}/api/auth/google/login?state=${encodeURIComponent(state)}`;
};

// Get current user info
export const getCurrentUser = async (): Promise<MeResponse> => {
  const response = await api.get<MeResponse>('/api/auth/me');
  return response.data;
};

// Get auth status
export const getAuthStatus = async (): Promise<AuthStatus> => {
  const response = await api.get<AuthStatus>('/api/auth/status');
  return response.data;
};

// Logout
export const logout = async (): Promise<{ success: boolean; message: string }> => {
  const response = await api.post<{ success: boolean; message: string }>('/api/auth/logout');
  // Clear local token
  setAuthToken(null);
  return response.data;
};

export const refreshSession = async (overrideToken?: string): Promise<AuthSessionResponse> => {
  const token = overrideToken || refreshToken;
  if (!token) {
    throw new Error('Missing refresh token');
  }
  const response = await api.post<AuthSessionResponse>('/api/auth/refresh', {
    refresh_token: token,
  });
  setAuthSession(
    response.data.access_token,
    response.data.refresh_token,
    response.data.access_token_expires_at
  );
  return response.data;
};

export const exchangeAuthCode = async (code: string): Promise<ExchangeCodeResponse> => {
  const response = await api.post<ExchangeCodeResponse>('/api/auth/exchange', {
    code,
  });
  setAuthSession(
    response.data.access_token,
    response.data.refresh_token,
    response.data.access_token_expires_at
  );
  return response.data;
};

// Exchange Google authorization code for one-time code
// state 驗證已移至前端 sessionStorage，後端不再驗證
export const exchangeGoogleCode = async (code: string): Promise<ExchangeGoogleCodeResponse> => {
  const response = await api.post<ExchangeGoogleCodeResponse>('/api/auth/google/exchange-code', {
    code,
  });
  return response.data;
};

// ========================================
// API Token Management (Phase 5)
// ========================================

// List user's API tokens
export const listAPITokens = async (): Promise<APITokenListResponse> => {
  const response = await api.get<APITokenListResponse>('/api/auth/token/list');
  return response.data;
};

// Delete/revoke an API token
export const revokeAPIToken = async (tokenId: number): Promise<{ success: boolean; message: string }> => {
  const response = await api.delete<{ success: boolean; message: string }>(`/api/auth/token/${tokenId}`);
  return response.data;
};

// ========================================
// Sheet Management API (Phase 5)
// ========================================

// Get user's sheet info
export const getMySheet = async (): Promise<SheetResponse> => {
  const response = await api.get<SheetResponse>('/api/sheets/my-sheet');
  return response.data;
};

// Create a new sheet
export const createSheet = async (title?: string): Promise<SheetResponse> => {
  const response = await api.post<SheetResponse>('/api/sheets/create', {
    title: title || '語音記帳',
  });
  return response.data;
};

// Create a new sheet and replace existing binding
export const createNewSheet = async (title?: string): Promise<SheetResponse> => {
  const response = await api.post<SheetResponse>('/api/sheets/create-new', {
    title: title || '語音記帳',
  });
  return response.data;
};

// Link an existing sheet
export const linkSheet = async (sheetUrl: string): Promise<SheetResponse> => {
  const response = await api.post<SheetResponse>(`/api/sheets/link?sheet_url=${encodeURIComponent(sheetUrl)}`);
  return response.data;
};

// List all sheets from Google Drive
export const listDriveSheets = async (): Promise<DriveSheetListResponse> => {
  const response = await api.get<DriveSheetListResponse>('/api/sheets/list');
  return response.data;
};

// Select a sheet from the list
export const selectSheet = async (sheetId: string, sheetName?: string): Promise<SheetResponse> => {
  console.log('selectSheet API called with:', { sheetId, sheetName });
  const response = await api.post<SheetResponse>('/api/sheets/select', {
    sheet_id: sheetId,
    sheet_name: sheetName,
  });
  console.log('selectSheet API response:', response.data);
  return response.data;
};

// ========================================
// Dashboard API (enhance-homepage-dashboard)
// ========================================

export type CategorySummary = {
  category: string;
  total: number;
  percentage: number;
};

export type MonthSummary = {
  total: number;
  record_count: number;
  top_categories: CategorySummary[];
};

export type RecentRecord = {
  時間: string;
  名稱: string;
  類別: string;
  花費: number;
};

export type DailyTrend = {
  date: string;
  total: number;
};

export type BudgetStatus = {
  monthly_limit: number | null;
  spent: number;
  remaining: number | null;
  percentage: number | null;
};

export type DashboardSummary = {
  month_summary: MonthSummary;
  recent_records: RecentRecord[];
  daily_trend: DailyTrend[];
  budget: BudgetStatus;
};

export type DashboardSummaryResponse = {
  success: boolean;
  data: DashboardSummary;
};

export type BudgetResponse = {
  success: boolean;
  monthly_budget: number | null;
  message: string;
};

// Get dashboard summary (month stats, recent records, daily trend, budget)
export const getDashboardSummary = async (): Promise<DashboardSummaryResponse> => {
  const response = await api.get<DashboardSummaryResponse>('/api/accounting/summary');
  return response.data;
};

// Get user budget setting
export const getUserBudget = async (): Promise<BudgetResponse> => {
  const response = await api.get<BudgetResponse>('/api/auth/settings/budget');
  return response.data;
};

// Set user budget (pass null to clear budget)
export const setUserBudget = async (monthlyBudget: number | null): Promise<BudgetResponse> => {
  const response = await api.put<BudgetResponse>('/api/auth/settings/budget', {
    monthly_budget: monthlyBudget,
  });
  return response.data;
};

// Quick entry presets for fast accounting
export type QuickEntryPreset = {
  name: string;
  category: string;
  defaultAmount: number;
  icon: string;
};

export const QUICK_ENTRY_PRESETS: QuickEntryPreset[] = [
  { name: '早餐', category: '飲食', defaultAmount: 50, icon: '🌅' },
  { name: '午餐', category: '飲食', defaultAmount: 100, icon: '🍱' },
  { name: '晚餐', category: '飲食', defaultAmount: 150, icon: '🍽️' },
  { name: '交通', category: '交通', defaultAmount: 30, icon: '🚌' },
  { name: '咖啡', category: '飲食', defaultAmount: 80, icon: '☕' },
];

export default api;
