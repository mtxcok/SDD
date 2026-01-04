import axios from 'axios';
import { message } from 'ant-design-vue';
import type { Agent, Allocation, Token, AllocationCreate } from '../types';

// Axios Instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
});

// Request Interceptor for JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor for Errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        // Handle unauthorized (e.g., redirect to login)
        localStorage.removeItem('access_token');
        if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
        }
      } else {
        message.error(data.detail || data.message || 'Request failed');
      }
    } else {
      message.error('Network error');
    }
    return Promise.reject(error);
  }
);

// API Functions
export const authApi = {
  login: async (data: any) => {
    // OAuth2PasswordRequestForm expects form-urlencoded data
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    return api.post<Token>('/auth/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
  },
  register: async (data: any) => {
    return api.post('/auth/register', data);
  },
};


export const agentsApi = {
  list: async () => {
    return api.get<Agent[]>('/agents/');
  },
  delete: async (id: number) => {
    return api.delete<{ ok: boolean }>(`/agents/${id}`);
  },
};

export const allocationsApi = {
  create: async (data: AllocationCreate) => {
    return api.post<Allocation>('/allocations/create', data);
  },
  release: async (id: number) => {
    return api.post<{ ok: boolean }>(`/allocations/${id}/release`);
  },
  list: async (agentId?: number) => {
    const params = agentId ? { agent_id: agentId } : {};
    return api.get<Allocation[]>('/allocations/', { params });
  },
};

export const healthApi = {
  check: async () => {
    return api.get<{ status: string }>('/health');
  },
};

export default api;
