import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '/api';
const normalizedBaseURL = API_URL.endsWith('/') ? API_URL : `${API_URL}/`;

const api = axios.create({
  baseURL: normalizedBaseURL,
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

// Helper to ensure paths are relative to the API base URL
const toPath = (path) => (path.startsWith('/') ? path.substring(1) : path);

// Auth
export const login = (email, password) => 
  api.post(toPath('auth/login'), { email, password });

export const register = (data) => 
  api.post(toPath('auth/register'), data);

export const getCurrentUser = () => 
  api.get(toPath('auth/me'));

// Videos
export const getVideos = (params) => 
  api.get(toPath('videos'), { params });

export const getVideo = (id) => 
  api.get(toPath(`videos/${id}`));

export const createVideo = (data) => 
  api.post(toPath('videos'), data);

// Annotations
export const getAnnotations = (videoId) => 
  api.get(toPath('annotations'), { params: { video_id: videoId } });

export const createAnnotation = (data) => 
  api.post(toPath('annotations'), data);

// Best Practices
export const getBestPractices = (category) => 
  api.get(toPath('practices'), { params: { category } });

// Reports
export const getVideoReport = (videoId) => 
  api.get(toPath(`reports/video/${videoId}`));

// AI Analysis
export const analyzeVideo = (videoId) =>
  api.post(toPath(`ai/analyze/${videoId}`), {});

export const getAnalysisStatus = (videoId) =>
  api.get(toPath(`ai/status/${videoId}`));

export default api;

