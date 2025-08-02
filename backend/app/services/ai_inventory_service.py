# AI Inventory Management Service
# Comprehensive service for managing AI models and their lifecycle

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import logging

from ..models.ai_model import AIModel, ModelType, RiskLevel, ModelStatus, ComplianceStatus
from ..models.requirement import RequirementAssessment, ComplianceLevel
from ..models.organization import Organization
from ..models.user import User

logger = logging.getLogger(__name__)

class AIInventoryService:
    """Service for managing AI model inventory and lifecycle"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_ai_model(self, model_data: Dict[str, Any], user_id: int) -> AIModel:
        """Create a new AI model in the inventory"""
        try:
            # Get user's organization
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Create AI model
            ai_model = AIModel(
                name=model_data.get('name'),
                description=model_data.get('description'),
                version=model_data.get('version', '1.0.0'),
                model_type=ModelType(model_data.get('model_type', 'machine_learning')),
                framework=model_data.get('framework'),
                algorithm=model_data.get('algorithm'),
                input_data_types=json.dumps(model_data.get('input_data_types', [])),
                output_data_types=json.dumps(model_data.get('output_data_types', [])),
                status=ModelStatus(model_data.get('status', 'development')),
                business_purpose=model_data.get('business_purpose'),
                stakeholders=json.dumps(model_data.get('stakeholders', [])),
                training_data_source=model_data.get('training_data_source'),
                data_classification=model_data.get('data_classification', 'Internal'),
                organization_id=user.organization_id,
                created_by=user_id
            )
            
            # Calculate initial risk assessment
            ai_model = self._calculate_risk_assessment(ai_model, model_data)
            
            self.db.add(ai_model)
            self.db.commit()
            self.db.refresh(ai_model)
            
            logger.info(f"Created AI model: {ai_model.name} (ID: {ai_model.id})")
            return ai_model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating AI model: {str(e)}")
            raise
    
    def get_ai_models(self, organization_id: int, filters: Optional[Dict] = None) -> List[AIModel]:
        """Get AI models for an organization with optional filters"""
        query = self.db.query(AIModel).filter(AIModel.organization_id == organization_id)
        
        if filters:
            if 'status' in filters:
                query = query.filter(AIModel.status == ModelStatus(filters['status']))
            if 'model_type' in filters:
                query = query.filter(AIModel.model_type == ModelType(filters['model_type']))
            if 'risk_level' in filters:
                query = query.filter(AIModel.risk_level == RiskLevel(filters['risk_level']))
            if 'compliance_status' in filters:
                query = query.filter(AIModel.compliance_status == ComplianceStatus(filters['compliance_status']))
        
        return query.all()
    
    def get_ai_model(self, model_id: int, organization_id: int) -> Optional[AIModel]:
        """Get a specific AI model"""
        return self.db.query(AIModel).filter(
            AIModel.id == model_id,
            AIModel.organization_id == organization_id
        ).first()
    
    def update_ai_model(self, model_id: int, model_data: Dict[str, Any], user_id: int) -> AIModel:
        """Update an AI model"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            ai_model = self.db.query(AIModel).filter(
                AIModel.id == model_id,
                AIModel.organization_id == user.organization_id
            ).first()
            
            if not ai_model:
                raise ValueError("AI model not found")
            
            # Update fields
            for field, value in model_data.items():
                if hasattr(ai_model, field) and field not in ['id', 'created_date', 'organization_id', 'created_by']:
                    if field == 'model_type' and value:
                        setattr(ai_model, field, ModelType(value))
                    elif field == 'status' and value:
                        setattr(ai_model, field, ModelStatus(value))
                    elif field == 'risk_level' and value:
                        setattr(ai_model, field, RiskLevel(value))
                    elif field == 'compliance_status' and value:
                        setattr(ai_model, field, ComplianceStatus(value))
                    elif field in ['input_data_types', 'output_data_types', 'stakeholders'] and isinstance(value, list):
                        setattr(ai_model, field, json.dumps(value))
                    else:
                        setattr(ai_model, field, value)
            
            # Recalculate risk assessment if relevant fields changed
            ai_model = self._calculate_risk_assessment(ai_model, model_data)
            
            ai_model.last_updated = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(ai_model)
            
            logger.info(f"Updated AI model: {ai_model.name} (ID: {ai_model.id})")
            return ai_model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating AI model: {str(e)}")
            raise
    
    def delete_ai_model(self, model_id: int, organization_id: int) -> bool:
        """Delete an AI model"""
        try:
            ai_model = self.db.query(AIModel).filter(
                AIModel.id == model_id,
                AIModel.organization_id == organization_id
            ).first()
            
            if not ai_model:
                return False
            
            self.db.delete(ai_model)
            self.db.commit()
            
            logger.info(f"Deleted AI model: {ai_model.name} (ID: {ai_model.id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting AI model: {str(e)}")
            raise
    
    def get_inventory_summary(self, organization_id: int) -> Dict[str, Any]:
        """Get inventory summary statistics"""
        models = self.get_ai_models(organization_id)
        
        summary = {
            'total_models': len(models),
            'by_status': {},
            'by_type': {},
            'by_risk_level': {},
            'by_compliance_status': {},
            'average_compliance_score': 0.0,
            'models_needing_attention': 0,
            'models_in_production': 0,
            'high_risk_models': 0
        }
        
        if not models:
            return summary
        
        # Calculate statistics
        compliance_scores = []
        for model in models:
            # Status distribution
            status = model.status.value if model.status else 'unknown'
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # Type distribution
            model_type = model.model_type.value if model.model_type else 'unknown'
            summary['by_type'][model_type] = summary['by_type'].get(model_type, 0) + 1
            
            # Risk level distribution
            risk_level = model.risk_level.value if model.risk_level else 'unknown'
            summary['by_risk_level'][risk_level] = summary['by_risk_level'].get(risk_level, 0) + 1
            
            # Compliance status distribution
            compliance_status = model.compliance_status.value if model.compliance_status else 'unknown'
            summary['by_compliance_status'][compliance_status] = summary['by_compliance_status'].get(compliance_status, 0) + 1
            
            # Compliance scores
            if model.compliance_score:
                compliance_scores.append(model.compliance_score)
            
            # Models needing attention (non-compliant or high risk)
            if (model.compliance_status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT] or
                model.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]):
                summary['models_needing_attention'] += 1
            
            # Production models
            if model.status == ModelStatus.PRODUCTION:
                summary['models_in_production'] += 1
            
            # High risk models
            if model.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                summary['high_risk_models'] += 1
        
        # Average compliance score
        if compliance_scores:
            summary['average_compliance_score'] = sum(compliance_scores) / len(compliance_scores)
        
        return summary
    
    def _calculate_risk_assessment(self, ai_model: AIModel, model_data: Dict[str, Any]) -> AIModel:
        """Calculate risk assessment for an AI model"""
        try:
            # Base risk score calculation
            risk_score = 0.0
            
            # Model type risk factors
            type_risk_factors = {
                ModelType.GENERATIVE_AI: 30,
                ModelType.DEEP_LEARNING: 25,
                ModelType.NATURAL_LANGUAGE: 20,
                ModelType.COMPUTER_VISION: 15,
                ModelType.RECOMMENDATION: 15,
                ModelType.PREDICTIVE_ANALYTICS: 10,
                ModelType.MACHINE_LEARNING: 10,
                ModelType.DECISION_SUPPORT: 20,
                ModelType.OTHER: 15
            }
            
            if ai_model.model_type:
                risk_score += type_risk_factors.get(ai_model.model_type, 15)
            
            # Data classification risk
            data_risk_factors = {
                'Restricted': 25,
                'Confidential': 20,
                'Internal': 10,
                'Public': 5
            }
            
            if ai_model.data_classification:
                risk_score += data_risk_factors.get(ai_model.data_classification, 10)
            
            # Status risk (production models have higher risk)
            if ai_model.status == ModelStatus.PRODUCTION:
                risk_score += 20
            elif ai_model.status == ModelStatus.STAGING:
                risk_score += 10
            
            # Business purpose risk (customer-facing models have higher risk)
            if ai_model.business_purpose and any(keyword in ai_model.business_purpose.lower() 
                                               for keyword in ['customer', 'public', 'external', 'user-facing']):
                risk_score += 15
            
            # Calculate individual risk components
            ai_model.bias_risk = min(risk_score * 0.8, 100.0)  # Bias risk
            ai_model.privacy_risk = min(risk_score * 0.9, 100.0)  # Privacy risk
            ai_model.security_risk = min(risk_score * 0.7, 100.0)  # Security risk
            
            # Overall risk score
            ai_model.risk_score = min(risk_score, 100.0)
            
            # Determine risk level
            if ai_model.risk_score >= 80:
                ai_model.risk_level = RiskLevel.CRITICAL
            elif ai_model.risk_score >= 60:
                ai_model.risk_level = RiskLevel.HIGH
            elif ai_model.risk_score >= 40:
                ai_model.risk_level = RiskLevel.MEDIUM
            elif ai_model.risk_score >= 20:
                ai_model.risk_level = RiskLevel.LOW
            else:
                ai_model.risk_level = RiskLevel.MINIMAL
            
            return ai_model
            
        except Exception as e:
            logger.error(f"Error calculating risk assessment: {str(e)}")
            # Set default values if calculation fails
            ai_model.risk_score = 50.0
            ai_model.risk_level = RiskLevel.MEDIUM
            ai_model.bias_risk = 50.0
            ai_model.privacy_risk = 50.0
            ai_model.security_risk = 50.0
            return ai_model
    
    def update_compliance_assessment(self, model_id: int, compliance_data: Dict[str, Any]) -> AIModel:
        """Update compliance assessment for an AI model"""
        try:
            ai_model = self.db.query(AIModel).filter(AIModel.id == model_id).first()
            if not ai_model:
                raise ValueError("AI model not found")
            
            # Update compliance fields
            if 'compliance_score' in compliance_data:
                ai_model.compliance_score = compliance_data['compliance_score']
            
            if 'compliance_status' in compliance_data:
                ai_model.compliance_status = ComplianceStatus(compliance_data['compliance_status'])
            
            if 'last_audit_date' in compliance_data:
                ai_model.last_audit_date = datetime.fromisoformat(compliance_data['last_audit_date'])
            
            if 'next_audit_date' in compliance_data:
                ai_model.next_audit_date = datetime.fromisoformat(compliance_data['next_audit_date'])
            
            ai_model.last_updated = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(ai_model)
            
            return ai_model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating compliance assessment: {str(e)}")
            raise

