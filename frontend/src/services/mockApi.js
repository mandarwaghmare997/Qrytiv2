// Mock API service for frontend-only deployment
// Eliminates dependency on external backend services

class MockApiService {
  constructor() {
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

    // Demo users
    this.demoUsers = {
      "hello@qryti.com": {
        password: "Mandar@123",
        role: "admin",
        name: "Qryti Admin",
        organization: "Qryti"
      },
      "admin@demo.qryti.com": {
        password: "admin123",
        role: "admin", 
        name: "Admin User",
        organization: "Qryti Demo Organization"
      },
      "user@demo.qryti.com": {
        password: "demo123",
        role: "user",
        name: "Demo User", 
        organization: "Qryti Demo Organization"
      }
    };
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

  // Get stored token
  getToken() {
    return this.token;
  }

  // Mock health check - always returns healthy
  async healthCheck() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          status: "healthy",
          timestamp: Date.now() / 1000,
          version: "2.0.0",
          environment: "frontend-only",
          uptime: "operational"
        });
      }, 100);
    });
  }

  // Mock login
  async login(email, password) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const normalizedEmail = email.toLowerCase().trim();
        
        if (!normalizedEmail || !password) {
          reject(new Error("Email and password are required"));
          return;
        }

        // Check demo users
        if (normalizedEmail in this.demoUsers && 
            this.demoUsers[normalizedEmail].password === password) {
          
          const userData = { ...this.demoUsers[normalizedEmail] };
          delete userData.password; // Remove password from response
          userData.email = normalizedEmail;
          
          // Generate a simple token
          const token = `mock_token_${normalizedEmail}_${Date.now()}`;
          
          resolve({
            access_token: token,
            token_type: "bearer",
            user: userData
          });
        } else {
          reject(new Error("Invalid credentials"));
        }
      }, 500); // Simulate network delay
    });
  }

  // Mock user registration
  async register(userData) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          message: "Registration successful",
          user: userData
        });
      }, 500);
    });
  }

  // Mock get current user
  async getCurrentUser() {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (this.token && this.user) {
          resolve(this.user);
        } else {
          reject(new Error("Not authenticated"));
        }
      }, 200);
    });
  }

  // Mock get users (admin only)
  async getUsers() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: 1, email: "user1@demo.com", name: "User 1", role: "user" },
          { id: 2, email: "user2@demo.com", name: "User 2", role: "user" },
          { id: 3, email: "admin@demo.com", name: "Admin", role: "admin" }
        ]);
      }, 300);
    });
  }

  // Mock get app info
  async getAppInfo() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          name: "Qrytiv2 Platform",
          version: "2.0.0",
          environment: "frontend-only",
          description: "ISO 42001 AI Governance Platform"
        });
      }, 200);
    });
  }

  // Logout
  logout() {
    this.removeToken();
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token;
  }

  // Mock request method for compatibility
  async request(endpoint, options = {}) {
    // This is a mock implementation
    console.log(`Mock API request to ${endpoint}`, options);
    
    if (endpoint.includes('/health')) {
      return this.healthCheck();
    }
    
    if (endpoint.includes('/login')) {
      const body = JSON.parse(options.body || '{}');
      return this.login(body.email, body.password);
    }
    
    if (endpoint.includes('/me')) {
      return this.getCurrentUser();
    }
    
    if (endpoint.includes('/info')) {
      return this.getAppInfo();
    }
    
    // Default response
    return Promise.resolve({ message: "Mock API response" });
  }
}

// Create and export singleton instance
const mockApiService = new MockApiService();
export default mockApiService;

