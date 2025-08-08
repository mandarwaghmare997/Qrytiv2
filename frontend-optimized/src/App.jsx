import React, { useState, useEffect } from 'react';
import './App.css';
import api from './services/api';
import mockApi from './services/mockApi';
import config from './config';

// Use mock API in development mode
const apiService = config.development.mockData ? mockApi : api;
import AdminDashboard from './components/AdminDashboard';
import AdminDashboardNew from './components/AdminDashboardNew';
import AIModelRegistry from './components/AIModelRegistry';
import GapAssessmentProfessional from './components/GapAssessmentProfessional';
import ComplianceReports from './components/ComplianceReports';
import Certifications from './components/Certifications';
import OTPVerification from './components/OTPVerification';
import ISO42001Compliance from './components/ISO42001Compliance.jsx';
import MobileNavigation from './components/MobileNavigation';
import qrytiLogo from './assets/qryti-logo.png';
import './components/AIModelRegistry.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiStatus, setApiStatus] = useState('checking');
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, ai-models, admin, iso-compliance

  // Login form state
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });

  // Check API health and authentication status on mount
  useEffect(() => {
    checkApiHealth();
    checkAuthStatus();
  }, []);

  const checkApiHealth = async () => {
    try {
      await apiService.healthCheck();
      setApiStatus('healthy');
    } catch (error) {
      setApiStatus('error');
      console.error('API health check failed:', error);
    }
  };

  const checkAuthStatus = async () => {
    const token = apiService.getToken();
    const storedUser = apiService.getUser();
    
    if (token) {
      // If we have stored user data, use it immediately
      if (storedUser) {
        setUser(storedUser);
        setIsAuthenticated(true);
      }
      
      try {
        // Validate token and get fresh user info
        const response = await fetch(`${config.API_BASE_URL}/api/v1/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setIsAuthenticated(true);
          // Update stored user data
          api.setToken(token, userData);
        } else {
          // Token is invalid, remove it
          api.removeToken();
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // If we have stored user data, keep the session active
        if (!storedUser) {
          api.removeToken();
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setLoginForm(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiService.login(loginForm.email, loginForm.password);
      
      if (response.access_token) {
        const userData = response.user || { email: loginForm.email, name: loginForm.email.split('@')[0] };
        apiService.setToken(response.access_token, userData);
        setUser(userData);
        setIsAuthenticated(true);
        setCurrentView('dashboard');
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.message.includes('Network')) {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    apiService.logout();
    setUser(null);
    setIsAuthenticated(false);
    setCurrentView('dashboard');
    setLoginForm({ email: '', password: '' });
  };

  const handleNavigate = (view) => {
    setCurrentView(view);
  };

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="login-container">
        <div className="login-background">
          <div className="login-card">
            <div className="login-header">
              <img src={qrytiLogo} alt="Qryti" className="login-logo" />
              <h1>Welcome to Qryti</h1>
              <p>ISO 42001 AI Governance Platform</p>
            </div>

            <form onSubmit={handleLogin} className="login-form">
              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={loginForm.email}
                  onChange={handleInputChange}
                  placeholder="Enter your email"
                  required
                  disabled={loading}
                  autoComplete="email"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={loginForm.password}
                  onChange={handleInputChange}
                  placeholder="Enter your password"
                  required
                  disabled={loading}
                  autoComplete="current-password"
                />
              </div>

              <button 
                type="submit" 
                className="login-button"
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </button>

              <div className="login-footer">
                <a href="#" className="forgot-password">Forgot Password?</a>
              </div>
            </form>

            <div className="api-status">
              API Status: {apiStatus === 'healthy' ? '✅ Connected' : apiStatus === 'error' ? '❌ Disconnected' : '🔄 Checking...'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Determine if user is admin
  const isAdmin = user?.role === 'admin' || user?.email?.includes('admin');

  // Show admin dashboard for admin users
  if (isAdmin && currentView === 'dashboard') {
    return (
      <AdminDashboard 
        user={user} 
        onNavigate={handleNavigate}
        onLogout={handleLogout}
      />
    );
  }

  // Regular dashboard for client users
  if (currentView === 'dashboard') {
    return (
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <div className="header-left">
              <img src={qrytiLogo} alt="Qryti" className="header-logo" />
              <h1>Qryti Platform</h1>
            </div>
            <div className="header-right">
              <span>Welcome, {user?.name || user?.email}</span>
              <button onClick={handleLogout} className="logout-btn">Logout</button>
            </div>
          </div>
        </header>

        <main className="app-main">
          <div className="dashboard-container">
            <div className="dashboard-header">
              <h2>ISO 42001 AI Governance Dashboard</h2>
              <p>Manage your AI compliance journey</p>
            </div>

            <div className="dashboard-grid">
              <div className="dashboard-card clickable" onClick={() => handleNavigate('ai-models')}>
                <div className="card-icon">🤖</div>
                <div className="card-content">
                  <h3>AI Model Registry</h3>
                  <p>Register and manage your AI models</p>
                </div>
                <div className="card-arrow">→</div>
              </div>

              <div className="dashboard-card clickable" onClick={() => handleNavigate('iso-compliance')}>
                <div className="card-icon">📋</div>
                <div className="card-content">
                  <h3>ISO 42001 Compliance</h3>
                  <p>Start your ISO 42001 journey for {user?.organization || 'your organization'}</p>
                </div>
                <div className="card-arrow">→</div>
              </div>

              <div className="dashboard-card clickable" onClick={() => handleNavigate('gap-assessment')}>
                <div className="card-icon">🎯</div>
                <div className="card-content">
                  <h3>Gap Assessment</h3>
                  <p>Evaluate your current compliance status</p>
                </div>
                <div className="card-arrow">→</div>
              </div>

              <div className="dashboard-card clickable" onClick={() => handleNavigate('compliance-reports')}>
                <div className="card-icon">📊</div>
                <div className="card-content">
                  <h3>Compliance Reports</h3>
                  <p>View your compliance progress and reports</p>
                </div>
                <div className="card-arrow">→</div>
              </div>

              <div className="dashboard-card clickable" onClick={() => handleNavigate('certifications')}>
                <div className="card-icon">🏆</div>
                <div className="card-content">
                  <h3>Certifications</h3>
                  <p>Track your certification status</p>
                </div>
                <div className="card-arrow">→</div>
              </div>
            </div>
          </div>
        </main>

        <MobileNavigation 
          currentView={currentView}
          onNavigate={handleNavigate}
          user={user}
        />
      </div>
    );
  }

  // Other views
  return (
    <div className="app">
      {currentView === 'ai-models' && (
        <AIModelRegistry 
          user={user} 
          onNavigate={handleNavigate}
          onLogout={handleLogout}
        />
      )}
      {currentView === 'iso-compliance' && (
        <ISO42001Compliance 
          user={user} 
          onNavigate={handleNavigate}
          onLogout={handleLogout}
        />
      )}
      {currentView === 'gap-assessment' && (
        <GapAssessmentProfessional 
          user={user} 
          onNavigate={handleNavigate}
          onLogout={handleLogout}
        />
      )}
      {currentView === 'compliance-reports' && (
        <ComplianceReports 
          user={user} 
          onBack={() => handleNavigate('dashboard')}
          onLogout={handleLogout}
        />
      )}
      {currentView === 'certifications' && (
        <Certifications 
          user={user} 
          onBack={() => handleNavigate('dashboard')}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;

