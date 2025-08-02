import React, { useState, useEffect, useRef } from 'react';
import './OTPVerification.css';
import qrytiLogo from '../assets/qryti-logo.png';

const OTPVerification = ({ email, onVerify, onResend, onBack, loading = false }) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [resendCooldown, setResendCooldown] = useState(0);
  const [isVerifying, setIsVerifying] = useState(false);
  const inputRefs = useRef([]);

  // Cooldown timer for resend
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const handleInputChange = (index, value) => {
    // Only allow digits
    if (!/^\d*$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
    setError('');

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all fields are filled
    if (newOtp.every(digit => digit !== '') && value) {
      handleVerify(newOtp.join(''));
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    const newOtp = [...otp];
    
    for (let i = 0; i < pastedData.length; i++) {
      newOtp[i] = pastedData[i];
    }
    
    setOtp(newOtp);
    
    // Focus the next empty input or the last input
    const nextEmptyIndex = newOtp.findIndex(digit => digit === '');
    const focusIndex = nextEmptyIndex === -1 ? 5 : nextEmptyIndex;
    inputRefs.current[focusIndex]?.focus();

    // Auto-submit if all fields are filled
    if (newOtp.every(digit => digit !== '')) {
      handleVerify(newOtp.join(''));
    }
  };

  const handleVerify = async (otpCode = null) => {
    const code = otpCode || otp.join('');
    
    if (code.length !== 6) {
      setError('Please enter all 6 digits');
      return;
    }

    setIsVerifying(true);
    setError('');

    try {
      await onVerify(code);
    } catch (error) {
      setError(error.message || 'Invalid verification code. Please try again.');
      // Clear OTP on error
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    
    try {
      await onResend();
      setResendCooldown(60); // 60 second cooldown
      setError('');
      // Clear current OTP
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } catch (error) {
      setError(error.message || 'Failed to resend code. Please try again.');
    }
  };

  const isOtpComplete = otp.every(digit => digit !== '');

  return (
    <div className="otp-verification-container">
      <div className="otp-background">
        <div className="otp-card">
          <div className="otp-header">
            <img src={qrytiLogo} alt="Qryti" className="otp-logo" />
            <h1>Verify Your Email</h1>
            <p>We've sent a 6-digit verification code to</p>
            <div className="email-display">{email}</div>
          </div>

          <div className="otp-form">
            {error && (
              <div className="error-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                {error}
              </div>
            )}

            <div className="otp-inputs">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={el => inputRefs.current[index] = el}
                  type="text"
                  inputMode="numeric"
                  maxLength="1"
                  value={digit}
                  onChange={(e) => handleInputChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={handlePaste}
                  className={`otp-input ${error ? 'error' : ''} ${digit ? 'filled' : ''}`}
                  disabled={isVerifying || loading}
                  autoComplete="one-time-code"
                />
              ))}
            </div>

            <div className="otp-actions">
              <button 
                type="button"
                className="verify-button"
                onClick={() => handleVerify()}
                disabled={!isOtpComplete || isVerifying || loading}
              >
                {isVerifying || loading ? (
                  <>
                    <div className="spinner"></div>
                    Verifying...
                  </>
                ) : (
                  <>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <path d="M22 4L12 14.01l-3-3"/>
                    </svg>
                    Verify & Login
                  </>
                )}
              </button>
            </div>

            <div className="otp-footer">
              <div className="resend-section">
                <span>Didn't receive the code?</span>
                <button 
                  type="button"
                  className={`resend-button ${resendCooldown > 0 ? 'disabled' : ''}`}
                  onClick={handleResend}
                  disabled={resendCooldown > 0}
                >
                  {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Code'}
                </button>
              </div>
              
              <button 
                type="button"
                className="back-button"
                onClick={onBack}
                disabled={isVerifying || loading}
              >
                ← Back to Login
              </button>
            </div>
          </div>

          <div className="otp-help">
            <div className="help-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <path d="M12 17h.01"/>
              </svg>
              <div>
                <strong>Having trouble?</strong>
                <p>Check your spam folder or contact support if you don't receive the code within 5 minutes.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OTPVerification;

