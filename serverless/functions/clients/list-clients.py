"""
List Clients Lambda Function
Returns all active clients

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
from utils import lambda_handler_wrapper, success_response, error_response

@require_auth
@lambda_handler_wrapper
def lambda_handler(event, context):
    """Get all active clients"""
    try:
        # Get all clients from database
        clients = db.get_all_clients()
        
        # Format response data
        client_list = []
        for client in clients:
            client_list.append({
                'client_id': client['client_id'],
                'name': client['name'],
                'description': client['description'],
                'contact_email': client['contact_email'],
                'contact_phone': client['contact_phone'],
                'created_at': client['created_at']
            })
        
        return success_response(client_list, f"Retrieved {len(client_list)} clients")
        
    except Exception as e:
        print(f"List clients error: {e}")
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

