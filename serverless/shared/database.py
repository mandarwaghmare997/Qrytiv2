"""
DynamoDB Database Layer for Qrytiv2 Serverless
Handles all database operations with DynamoDB

Developed by: Qryti Dev Team
"""

import boto3
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DynamoDBClient:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.users_table = self.dynamodb.Table('qryti-users')
        self.clients_table = self.dynamodb.Table('qryti-clients')
        self.models_table = self.dynamodb.Table('qryti-models')
        self.reports_table = self.dynamodb.Table('qryti-reports')

    def _serialize_item(self, item: Dict) -> Dict:
        """Convert Python types to DynamoDB compatible types"""
        if isinstance(item, dict):
            return {k: self._serialize_item(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [self._serialize_item(i) for i in item]
        elif isinstance(item, float):
            return Decimal(str(item))
        elif isinstance(item, datetime):
            return item.isoformat()
        return item

    def _deserialize_item(self, item: Dict) -> Dict:
        """Convert DynamoDB types to Python types"""
        if isinstance(item, dict):
            return {k: self._deserialize_item(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [self._deserialize_item(i) for i in item]
        elif isinstance(item, Decimal):
            return float(item)
        return item

    # User Operations
    def create_user(self, email: str, password_hash: str, full_name: str, 
                   organization: str, role: str = 'user') -> Dict:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        user_data = {
            'PK': f'USER#{user_id}',
            'SK': 'PROFILE',
            'user_id': user_id,
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'organization': organization,
            'role': role,
            'is_active': True,
            'created_at': now,
            'last_login': None
        }
        
        try:
            self.users_table.put_item(Item=self._serialize_item(user_data))
            return self._deserialize_item(user_data)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            response = self.users_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            items = response.get('Items', [])
            return self._deserialize_item(items[0]) if items else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            response = self.users_table.get_item(
                Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'}
            )
            item = response.get('Item')
            return self._deserialize_item(item) if item else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            now = datetime.now(timezone.utc).isoformat()
            self.users_table.update_item(
                Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'},
                UpdateExpression='SET last_login = :timestamp',
                ExpressionAttributeValues={':timestamp': now}
            )
            return True
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False

    # Client Operations
    def create_client(self, name: str, description: str, contact_email: str, 
                     contact_phone: str) -> Dict:
        """Create a new client"""
        client_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        client_data = {
            'PK': f'CLIENT#{client_id}',
            'SK': 'DETAILS',
            'client_id': client_id,
            'name': name,
            'description': description,
            'contact_email': contact_email,
            'contact_phone': contact_phone,
            'is_active': True,
            'created_at': now
        }
        
        try:
            self.clients_table.put_item(Item=self._serialize_item(client_data))
            return self._deserialize_item(client_data)
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            raise

    def get_all_clients(self) -> List[Dict]:
        """Get all active clients"""
        try:
            response = self.clients_table.scan(
                FilterExpression='is_active = :active',
                ExpressionAttributeValues={':active': True}
            )
            items = response.get('Items', [])
            return [self._deserialize_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting clients: {e}")
            return []

    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        """Get client by ID"""
        try:
            response = self.clients_table.get_item(
                Key={'PK': f'CLIENT#{client_id}', 'SK': 'DETAILS'}
            )
            item = response.get('Item')
            return self._deserialize_item(item) if item else None
        except Exception as e:
            logger.error(f"Error getting client by ID: {e}")
            return None

    # AI Model Operations
    def create_model(self, name: str, version: str, client_id: str, model_type: str,
                    risk_level: str, framework: str = None, algorithm: str = None,
                    description: str = None, business_purpose: str = None,
                    monitoring_enabled: bool = False) -> Dict:
        """Create a new AI model"""
        model_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        model_data = {
            'PK': f'MODEL#{model_id}',
            'SK': 'DETAILS',
            'model_id': model_id,
            'name': name,
            'version': version,
            'client_id': client_id,
            'type': model_type,
            'risk_level': risk_level,
            'framework': framework,
            'algorithm': algorithm,
            'description': description,
            'business_purpose': business_purpose,
            'monitoring_enabled': monitoring_enabled,
            'created_at': now,
            'status': 'active'
        }
        
        try:
            self.models_table.put_item(Item=self._serialize_item(model_data))
            return self._deserialize_item(model_data)
        except Exception as e:
            logger.error(f"Error creating model: {e}")
            raise

    def get_models_by_client(self, client_id: str) -> List[Dict]:
        """Get all models for a client"""
        try:
            response = self.models_table.scan(
                FilterExpression='client_id = :client_id AND #status = :status',
                ExpressionAttributeValues={
                    ':client_id': client_id,
                    ':status': 'active'
                },
                ExpressionAttributeNames={'#status': 'status'}
            )
            items = response.get('Items', [])
            return [self._deserialize_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting models by client: {e}")
            return []

    def get_all_models(self) -> List[Dict]:
        """Get all active models"""
        try:
            response = self.models_table.scan(
                FilterExpression='#status = :status',
                ExpressionAttributeValues={':status': 'active'},
                ExpressionAttributeNames={'#status': 'status'}
            )
            items = response.get('Items', [])
            return [self._deserialize_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting all models: {e}")
            return []

    # Report Operations
    def create_report(self, user_id: str, report_type: str, title: str, 
                     s3_key: str = None) -> Dict:
        """Create a new report record"""
        report_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        report_data = {
            'PK': f'REPORT#{report_id}',
            'SK': 'METADATA',
            'report_id': report_id,
            'user_id': user_id,
            'type': report_type,
            'title': title,
            's3_key': s3_key,
            'status': 'generated',
            'created_at': now
        }
        
        try:
            self.reports_table.put_item(Item=self._serialize_item(report_data))
            return self._deserialize_item(report_data)
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            raise

    def get_reports_by_user(self, user_id: str) -> List[Dict]:
        """Get all reports for a user"""
        try:
            response = self.reports_table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            items = response.get('Items', [])
            return [self._deserialize_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting reports by user: {e}")
            return []

# Global database instance
db = DynamoDBClient()

# Initialize demo data
def init_demo_data():
    """Initialize demo data for development"""
    try:
        # Check if demo clients already exist
        existing_clients = db.get_all_clients()
        if len(existing_clients) >= 3:
            logger.info("Demo data already exists")
            return

        # Create demo clients
        demo_clients = [
            {
                'name': 'Acme Corporation',
                'description': 'Large enterprise client focusing on AI governance',
                'contact_email': 'contact@acme.com',
                'contact_phone': '+1-555-0123'
            },
            {
                'name': 'TechStart Inc',
                'description': 'Startup company implementing AI compliance',
                'contact_email': 'hello@techstart.com',
                'contact_phone': '+1-555-0456'
            },
            {
                'name': 'Global Industries',
                'description': 'Multinational corporation with AI initiatives',
                'contact_email': 'info@globalind.com',
                'contact_phone': '+1-555-0789'
            }
        ]

        for client_data in demo_clients:
            db.create_client(**client_data)
            logger.info(f"Created demo client: {client_data['name']}")

    except Exception as e:
        logger.error(f"Error initializing demo data: {e}")

