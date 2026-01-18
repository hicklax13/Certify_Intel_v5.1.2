/**
 * API Client for Certify Intel Mobile
 */
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configure base URL - change for production
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle response errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized - redirect to login
            AsyncStorage.removeItem('auth_token');
        }
        return Promise.reject(error);
    }
);

// ============== API Functions ==============

// Dashboard
export const getDashboardStats = () => api.get('/api/dashboard/stats');

// Competitors
export const getCompetitors = () => api.get('/api/competitors');
export const getCompetitor = (id) => api.get(`/api/competitors/${id}`);
export const updateCompetitor = (id, data) => api.put(`/api/competitors/${id}`, data);
export const createCompetitor = (data) => api.post('/api/competitors', data);

// Changes
export const getChanges = (days = 7, severity = null) => {
    let url = `/api/changes?days=${days}`;
    if (severity) url += `&severity=${severity}`;
    return api.get(url);
};

// Analytics
export const getCompetitorAnalysis = (id) => api.get(`/api/analytics/competitor/${id}`);
export const getHeatmap = () => api.get('/api/analytics/heatmap');

// External Data
export const getExternalData = (compName) => api.get(`/api/external/${compName}`);
export const getTrafficData = (domain) => api.get(`/api/traffic/${domain}`);
export const getSocialMentions = (compName) => api.get(`/api/social/${compName}`);

// Win/Loss
export const getWinLossRecords = () => api.get('/api/winloss');
export const addWinLossRecord = (data) => api.post('/api/winloss', data);
export const getWinLossStats = () => api.get('/api/winloss/stats');

// Scraping
export const triggerScrape = (id) => api.post(`/api/scrape/${id}`);
export const triggerScrapeAll = () => api.post('/api/scrape/all');

// Alerts
export const sendDailyDigest = () => api.post('/api/alerts/send-digest');
export const sendWeeklySummary = () => api.post('/api/alerts/send-summary');

// Auth
export const login = (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/token', formData.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
};

export const getCurrentUser = () => api.get('/api/auth/me');

// Export
export const exportExcel = () => `${API_BASE_URL}/api/export/excel`;
export const exportJSON = () => `${API_BASE_URL}/api/export/json`;

export default api;
