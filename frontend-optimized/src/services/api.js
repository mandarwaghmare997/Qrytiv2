/**
 * Optimized API Service for Qrytiv2 Serverless Backend
 * Handles all HTTP requests to AWS Lambda functions via API Gateway
 */

import config, { buildApiUrl, getStorageKey } from '../config.js';

class ApiService {
  constructor() {
    this.baseURL = config.api.baseURL;
    this.timeout = config.api.timeout;
    this.retries = config.api.retries;
    this.cache = new Map();
    this.requestQueue = new Map();
  }

  // Get authentication token
  getAuthToken() {
    return localStorage.getItem(getStorageKey('authToken'));
  }

  // Set authentication token
  setAuthToken(token) {
    if (token) {
      localStorage.setItem(getStorageKey('authToken'), token);
    } else {
      localStorage.removeItem(getStorageKey('authToken'));
    }
  }

  // Get default headers
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    if (includeAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  // Cache management
  getCacheKey(url, options = {}) {
    return `${url}_${JSON.stringify(options)}`;
  }

  getFromCache(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < config.performance.cache.duration) {
      return cached.data;
    }
    this.cache.delete(key);
    return null;
  }

  setCache(key, data) {
    if (this.cache.size >= config.performance.cache.maxSize) {
      // Remove oldest entry
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  // Request deduplication
  async deduplicateRequest(key, requestFn) {
    if (this.requestQueue.has(key)) {
      return this.requestQueue.get(key);
    }

    const promise = requestFn();
    this.requestQueue.set(key, promise);

    try {
      const result = await promise;
      this.requestQueue.delete(key);
      return result;
    } catch (error) {
      this.requestQueue.delete(key);
      throw error;
    }
  }

  // Core HTTP methods with retry logic
  async request(url, options = {}) {
    const fullUrl = url.startsWith('http') ? url : buildApiUrl(url);
    const requestOptions = {
      method: 'GET',
      headers: this.getHeaders(options.includeAuth !== false),
      ...options
    };

    // Add timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    requestOptions.signal = controller.signal;

    let lastError;
    
    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const response = await fetch(fullUrl, requestOptions);
        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new ApiError(
            errorData.error || `HTTP ${response.status}`,
            response.status,
            errorData
          );
        }

        const data = await response.json();
        return data;

      } catch (error) {
        lastError = error;
        
        // Don't retry on authentication errors or client errors
        if (error.status >= 400 && error.status < 500) {
          break;
        }

        // Don't retry on last attempt
        if (attempt === this.retries) {
          break;
        }

        // Wait before retry
        await new Promise(resolve => 
          setTimeout(resolve, config.errors.retryDelay * (attempt + 1))
        );
      }
    }

    clearTimeout(timeoutId);
    throw lastError;
  }

  // GET request with caching
  async get(url, options = {}) {
    const cacheKey = this.getCacheKey(url, options);
    
    // Check cache first
    if (config.performance.cache.enabled && !options.skipCache) {
      const cached = this.getFromCache(cacheKey);
      if (cached) {
        return cached;
      }
    }

    // Deduplicate identical requests
    return this.deduplicateRequest(cacheKey, async () => {
      const data = await this.request(url, { ...options, method: 'GET' });
      
      // Cache successful responses
      if (config.performance.cache.enabled && !options.skipCache) {
        this.setCache(cacheKey, data);
      }
      
      return data;
    });
  }

  // POST request
  async post(url, body = null, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : null
    });
  }

  // PUT request
  async put(url, body = null, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : null
    });
  }

  // DELETE request
  async delete(url, options = {}) {
    return this.request(url, {
      ...options,
      method: 'DELETE'
    });
  }

  // Authentication methods
  async login(email, password) {
    const response = await this.post(config.api.endpoints.login, {
      email,
      password
    }, { includeAuth: false });

    if (response.success && response.data.token) {
      this.setAuthToken(response.data.token);
      
      // Cache user profile
      if (response.data.user) {
        localStorage.setItem(
          getStorageKey('userProfile'), 
          JSON.stringify(response.data.user)
        );
      }
    }

    return response;
  }

  async register(userData) {
    const response = await this.post(config.api.endpoints.register, userData, {
      includeAuth: false
    });

    if (response.success && response.data.token) {
      this.setAuthToken(response.data.token);
      
      // Cache user profile
      if (response.data.user) {
        localStorage.setItem(
          getStorageKey('userProfile'), 
          JSON.stringify(response.data.user)
        );
      }
    }

    return response;
  }

  async verifyToken() {
    try {
      const response = await this.get(config.api.endpoints.verify);
      return response.success;
    } catch (error) {
      if (error.status === 401) {
        this.logout();
      }
      return false;
    }
  }

  logout() {
    this.setAuthToken(null);
    localStorage.removeItem(getStorageKey('userProfile'));
    this.cache.clear();
  }

  // User methods
  async getUserProfile() {
    return this.get(config.api.endpoints.profile);
  }

  async updateUserProfile(profileData) {
    const response = await this.put(config.api.endpoints.profile, profileData);
    
    // Update cached profile
    if (response.success && response.data) {
      localStorage.setItem(
        getStorageKey('userProfile'), 
        JSON.stringify(response.data)
      );
    }
    
    return response;
  }

  // Client methods
  async getClients() {
    return this.get(config.api.endpoints.clients);
  }

  async createClient(clientData) {
    const response = await this.post(config.api.endpoints.clients, clientData);
    
    // Invalidate clients cache
    this.cache.forEach((value, key) => {
      if (key.includes(config.api.endpoints.clients)) {
        this.cache.delete(key);
      }
    });
    
    return response;
  }

  // AI Model methods
  async getModels(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString();
    const url = queryParams 
      ? `${config.api.endpoints.models}?${queryParams}`
      : config.api.endpoints.models;
    
    return this.get(url);
  }

  async registerModel(modelData) {
    const response = await this.post(config.api.endpoints.models, modelData);
    
    // Invalidate models cache
    this.cache.forEach((value, key) => {
      if (key.includes(config.api.endpoints.models)) {
        this.cache.delete(key);
      }
    });
    
    return response;
  }

  async updateModel(modelId, modelData) {
    const response = await this.put(`${config.api.endpoints.models}/${modelId}`, modelData);
    
    // Invalidate models cache
    this.cache.forEach((value, key) => {
      if (key.includes(config.api.endpoints.models)) {
        this.cache.delete(key);
      }
    });
    
    return response;
  }

  // Report methods
  async getReports() {
    return this.get(config.api.endpoints.reports);
  }

  async generateReport(reportData) {
    return this.post(config.api.endpoints.generateReport, reportData);
  }

  async downloadReport(reportId) {
    return this.get(`${config.api.endpoints.reports}/${reportId}/download`);
  }

  // Health check
  async healthCheck() {
    try {
      const response = await this.get('/health', { includeAuth: false });
      return response.success || true;
    } catch (error) {
      return false;
    }
  }

  // Clear all caches
  clearCache() {
    this.cache.clear();
  }

  // Get cache statistics
  getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: config.performance.cache.maxSize,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Custom error class
class ApiError extends Error {
  constructor(message, status, data = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Create and export singleton instance
const apiService = new ApiService();

export default apiService;
export { ApiError };

// Named exports for convenience
export const {
  login,
  register,
  logout,
  verifyToken,
  getUserProfile,
  updateUserProfile,
  getClients,
  createClient,
  getModels,
  registerModel,
  updateModel,
  getReports,
  generateReport,
  downloadReport,
  healthCheck
} = apiService;

