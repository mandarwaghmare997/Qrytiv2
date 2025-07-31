from src.models.user import db
from datetime import datetime

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')  # draft, in_progress, completed, certified
    overall_score = db.Column(db.Numeric(5, 2), default=0.0)
    target_certification = db.Column(db.String(100), default='ISO 42001')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_completion_date = db.Column(db.DateTime)
    actual_completion_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='assessments')
    creator = db.relationship('User', foreign_keys=[created_by])
    stages = db.relationship('AssessmentStage', back_populates='assessment')
    
    def calculate_overall_score(self):
        """Calculate overall assessment score based on stage scores"""
        if not self.stages:
            return 0.0
        
        total_score = sum(stage.score for stage in self.stages if not stage.is_skipped)
        completed_stages = len([stage for stage in self.stages if not

