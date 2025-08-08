"""
Database models for Qrytiv2 application
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profile management"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, email, password, full_name, organization=None, role='user'):
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.organization = organization
        self.role = role
    
    def set_password(self, password):
        """Hash and set password"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'organization': self.organization,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class Client(db.Model):
    """Client model for project management"""
    
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with projects
    projects = db.relationship('Project', backref='client', lazy=True)
    
    def to_dict(self):
        """Convert client to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Client {self.name}>'

class Project(db.Model):
    """Project model for tracking compliance projects"""
    
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_projects')
    
    def to_dict(self):
        """Convert project to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'client_id': self.client_id,
            'client_name': self.client.name if self.client else None,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Project {self.name}>'

def init_database(app):
    """Initialize database with demo data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if demo users already exist
        if User.query.count() == 0:
            # Create demo users
            demo_users = [
                User(
                    email="hello@qryti.com",
                    password="Mandar@123",
                    full_name="Qryti Admin",
                    organization="Qryti",
                    role="admin"
                ),
                User(
                    email="admin@demo.qryti.com",
                    password="admin123",
                    full_name="Admin User",
                    organization="Qryti Demo Organization",
                    role="admin"
                ),
                User(
                    email="user@demo.qryti.com",
                    password="demo123",
                    full_name="Demo User",
                    organization="Qryti Demo Organization",
                    role="user"
                )
            ]
            
            for user in demo_users:
                db.session.add(user)
            
            db.session.commit()
            print("Demo users created successfully")
        
        # Check if demo clients already exist
        if Client.query.count() == 0:
            # Create demo clients
            demo_clients = [
                Client(
                    name="Acme Corporation",
                    description="Large enterprise client focusing on AI governance",
                    contact_email="contact@acme.com",
                    contact_phone="+1-555-0123"
                ),
                Client(
                    name="TechStart Inc",
                    description="Startup company implementing AI compliance",
                    contact_email="hello@techstart.com",
                    contact_phone="+1-555-0456"
                ),
                Client(
                    name="Global Industries",
                    description="Multinational corporation with AI initiatives",
                    contact_email="info@globalind.com",
                    contact_phone="+1-555-0789"
                )
            ]
            
            for client in demo_clients:
                db.session.add(client)
            
            db.session.commit()
            print("Demo clients created successfully")

