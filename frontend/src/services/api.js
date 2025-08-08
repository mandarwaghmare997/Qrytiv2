// API service for Qrytiv2 frontend
// Handles all API communication with the backend

import config from '../config';

class ApiService {
  constructor() {
    this.baseURL = config.API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
    this.user = null;
    
    // Restore user data from localStorage if available
    const storedUser = localStorage.getItem('user_data');
    if (storedUser) {
      try {
        this.user = JSON.parse(storedUser);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('user_data');
      }
    }
  }

  // Set authentication token and user data
  setToken(token, userData = null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
      if (userData) {
        this.user = userData;
        localStorage.setItem('user_data', JSON.stringify(userData));
      }
    } else {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      this.user = null;
    }
  }

  // Remove token and clear session
  removeToken() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }

  // Get stored user data
  getUser() {
    return this.user;
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
      // Store both token and user data
      const userData = response.user || { email, name: email.split('@')[0] };
      this.setToken(response.access_token, userData);
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

  // Get clients
  async getClients() {
    return this.request(config.ENDPOINTS.CLIENTS, { auth: false });
  }

  // Generic HTTP methods
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }

  // Get app info
  async getAppInfo() {
    return this.request(config.ENDPOINTS.INFO, { auth: false });
  }

  // Logout
  logout() {
    this.removeToken();
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

