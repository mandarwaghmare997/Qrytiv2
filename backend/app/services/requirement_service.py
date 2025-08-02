# Requirements Management Service
# Service for managing ISO 42001 requirements and assessments

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import logging

from ..models.requirement import (
    Requirement, RequirementAssessment, GapAnalysis,
    RequirementCategory, RequirementType, AssessmentStatus, ComplianceLevel
)
from ..models.ai_model import AIModel
from ..models.organization import Organization
from ..models.user import User

logger = logging.getLogger(__name__)

class RequirementService:
    """Service for managing ISO 42001 requirements and assessments"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_iso42001_requirements(self) -> List[Requirement]:
        """Initialize the standard ISO 42001 requirements"""
        try:
            # Check if requirements already exist
            existing_count = self.db.query(Requirement).count()
            if existing_count > 0:
                logger.info("ISO 42001 requirements already initialized")
                return self.db.query(Requirement).all()
            
            # ISO 42001 requirements structure
            requirements_data = [
                # Context of the Organization (Clause 4)
                {
                    "requirement_id": "4.1",
                    "title": "Understanding the organization and its context",
                    "description": "The organization shall determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its AI management system.",
                    "category": RequirementCategory.CONTEXT_ORGANIZATION,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "4.1",
                    "objective": "Establish organizational context for AI management",
                    "guidance": "Consider technological, legal, regulatory, financial, competitive, market, cultural, social and economic environment factors.",
                    "evidence_required": "Documented analysis of internal and external factors affecting AI management"
                },
                {
                    "requirement_id": "4.2",
                    "title": "Understanding the needs and expectations of interested parties",
                    "description": "The organization shall determine the interested parties that are relevant to the AI management system and the relevant requirements of these interested parties.",
                    "category": RequirementCategory.CONTEXT_ORGANIZATION,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "4.2",
                    "objective": "Identify and understand stakeholder requirements",
                    "guidance": "Include customers, regulators, employees, suppliers, and society at large.",
                    "evidence_required": "Stakeholder analysis and requirements documentation"
                },
                {
                    "requirement_id": "4.3",
                    "title": "Determining the scope of the AI management system",
                    "description": "The organization shall determine the boundaries and applicability of the AI management system to establish its scope.",
                    "category": RequirementCategory.CONTEXT_ORGANIZATION,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "4.3",
                    "objective": "Define clear scope and boundaries for AI management",
                    "guidance": "Consider physical locations, organizational units, activities, and AI systems.",
                    "evidence_required": "Documented scope statement with clear boundaries"
                },
                {
                    "requirement_id": "4.4",
                    "title": "AI management system",
                    "description": "The organization shall establish, implement, maintain and continually improve an AI management system, including the processes needed and their interactions.",
                    "category": RequirementCategory.CONTEXT_ORGANIZATION,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "4.4",
                    "objective": "Establish comprehensive AI management system",
                    "guidance": "Include all AI lifecycle processes and their interactions.",
                    "evidence_required": "AI management system documentation and process maps"
                },
                
                # Leadership (Clause 5)
                {
                    "requirement_id": "5.1",
                    "title": "Leadership and commitment",
                    "description": "Top management shall demonstrate leadership and commitment with respect to the AI management system.",
                    "category": RequirementCategory.LEADERSHIP,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "5.1",
                    "objective": "Ensure top management commitment to AI governance",
                    "guidance": "Leadership must actively support and participate in AI governance.",
                    "evidence_required": "Leadership commitment statements and participation records"
                },
                {
                    "requirement_id": "5.2",
                    "title": "AI policy",
                    "description": "Top management shall establish an AI policy that is appropriate to the purpose and context of the organization.",
                    "category": RequirementCategory.LEADERSHIP,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "5.2",
                    "objective": "Establish comprehensive AI policy framework",
                    "guidance": "Policy should address ethical AI use, risk management, and compliance.",
                    "evidence_required": "Approved AI policy document and communication records"
                },
                {
                    "requirement_id": "5.3",
                    "title": "Organizational roles, responsibilities and authorities",
                    "description": "Top management shall ensure that the responsibilities and authorities for relevant roles are assigned and communicated within the organization.",
                    "category": RequirementCategory.LEADERSHIP,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "5.3",
                    "objective": "Define clear AI governance roles and responsibilities",
                    "guidance": "Include AI governance board, AI ethics committee, and operational roles.",
                    "evidence_required": "Role definitions, responsibility matrices, and communication records"
                },
                
                # Planning (Clause 6)
                {
                    "requirement_id": "6.1",
                    "title": "Actions to address risks and opportunities",
                    "description": "When planning for the AI management system, the organization shall consider the issues and requirements and determine the risks and opportunities.",
                    "category": RequirementCategory.PLANNING,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "6.1",
                    "objective": "Identify and address AI-related risks and opportunities",
                    "guidance": "Include technical, ethical, legal, and business risks.",
                    "evidence_required": "Risk and opportunity register with treatment plans"
                },
                {
                    "requirement_id": "6.2",
                    "title": "AI objectives and planning to achieve them",
                    "description": "The organization shall establish AI objectives at relevant functions and levels and plan how to achieve them.",
                    "category": RequirementCategory.PLANNING,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "6.2",
                    "objective": "Set measurable AI objectives and implementation plans",
                    "guidance": "Objectives should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound).",
                    "evidence_required": "AI objectives documentation and implementation plans"
                },
                
                # Support (Clause 7)
                {
                    "requirement_id": "7.1",
                    "title": "Resources",
                    "description": "The organization shall determine and provide the resources needed for the establishment, implementation, maintenance and continual improvement of the AI management system.",
                    "category": RequirementCategory.SUPPORT,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "7.1",
                    "objective": "Ensure adequate resources for AI management",
                    "guidance": "Include human resources, infrastructure, technology, and financial resources.",
                    "evidence_required": "Resource allocation documentation and budget approvals"
                },
                {
                    "requirement_id": "7.2",
                    "title": "Competence",
                    "description": "The organization shall determine the necessary competence of person(s) doing work under its control that affects the performance of the AI management system.",
                    "category": RequirementCategory.SUPPORT,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "7.2",
                    "objective": "Ensure competent personnel for AI management",
                    "guidance": "Include technical, ethical, and governance competencies.",
                    "evidence_required": "Competency frameworks, training records, and assessments"
                },
                {
                    "requirement_id": "7.3",
                    "title": "Awareness",
                    "description": "Persons doing work under the organization's control shall be aware of the AI policy, their contribution to the effectiveness of the AI management system, and the implications of not conforming.",
                    "category": RequirementCategory.SUPPORT,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "7.3",
                    "objective": "Ensure AI awareness across the organization",
                    "guidance": "Include awareness programs and communication strategies.",
                    "evidence_required": "Awareness program documentation and training records"
                },
                {
                    "requirement_id": "7.4",
                    "title": "Communication",
                    "description": "The organization shall determine the internal and external communications relevant to the AI management system.",
                    "category": RequirementCategory.SUPPORT,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "7.4",
                    "objective": "Establish effective AI communication processes",
                    "guidance": "Include stakeholder communication and transparency requirements.",
                    "evidence_required": "Communication plans and stakeholder engagement records"
                },
                {
                    "requirement_id": "7.5",
                    "title": "Documented information",
                    "description": "The AI management system shall include documented information required by this document and determined by the organization as being necessary for the effectiveness of the AI management system.",
                    "category": RequirementCategory.SUPPORT,
                    "requirement_type": RequirementType.MANDATORY,
                    "clause_reference": "7.5",
                    "objective": "Maintain comprehensive AI documentation",
                    "guidance": "Include policies, procedures, records, and technical documentation.",
                    "evidence_required": "Document control procedures and information management systems"
                }
            ]
            
            # Create requirement objects
            requirements = []
            for req_data in requirements_data:
                requirement = Requirement(**req_data)
                self.db.add(requirement)
                requirements.append(requirement)
            
            self.db.commit()
            logger.info(f"Initialized {len(requirements)} ISO 42001 requirements")
            return requirements
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error initializing requirements: {str(e)}")
            raise
    
    def get_requirements(self, filters: Optional[Dict] = None) -> List[Requirement]:
        """Get requirements with optional filters"""
        query = self.db.query(Requirement).filter(Requirement.is_active == True)
        
        if filters:
            if 'category' in filters:
                query = query.filter(Requirement.category == RequirementCategory(filters['category']))
            if 'requirement_type' in filters:
                query = query.filter(Requirement.requirement_type == RequirementType(filters['requirement_type']))
        
        return query.order_by(Requirement.requirement_id).all()
    
    def create_requirement_assessment(self, assessment_data: Dict[str, Any], user_id: int) -> RequirementAssessment:
        """Create a new requirement assessment"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            assessment = RequirementAssessment(
                requirement_id=assessment_data['requirement_id'],
                ai_model_id=assessment_data['ai_model_id'],
                organization_id=user.organization_id,
                compliance_level=ComplianceLevel(assessment_data.get('compliance_level', 'not_applicable')),
                compliance_score=assessment_data.get('compliance_score', 0.0),
                current_state=assessment_data.get('current_state'),
                gap_analysis=assessment_data.get('gap_analysis'),
                evidence_provided=assessment_data.get('evidence_provided'),
                recommendations=assessment_data.get('recommendations'),
                risk_level=assessment_data.get('risk_level', 'medium'),
                risk_description=assessment_data.get('risk_description'),
                mitigation_plan=assessment_data.get('mitigation_plan'),
                target_completion_date=datetime.fromisoformat(assessment_data['target_completion_date']) if assessment_data.get('target_completion_date') else None,
                assessed_by=user_id
            )
            
            self.db.add(assessment)
            self.db.commit()
            self.db.refresh(assessment)
            
            logger.info(f"Created requirement assessment: {assessment.id}")
            return assessment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating requirement assessment: {str(e)}")
            raise
    
    def get_assessments_for_model(self, ai_model_id: int, organization_id: int) -> List[RequirementAssessment]:
        """Get all assessments for a specific AI model"""
        return self.db.query(RequirementAssessment).filter(
            RequirementAssessment.ai_model_id == ai_model_id,
            RequirementAssessment.organization_id == organization_id
        ).all()
    
    def update_assessment(self, assessment_id: int, assessment_data: Dict[str, Any], user_id: int) -> RequirementAssessment:
        """Update a requirement assessment"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            assessment = self.db.query(RequirementAssessment).filter(
                RequirementAssessment.id == assessment_id,
                RequirementAssessment.organization_id == user.organization_id
            ).first()
            
            if not assessment:
                raise ValueError("Assessment not found")
            
            # Update fields
            for field, value in assessment_data.items():
                if hasattr(assessment, field) and field not in ['id', 'created_date', 'organization_id']:
                    if field == 'compliance_level' and value:
                        setattr(assessment, field, ComplianceLevel(value))
                    elif field == 'status' and value:
                        setattr(assessment, field, AssessmentStatus(value))
                    elif field in ['target_completion_date', 'actual_completion_date', 'next_review_date'] and value:
                        setattr(assessment, field, datetime.fromisoformat(value))
                    else:
                        setattr(assessment, field, value)
            
            assessment.last_updated = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(assessment)
            
            return assessment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating assessment: {str(e)}")
            raise
    
    def get_compliance_summary(self, organization_id: int, ai_model_id: Optional[int] = None) -> Dict[str, Any]:
        """Get compliance summary for organization or specific model"""
        query = self.db.query(RequirementAssessment).filter(
            RequirementAssessment.organization_id == organization_id
        )
        
        if ai_model_id:
            query = query.filter(RequirementAssessment.ai_model_id == ai_model_id)
        
        assessments = query.all()
        
        summary = {
            'total_assessments': len(assessments),
            'by_compliance_level': {},
            'by_status': {},
            'average_compliance_score': 0.0,
            'high_risk_assessments': 0,
            'overdue_assessments': 0,
            'completed_assessments': 0
        }
        
        if not assessments:
            return summary
        
        compliance_scores = []
        current_date = datetime.utcnow()
        
        for assessment in assessments:
            # Compliance level distribution
            compliance_level = assessment.compliance_level.value if assessment.compliance_level else 'unknown'
            summary['by_compliance_level'][compliance_level] = summary['by_compliance_level'].get(compliance_level, 0) + 1
            
            # Status distribution
            status = assessment.status.value if assessment.status else 'unknown'
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # Compliance scores
            if assessment.compliance_score:
                compliance_scores.append(assessment.compliance_score)
            
            # High risk assessments
            if assessment.risk_level in ['high', 'critical']:
                summary['high_risk_assessments'] += 1
            
            # Overdue assessments
            if (assessment.target_completion_date and 
                assessment.target_completion_date < current_date and 
                assessment.status != AssessmentStatus.COMPLETED):
                summary['overdue_assessments'] += 1
            
            # Completed assessments
            if assessment.status == AssessmentStatus.COMPLETED:
                summary['completed_assessments'] += 1
        
        # Average compliance score
        if compliance_scores:
            summary['average_compliance_score'] = sum(compliance_scores) / len(compliance_scores)
        
        return summary

