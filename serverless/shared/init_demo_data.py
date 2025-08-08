"""
Demo Data Initialization for Qrytiv2 Serverless
Creates demo users, clients, and models for development and testing

Developed by: Qryti Dev Team
"""

import sys
import os
from datetime import datetime, timezone

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from database import db
from auth import auth_service

def init_demo_users():
    """Initialize demo users"""
    demo_users = [
        {
            'email': 'hello@qryti.com',
            'password': 'Mandar@123',
            'full_name': 'Qryti Admin',
            'organization': 'Qryti Technologies',
            'role': 'admin'
        },
        {
            'email': 'user@demo.qryti.com',
            'password': 'demo123',
            'full_name': 'Demo User',
            'organization': 'Demo Organization',
            'role': 'user'
        },
        {
            'email': 'admin@demo.qryti.com',
            'password': 'admin123',
            'full_name': 'Demo Admin',
            'organization': 'Demo Corporation',
            'role': 'admin'
        },
        {
            'email': 'manager@qryti.com',
            'password': 'manager123',
            'full_name': 'AI Manager',
            'organization': 'Enterprise Corp',
            'role': 'user'
        }
    ]
    
    created_users = []
    for user_data in demo_users:
        try:
            # Check if user already exists
            existing_user = db.get_user_by_email(user_data['email'])
            if existing_user:
                print(f"User {user_data['email']} already exists")
                created_users.append(existing_user)
                continue
            
            # Hash password
            password_hash = auth_service.hash_password(user_data['password'])
            
            # Create user
            user = db.create_user(
                email=user_data['email'],
                password_hash=password_hash,
                full_name=user_data['full_name'],
                organization=user_data['organization'],
                role=user_data['role']
            )
            
            created_users.append(user)
            print(f"Created demo user: {user_data['email']}")
            
        except Exception as e:
            print(f"Error creating user {user_data['email']}: {e}")
    
    return created_users

def init_demo_clients():
    """Initialize demo clients"""
    demo_clients = [
        {
            'name': 'Acme Corporation',
            'description': 'Large enterprise client focusing on AI governance and compliance',
            'contact_email': 'contact@acme.com',
            'contact_phone': '+1-555-0123'
        },
        {
            'name': 'TechStart Inc',
            'description': 'Innovative startup company implementing AI compliance frameworks',
            'contact_email': 'hello@techstart.com',
            'contact_phone': '+1-555-0456'
        },
        {
            'name': 'Global Industries',
            'description': 'Multinational corporation with diverse AI initiatives across sectors',
            'contact_email': 'info@globalind.com',
            'contact_phone': '+1-555-0789'
        },
        {
            'name': 'FinTech Solutions',
            'description': 'Financial technology company specializing in AI-driven analytics',
            'contact_email': 'support@fintech.com',
            'contact_phone': '+1-555-0321'
        },
        {
            'name': 'Healthcare AI Labs',
            'description': 'Medical research organization developing AI diagnostic tools',
            'contact_email': 'research@healthai.com',
            'contact_phone': '+1-555-0654'
        }
    ]
    
    created_clients = []
    for client_data in demo_clients:
        try:
            # Check if client already exists (by name)
            existing_clients = db.get_all_clients()
            if any(c['name'] == client_data['name'] for c in existing_clients):
                print(f"Client {client_data['name']} already exists")
                continue
            
            client = db.create_client(**client_data)
            created_clients.append(client)
            print(f"Created demo client: {client_data['name']}")
            
        except Exception as e:
            print(f"Error creating client {client_data['name']}: {e}")
    
    return created_clients

def init_demo_models(clients):
    """Initialize demo AI models"""
    if not clients:
        print("No clients available for creating demo models")
        return []
    
    demo_models = [
        {
            'name': 'Customer Sentiment Analyzer',
            'version': '2.1.0',
            'client_id': clients[0]['client_id'],  # Acme Corporation
            'model_type': 'nlp',
            'risk_level': 'medium',
            'framework': 'TensorFlow',
            'algorithm': 'BERT',
            'description': 'Advanced NLP model for analyzing customer sentiment from reviews and feedback',
            'business_purpose': 'Improve customer satisfaction and product development',
            'monitoring_enabled': True
        },
        {
            'name': 'Fraud Detection System',
            'version': '1.5.2',
            'client_id': clients[1]['client_id'],  # TechStart Inc
            'model_type': 'classification',
            'risk_level': 'high',
            'framework': 'PyTorch',
            'algorithm': 'Random Forest',
            'description': 'Machine learning model for detecting fraudulent transactions in real-time',
            'business_purpose': 'Prevent financial fraud and protect customer assets',
            'monitoring_enabled': True
        },
        {
            'name': 'Demand Forecasting Model',
            'version': '3.0.1',
            'client_id': clients[2]['client_id'],  # Global Industries
            'model_type': 'regression',
            'risk_level': 'low',
            'framework': 'Scikit-learn',
            'algorithm': 'Linear Regression',
            'description': 'Predictive model for forecasting product demand across multiple markets',
            'business_purpose': 'Optimize inventory management and supply chain operations',
            'monitoring_enabled': False
        },
        {
            'name': 'Image Recognition API',
            'version': '1.0.0',
            'client_id': clients[0]['client_id'],  # Acme Corporation
            'model_type': 'computer_vision',
            'risk_level': 'medium',
            'framework': 'TensorFlow',
            'algorithm': 'CNN',
            'description': 'Computer vision model for automated image classification and object detection',
            'business_purpose': 'Automate quality control processes in manufacturing',
            'monitoring_enabled': True
        },
        {
            'name': 'Recommendation Engine',
            'version': '2.3.0',
            'client_id': clients[1]['client_id'],  # TechStart Inc
            'model_type': 'recommendation',
            'risk_level': 'low',
            'framework': 'Apache Spark',
            'algorithm': 'Collaborative Filtering',
            'description': 'Personalized recommendation system for e-commerce platform',
            'business_purpose': 'Increase customer engagement and sales conversion',
            'monitoring_enabled': False
        },
        {
            'name': 'Risk Assessment Model',
            'version': '1.2.0',
            'client_id': clients[2]['client_id'],  # Global Industries
            'model_type': 'classification',
            'risk_level': 'critical',
            'framework': 'XGBoost',
            'algorithm': 'Gradient Boosting',
            'description': 'Advanced risk assessment model for financial portfolio management',
            'business_purpose': 'Minimize investment risks and optimize portfolio performance',
            'monitoring_enabled': True
        }
    ]
    
    created_models = []
    for model_data in demo_models:
        try:
            model = db.create_model(
                name=model_data['name'],
                version=model_data['version'],
                client_id=model_data['client_id'],
                model_type=model_data['model_type'],
                risk_level=model_data['risk_level'],
                framework=model_data['framework'],
                algorithm=model_data['algorithm'],
                description=model_data['description'],
                business_purpose=model_data['business_purpose'],
                monitoring_enabled=model_data['monitoring_enabled']
            )
            
            created_models.append(model)
            print(f"Created demo model: {model_data['name']}")
            
        except Exception as e:
            print(f"Error creating model {model_data['name']}: {e}")
    
    return created_models

def initialize_all_demo_data():
    """Initialize all demo data"""
    print("Initializing demo data for Qrytiv2...")
    
    try:
        # Initialize users
        print("\n1. Creating demo users...")
        users = init_demo_users()
        print(f"Created {len(users)} users")
        
        # Initialize clients
        print("\n2. Creating demo clients...")
        clients = init_demo_clients()
        print(f"Created {len(clients)} clients")
        
        # Initialize models
        print("\n3. Creating demo AI models...")
        models = init_demo_models(clients)
        print(f"Created {len(models)} models")
        
        print(f"\n✅ Demo data initialization complete!")
        print(f"Summary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Clients: {len(clients)}")
        print(f"  - AI Models: {len(models)}")
        
        return {
            'users': users,
            'clients': clients,
            'models': models
        }
        
    except Exception as e:
        print(f"Error during demo data initialization: {e}")
        return None

# Lambda function for initializing demo data
def lambda_handler(event, context):
    """Lambda function to initialize demo data"""
    try:
        result = initialize_all_demo_data()
        
        if result:
            return {
                'statusCode': 200,
                'body': {
                    'success': True,
                    'message': 'Demo data initialized successfully',
                    'summary': {
                        'users': len(result['users']),
                        'clients': len(result['clients']),
                        'models': len(result['models'])
                    }
                }
            }
        else:
            return {
                'statusCode': 500,
                'body': {
                    'success': False,
                    'message': 'Failed to initialize demo data'
                }
            }
            
    except Exception as e:
        print(f"Lambda error: {e}")
        return {
            'statusCode': 500,
            'body': {
                'success': False,
                'message': f'Error: {str(e)}'
            }
        }

# For local testing
if __name__ == "__main__":
    initialize_all_demo_data()

