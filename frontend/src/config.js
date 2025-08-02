// Frontend configuration for Qrytiv2
// API endpoints and environment settings

const config = {
  // API Base URL - Production backend
  API_BASE_URL: 'https://3dhkilcj59gx.manus.space',
  
  // Environment
  ENVIRONMENT: 'production',
  
  // API Endpoints
  ENDPOINTS: {
    HEALTH: '/health',
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    USERS: '/api/v1/users/',
    INFO: '/api/v1/info',
    DOCS: '/api/docs'
  },
  
  // Demo credentials for testing
  DEMO_USERS: {
    admin: {
      email: 'admin@demo.qryti.com',
      password: 'admin123'
    },
    user: {
      email: 'user@demo.qryti.com', 
      password: 'demo123'
    }
  },
  
  // App settings
  APP_NAME: 'Qrytiv2',
  VERSION: '2.0.0',
  
  // Features
  FEATURES: {
    AUTHENTICATION: true,
    DEMO_MODE: true,
    OFFLINE_MODE: false
  }
};

export default config;

