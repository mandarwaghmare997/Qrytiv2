// API service for Qrytiv2 frontend
// Handles all API communication with the backend

import config from '../config.js';

class ApiService {
  constructor() {
    this.baseURL = config.API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  // Get authentication headers
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Generic API request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const defaultOptions = {
      headers: this.getHeaders(options.auth !== false),
    };

    const requestOptions = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request(config.ENDPOINTS.HEALTH, { auth: false });
  }

  // User authentication
  async login(email, password) {
    const response = await this.request(config.ENDPOINTS.LOGIN, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      auth: false
    });

    if (response.access_token) {
      this.setToken(response.access_token);
    }

    return response;
  }

  // User registration
  async register(userData) {
    return this.request(config.ENDPOINTS.REGISTER, {
      method: 'POST',
      body: JSON.stringify(userData),
      auth: false
    });
  }

  // Get current user info
  async getCurrentUser() {
    return this.request('/api/v1/auth/me');
  }

  // List users (admin only)
  async getUsers() {
    return this.request(config.ENDPOINTS.USERS);
  }

  // Get app info
  async getAppInfo() {
    return this.request(config.ENDPOINTS.INFO, { auth: false });
  }

  // Logout
  logout() {
    this.setToken(null);
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token;
  }

  // Get stored token
  getToken() {
    return this.token;
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;

