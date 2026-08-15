/**
 * Centralized API client for TyreIQ.
 * Initially serves mock data. Switch VITE_USE_MOCK=false to use real backend.
 */
import axios from 'axios';
import { API_BASE_URL, USE_MOCK_DATA } from '../utils/constants';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[API Error]', error.message);
    return Promise.reject(error);
  }
);

export { USE_MOCK_DATA };
export default apiClient;
