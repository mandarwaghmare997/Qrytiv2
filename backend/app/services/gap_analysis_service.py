# Gap Analysis and Compliance Scoring Service
# Advanced service for automated gap analysis and compliance scoring

from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import logging
import statistics

from ..models.requirement import (
    Requirement, RequirementAssessment, GapAnalysis,
    RequirementCategory, ComplianceLevel, AssessmentStatus
)
from ..models.ai_model import AIModel, RiskLevel, ComplianceStatus
from ..models.organization import Organization
from ..models.user import User

logger = logging.getLogger(__name__)

class GapAnalysisService:
    """Service for automated gap analysis and compliance scoring"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def conduct_gap_analysis(self, organization_id: int, ai_model_id: Optional[int] = None, 
                           user_id: int = None) -> GapAnalysis:
        """Conduct comprehensive gap analysis for organization or specific AI model"""
        try:
            # Get all requirements
            requirements = self.db.query(Requirement).filter(Requirement.is_active == True).all()
            
            # Get existing assessments
            assessment_query = self.db.query(RequirementAssessment).filter(
                RequirementAssessment.organization_id == organization_id
            )
            
            if ai_model_id:
                assessment_query = assessment_query.filter(
                    RequirementAssessment.ai_model_id == ai_model_id
                )
            
            assessments = assessment_query.all()
            
            # Calculate compliance metrics
            compliance_metrics = self._calculate_compliance_metrics(requirements, assessments)
            
            # Identify gaps
            gaps = self._identify_gaps(requirements, assessments)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(gaps, compliance_metrics)
            
            # Create gap analysis record
            gap_analysis = GapAnalysis(
                organization_id=organization_id,
                ai_model_id=ai_model_id,
                analysis_name=f"Gap Analysis - {datetime.utcnow().strftime('%Y-%m-%d')}",
                description=f"Automated gap analysis for {'specific AI model' if ai_model_id else 'organization-wide'} ISO 42001 compliance",
                scope="ISO 42001 requirements assessment",
                overall_compliance_score=compliance_metrics['overall_score'],
                total_requirements=compliance_metrics['total_requirements'],
                compliant_requirements=compliance_metrics['compliant_requirements'],
                non_compliant_requirements=compliance_metrics['non_compliant_requirements'],
                partially_compliant_requirements=compliance_metrics['partially_compliant_requirements'],
                critical_gaps=json.dumps(gaps['critical']),
                high_priority_gaps=json.dumps(gaps['high']),
                medium_priority_gaps=json.dumps(gaps['medium']),
                low_priority_gaps=json.dumps(gaps['low']),
                immediate_actions=json.dumps(recommendations['immediate']),
                short_term_actions=json.dumps(recommendations['short_term']),
                long_term_actions=json.dumps(recommendations['long_term']),
                estimated_effort=self._estimate_effort(gaps),
                estimated_cost=self._estimate_cost(gaps),
                conducted_by=user_id
            )
            
            self.db.add(gap_analysis)
            self.db.commit()
            self.db.refresh(gap_analysis)
            
            logger.info(f"Conducted gap analysis: {gap_analysis.id}")
            return gap_analysis
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error conducting gap analysis: {str(e)}")
            raise
    
    def calculate_compliance_score(self, organization_id: int, ai_model_id: Optional[int] = None) -> Dict[str, Any]:
        """Calculate detailed compliance score"""
        try:
            # Get assessments
            assessment_query = self.db.query(RequirementAssessment).filter(
                RequirementAssessment.organization_id == organization_id
            )
            
            if ai_model_id:
                assessment_query = assessment_query.filter(
                    RequirementAssessment.ai_model_id == ai_model_id
                )
            
            assessments = assessment_query.all()
            
            if not assessments:
                return {
                    'overall_score': 0.0,
                    'category_scores': {},
                    'risk_adjusted_score': 0.0,
                    'maturity_level': 'Initial',
                    'recommendations': []
                }
            
            # Calculate scores by category
            category_scores = {}
            total_weighted_score = 0.0
            total_weight = 0.0
            
            # Category weights (based on ISO 42001 importance)
            category_weights = {
                RequirementCategory.CONTEXT_ORGANIZATION: 0.15,
                RequirementCategory.LEADERSHIP: 0.20,
                RequirementCategory.PLANNING: 0.15,
                RequirementCategory.SUPPORT: 0.15,
                RequirementCategory.OPERATION: 0.20,
                RequirementCategory.PERFORMANCE_EVALUATION: 0.10,
                RequirementCategory.IMPROVEMENT: 0.05
            }
            
            # Group assessments by category
            assessments_by_category = {}
            for assessment in assessments:
                requirement = self.db.query(Requirement).filter(
                    Requirement.id == assessment.requirement_id
                ).first()
                
                if requirement and requirement.category:
                    category = requirement.category
                    if category not in assessments_by_category:
                        assessments_by_category[category] = []
                    assessments_by_category[category].append(assessment)
            
            # Calculate category scores
            for category, category_assessments in assessments_by_category.items():
                scores = [a.compliance_score for a in category_assessments if a.compliance_score is not None]
                
                if scores:
                    category_score = statistics.mean(scores)
                    category_scores[category.value] = {
                        'score': category_score,
                        'assessments_count': len(category_assessments),
                        'weight': category_weights.get(category, 0.1)
                    }
                    
                    # Add to weighted total
                    weight = category_weights.get(category, 0.1)
                    total_weighted_score += category_score * weight
                    total_weight += weight
            
            # Calculate overall score
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Calculate risk-adjusted score
            risk_adjusted_score = self._calculate_risk_adjusted_score(assessments, overall_score)
            
            # Determine maturity level
            maturity_level = self._determine_maturity_level(overall_score, category_scores)
            
            # Generate recommendations
            recommendations = self._generate_score_recommendations(overall_score, category_scores)
            
            return {
                'overall_score': round(overall_score, 2),
                'category_scores': category_scores,
                'risk_adjusted_score': round(risk_adjusted_score, 2),
                'maturity_level': maturity_level,
                'total_assessments': len(assessments),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {str(e)}")
            raise
    
    def update_ai_model_compliance(self, ai_model_id: int) -> AIModel:
        """Update AI model compliance status based on assessments"""
        try:
            ai_model = self.db.query(AIModel).filter(AIModel.id == ai_model_id).first()
            if not ai_model:
                raise ValueError("AI model not found")
            
            # Calculate compliance score for this model
            compliance_data = self.calculate_compliance_score(
                ai_model.organization_id, 
                ai_model_id
            )
            
            # Update model compliance fields
            ai_model.compliance_score = compliance_data['overall_score']
            
            # Determine compliance status
            if compliance_data['overall_score'] >= 90:
                ai_model.compliance_status = ComplianceStatus.COMPLIANT
            elif compliance_data['overall_score'] >= 70:
                ai_model.compliance_status = ComplianceStatus.PARTIALLY_COMPLIANT
            elif compliance_data['overall_score'] >= 50:
                ai_model.compliance_status = ComplianceStatus.UNDER_REVIEW
            else:
                ai_model.compliance_status = ComplianceStatus.NON_COMPLIANT
            
            ai_model.last_updated = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(ai_model)
            
            return ai_model
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating AI model compliance: {str(e)}")
            raise
    
    def _calculate_compliance_metrics(self, requirements: List[Requirement], 
                                    assessments: List[RequirementAssessment]) -> Dict[str, Any]:
        """Calculate basic compliance metrics"""
        total_requirements = len(requirements)
        
        # Count assessments by compliance level
        compliant_count = 0
        partially_compliant_count = 0
        non_compliant_count = 0
        
        # Create assessment lookup
        assessment_lookup = {a.requirement_id: a for a in assessments}
        
        compliance_scores = []
        
        for requirement in requirements:
            assessment = assessment_lookup.get(requirement.id)
            
            if assessment:
                if assessment.compliance_level == ComplianceLevel.FULLY_COMPLIANT:
                    compliant_count += 1
                elif assessment.compliance_level == ComplianceLevel.LARGELY_COMPLIANT:
                    compliant_count += 1
                elif assessment.compliance_level == ComplianceLevel.PARTIALLY_COMPLIANT:
                    partially_compliant_count += 1
                elif assessment.compliance_level == ComplianceLevel.NON_COMPLIANT:
                    non_compliant_count += 1
                
                if assessment.compliance_score is not None:
                    compliance_scores.append(assessment.compliance_score)
        
        # Calculate overall score
        overall_score = statistics.mean(compliance_scores) if compliance_scores else 0.0
        
        return {
            'total_requirements': total_requirements,
            'compliant_requirements': compliant_count,
            'partially_compliant_requirements': partially_compliant_count,
            'non_compliant_requirements': non_compliant_count,
            'not_assessed_requirements': total_requirements - len(assessments),
            'overall_score': overall_score
        }
    
    def _identify_gaps(self, requirements: List[Requirement], 
                      assessments: List[RequirementAssessment]) -> Dict[str, List[Dict]]:
        """Identify gaps by priority level"""
        gaps = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        assessment_lookup = {a.requirement_id: a for a in assessments}
        
        for requirement in requirements:
            assessment = assessment_lookup.get(requirement.id)
            
            gap_info = {
                'requirement_id': requirement.requirement_id,
                'title': requirement.title,
                'category': requirement.category.value,
                'current_state': assessment.current_state if assessment else 'Not assessed',
                'gap_description': assessment.gap_analysis if assessment else 'No assessment conducted',
                'recommendations': assessment.recommendations if assessment else 'Assessment required'
            }
            
            # Determine gap priority
            if not assessment:
                # Not assessed - high priority for mandatory requirements
                if requirement.requirement_type.value == 'mandatory':
                    gaps['high'].append(gap_info)
                else:
                    gaps['medium'].append(gap_info)
            elif assessment.compliance_level == ComplianceLevel.NON_COMPLIANT:
                # Non-compliant - critical or high priority
                if assessment.risk_level in ['critical', 'high']:
                    gaps['critical'].append(gap_info)
                else:
                    gaps['high'].append(gap_info)
            elif assessment.compliance_level == ComplianceLevel.PARTIALLY_COMPLIANT:
                # Partially compliant - medium priority
                gaps['medium'].append(gap_info)
            elif assessment.compliance_score and assessment.compliance_score < 80:
                # Low compliance score - medium priority
                gaps['medium'].append(gap_info)
        
        return gaps
    
    def _generate_recommendations(self, gaps: Dict[str, List[Dict]], 
                                compliance_metrics: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate actionable recommendations"""
        recommendations = {
            'immediate': [],
            'short_term': [],
            'long_term': []
        }
        
        # Immediate actions (critical gaps)
        if gaps['critical']:
            recommendations['immediate'].extend([
                f"Address {len(gaps['critical'])} critical compliance gaps immediately",
                "Establish emergency response team for critical non-compliance issues",
                "Implement temporary controls to mitigate high-risk exposures"
            ])
        
        # Short-term actions (high and medium priority gaps)
        high_medium_gaps = len(gaps['high']) + len(gaps['medium'])
        if high_medium_gaps > 0:
            recommendations['short_term'].extend([
                f"Develop remediation plan for {high_medium_gaps} identified gaps",
                "Assign dedicated resources for compliance improvement",
                "Implement regular monitoring and reporting mechanisms"
            ])
        
        # Long-term actions (overall improvement)
        if compliance_metrics['overall_score'] < 80:
            recommendations['long_term'].extend([
                "Establish comprehensive AI governance framework",
                "Implement continuous compliance monitoring system",
                "Develop AI ethics and governance training program",
                "Create automated compliance assessment tools"
            ])
        
        return recommendations
    
    def _calculate_risk_adjusted_score(self, assessments: List[RequirementAssessment], 
                                     base_score: float) -> float:
        """Calculate risk-adjusted compliance score"""
        if not assessments:
            return base_score
        
        # Count high-risk assessments
        high_risk_count = sum(1 for a in assessments if a.risk_level in ['high', 'critical'])
        total_assessments = len(assessments)
        
        # Apply risk penalty
        risk_ratio = high_risk_count / total_assessments
        risk_penalty = risk_ratio * 20  # Up to 20 point penalty
        
        return max(0.0, base_score - risk_penalty)
    
    def _determine_maturity_level(self, overall_score: float, category_scores: Dict) -> str:
        """Determine AI governance maturity level"""
        if overall_score >= 90:
            return "Optimized"
        elif overall_score >= 80:
            return "Managed"
        elif overall_score >= 70:
            return "Defined"
        elif overall_score >= 60:
            return "Repeatable"
        else:
            return "Initial"
    
    def _generate_score_recommendations(self, overall_score: float, 
                                      category_scores: Dict) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        if overall_score < 60:
            recommendations.append("Establish basic AI governance framework")
            recommendations.append("Conduct comprehensive risk assessment")
        elif overall_score < 80:
            recommendations.append("Strengthen compliance monitoring processes")
            recommendations.append("Improve documentation and evidence collection")
        else:
            recommendations.append("Focus on continuous improvement")
            recommendations.append("Implement advanced AI governance practices")
        
        # Category-specific recommendations
        for category, data in category_scores.items():
            if data['score'] < 70:
                recommendations.append(f"Improve {category.replace('_', ' ').title()} processes")
        
        return recommendations
    
    def _estimate_effort(self, gaps: Dict[str, List[Dict]]) -> str:
        """Estimate effort required for gap remediation"""
        total_gaps = sum(len(gap_list) for gap_list in gaps.values())
        
        if total_gaps == 0:
            return "Minimal effort required"
        elif total_gaps <= 5:
            return "1-2 months"
        elif total_gaps <= 15:
            return "3-6 months"
        else:
            return "6-12 months"
    
    def _estimate_cost(self, gaps: Dict[str, List[Dict]]) -> float:
        """Estimate cost for gap remediation"""
        # Simple cost estimation based on gap count and priority
        cost = 0.0
        cost += len(gaps['critical']) * 50000  # $50k per critical gap
        cost += len(gaps['high']) * 25000     # $25k per high priority gap
        cost += len(gaps['medium']) * 10000   # $10k per medium priority gap
        cost += len(gaps['low']) * 5000       # $5k per low priority gap
        
        return cost

