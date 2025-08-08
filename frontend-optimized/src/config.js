/**
 * Configuration for Qrytiv2 Frontend (Serverless)
 * Optimized for AWS Lambda + API Gateway backend
 */

// Environment-based configuration
const environment = import.meta.env.MODE || 'development';

const config = {
  // API Configuration
  api: {
    // Will be replaced with actual API Gateway URL after deployment
    baseURL: environment === 'production' 
      ? 'https://api.qryti.com/api/v1'  // Production API Gateway
      : environment === 'staging'
      ? 'https://staging-api.qryti.com/api/v1'  // Staging API Gateway
      : 'http://localhost:3000/api/v1',  // Local development
    
    timeout: 30000, // 30 seconds for Lambda cold starts
    retries: 3,
    
    // Endpoints
    endpoints: {
      // Authentication
      login: '/auth/login',
      register: '/auth/register',
      verify: '/auth/verify',
      
      // Users
      profile: '/users/profile',
      
      // Clients
      clients: '/clients',
      
      // AI Models
      models: '/models',
      
      // Reports
      reports: '/reports',
      generateReport: '/reports/generate',
      
      // Email
      sendWelcome: '/email/welcome'
    }
  },

  // Application Configuration
  app: {
    name: 'Qryti',
    version: '2.0.0',
    description: 'ISO 42001 AI Governance Platform',
    
    // Features
    features: {
      emailNotifications: true,
      reportGeneration: true,
      modelRegistry: true,
      complianceTracking: true,
      userManagement: true
    },
    
    // UI Configuration
    ui: {
      theme: 'light',
      animations: true,
      compactMode: false,
      showBeta: environment !== 'production'
    }
  },

  // Storage Configuration
  storage: {
    // Local storage keys
    keys: {
      authToken: 'qryti_auth_token',
      userProfile: 'qryti_user_profile',
      preferences: 'qryti_preferences'
    },
    
    // Session configuration
    session: {
      timeout: 24 * 60 * 60 * 1000, // 24 hours
      refreshThreshold: 60 * 60 * 1000 // 1 hour before expiry
    }
  },

  // Performance Configuration
  performance: {
    // Lazy loading
    lazyLoading: true,
    
    // Caching
    cache: {
      enabled: true,
      duration: 5 * 60 * 1000, // 5 minutes
      maxSize: 100 // Maximum cached items
    },
    
    // Pagination
    pagination: {
      defaultPageSize: 20,
      maxPageSize: 100
    }
  },

  // Error Handling
  errors: {
    retryAttempts: 3,
    retryDelay: 1000, // 1 second
    showDetailedErrors: environment !== 'production'
  },

  // Analytics (if needed)
  analytics: {
    enabled: environment === 'production',
    trackingId: import.meta.env.VITE_GA_TRACKING_ID || ''
  },

  // Development Configuration
  development: {
    enableDevTools: environment === 'development',
    mockData: environment === 'development',
    debugMode: environment === 'development'
  }
};

// Validation
if (!config.api.baseURL) {
  console.warn('API base URL not configured');
}

// Export configuration
export default config;

// Named exports for convenience
export const { api, app, storage, performance, errors } = config;

// Environment helpers
export const isDevelopment = environment === 'development';
export const isProduction = environment === 'production';
export const isStaging = environment === 'staging';

// API URL builder helper
export const buildApiUrl = (endpoint) => {
  const baseURL = config.api.baseURL.replace(/\/$/, ''); // Remove trailing slash
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseURL}${cleanEndpoint}`;
};

// Feature flag helper
export const isFeatureEnabled = (feature) => {
  return config.app.features[feature] || false;
};

// Storage helpers
export const getStorageKey = (key) => {
  return config.storage.keys[key] || key;
};

// Performance helpers
export const shouldLazyLoad = () => {
  return config.performance.lazyLoading;
};

export const getCacheDuration = () => {
  return config.performance.cache.duration;
};

