from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.models.organization import Organization
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def validate_business_email(email):
    """Validate that email is from a business domain (not personal)"""
    personal_domains = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'aol.com', 'icloud.com', 'live.com', 'msn.com'
    ]
    
    domain = email.split('@')[1].lower()
    return domain not in personal_domains

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'organization_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate business email
        if not validate_business_email(email):
            return jsonify({'error': 'Please use a business email address'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'User already exists'}), 400
        
        # Get or create organization
        domain = email.split('@')[1]
        organization = Organization.query.filter_by(domain=domain).first()
        
        if not organization:
            organization = Organization(
                name=data['organization_name'],
                domain=domain
            )
            db.session.add(organization)
            db.session.flush()  # Get the ID
        
        # Create user
        user = User(
            email=email,
            first_name=data['first_name'],
            last_name=data['last_name'],
            position=data.get('position', ''),
            phone=data.get('phone', ''),
            organization_id=organization.id
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'organization': organization.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'organization': user.organization.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    # For now, return a sample profile
    # In a real app, you'd get this from JWT token
    return jsonify({
        'user': {
            'id': 1,
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin'
        }
    }), 200

