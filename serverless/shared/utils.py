"""
Utility Functions for Qrytiv2 Serverless
Common utilities for Lambda functions

Developed by: Qryti Dev Team
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def create_response(status_code: int, body: Dict[str, Any], 
                   headers: Optional[Dict[str, str]] = None) -> Dict:
    """Create a standardized Lambda response"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, default=str)
    }

def success_response(data: Any, message: str = "Success") -> Dict:
    """Create a success response"""
    return create_response(200, {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

def error_response(status_code: int, error: str, details: str = None) -> Dict:
    """Create an error response"""
    body = {
        'success': False,
        'error': error,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    if details:
        body['details'] = details
    
    return create_response(status_code, body)

def validation_error_response(errors: Dict[str, str]) -> Dict:
    """Create a validation error response"""
    return create_response(400, {
        'success': False,
        'error': 'Validation failed',
        'validation_errors': errors,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

def handle_cors_preflight(event: Dict) -> Optional[Dict]:
    """Handle CORS preflight requests"""
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {}, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Max-Age': '86400'
        })
    return None

def parse_json_body(event: Dict) -> Dict:
    """Parse JSON body from Lambda event"""
    try:
        body = event.get('body', '{}')
        if isinstance(body, str):
            return json.loads(body)
        return body
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in request body")

def get_path_parameter(event: Dict, param_name: str) -> Optional[str]:
    """Get path parameter from Lambda event"""
    path_params = event.get('pathParameters') or {}
    return path_params.get(param_name)

def get_query_parameter(event: Dict, param_name: str, default: str = None) -> Optional[str]:
    """Get query parameter from Lambda event"""
    query_params = event.get('queryStringParameters') or {}
    return query_params.get(param_name, default)

def validate_required_fields(data: Dict, required_fields: list) -> Dict[str, str]:
    """Validate required fields in data"""
    errors = {}
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    return errors

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        return str(value)
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    return value

def format_datetime(dt: datetime) -> str:
    """Format datetime for API responses"""
    if isinstance(dt, str):
        return dt
    return dt.isoformat() if dt else None

def log_lambda_event(event: Dict, context: Any, function_name: str):
    """Log Lambda function invocation"""
    logger.info(f"Lambda function {function_name} invoked")
    logger.info(f"HTTP Method: {event.get('httpMethod')}")
    logger.info(f"Path: {event.get('path')}")
    logger.info(f"Request ID: {context.aws_request_id}")

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, errors: Dict[str, str] = None):
        self.message = message
        self.errors = errors or {}
        super().__init__(self.message)

def lambda_handler_wrapper(func):
    """Decorator to wrap Lambda handlers with common functionality"""
    def wrapper(event, context):
        try:
            # Log the invocation
            log_lambda_event(event, context, func.__name__)
            
            # Handle CORS preflight
            cors_response = handle_cors_preflight(event)
            if cors_response:
                return cors_response
            
            # Call the actual function
            return func(event, context)
            
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {e.message}")
            return validation_error_response(e.errors)
        except ValueError as e:
            logger.warning(f"Value error in {func.__name__}: {e}")
            return error_response(400, str(e))
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return error_response(500, "Internal server error")
    
    return wrapper

# Email validation regex
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email: str) -> bool:
    """Validate email format"""
    return bool(EMAIL_REGEX.match(email))

def generate_presigned_url(bucket: str, key: str, expiration: int = 3600) -> str:
    """Generate presigned URL for S3 object"""
    import boto3
    from botocore.exceptions import ClientError
    
    try:
        s3_client = boto3.client('s3')
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {e}")
        raise

def upload_to_s3(bucket: str, key: str, data: bytes, content_type: str = 'application/octet-stream') -> bool:
    """Upload data to S3"""
    import boto3
    from botocore.exceptions import ClientError
    
    try:
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            ContentType=content_type
        )
        return True
    except ClientError as e:
        logger.error(f"Error uploading to S3: {e}")
        return False

