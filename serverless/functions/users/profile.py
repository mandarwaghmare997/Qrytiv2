"""
User Profile Lambda Function
Handles getting and updating user profile information

Developed by: Qryti Dev Team
"""

import json
import sys
import os

# Add shared modules to path
sys.path.append('/opt/python')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from database import db
from auth import require_auth
from utils import lambda_handler_wrapper, parse_json_body, validation_error_response, success_response, error_response, sanitize_string

@require_auth
@lambda_handler_wrapper
def lambda_handler(event, context):
    """Handle user profile operations"""
    try:
        user = event['user']
        user_id = user['user_id']
        http_method = event.get('httpMethod', 'GET')
        
        if http_method == 'GET':
            # Get user profile
            user_data = db.get_user_by_id(user_id)
            if not user_data:
                return error_response(404, "User not found")
            
            # Format response (exclude sensitive data)
            profile_data = {
                'user_id': user_data['user_id'],
                'email': user_data['email'],
                'full_name': user_data['full_name'],
                'organization': user_data['organization'],
                'role': user_data['role'],
                'is_active': user_data['is_active'],
                'created_at': user_data['created_at'],
                'last_login': user_data.get('last_login')
            }
            
            return success_response(profile_data, "Profile retrieved successfully")
        
        elif http_method == 'PUT':
            # Update user profile
            body = parse_json_body(event)
            
            # Get current user data
            current_user = db.get_user_by_id(user_id)
            if not current_user:
                return error_response(404, "User not found")
            
            # Validate and sanitize input
            validation_errors = {}
            
            full_name = body.get('full_name')
            organization = body.get('organization')
            
            if full_name is not None:
                full_name = sanitize_string(full_name)
                if len(full_name) < 2:
                    validation_errors['full_name'] = "Full name must be at least 2 characters"
            
            if organization is not None:
                organization = sanitize_string(organization)
                if len(organization) < 2:
                    validation_errors['organization'] = "Organization must be at least 2 characters"
            
            if validation_errors:
                return validation_error_response(validation_errors)
            
            # Update user data
            update_data = {}
            if full_name is not None:
                update_data['full_name'] = full_name
            if organization is not None:
                update_data['organization'] = organization
            
            if not update_data:
                return error_response(400, "No valid fields to update")
            
            # Update in database
            try:
                # For simplicity, we'll recreate the user record with updated data
                # In a real implementation, you'd use DynamoDB's UpdateItem
                updated_user = current_user.copy()
                updated_user.update(update_data)
                
                # This is a simplified update - in production, use proper DynamoDB update operations
                db.users_table.put_item(Item=db._serialize_item(updated_user))
                
                # Format response
                profile_data = {
                    'user_id': updated_user['user_id'],
                    'email': updated_user['email'],
                    'full_name': updated_user['full_name'],
                    'organization': updated_user['organization'],
                    'role': updated_user['role'],
                    'is_active': updated_user['is_active'],
                    'created_at': updated_user['created_at'],
                    'last_login': updated_user.get('last_login')
                }
                
                return success_response(profile_data, "Profile updated successfully")
                
            except Exception as e:
                print(f"Error updating profile: {e}")
                return error_response(500, "Failed to update profile")
        
        else:
            return error_response(405, "Method not allowed")
        
    except Exception as e:
        print(f"Profile error: {e}")
        return error_response(500, "Internal server error")

# For local testing
if __name__ == "__main__":
    # Test GET
    test_event_get = {
        'httpMethod': 'GET',
        'headers': {
            'Authorization': 'Bearer your-test-token-here'
        },
        'user': {
            'user_id': 'test-user-id',
            'email': 'test@example.com',
            'role': 'user'
        }
    }
    
    # Test PUT
    test_event_put = {
        'httpMethod': 'PUT',
        'headers': {
            'Authorization': 'Bearer your-test-token-here'
        },
        'body': json.dumps({
            'full_name': 'Updated Name',
            'organization': 'Updated Organization'
        }),
        'user': {
            'user_id': 'test-user-id',
            'email': 'test@example.com',
            'role': 'user'
        }
    }
    
    class TestContext:
        aws_request_id = 'test-request-id'
    
    print("Testing GET:")
    result = lambda_handler(test_event_get, TestContext())
    print(json.dumps(result, indent=2))
    
    print("\nTesting PUT:")
    result = lambda_handler(test_event_put, TestContext())
    print(json.dumps(result, indent=2))

