import axios from 'axios';

// Base URL for API - change to your Railway URL in production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
  validateReferralCode: (code) => api.get(`/auth/validate-referral/${code}`),
};

// Users endpoints
export const usersAPI = {
  getProfile: (userId) => api.get(`/users/profile/${userId}`),
  search: (params) => api.get('/users/search', { params }),
  likeUser: (userId) => api.post(`/users/like/${userId}`),
  getMatches: () => api.get('/users/matches'),
  updateProfile: (data) => api.put('/users/profile', data),
};

// Chat endpoints
export const chatAPI = {
  getConversations: () => api.get('/chat/conversations'),
  getMessages: (chatId, page = 1) => api.get(`/chat/messages/${chatId}`, { params: { page } }),
  sendMessage: (recipientId, content) => api.post('/chat/send', { recipient_id: recipientId, content }),
  startChat: (userId) => api.post(`/chat/start/${userId}`),
  getUnreadCount: () => api.get('/chat/unread-count'),
};

// Referrals endpoints
export const referralsAPI = {
  getMyReferrals: () => api.get('/referrals/my-referrals'),
  getTree: () => api.get('/referrals/tree'),
  getMyReferrer: () => api.get('/referrals/my-referrer'),
  getChain: (userId) => api.get(`/referrals/chain/${userId}`),
  getStats: () => api.get('/referrals/stats'),
};

export default api;

