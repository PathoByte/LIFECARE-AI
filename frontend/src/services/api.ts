import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (userData: any) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (token: string) => {
    const response = await api.get('/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  updateUser: async (userData: any, token: string) => {
    const response = await api.put('/auth/me', userData, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

// Health API
export const healthAPI = {
  createReading: async (reading: any) => {
    const response = await api.post('/health/readings', reading);
    return response.data;
  },

  getReadings: async (userId?: string, limit = 100, skip = 0) => {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    params.append('limit', limit.toString());
    params.append('skip', skip.toString());
    
    const response = await api.get(`/health/readings?${params}`);
    return response.data;
  },

  getReading: async (readingId: number) => {
    const response = await api.get(`/health/readings/${readingId}`);
    return response.data;
  },

  predict: async (data: { heart_rate: number; blood_oxygen: number; temperature?: number }) => {
    const response = await api.post('/health/predict', data);
    return response.data;
  },

  getMetrics: async (userId: string, days = 7) => {
    const response = await api.get(`/health/metrics/${userId}?days=${days}`);
    return response.data;
  },

  getDashboardData: async (userId: string) => {
    const response = await api.get(`/health/dashboard/${userId}`);
    return response.data;
  },
};

// Alerts API
export const alertsAPI = {
  getAlerts: async (userId?: string, isRead?: boolean, limit = 50, skip = 0) => {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (isRead !== undefined) params.append('is_read', isRead.toString());
    params.append('limit', limit.toString());
    params.append('skip', skip.toString());
    
    const response = await api.get(`/alerts?${params}`);
    return response.data;
  },

  markAsRead: async (alertId: number) => {
    const response = await api.put(`/alerts/${alertId}/read`);
    return response.data;
  },

  deleteAlert: async (alertId: number) => {
    const response = await api.delete(`/alerts/${alertId}`);
    return response.data;
  },
};

export default api;