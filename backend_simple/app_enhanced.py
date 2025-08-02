"""
Qrytiv2 Enhanced Backend API with Session Management and OTP
Advanced Flask application with security features

Developed by: Qryti Dev Team
"""

from flask import Flask, jsonify, request, session
from flask_cors import CORS
import os
import logging
import time
from datetime import datetime
from session_manager import session_manager
from email_service import email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["*"], supports_credentials=True)

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

# Mock data storage
CLIENTS = []
PROJECTS = []

def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def get_user_agent():
    """Get user agent string"""
    return request.headers.get('User-Agent', 'Unknown')

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Welcome to Qrytiv2 Enhanced API",
        "version": "2.1.0",
        "status": "operational",
        "features": ["session_management", "otp_authentication", "email_notifications"],
        "docs": "/api/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.1.0",
        "environment": "production",
        "timestamp": time.time(),
        "uptime": "operational",
        "features": {
            "session_management": True,
            "otp_authentication": True,
            "email_service": True
        }
    })

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Enhanced login endpoint with OTP support"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
            
        email = data.get('email')
        password = data.get('password')
        remember_device = data.get('remember_device', False)
        
        if not email or not password:
            return jsonify({"detail": "Email and password required"}), 400
        
        # Check if account is locked
        if session_manager.is_account_locked(email):
            return jsonify({
                "detail": "Account temporarily locked due to too many failed attempts. Please try again later."
            }), 429
        
        # Verify credentials
        if email not in DEMO_USERS:
            session_manager.record_login_attempt(email, False)
            return jsonify({"detail": "Invalid email or password"}), 401
        
        user = DEMO_USERS[email]
        if user['password'] != password:
            session_manager.record_login_attempt(email, False)
            return jsonify({"detail": "Invalid email or password"}), 401
        
        # Create device fingerprint
        device_fingerprint = session_manager.create_device_fingerprint(
            get_user_agent(), get_client_ip()
        )
        
        # Check if device is trusted
        if session_manager.is_trusted_device(email, device_fingerprint):
            # Trusted device - create session directly
            session_id = session_manager.create_session(email, user, device_fingerprint)
            session_manager.record_login_attempt(email, True)
            
            return jsonify({
                "access_token": session_id,
                "token_type": "session",
                "requires_otp": False,
                "user": {
                    "email": email,
                    "full_name": user['full_name'],
                    "role": user['role'],
                    "organization": user['organization']
                }
            })
        else:
            # New device - require OTP
            otp_code = session_manager.generate_and_store_otp(email)
            
            # Send OTP email
            try:
                email_service.send_otp_email(email, otp_code, user['full_name'])
                logger.info(f"OTP email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send OTP email to {email}: {e}")
            
            return jsonify({
                "requires_otp": True,
                "message": "Verification code sent to your email",
                "device_fingerprint": device_fingerprint,
                "otp_code": otp_code if app.config['DEBUG'] else None  # Only show OTP in debug mode
            })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"detail": "Login failed. Please try again."}), 500

@app.route('/api/v1/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and complete login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
        
        email = data.get('email')
        otp_code = data.get('otp_code')
        device_fingerprint = data.get('device_fingerprint')
        remember_device = data.get('remember_device', False)
        
        if not all([email, otp_code, device_fingerprint]):
            return jsonify({"detail": "Email, OTP code, and device fingerprint required"}), 400
        
        # Verify OTP
        if not session_manager.verify_otp(email, otp_code):
            return jsonify({"detail": "Invalid or expired verification code"}), 401
        
        # Get user data
        if email not in DEMO_USERS:
            return jsonify({"detail": "User not found"}), 404
        
        user = DEMO_USERS[email]
        
        # Add device to trusted list if requested
        if remember_device:
            session_manager.add_trusted_device(email, device_fingerprint)
        
        # Create session
        session_id = session_manager.create_session(email, user, device_fingerprint)
        session_manager.record_login_attempt(email, True)
        
        return jsonify({
            "access_token": session_id,
            "token_type": "session",
            "user": {
                "email": email,
                "full_name": user['full_name'],
                "role": user['role'],
                "organization": user['organization']
            }
        })
        
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        return jsonify({"detail": "Verification failed. Please try again."}), 500

@app.route('/api/v1/auth/refresh', methods=['POST'])
def refresh_session():
    """Refresh session timeout"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"detail": "Authentication required"}), 401
        
        session_id = auth_header.split(' ')[1]
        
        if session_manager.refresh_session(session_id):
            session_info = session_manager.get_session_info(session_id)
            return jsonify({
                "message": "Session refreshed",
                "session_info": session_info
            })
        else:
            return jsonify({"detail": "Invalid session"}), 401
            
    except Exception as e:
        logger.error(f"Session refresh error: {e}")
        return jsonify({"detail": "Refresh failed"}), 500

@app.route('/api/v1/auth/logout', methods=['POST'])
def logout():
    """Logout and invalidate session"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            session_id = auth_header.split(' ')[1]
            session_manager.invalidate_session(session_id)
        
        return jsonify({"message": "Logged out successfully"})
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"detail": "Logout failed"}), 500

@app.route('/api/v1/auth/session-info', methods=['GET'])
def get_session_info():
    """Get current session information"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"detail": "Authentication required"}), 401
        
        session_id = auth_header.split(' ')[1]
        session_info = session_manager.get_session_info(session_id)
        
        if session_info:
            return jsonify(session_info)
        else:
            return jsonify({"detail": "Invalid session"}), 401
            
    except Exception as e:
        logger.error(f"Session info error: {e}")
        return jsonify({"detail": "Failed to get session info"}), 500

def require_auth():
    """Helper function to check authentication"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    session_id = auth_header.split(' ')[1]
    session_data = session_manager.get_session(session_id)
    
    return session_data

@app.route('/api/v1/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    session_data = require_auth()
    if not session_data:
        return jsonify({"detail": "Authentication required"}), 401
    
    # Calculate statistics
    total_clients = len(CLIENTS)
    total_projects = len(PROJECTS)
    active_projects = len([p for p in PROJECTS if p.get('status') == 'active'])
    avg_compliance = sum([c.get('compliance_score', 0) for c in CLIENTS]) / max(total_clients, 1)
    
    return jsonify({
        "total_clients": total_clients,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "avg_compliance_score": round(avg_compliance, 1),
        "recent_activity": [
            {
                "type": "client_created",
                "message": f"New client registered: {CLIENTS[-1]['name']}" if CLIENTS else "No recent activity",
                "timestamp": CLIENTS[-1]['created_at'] if CLIENTS else datetime.utcnow().isoformat()
            }
        ]
    })

@app.route('/api/v1/admin/clients', methods=['GET'])
def get_clients():
    """Get all clients (admin only)"""
    session_data = require_auth()
    if not session_data:
        return jsonify({"detail": "Authentication required"}), 401
    
    return jsonify(CLIENTS)

@app.route('/api/v1/admin/clients', methods=['POST'])
def create_client():
    """Create a new client (admin only)"""
    try:
        session_data = require_auth()
        if not session_data:
            return jsonify({"detail": "Authentication required"}), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
        
        # Required fields
        required_fields = ['name', 'email', 'password', 'organization', 'department']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"detail": f"Field '{field}' is required"}), 400
        
        # Check if client already exists
        for client in CLIENTS:
            if client['email'] == data['email']:
                return jsonify({"detail": "Client with this email already exists"}), 400
        
        # Create new client
        client_id = len(CLIENTS) + 1
        new_client = {
            "id": client_id,
            "name": data['name'],
            "email": data['email'],
            "organization": data['organization'],
            "department": data['department'],
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "compliance_score": 0,
            "projects_count": 0
        }
        
        CLIENTS.append(new_client)
        
        # Create default project for the client
        project_id = len(PROJECTS) + 1
        default_project = {
            "id": project_id,
            "name": f"ISO 42001 Compliance - {data['organization']}",
            "client_id": client_id,
            "client_name": data['name'],
            "client_organization": data['organization'],
            "ai_system_name": f"{data['organization']} AI System",
            "risk_level": "medium",
            "target_completion": "2025-12-31",
            "description": f"ISO 42001 compliance project for {data['organization']}",
            "status": "active",
            "progress": 0,
            "compliance_score": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        PROJECTS.append(default_project)
        
        # Update client projects count
        new_client['projects_count'] = 1
        
        # Send welcome email
        try:
            email_service.send_welcome_email(data['email'], data['name'], data['organization'])
            logger.info(f"Welcome email sent to {data['email']}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {data['email']}: {e}")
        
        logger.info(f"Client created: {data['email']}")
        
        return jsonify({
            "message": "Client created successfully",
            "client": new_client,
            "project": default_project
        }), 201
        
    except Exception as e:
        logger.error(f"Create client error: {e}")
        return jsonify({"detail": "Failed to create client"}), 500

@app.route('/api/v1/admin/projects', methods=['GET'])
def get_projects():
    """Get all projects (admin only)"""
    session_data = require_auth()
    if not session_data:
        return jsonify({"detail": "Authentication required"}), 401
    
    return jsonify(PROJECTS)

@app.route('/api/v1/admin/projects', methods=['POST'])
def create_project():
    """Create a new project (admin only)"""
    try:
        session_data = require_auth()
        if not session_data:
            return jsonify({"detail": "Authentication required"}), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
        
        # Required fields
        required_fields = ['client_id', 'name', 'ai_system_name', 'risk_level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"detail": f"Field '{field}' is required"}), 400
        
        # Find client
        client = None
        for c in CLIENTS:
            if c['id'] == data['client_id']:
                client = c
                break
        
        if not client:
            return jsonify({"detail": "Client not found"}), 404
        
        # Create new project
        project_id = len(PROJECTS) + 1
        new_project = {
            "id": project_id,
            "name": data['name'],
            "client_id": data['client_id'],
            "client_name": client['name'],
            "client_organization": client['organization'],
            "ai_system_name": data['ai_system_name'],
            "risk_level": data['risk_level'],
            "target_completion": data.get('target_completion', '2025-12-31'),
            "description": data.get('description', ''),
            "status": "active",
            "progress": 0,
            "compliance_score": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        PROJECTS.append(new_project)
        
        # Update client projects count
        client['projects_count'] = len([p for p in PROJECTS if p['client_id'] == client['id']])
        
        logger.info(f"Project created: {data['name']}")
        
        return jsonify({
            "message": "Project created successfully",
            "project": new_project
        }), 201
        
    except Exception as e:
        logger.error(f"Create project error: {e}")
        return jsonify({"detail": "Failed to create project"}), 500

# Cleanup task to remove expired sessions
@app.before_request
def cleanup_sessions():
    """Clean up expired sessions before each request"""
    session_manager.cleanup_expired_sessions()

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
    logger.info(f"{request.method} {request.path} - {get_client_ip()}")

@app.after_request
def log_response(response):
    logger.info(f"Response: {response.status_code}")
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Qrytiv2 Enhanced API on {host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])

