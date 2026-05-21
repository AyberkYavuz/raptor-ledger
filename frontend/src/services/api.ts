// frontend/src/services/api.ts
import axios from 'axios';

// --- VITE NATIVE ENVIRONMENT CONFIGURATION ---
// Instead of process.env, we use import.meta.env matching modern bundling specs
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically inject your JWT token into outbound request streams if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('raptor_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
