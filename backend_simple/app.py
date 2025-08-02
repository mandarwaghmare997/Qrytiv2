"""
Qrytiv2 Simple Backend API
Lightweight Flask application for production deployment

Developed by: Qryti Dev Team
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import logging
import time
from datetime import datetime

# Import email service
from email_service_enhanced import email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["*"])

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Demo users for authentication
DEMO_USERS = {
    "hello@qryti.com": {
        "password": "Mandar@123",
        "role": "admin",
        "full_name": "Qryti Admin",
        "organization": "Qryti"
    },
    "admin@demo.qryti.com": {
        "password": "admin123",
        "role": "admin",
        "full_name": "Admin User",
        "organization": "Qryti Demo Organization"
    },
    "user@demo.qryti.com": {
        "password": "demo123", 
        "role": "user",
        "full_name": "Demo User",
        "organization": "Qryti Demo Organization"
    }
}

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Welcome to Qrytiv2 API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "environment": "production",
        "timestamp": time.time(),
        "uptime": "operational"
    })

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"detail": "Email and password required"}), 400
            
        # Check demo users
        if email in DEMO_USERS:
            user = DEMO_USERS[email]
            if user['password'] == password:
                # Return success response with token
                return jsonify({
                    "access_token": f"demo-token-{email.split('@')[0]}",
                    "token_type": "bearer",
                    "user": {
                        "email": email,
                        "full_name": user['full_name'],
                        "role": user['role'],
                        "organization": user['organization']
                    }
                })
        
        return jsonify({"detail": "Invalid email or password"}), 401
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"detail": "Login failed. Please try again."}), 500

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """Registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
            
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        organization_name = data.get('organization_name')
        
        if not all([email, password, full_name, organization_name]):
            return jsonify({"detail": "All fields required: email, password, full_name, organization_name"}), 400
            
        # Check if user already exists
        if email in DEMO_USERS:
            return jsonify({"detail": "User with this email already exists"}), 400
            
        # For demo purposes, just return success
        return jsonify({
            "message": "Registration successful. Please check your email for verification.",
            "user": {
                "email": email,
                "full_name": full_name,
                "organization": organization_name
            }
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"detail": "Registration failed. Please try again."}), 500

@app.route('/api/v1/users/', methods=['GET'])
def list_users():
    """List users endpoint (requires authentication)"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"detail": "Authentication required"}), 401
        
    # For demo purposes, return demo users
    users = []
    for email, user_data in DEMO_USERS.items():
        users.append({
            "email": email,
            "full_name": user_data['full_name'],
            "role": user_data['role'],
            "organization": user_data['organization'],
            "is_active": True,
            "is_verified": True
        })
    
    return jsonify(users)

@app.route('/api/v1/info')
def app_info():
    """Application information endpoint"""
    return jsonify({
        "app_name": "Qrytiv2",
        "version": "2.0.0",
        "environment": "production",
        "debug": app.config['DEBUG'],
        "features": {
            "authentication": True,
            "user_management": True,
            "demo_mode": True,
            "cors_enabled": True
        },
        "endpoints": {
            "health": "/health",
            "login": "/api/v1/auth/login",
            "register": "/api/v1/auth/register",
            "users": "/api/v1/users/"
        }
    })

@app.route('/api/v1/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to email for verification"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
            
        email = data.get('email')
        
        if not email:
            return jsonify({"detail": "Email required"}), 400
            
        # Generate and send OTP
        otp = email_service.generate_otp(email)
        success = email_service.send_otp_email(email, otp)
        
        if success:
            return jsonify({
                "message": "OTP sent successfully",
                "email": email,
                "demo_mode": email_service.demo_mode,
                "demo_otp": otp if email_service.demo_mode else None
            })
        else:
            return jsonify({"detail": "Failed to send OTP"}), 500
            
    except Exception as e:
        logger.error(f"Send OTP error: {e}")
        return jsonify({"detail": "Failed to send OTP. Please try again."}), 500

@app.route('/api/v1/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and complete authentication"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
            
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({"detail": "Email and OTP required"}), 400
            
        # Verify OTP
        is_valid = email_service.verify_otp(email, otp)
        
        if is_valid:
            # Check if user exists in demo users
            if email in DEMO_USERS:
                user = DEMO_USERS[email]
                return jsonify({
                    "access_token": f"demo-token-{email.split('@')[0]}",
                    "token_type": "bearer",
                    "user": {
                        "email": email,
                        "full_name": user['full_name'],
                        "role": user['role'],
                        "organization": user['organization']
                    },
                    "message": "OTP verified successfully"
                })
            else:
                # For non-demo users, create a basic user profile
                return jsonify({
                    "access_token": f"verified-token-{email.split('@')[0]}",
                    "token_type": "bearer",
                    "user": {
                        "email": email,
                        "full_name": email.split('@')[0].title(),
                        "role": "user",
                        "organization": "Verified User"
                    },
                    "message": "OTP verified successfully"
                })
        else:
            return jsonify({"detail": "Invalid or expired OTP"}), 400
            
    except Exception as e:
        logger.error(f"Verify OTP error: {e}")
        return jsonify({"detail": "OTP verification failed. Please try again."}), 500

@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "title": "Qrytiv2 API Documentation",
        "version": "2.0.0",
        "description": "ISO 42001 AI Governance Platform API",
        "endpoints": {
            "GET /": "Root endpoint with API information",
            "GET /health": "Health check endpoint",
            "POST /api/v1/auth/login": "User authentication",
            "POST /api/v1/auth/register": "User registration",
            "POST /api/v1/auth/send-otp": "Send OTP for email verification",
            "POST /api/v1/auth/verify-otp": "Verify OTP and complete authentication",
            "GET /api/v1/users/": "List users (authenticated)",
            "GET /api/v1/info": "Application information"
        },
        "demo_users": {
            "hello@qryti.com": "Mandar@123",
            "admin@demo.qryti.com": "admin123",
            "user@demo.qryti.com": "demo123"
        },
        "otp_flow": {
            "1": "POST /api/v1/auth/send-otp with email",
            "2": "Check email for OTP code (or console in demo mode)",
            "3": "POST /api/v1/auth/verify-otp with email and OTP"
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"detail": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"detail": "Internal server error"}), 500

# Request logging middleware
@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response(response):
    logger.info(f"Response: {response.status_code}")
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Qrytiv2 API on {host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])

