// Frontend configuration for Qrytiv2
// API endpoints and environment settings

const config = {
  // API Base URL - Email-enabled backend via CloudFlare tunnel
  API_BASE_URL: 'https://ethiopia-have-alternatively-remark.trycloudflare.com',
  
  // Environment
  ENVIRONMENT: 'production',
  
  // API Endpoints
  ENDPOINTS: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    USERS: '/api/v1/users',
    CLIENTS: '/api/v1/clients',
    HEALTH: '/health',
    DOCS: '/api/docs'
  },
  
  // Application Settings
  APP_NAME: 'Qrytiv2',
  VERSION: '2.0.0'
};

export default config;

