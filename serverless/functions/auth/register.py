"""
Registration Lambda Function
Handles user registration and welcome email sending

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
from email_service import email_service
from utils import lambda_handler_wrapper, parse_json_body, validation_error_response, success_response, error_response, validate_required_fields, sanitize_string

@lambda_handler_wrapper
def lambda_handler(event, context):
    """Handle user registration"""
    try:
        # Parse request body
        body = parse_json_body(event)
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'organization_name']
        validation_errors = validate_required_fields(body, required_fields)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        email = body['email'].lower().strip()
        password = body['password']
        full_name = sanitize_string(body['full_name'])
        organization_name = sanitize_string(body['organization_name'])
        role = body.get('role', 'user')
        
        # Validate email format
        if not auth_service.validate_email(email):
            validation_errors['email'] = "Invalid email format"
        
        # Validate password strength
        is_valid_password, password_message = auth_service.validate_password(password)
        if not is_valid_password:
            validation_errors['password'] = password_message
        
        # Validate name length
        if len(full_name) < 2:
            validation_errors['full_name'] = "Full name must be at least 2 characters"
        
        if len(organization_name) < 2:
            validation_errors['organization_name'] = "Organization name must be at least 2 characters"
        
        # Return validation errors if any
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            return error_response(409, "User with this email already exists")
        
        # Hash password
        password_hash = auth_service.hash_password(password)
        
        # Create user in database
        user_data = db.create_user(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            organization=organization_name,
            role=role
        )
        
        # Send welcome email (async, don't fail registration if email fails)
        email_status = "sent"
        try:
            email_success = email_service.send_welcome_email(
                email, 
                full_name, 
                organization_name
            )
            if not email_success:
                email_status = "failed"
        except Exception as e:
            print(f"Email sending error: {e}")
            email_status = "failed"
        
        # Create authentication response
        auth_response = auth_service.create_auth_response(user_data)
        
        if not auth_response['success']:
            return error_response(500, "User created but failed to generate authentication token")
        
        # Add email status to response
        auth_response['email_status'] = email_status
        
        return success_response(auth_response, "Registration successful. Welcome to Qryti!")
        
    except Exception as e:
        print(f"Registration error: {e}")
        return error_response(500, "Internal server error")

# For local testing
if __name__ == "__main__":
    test_event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'email': 'newuser@example.com',
            'password': 'password123',
            'full_name': 'New User',
            'organization_name': 'Test Organization'
        })
    }
    
    class TestContext:
        aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, TestContext())
    print(json.dumps(result, indent=2))

