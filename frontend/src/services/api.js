// API service for Qrytiv2 frontend
// Handles all API communication with the backend

import config from '../config.js';

class ApiService {
  constructor() {
    this.baseURL = config.API_BASE_URL;
    this.token = localStorage.getItem('auth_token');
    this.user = JSON.parse(localStorage.getItem('user_data') || 'null');
  }

  // Set authentication token and user data
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      this.user = null;
    }
  }

  // Set user data
  setUser(userData) {
    this.user = userData;
    if (userData) {
      localStorage.setItem('user_data', JSON.stringify(userData));
    } else {
      localStorage.removeItem('user_data');
    }
  }

  // Get user data
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
      
      // Handle session expiry
      if (response.status === 401) {
        this.logout();
        window.location.reload();
        return;
      }
      
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
    return this.request('/health', { auth: false });
  }

  // User authentication
  async login(email, password) {
    const response = await this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      auth: false
    });

    if (response.access_token) {
      this.setToken(response.access_token);
      this.setUser(response.user);
    }

    return response;
  }

  // OTP verification
  async verifyOTP(email, otpCode, deviceFingerprint, rememberDevice = false) {
    const response = await this.request('/api/v1/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ 
        email, 
        otp_code: otpCode, 
        device_fingerprint: deviceFingerprint,
        remember_device: rememberDevice 
      }),
      auth: false
    });

    if (response.access_token) {
      this.setToken(response.access_token);
      this.setUser(response.user);
    }

    return response;
  }

  // Refresh session
  async refreshSession() {
    try {
      return await this.request('/api/v1/auth/refresh', {
        method: 'POST'
      });
    } catch (error) {
      this.logout();
      throw error;
    }
  }

  // Get session info
  async getSessionInfo() {
    return this.request('/api/v1/auth/session-info');
  }

  // Admin endpoints
  async getAdminStats() {
    return this.request('/api/v1/admin/stats');
  }

  async getClients() {
    return this.request('/api/v1/admin/clients');
  }

  async createClient(clientData) {
    return this.request('/api/v1/admin/clients', {
      method: 'POST',
      body: JSON.stringify(clientData)
    });
  }

  async getProjects() {
    return this.request('/api/v1/admin/projects');
  }

  async createProject(projectData) {
    return this.request('/api/v1/admin/projects', {
      method: 'POST',
      body: JSON.stringify(projectData)
    });
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
  async logout() {
    try {
      await this.request('/api/v1/auth/logout', {
        method: 'POST'
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.setToken(null);
      this.setUser(null);
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token && !!this.user;
  }

  // Get stored token
  getToken() {
    return this.token;
  }

  // Auto-refresh session periodically
  startSessionRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }

    this.refreshInterval = setInterval(async () => {
      if (this.isAuthenticated()) {
        try {
          await this.refreshSession();
        } catch (error) {
          console.error('Session refresh failed:', error);
        }
      }
    }, 5 * 60 * 1000); // Refresh every 5 minutes
  }

  // Stop session refresh
  stopSessionRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;

