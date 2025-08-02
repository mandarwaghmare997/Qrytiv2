import React, { useState, useEffect } from 'react';
import './App.css';
import apiService from './services/api.js';
import config from './config.js';
import AIModelRegistry from './components/AIModelRegistry.jsx';
import AdminDashboardNew from './components/AdminDashboardNew.jsx';
import ISO42001Compliance from './components/ISO42001Compliance.jsx';
import GapAssessmentNew from './components/GapAssessmentNew.jsx';
import qrytiLogo from './assets/qryti-logo.png';
import './components/AIModelRegistry.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('dashboard');
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });
  const [otpForm, setOtpForm] = useState({
    email: '',
    otpCode: '',
    deviceFingerprint: '',
    rememberDevice: false
  });
  const [showOtpForm, setShowOtpForm] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Check API health
      await apiService.healthCheck();
      setApiStatus('connected');

      // Check if user is already authenticated
      if (apiService.isAuthenticated()) {
        const userData = apiService.getUser();
        if (userData) {
          setUser(userData);
          setCurrentView(userData.role === 'admin' ? 'admin' : 'dashboard');
          apiService.startSessionRefresh();
        } else {
          // Token exists but no user data, try to get session info
          try {
            const sessionInfo = await apiService.getSessionInfo();
            if (sessionInfo && sessionInfo.email) {
              // Create minimal user object from session info
              const userFromSession = {
                email: sessionInfo.email,
                full_name: sessionInfo.email.split('@')[0],
                role: sessionInfo.email === 'hello@qryti.com' ? 'admin' : 'user'
              };
              setUser(userFromSession);
              setCurrentView(userFromSession.role === 'admin' ? 'admin' : 'dashboard');
              apiService.setUser(userFromSession);
              apiService.startSessionRefresh();
            } else {
              // Invalid session, clear auth
              apiService.logout();
            }
          } catch (error) {
            // Session invalid, clear auth
            console.log('Session invalid, clearing auth');
            apiService.logout();
          }
        }
      }
    } catch (error) {
      console.error('Failed to connect to API:', error);
      setApiStatus('disconnected');
      setError('Unable to connect to server. Please check your connection.');
    } finally {
      setLoading(false);
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

  const handleOtpInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setOtpForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error when user starts typing
    if (error) {
      setError('');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Demo mode - bypass authentication for testing
      if (loginForm.email === 'demo@qryti.com' || loginForm.email === 'test@example.com') {
        const demoUser = {
          email: loginForm.email,
          full_name: 'Demo User',
          organization: 'Demo Organization',
          role: 'user'
        };
        setUser(demoUser);
        setCurrentView('dashboard');
        setLoading(false);
        return;
      }

      const response = await apiService.login(loginForm.email, loginForm.password);
      
      if (response.requires_otp) {
        // OTP required for new device
        setOtpForm({
          email: loginForm.email,
          otpCode: '',
          deviceFingerprint: response.device_fingerprint,
          rememberDevice: false
        });
        setShowOtpForm(true);
        setError(''); // Clear any previous errors
      } else {
        // Direct login successful
        setUser(response.user);
        apiService.startSessionRefresh();
        setLoginForm({ email: '', password: '' });
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.message.includes('Network')) {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError(error.message || 'Login failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOtpVerification = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiService.verifyOTP(
        otpForm.email,
        otpForm.otpCode,
        otpForm.deviceFingerprint,
        otpForm.rememberDevice
      );

      setUser(response.user);
      apiService.startSessionRefresh();
      setShowOtpForm(false);
      setOtpForm({ email: '', otpCode: '', deviceFingerprint: '', rememberDevice: false });
      setLoginForm({ email: '', password: '' });
    } catch (error) {
      console.error('OTP verification error:', error);
      setError(error.message || 'Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
      apiService.stopSessionRefresh();
      setUser(null);
      setCurrentView('dashboard');
      setError('');
      setShowOtpForm(false);
      setLoginForm({ email: '', password: '' });
      setOtpForm({ email: '', otpCode: '', deviceFingerprint: '', rememberDevice: false });
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      apiService.logout();
      apiService.stopSessionRefresh();
      setUser(null);
    }
  };

  const handleNavigate = (view) => {
    setCurrentView(view);
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading Qryti Platform...</p>
        </div>
      </div>
    );
  }

  // Show login form if not authenticated
  if (!user) {
    return (
      <div className="login-container">
        <div className="login-background">
          <div className="login-card">
            <div className="login-header">
              <img src={qrytiLogo} alt="Qryti" className="login-logo" />
              <h1>Welcome to Qryti</h1>
              <p>ISO 42001 AI Governance Platform</p>
            </div>

            {!showOtpForm ? (
              <form onSubmit={handleLogin} className="login-form">
                {error && (
                  <div className="error-message">
                    <span className="error-icon">⚠️</span>
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
            ) : (
              <form onSubmit={handleOtpVerification} className="otp-form">
                <div className="otp-header">
                  <div className="otp-icon">🔐</div>
                  <h3>Verify New Device</h3>
                  <p>We've sent a verification code to</p>
                  <p className="email-highlight">{otpForm.email}</p>
                  <p className="otp-note">Check your email for the 6-digit code</p>
                </div>

                {error && (
                  <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    {error}
                  </div>
                )}

                <div className="form-group">
                  <label htmlFor="otpCode">Verification Code</label>
                  <input
                    id="otpCode"
                    name="otpCode"
                    type="text"
                    value={otpForm.otpCode}
                    onChange={handleOtpInputChange}
                    placeholder="Enter 6-digit code"
                    maxLength="6"
                    required
                    disabled={loading}
                    className="otp-input"
                  />
                </div>

                <div className="form-group checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="rememberDevice"
                      checked={otpForm.rememberDevice}
                      onChange={handleOtpInputChange}
                      disabled={loading}
                    />
                    <span className="checkmark"></span>
                    Remember this device for 30 days
                  </label>
                </div>

                <div className="otp-actions">
                  <button 
                    type="submit" 
                    className="verify-btn primary" 
                    disabled={loading || otpForm.otpCode.length !== 6}
                  >
                    {loading ? 'Verifying...' : 'Verify & Login'}
                  </button>
                  <button 
                    type="button" 
                    className="back-btn secondary"
                    onClick={() => {
                      setShowOtpForm(false);
                      setError('');
                    }}
                    disabled={loading}
                  >
                    ← Back to Login
                  </button>
                </div>
              </form>
            )}

            <div className="api-status">
              <span className={`status-indicator ${apiStatus}`}></span>
              API Status: {apiStatus === 'connected' ? '✅ Connected' : apiStatus === 'disconnected' ? '❌ Disconnected' : '🔄 Checking...'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Determine if user is admin
  const isAdmin = user?.role === 'admin' || user?.email === 'hello@qryti.com';

  // Show admin dashboard for admin users
  if (isAdmin && currentView === 'dashboard') {
    return (
      <AdminDashboardNew 
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
              <span>Welcome, {user?.full_name || user?.email}</span>
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

              <div className="dashboard-card">
                <div className="card-icon">📊</div>
                <div className="card-content">
                  <h3>Compliance Reports</h3>
                  <p>View your compliance progress and reports</p>
                </div>
                <div className="card-status">Coming Soon</div>
              </div>

              <div className="dashboard-card">
                <div className="card-icon">🏆</div>
                <div className="card-content">
                  <h3>Certifications</h3>
                  <p>Track your certification status</p>
                </div>
                <div className="card-status">Coming Soon</div>
              </div>
            </div>
          </div>
        </main>
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
        <GapAssessmentNew 
          user={user} 
          onNavigate={handleNavigate}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;

