"""
Login Lambda Function
Handles user authentication and JWT token generation

Developed by: Qryti Dev Team
"""

import json
import sys
import os

# Add shared modules to path
sys.path.append('/opt/python')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from database import db
from auth import auth_service
from utils import lambda_handler_wrapper, parse_json_body, validation_error_response, success_response, error_response, validate_required_fields

@lambda_handler_wrapper
def lambda_handler(event, context):
    """Handle user login"""
    try:
        # Parse request body
        body = parse_json_body(event)
        
        # Validate required fields
        required_fields = ['email', 'password']
        validation_errors = validate_required_fields(body, required_fields)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        email = body['email'].lower().strip()
        password = body['password']
        
        # Validate email format
        if not auth_service.validate_email(email):
            return error_response(400, "Invalid email format")
        
        # Get user from database
        user = db.get_user_by_email(email)
        if not user:
            return error_response(401, "Invalid email or password")
        
        # Check if user is active
        if not user.get('is_active', True):
            return error_response(401, "Account is deactivated")
        
        # Verify password
        if not auth_service.verify_password(password, user['password_hash']):
            return error_response(401, "Invalid email or password")
        
        # Update last login
        db.update_user_last_login(user['user_id'])
        
        # Create authentication response
        auth_response = auth_service.create_auth_response(user)
        
        if not auth_response['success']:
            return error_response(500, "Failed to create authentication token")
        
        return success_response(auth_response, "Login successful")
        
    except Exception as e:
        print(f"Login error: {e}")
        return error_response(500, "Internal server error")

# For local testing
if __name__ == "__main__":
    test_event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'email': 'user@demo.qryti.com',
            'password': 'demo123'
        })
    }
    
    class TestContext:
        aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, TestContext())
    print(json.dumps(result, indent=2))

