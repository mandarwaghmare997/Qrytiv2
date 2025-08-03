// Frontend configuration for Qrytiv2
// API endpoints and environment settings

const config = {
  // API Base URL - Production EC2 backend via CloudFlare Tunnel (Working Backend)
  API_BASE_URL: 'https://points-steal-combined-blame.trycloudflare.com',
  
  // Environment
  ENVIRONMENT: 'production',
  
  // API Endpoints
  ENDPOINTS: {
    HEALTH: '/health',
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    USERS: '/api/v1/users/',
    INFO: '/api/v1/info',
    DOCS: '/api/docs',
    SEND_OTP: '/api/v1/auth/send-otp',
    VERIFY_OTP: '/api/v1/auth/verify-otp'
  },
  
  // Admin credentials
  ADMIN_CREDENTIALS: {
    email: 'hello@qryti.com',
    password: 'Mandar@123'
  },
  
  // Demo credentials
  DEMO_CREDENTIALS: {
    email: 'user@demo.qryti.com',
    password: 'demo123'
  },
  
  // App settings
  APP_NAME: 'Qrytiv2',
  VERSION: '2.0.0',
  
  // Features
  FEATURES: {
    AUTHENTICATION: true,
    DEMO_MODE: true,
    OFFLINE_MODE: false,
    OTP_VERIFICATION: true
  }
};

export default config;

