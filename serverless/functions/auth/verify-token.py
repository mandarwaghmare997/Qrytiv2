"""
Token Verification Lambda Function
Verifies JWT tokens and returns user information

Developed by: Qryti Dev Team
"""

import json
import sys
import os

# Add shared modules to path
sys.path.append('/opt/python')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from auth import auth_service
from utils import lambda_handler_wrapper, success_response, error_response

@lambda_handler_wrapper
def lambda_handler(event, context):
    """Verify JWT token and return user information"""
    try:
        # Extract token from Authorization header
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header:
            return error_response(401, "Authorization header required")
        
        token = auth_service.extract_token_from_header(auth_header)
        if not token:
            return error_response(401, "Invalid authorization format")
        
        # Verify token
        is_valid, user_data = auth_service.verify_token(token)
        if not is_valid:
            return error_response(401, "Invalid or expired token")
        
        return success_response({
            'valid': True,
            'user': user_data
        }, "Token is valid")
        
    except Exception as e:
        print(f"Token verification error: {e}")
        return error_response(500, "Internal server error")

# For local testing
if __name__ == "__main__":
    test_event = {
        'httpMethod': 'GET',
        'headers': {
            'Authorization': 'Bearer your-test-token-here'
        }
    }
    
    class TestContext:
        aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, TestContext())
    print(json.dumps(result, indent=2))

