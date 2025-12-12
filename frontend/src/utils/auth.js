import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
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

// Auth API functions
export const authAPI = {
  // Register new user
  register: async (email, password, fullName, referralCode) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName || undefined,
      referral_code: referralCode || undefined,
    });
    return response.data;
  },

  // Login user
  login: async (email, password) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Token management
export const tokenManager = {
  setToken: (token) => {
    localStorage.setItem('access_token', token);
  },
  getToken: () => {
    return localStorage.getItem('access_token');
  },
  removeToken: () => {
    localStorage.removeItem('access_token');
  },
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
};

export default api;

