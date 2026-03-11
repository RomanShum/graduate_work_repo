// src/api/client.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

console.log('🌐 API Client initialized with URL:', API_BASE_URL);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Логирование запросов и добавление JWT-токена
apiClient.interceptors.request.use(request => {
  const token = localStorage.getItem('access_token');
  if (token) {
    request.headers = request.headers || {};
    request.headers.Authorization = `Bearer ${token}`;
  }

  console.log('🚀 Request:', {
    method: request.method?.toUpperCase(),
    url: request.url,
    params: request.params
  });
  return request;
});

// Логирование ответов
apiClient.interceptors.response.use(
  response => {
    console.log('✅ Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  error => {
    console.error('❌ API Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    });

    if (error.response?.status === 401) {
      // Токен недействителен — очищаем и возвращаем на форму авторизации
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.reload();
    }

    return Promise.reject(error);
  }
);

export default apiClient;