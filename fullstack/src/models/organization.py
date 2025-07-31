from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import db from a separate module to avoid circular imports
db = None

def init_db(database):
    global db
    db = database

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    country = db.Column(db.String(100))
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'industry': self.industry,
            'size': self.size,
            'country': self.country,
            'description': self.description,
            'website': self.website,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

