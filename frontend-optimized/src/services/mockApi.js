/**
 * Mock API Service for Development Testing
 * Provides local mock data while serverless backend is being deployed
 */

// Mock data
const mockUsers = [
  {
    id: '1',
    email: 'hello@qryti.com',
    password: 'Mandar@123', // In real app, this would be hashed
    name: 'Mandar Waghmare',
    role: 'admin',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '2',
    email: 'user@demo.qryti.com',
    password: 'demo123',
    name: 'Demo User',
    role: 'user',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '3',
    email: 'admin@demo.qryti.com',
    password: 'admin123',
    name: 'Admin User',
    role: 'admin',
    created_at: '2025-01-01T00:00:00Z'
  }
];

const mockClients = [
  {
    id: '1',
    name: 'Acme Corporation',
    industry: 'Technology',
    contact_email: 'contact@acme.com',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '2',
    name: 'TechStart Inc',
    industry: 'Startup',
    contact_email: 'hello@techstart.com',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '3',
    name: 'Global Industries',
    industry: 'Manufacturing',
    contact_email: 'info@global.com',
    created_at: '2025-01-01T00:00:00Z'
  }
];

const mockModels = [
  {
    id: '1',
    name: 'Customer Sentiment Analysis',
    client_id: '1',
    client_name: 'Acme Corporation',
    type: 'NLP',
    risk_level: 'Medium',
    status: 'Active',
    created_at: '2025-01-01T00:00:00Z'
  },
  {
    id: '2',
    name: 'Fraud Detection System',
    client_id: '2',
    client_name: 'TechStart Inc',
    type: 'Classification',
    risk_level: 'High',
    status: 'Under Review',
    created_at: '2025-01-01T00:00:00Z'
  }
];

class MockApiService {
  constructor() {
    this.isOnline = true;
    this.delayMs = 500; // Simulate network delay
  }

  // Simulate network delay
  async delay(ms = this.delayMs) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Mock response wrapper
  mockResponse(data, success = true) {
    return {
      success,
      data,
      message: success ? 'Success' : 'Error',
      timestamp: new Date().toISOString()
    };
  }

  // Authentication token management
  getToken() {
    return localStorage.getItem('qryti_auth_token');
  }

  setToken(token, user) {
    localStorage.setItem('qryti_auth_token', token);
    localStorage.setItem('qryti_user_profile', JSON.stringify(user));
  }

  getUser() {
    const userStr = localStorage.getItem('qryti_user_profile');
    return userStr ? JSON.parse(userStr) : null;
  }

  removeToken() {
    localStorage.removeItem('qryti_auth_token');
    localStorage.removeItem('qryti_user_profile');
  }

  // Health check
  async healthCheck() {
    await this.delay(100);
    return this.mockResponse({ status: 'healthy', service: 'mock-api' });
  }

  // Authentication methods
  async login(email, password) {
    await this.delay();
    
    const user = mockUsers.find(u => u.email === email && u.password === password);
    
    if (user) {
      const token = `mock-jwt-token-${Date.now()}`;
      const userResponse = {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      };
      
      return {
        success: true,
        access_token: token,
        user: userResponse,
        expires_in: 86400 // 24 hours
      };
    } else {
      throw new Error('Invalid credentials');
    }
  }

  async register(userData) {
    await this.delay();
    
    // Check if user already exists
    const existingUser = mockUsers.find(u => u.email === userData.email);
    if (existingUser) {
      throw new Error('User already exists');
    }

    const newUser = {
      id: String(mockUsers.length + 1),
      email: userData.email,
      password: userData.password,
      name: userData.name || userData.email.split('@')[0],
      role: 'user',
      created_at: new Date().toISOString()
    };

    mockUsers.push(newUser);

    const token = `mock-jwt-token-${Date.now()}`;
    const userResponse = {
      id: newUser.id,
      email: newUser.email,
      name: newUser.name,
      role: newUser.role
    };

    return {
      success: true,
      access_token: token,
      user: userResponse,
      message: 'Registration successful'
    };
  }

  async verifyToken() {
    await this.delay(100);
    const token = this.getToken();
    return this.mockResponse({ valid: !!token });
  }

  // User methods
  async getUserProfile() {
    await this.delay();
    const user = this.getUser();
    if (!user) {
      throw new Error('Not authenticated');
    }
    return this.mockResponse(user);
  }

  async updateUserProfile(profileData) {
    await this.delay();
    const user = this.getUser();
    if (!user) {
      throw new Error('Not authenticated');
    }

    const updatedUser = { ...user, ...profileData };
    this.setToken(this.getToken(), updatedUser);
    
    return this.mockResponse(updatedUser);
  }

  // Client methods
  async getClients() {
    await this.delay();
    return this.mockResponse(mockClients);
  }

  async createClient(clientData) {
    await this.delay();
    
    const newClient = {
      id: String(mockClients.length + 1),
      ...clientData,
      created_at: new Date().toISOString()
    };

    mockClients.push(newClient);
    return this.mockResponse(newClient);
  }

  // AI Model methods
  async getModels(filters = {}) {
    await this.delay();
    let filteredModels = [...mockModels];

    if (filters.client_id) {
      filteredModels = filteredModels.filter(m => m.client_id === filters.client_id);
    }

    if (filters.status) {
      filteredModels = filteredModels.filter(m => m.status === filters.status);
    }

    return this.mockResponse(filteredModels);
  }

  async registerModel(modelData) {
    await this.delay();
    
    const client = mockClients.find(c => c.id === modelData.client_id);
    
    const newModel = {
      id: String(mockModels.length + 1),
      ...modelData,
      client_name: client ? client.name : 'Unknown Client',
      status: 'Under Review',
      created_at: new Date().toISOString()
    };

    mockModels.push(newModel);
    return this.mockResponse(newModel);
  }

  async updateModel(modelId, modelData) {
    await this.delay();
    
    const modelIndex = mockModels.findIndex(m => m.id === modelId);
    if (modelIndex === -1) {
      throw new Error('Model not found');
    }

    mockModels[modelIndex] = { ...mockModels[modelIndex], ...modelData };
    return this.mockResponse(mockModels[modelIndex]);
  }

  // Report methods
  async getReports() {
    await this.delay();
    const mockReports = [
      {
        id: '1',
        title: 'ISO 42001 Compliance Report',
        type: 'compliance',
        status: 'completed',
        created_at: '2025-01-01T00:00:00Z'
      },
      {
        id: '2',
        title: 'AI Model Risk Assessment',
        type: 'risk_assessment',
        status: 'in_progress',
        created_at: '2025-01-02T00:00:00Z'
      }
    ];
    
    return this.mockResponse(mockReports);
  }

  async generateReport(reportData) {
    await this.delay(2000); // Longer delay for report generation
    
    const newReport = {
      id: String(Date.now()),
      ...reportData,
      status: 'completed',
      download_url: `https://mock-s3-bucket.com/reports/${Date.now()}.pdf`,
      created_at: new Date().toISOString()
    };

    return this.mockResponse(newReport);
  }

  async downloadReport(reportId) {
    await this.delay();
    return this.mockResponse({
      download_url: `https://mock-s3-bucket.com/reports/${reportId}.pdf`,
      expires_in: 3600 // 1 hour
    });
  }

  // Logout
  logout() {
    this.removeToken();
  }
}

// Create singleton instance
const mockApi = new MockApiService();

export default mockApi;

