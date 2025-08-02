"""
Session Management and OTP Authentication System
Handles user sessions, device memory, and OTP verification
"""

import time
import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class SessionManager:
    def __init__(self):
        # In-memory storage (in production, use Redis or database)
        self.sessions = {}  # session_id -> session_data
        self.otp_codes = {}  # email -> otp_data
        self.trusted_devices = {}  # email -> [device_fingerprints]
        self.login_attempts = {}  # email -> attempt_data
        
        # Configuration
        self.SESSION_TIMEOUT = 600  # 10 minutes
        self.OTP_TIMEOUT = 300  # 5 minutes
        self.DEVICE_MEMORY_DAYS = 30
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOCKOUT_DURATION = 900  # 15 minutes
    
    def generate_session_id(self) -> str:
        """Generate a secure session ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def generate_otp(self) -> str:
        """Generate a 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def create_device_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Create a device fingerprint from user agent and IP"""
        device_string = f"{user_agent}:{ip_address}"
        return hashlib.sha256(device_string.encode()).hexdigest()[:16]
    
    def is_account_locked(self, email: str) -> bool:
        """Check if account is locked due to too many failed attempts"""
        if email not in self.login_attempts:
            return False
        
        attempt_data = self.login_attempts[email]
        if attempt_data['count'] >= self.MAX_LOGIN_ATTEMPTS:
            if time.time() - attempt_data['last_attempt'] < self.LOCKOUT_DURATION:
                return True
            else:
                # Reset attempts after lockout period
                del self.login_attempts[email]
        
        return False
    
    def record_login_attempt(self, email: str, success: bool):
        """Record a login attempt"""
        if success:
            # Clear failed attempts on successful login
            if email in self.login_attempts:
                del self.login_attempts[email]
        else:
            # Increment failed attempts
            if email not in self.login_attempts:
                self.login_attempts[email] = {'count': 0, 'last_attempt': 0}
            
            self.login_attempts[email]['count'] += 1
            self.login_attempts[email]['last_attempt'] = time.time()
    
    def is_trusted_device(self, email: str, device_fingerprint: str) -> bool:
        """Check if device is trusted for this user"""
        if email not in self.trusted_devices:
            return False
        
        trusted_list = self.trusted_devices[email]
        for device in trusted_list:
            if device['fingerprint'] == device_fingerprint:
                # Check if device trust hasn't expired
                if time.time() - device['added_at'] < (self.DEVICE_MEMORY_DAYS * 24 * 3600):
                    return True
                else:
                    # Remove expired device
                    trusted_list.remove(device)
        
        return False
    
    def add_trusted_device(self, email: str, device_fingerprint: str):
        """Add device to trusted list"""
        if email not in self.trusted_devices:
            self.trusted_devices[email] = []
        
        # Remove existing entry for this device
        self.trusted_devices[email] = [
            d for d in self.trusted_devices[email] 
            if d['fingerprint'] != device_fingerprint
        ]
        
        # Add new entry
        self.trusted_devices[email].append({
            'fingerprint': device_fingerprint,
            'added_at': time.time()
        })
        
        # Keep only last 5 trusted devices
        if len(self.trusted_devices[email]) > 5:
            self.trusted_devices[email] = self.trusted_devices[email][-5:]
    
    def generate_and_store_otp(self, email: str) -> str:
        """Generate and store OTP for email verification"""
        otp = self.generate_otp()
        
        self.otp_codes[email] = {
            'code': otp,
            'generated_at': time.time(),
            'attempts': 0
        }
        
        return otp
    
    def verify_otp(self, email: str, provided_otp: str) -> bool:
        """Verify OTP code"""
        if email not in self.otp_codes:
            return False
        
        otp_data = self.otp_codes[email]
        
        # Check if OTP has expired
        if time.time() - otp_data['generated_at'] > self.OTP_TIMEOUT:
            del self.otp_codes[email]
            return False
        
        # Check attempt limit
        if otp_data['attempts'] >= 3:
            del self.otp_codes[email]
            return False
        
        # Verify OTP
        if otp_data['code'] == provided_otp:
            del self.otp_codes[email]
            return True
        else:
            otp_data['attempts'] += 1
            return False
    
    def create_session(self, email: str, user_data: dict, device_fingerprint: str) -> str:
        """Create a new session"""
        session_id = self.generate_session_id()
        
        self.sessions[session_id] = {
            'email': email,
            'user_data': user_data,
            'device_fingerprint': device_fingerprint,
            'created_at': time.time(),
            'last_activity': time.time()
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data if valid"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if time.time() - session['last_activity'] > self.SESSION_TIMEOUT:
            del self.sessions[session_id]
            return None
        
        # Update last activity
        session['last_activity'] = time.time()
        return session
    
    def refresh_session(self, session_id: str) -> bool:
        """Refresh session timeout"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = time.time()
            return True
        return False
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session['last_activity'] > self.SESSION_TIMEOUT:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get session information for display"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            'email': session['email'],
            'created_at': datetime.fromtimestamp(session['created_at']).isoformat(),
            'last_activity': datetime.fromtimestamp(session['last_activity']).isoformat(),
            'expires_at': datetime.fromtimestamp(session['last_activity'] + self.SESSION_TIMEOUT).isoformat(),
            'device_fingerprint': session['device_fingerprint'][:8] + '...'  # Partial fingerprint for display
        }

# Global session manager instance
session_manager = SessionManager()

