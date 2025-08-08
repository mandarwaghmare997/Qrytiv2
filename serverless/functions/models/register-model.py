"""
AI Model Registration Lambda Function
Handles registration of new AI models

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
from utils import lambda_handler_wrapper, parse_json_body, validation_error_response, success_response, error_response, validate_required_fields, sanitize_string

@require_auth
@lambda_handler_wrapper
def lambda_handler(event, context):
    """Register a new AI model"""
    try:
        # Parse request body
        body = parse_json_body(event)
        
        # Validate required fields
        required_fields = ['name', 'version', 'client_id', 'type', 'risk_level']
        validation_errors = validate_required_fields(body, required_fields)
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Extract and sanitize data
        name = sanitize_string(body['name'])
        version = sanitize_string(body['version'])
        client_id = body['client_id']
        model_type = sanitize_string(body['type'])
        risk_level = body['risk_level']
        
        # Optional fields
        framework = sanitize_string(body.get('framework', '')) if body.get('framework') else None
        algorithm = sanitize_string(body.get('algorithm', '')) if body.get('algorithm') else None
        description = sanitize_string(body.get('description', '')) if body.get('description') else None
        business_purpose = sanitize_string(body.get('business_purpose', '')) if body.get('business_purpose') else None
        monitoring_enabled = body.get('monitoring_enabled', False)
        
        # Validate risk level
        valid_risk_levels = ['low', 'medium', 'high', 'critical']
        if risk_level not in valid_risk_levels:
            validation_errors['risk_level'] = f"Risk level must be one of: {', '.join(valid_risk_levels)}"
        
        # Validate model type
        valid_types = ['classification', 'regression', 'clustering', 'nlp', 'computer_vision', 'recommendation', 'other']
        if model_type not in valid_types:
            validation_errors['type'] = f"Model type must be one of: {', '.join(valid_types)}"
        
        # Validate name length
        if len(name) < 2:
            validation_errors['name'] = "Model name must be at least 2 characters"
        
        if len(version) < 1:
            validation_errors['version'] = "Version is required"
        
        # Return validation errors if any
        if validation_errors:
            return validation_error_response(validation_errors)
        
        # Verify client exists
        client = db.get_client_by_id(client_id)
        if not client:
            return error_response(404, "Client not found")
        
        # Create model in database
        model_data = db.create_model(
            name=name,
            version=version,
            client_id=client_id,
            model_type=model_type,
            risk_level=risk_level,
            framework=framework,
            algorithm=algorithm,
            description=description,
            business_purpose=business_purpose,
            monitoring_enabled=monitoring_enabled
        )
        
        # Format response
        response_data = {
            'model_id': model_data['model_id'],
            'name': model_data['name'],
            'version': model_data['version'],
            'client': {
                'client_id': client['client_id'],
                'name': client['name']
            },
            'type': model_data['type'],
            'risk_level': model_data['risk_level'],
            'framework': model_data['framework'],
            'algorithm': model_data['algorithm'],
            'description': model_data['description'],
            'business_purpose': model_data['business_purpose'],
            'monitoring_enabled': model_data['monitoring_enabled'],
            'created_at': model_data['created_at'],
            'status': model_data['status']
        }
        
        return success_response(response_data, "AI model registered successfully")
        
    except Exception as e:
        print(f"Model registration error: {e}")
        return error_response(500, "Internal server error")

# For local testing
if __name__ == "__main__":
    test_event = {
        'httpMethod': 'POST',
        'headers': {
            'Authorization': 'Bearer your-test-token-here'
        },
        'body': json.dumps({
            'name': 'Customer Sentiment Analyzer',
            'version': '1.0.0',
            'client_id': 'client-123',
            'type': 'nlp',
            'risk_level': 'medium',
            'framework': 'TensorFlow',
            'algorithm': 'BERT',
            'description': 'Analyzes customer sentiment from reviews',
            'business_purpose': 'Improve customer satisfaction',
            'monitoring_enabled': True
        })
    }
    
    class TestContext:
        aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, TestContext())
    print(json.dumps(result, indent=2))

