import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — attach JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/login', data),
  me: () => api.get('/me'),
  updateWhatsApp: (data) => api.put('/me/whatsapp', data),
};

export const productsAPI = {
  list: () => api.get('/products'),
  create: (formData) => api.post('/products', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};

export const autoRepliesAPI = {
  list: () => api.get('/autoreplies'),
  create: (data) => api.post('/autoreplies', data),
  update: (id, data) => api.put(`/autoreplies/${id}`, data),
  delete: (id) => api.delete(`/autoreplies/${id}`),
};

export const ordersAPI = {
  list: (status) => api.get('/orders', { params: { status_filter: status } }),
  create: (data) => api.post('/orders', data),
  updateStatus: (id, status) => api.put(`/orders/${id}/status`, { status }),
};

export const dashboardAPI = {
  summary: () => api.get('/dashboard'),
  revenue: (days) => api.get('/analytics/revenue', { params: { days } }),
};

export default api;
