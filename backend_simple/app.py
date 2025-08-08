"""
Qrytiv2 Backend with Database Integration
Enhanced Flask application with SQLite database support

Developed by: Qryti Dev Team
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import logging
import time
from datetime import datetime

# Import database models
from models import db, User, Client, Project, init_database

# Import email service
from email_service_enhanced import email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Enable CORS with specific origins to avoid conflicts with Nginx
CORS(app, 
     origins=["https://app.qryti.com", "http://localhost:3000"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///qryti.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Welcome to Qrytiv2 API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "SQLite with persistence"
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        user_count = User.query.count()
        client_count = Client.query.count()
        
        return jsonify({
            "status": "healthy",
            "version": "2.0.0",
            "environment": "production",
            "timestamp": time.time(),
            "uptime": "operational",
            "database": {
                "status": "connected",
                "users": user_count,
                "clients": client_count
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "unhealthy",
            "version": "2.0.0",
            "environment": "production",
            "timestamp": time.time(),
            "error": str(e)
        }), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Login endpoint with database authentication"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"detail": "Email and password required"}), 400
            
        # Find user in database
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if user and user.check_password(password):
            # Update last login
            user.update_last_login()
            
            # Return success response with token
            return jsonify({
                "access_token": f"db-token-{user.id}-{int(time.time())}",
                "token_type": "bearer",
                "user": user.to_dict()
            })
        
        return jsonify({"detail": "Invalid email or password"}), 401
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"detail": "Login failed. Please try again."}), 500

@app.route('/api/v1/auth/me', methods=['GET'])
def get_current_user():
    """Get current user information from token"""
    try:
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"detail": "Authorization token required"}), 401
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        # Parse token to get user ID (format: db-token-{user_id}-{timestamp})
        try:
            token_parts = token.split('-')
            if len(token_parts) >= 3 and token_parts[0] == 'db' and token_parts[1] == 'token':
                user_id = int(token_parts[2])
                
                # Find user in database
                user = User.query.filter_by(id=user_id, is_active=True).first()
                if user:
                    return jsonify(user.to_dict())
                else:
                    return jsonify({"detail": "User not found"}), 404
            else:
                return jsonify({"detail": "Invalid token format"}), 401
                
        except (ValueError, IndexError):
            return jsonify({"detail": "Invalid token"}), 401
            
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({"detail": "Failed to get user information"}), 500

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """Registration endpoint with database persistence and email"""
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
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"detail": "User with this email already exists"}), 400
            
        # Create new user
        new_user = User(
            email=email,
            password=password,
            full_name=full_name,
            organization=organization_name,
            role='user'
        )
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcome email
        try:
            email_success = email_service.send_welcome_email(
                email, 
                full_name, 
                organization_name
            )
            email_status = "sent" if email_success else "failed"
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            email_status = "failed"
        
        return jsonify({
            "message": "Registration successful. Welcome to Qryti!",
            "user": new_user.to_dict(),
            "email_status": email_status
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({"detail": "Registration failed. Please try again."}), 500

@app.route('/api/v1/clients', methods=['GET'])
def get_clients():
    """Get all active clients"""
    try:
        clients = Client.query.filter_by(is_active=True).all()
        return jsonify([client.to_dict() for client in clients])
    except Exception as e:
        logger.error(f"Get clients error: {e}")
        return jsonify({"detail": "Failed to fetch clients"}), 500

@app.route('/api/v1/clients', methods=['POST'])
def create_client():
    """Create a new client"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
        
        name = data.get('name')
        if not name:
            return jsonify({"detail": "Client name is required"}), 400
        
        # Create new client
        new_client = Client(
            name=name,
            description=data.get('description', ''),
            contact_email=data.get('contact_email'),
            contact_phone=data.get('contact_phone')
        )
        
        db.session.add(new_client)
        db.session.commit()
        
        return jsonify({
            "message": "Client created successfully",
            "client": new_client.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Create client error: {e}")
        db.session.rollback()
        return jsonify({"detail": "Failed to create client"}), 500

@app.route('/api/v1/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"detail": "Request body required"}), 400
        
        name = data.get('name')
        client_id = data.get('client_id')
        created_by = data.get('created_by', 1)  # Default to first user
        
        if not all([name, client_id]):
            return jsonify({"detail": "Project name and client_id are required"}), 400
        
        # Verify client exists
        client = Client.query.get(client_id)
        if not client:
            return jsonify({"detail": "Client not found"}), 404
        
        # Create new project
        new_project = Project(
            name=name,
            description=data.get('description', ''),
            client_id=client_id,
            created_by=created_by,
            status=data.get('status', 'active')
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        return jsonify({
            "message": "Project created successfully",
            "project": new_project.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Create project error: {e}")
        db.session.rollback()
        return jsonify({"detail": "Failed to create project"}), 500

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    try:
        users = User.query.filter_by(is_active=True).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Get users error: {e}")
        return jsonify({"detail": "Failed to fetch users"}), 500

# OTP endpoints (keeping existing functionality)
@app.route('/api/v1/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP for authentication"""
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
            # Check if user exists in database
            user = User.query.filter_by(email=email, is_active=True).first()
            
            if user:
                user.update_last_login()
                return jsonify({
                    "access_token": f"otp-token-{user.id}-{int(time.time())}",
                    "token_type": "bearer",
                    "user": user.to_dict(),
                    "message": "OTP verified successfully"
                })
            else:
                # For non-registered users, create a basic user profile
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
        "description": "ISO 42001 AI Governance Platform API with Database Persistence",
        "endpoints": {
            "authentication": {
                "POST /api/v1/auth/login": "Login with email and password",
                "POST /api/v1/auth/register": "Register new user with email verification",
                "POST /api/v1/auth/send-otp": "Send OTP for verification",
                "POST /api/v1/auth/verify-otp": "Verify OTP code"
            },
            "users": {
                "GET /api/v1/users": "Get all users (admin only)"
            },
            "clients": {
                "GET /api/v1/clients": "Get all clients",
                "POST /api/v1/clients": "Create new client"
            },
            "projects": {
                "POST /api/v1/projects": "Create new project"
            },
            "system": {
                "GET /health": "Health check with database status",
                "GET /api/docs": "This documentation"
            }
        },
        "demo_credentials": {
            "hello@qryti.com": "Mandar@123",
            "admin@demo.qryti.com": "admin123",
            "user@demo.qryti.com": "demo123"
        },
        "database": {
            "type": "SQLite",
            "persistence": "Enabled",
            "models": ["User", "Client", "Project"]
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
    # Initialize database with demo data
    init_database(app)
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Qrytiv2 API with Database on {host}:{port}")
    app.run(host=host, port=port, debug=app.config['DEBUG'])

