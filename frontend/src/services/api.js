import axios from 'axios';

// Get API base URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    
    // Add auth token to requests
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
      
      // Handle 401 Unauthorized
      if (error.response.status === 401) {
        // Clear token and redirect to login
        localStorage.removeItem('auth_token');
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  // Register new user
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },

  // Sign in user
  signin: async (credentials) => {
    const response = await api.post('/auth/signin', credentials);
    
    // Store the token in localStorage
    if (response.data.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    
    return response.data;
  },

  // Sign out user
  signout: async () => {
    // Clear token from localStorage
    localStorage.removeItem('auth_token');
    
    const response = await api.post('/auth/signout');
    return response.data;
  },

  // Check session status
  checkSession: async () => {
    const response = await api.get('/auth/session');
    return response.data;
  },

  // Request password reset
  requestPasswordReset: async (email) => {
    const response = await api.post('/auth/password-reset-request', { email });
    return response.data;
  },

  // Reset password with token
  resetPassword: async (token, password) => {
    const response = await api.post('/auth/password-reset', { token, password });
    return response.data;
  },
};

// Feedback API
export const feedbackAPI = {
  // Submit feedback
  submit: async (feedbackData) => {
    const response = await api.post('/feedback', feedbackData);
    return response.data;
  },

  // Get user's feedback submissions
  getMySubmissions: async () => {
    const response = await api.get('/feedback/my-submissions');
    return response.data;
  },

  // Get specific feedback by ID
  getById: async (id) => {
    const response = await api.get(`/feedback/${id}`);
    return response.data;
  },
};

// Admin API
export const adminAPI = {
  // Get all users
  getUsers: async (params = {}) => {
    const response = await api.get('/admin/users', { params });
    return response.data;
  },

  // Get all feedback with optional filters
  getFeedback: async (filters = {}) => {
    const response = await api.get('/admin/feedback', { params: filters });
    return response.data;
  },

  // Get platform metrics
  getMetrics: async (tenant = null) => {
    const params = tenant ? { tenant } : {};
    const response = await api.get('/admin/metrics', { params });
    return response.data;
  },

  // Get sentiment distribution
  getSentimentDistribution: async (tenant = null) => {
    const params = tenant ? { tenant } : {};
    const response = await api.get('/admin/sentiment-distribution', { params });
    return response.data;
  },

  // Get rating breakdown
  getRatingBreakdown: async (tenant = null) => {
    const params = tenant ? { tenant } : {};
    const response = await api.get('/admin/rating-breakdown', { params });
    return response.data;
  },

  // Get feedback trends
  getTrends: async (filters = {}) => {
    const response = await api.get('/admin/trends', { params: filters });
    return response.data;
  },

  // Get tenant comparison
  getTenantComparison: async () => {
    const response = await api.get('/admin/tenant-comparison');
    return response.data;
  },

  // Get engagement metrics
  getEngagement: async (tenant = null) => {
    const params = tenant ? { tenant } : {};
    const response = await api.get('/admin/engagement', { params });
    return response.data;
  },

  // Get recent activity
  getRecentActivity: async (limit = 10, tenant = null) => {
    const params = { limit };
    if (tenant) params.tenant = tenant;
    const response = await api.get('/admin/recent-activity', { params });
    return response.data;
  },

  // Export data
  exportData: async (filters = {}) => {
    const response = await api.post('/admin/export', { 
      format: 'csv',
      filters 
    });
    return response.data;
  },
};

export default api;
