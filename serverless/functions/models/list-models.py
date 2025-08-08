"""
List AI Models Lambda Function
Returns AI models with optional filtering

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
from utils import lambda_handler_wrapper, success_response, error_response, get_query_parameter

@require_auth
@lambda_handler_wrapper
def lambda_handler(event, context):
    """Get AI models with optional filtering"""
    try:
        user = event['user']
        
        # Get query parameters
        client_id = get_query_parameter(event, 'client_id')
        risk_level = get_query_parameter(event, 'risk_level')
        model_type = get_query_parameter(event, 'type')
        
        # Get models based on filters
        if client_id:
            models = db.get_models_by_client(client_id)
        else:
            models = db.get_all_models()
        
        # Apply additional filters
        if risk_level:
            models = [m for m in models if m.get('risk_level') == risk_level]
        
        if model_type:
            models = [m for m in models if m.get('type') == model_type]
        
        # Get client information for each model
        clients = db.get_all_clients()
        clients_dict = {client['client_id']: client for client in clients}
        
        # Format response data
        model_list = []
        for model in models:
            client_info = clients_dict.get(model.get('client_id'), {})
            
            model_data = {
                'model_id': model['model_id'],
                'name': model['name'],
                'version': model['version'],
                'type': model['type'],
                'risk_level': model['risk_level'],
                'framework': model.get('framework'),
                'algorithm': model.get('algorithm'),
                'description': model.get('description'),
                'business_purpose': model.get('business_purpose'),
                'monitoring_enabled': model.get('monitoring_enabled', False),
                'status': model.get('status', 'active'),
                'created_at': model['created_at'],
                'client': {
                    'client_id': client_info.get('client_id'),
                    'name': client_info.get('name', 'Unknown Client')
                }
            }
            model_list.append(model_data)
        
        # Sort by creation date (newest first)
        model_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Prepare summary statistics
        summary = {
            'total_models': len(model_list),
            'risk_distribution': {},
            'type_distribution': {},
            'monitoring_stats': {
                'enabled': len([m for m in model_list if m['monitoring_enabled']]),
                'disabled': len([m for m in model_list if not m['monitoring_enabled']])
            }
        }
        
        # Calculate risk distribution
        for model in model_list:
            risk = model['risk_level']
            summary['risk_distribution'][risk] = summary['risk_distribution'].get(risk, 0) + 1
        
        # Calculate type distribution
        for model in model_list:
            model_type = model['type']
            summary['type_distribution'][model_type] = summary['type_distribution'].get(model_type, 0) + 1
        
        response_data = {
            'models': model_list,
            'summary': summary,
            'filters_applied': {
                'client_id': client_id,
                'risk_level': risk_level,
                'type': model_type
            }
        }
        
        return success_response(response_data, f"Retrieved {len(model_list)} AI models")
        
    except Exception as e:
        print(f"List models error: {e}")
        return error_response(500, "Internal server error")

# For local testing
if __name__ == "__main__":
    test_event = {
        'httpMethod': 'GET',
        'headers': {
            'Authorization': 'Bearer your-test-token-here'
        },
        'queryStringParameters': {
            'risk_level': 'high'
        },
        'user': {
            'user_id': 'test-user-id',
            'email': 'test@example.com',
            'role': 'user'
        }
    }
    
    class TestContext:
        aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, TestContext())
    print(json.dumps(result, indent=2))

