"""
JWT Authentication Module for Qrytiv2 Serverless
Handles JWT token generation, validation, and user authentication

Developed by: Qryti Dev Team
"""

import jwt
import bcrypt
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'qryti-dev-secret-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

class AuthService:
    def __init__(self):
        self.secret = JWT_SECRET
        self.algorithm = JWT_ALGORITHM
        self.expiration_hours = JWT_EXPIRATION_HOURS

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    def generate_token(self, user_data: Dict) -> str:
        """Generate a JWT token for a user"""
        try:
            now = datetime.now(timezone.utc)
            expiration = now + timedelta(hours=self.expiration_hours)
            
            payload = {
                'user_id': user_data['user_id'],
                'email': user_data['email'],
                'role': user_data['role'],
                'full_name': user_data['full_name'],
                'organization': user_data['organization'],
                'iat': now,
                'exp': expiration,
                'iss': 'qryti-api'
            }
            
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating token: {e}")
            raise

    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Verify a JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            
            # Check if token is expired
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                return False, None
            
            user_data = {
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'role': payload.get('role'),
                'full_name': payload.get('full_name'),
                'organization': payload.get('organization')
            }
            
            return True, user_data
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return False, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return False, None

    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        if not authorization_header:
            return None
        
        parts = authorization_header.split(' ')
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]

    def create_auth_response(self, user_data: Dict) -> Dict:
        """Create authentication response with token and user data"""
        try:
            token = self.generate_token(user_data)
            
            return {
                'success': True,
                'token': token,
                'user': {
                    'user_id': user_data['user_id'],
                    'email': user_data['email'],
                    'full_name': user_data['full_name'],
                    'organization': user_data['organization'],
                    'role': user_data['role'],
                    'is_active': user_data.get('is_active', True)
                },
                'expires_in': self.expiration_hours * 3600  # seconds
            }
        except Exception as e:
            logger.error(f"Error creating auth response: {e}")
            return {
                'success': False,
                'error': 'Failed to create authentication response'
            }

    def validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        # Add more validation rules as needed
        return True, "Password is valid"

# Global auth service instance
auth_service = AuthService()

def require_auth(func):
    """Decorator to require authentication for Lambda functions"""
    def wrapper(event, context):
        try:
            # Extract token from Authorization header
            headers = event.get('headers', {})
            auth_header = headers.get('Authorization') or headers.get('authorization')
            
            if not auth_header:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                    },
                    'body': json.dumps({'error': 'Authorization header required'})
                }
            
            token = auth_service.extract_token_from_header(auth_header)
            if not token:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                    },
                    'body': json.dumps({'error': 'Invalid authorization format'})
                }
            
            # Verify token
            is_valid, user_data = auth_service.verify_token(token)
            if not is_valid:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                    },
                    'body': json.dumps({'error': 'Invalid or expired token'})
                }
            
            # Add user data to event
            event['user'] = user_data
            
            # Call the original function
            return func(event, context)
            
        except Exception as e:
            logger.error(f"Auth decorator error: {e}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({'error': 'Internal server error'})
            }
    
    return wrapper

def require_admin(func):
    """Decorator to require admin role"""
    @require_auth
    def wrapper(event, context):
        user = event.get('user', {})
        if user.get('role') != 'admin':
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({'error': 'Admin access required'})
            }
        
        return func(event, context)
    
    return wrapper

