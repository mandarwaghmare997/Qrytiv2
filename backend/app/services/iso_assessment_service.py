"""
ISO 42001 Assessment Service
Handles gap assessment logic, scoring, and NIST AI RMF integration
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import math

from ..models.iso_control import (
    ISOControl, ControlQuestion, QuestionResponse, AssessmentResponse,
    ResponseValue, ControlCategory, NISTFunction, RiskTemplate
)
from ..models.assessment import Assessment
from ..models.project import Project
from ..data.iso_42001_controls import (
    ISO_42001_CONTROLS, RISK_TEMPLATE_CONTROLS, 
    NIST_FUNCTION_WEIGHTS, CATEGORY_WEIGHTS
)

class ISOAssessmentService:
    def __init__(self, db: Session):
        self.db = db

    def initialize_controls_database(self) -> bool:
        """Initialize the ISO 42001 controls database from the framework data"""
        try:
            # Check if controls already exist
            existing_controls = self.db.query(ISOControl).count()
            if existing_controls > 0:
                return True  # Already initialized

            # Create controls and questions from framework data
            for control_data in ISO_42001_CONTROLS:
                # Create control
                control = ISOControl(
                    control_number=control_data["control_number"],
                    title=control_data["title"],
                    description=control_data["description"],
                    category=ControlCategory(control_data["category"]),
                    nist_function=NISTFunction(control_data["nist_function"]),
                    weight=control_data["weight"],
                    is_mandatory=control_data["is_mandatory"],
                    min_risk_template=RiskTemplate(control_data["min_risk_template"])
                )
                self.db.add(control)
                self.db.flush()  # Get the control ID

                # Create questions for this control
                for question_data in control_data["questions"]:
                    question = ControlQuestion(
                        control_id=control.id,
                        question_number=question_data["question_number"],
                        question_text=question_data["question_text"],
                        guidance=question_data.get("guidance"),
                        weight=question_data["weight"],
                        requires_evidence=question_data["requires_evidence"],
                        evidence_description=question_data.get("evidence_description")
                    )
                    self.db.add(question)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to initialize controls database: {str(e)}")

    def create_assessment(self, project_id: int, risk_template: str, assessment_data: Dict[str, Any]) -> Assessment:
        """Create a new ISO 42001 assessment for a project"""
        try:
            # Create the assessment
            assessment = Assessment(
                project_id=project_id,
                assessment_name=assessment_data.get("assessment_name", "ISO 42001 Compliance Assessment"),
                risk_template=RiskTemplate(risk_template),
                ai_system_name=assessment_data.get("ai_system_name"),
                ai_system_description=assessment_data.get("ai_system_description"),
                ai_system_type=assessment_data.get("ai_system_type"),
                intended_use=assessment_data.get("intended_use"),
                target_users=assessment_data.get("target_users"),
                deployment_environment=assessment_data.get("deployment_environment"),
                impact_level=assessment_data.get("impact_level"),
                risk_tolerance=assessment_data.get("risk_tolerance"),
                regulatory_requirements=assessment_data.get("regulatory_requirements", []),
                target_completion_date=assessment_data.get("target_completion_date")
            )
            self.db.add(assessment)
            self.db.flush()

            # Get applicable controls for the risk template
            applicable_control_numbers = RISK_TEMPLATE_CONTROLS.get(risk_template, [])
            applicable_controls = self.db.query(ISOControl).filter(
                ISOControl.control_number.in_(applicable_control_numbers)
            ).all()

            # Create assessment responses for each applicable control
            for control in applicable_controls:
                assessment_response = AssessmentResponse(
                    assessment_id=assessment.id,
                    control_id=control.id
                )
                self.db.add(assessment_response)

            self.db.commit()
            return assessment

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create assessment: {str(e)}")

    def get_assessment_overview(self, assessment_id: int) -> Dict[str, Any]:
        """Get comprehensive overview of an assessment"""
        assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise Exception("Assessment not found")

        # Get control responses with controls and questions
        control_responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment_id
        ).all()

        # Calculate category progress
        category_progress = {}
        for category in ControlCategory:
            category_controls = [cr for cr in control_responses if cr.control.category == category]
            if category_controls:
                completed = len([cr for cr in category_controls if cr.status == "completed"])
                total = len(category_controls)
                category_progress[category.value] = {
                    "completed": completed,
                    "total": total,
                    "percentage": (completed / total * 100) if total > 0 else 0,
                    "compliance_score": sum(cr.compliance_score for cr in category_controls) / total if total > 0 else 0
                }

        # Calculate NIST function progress
        nist_progress = {}
        for function in NISTFunction:
            function_controls = [cr for cr in control_responses if cr.control.nist_function == function]
            if function_controls:
                completed = len([cr for cr in function_controls if cr.status == "completed"])
                total = len(function_controls)
                nist_progress[function.value] = {
                    "completed": completed,
                    "total": total,
                    "percentage": (completed / total * 100) if total > 0 else 0,
                    "compliance_score": sum(cr.compliance_score for cr in function_controls) / total if total > 0 else 0
                }

        return {
            "assessment": {
                "id": assessment.id,
                "assessment_name": assessment.assessment_name,
                "risk_template": assessment.risk_template.value,
                "status": assessment.status.value,
                "overall_compliance_score": assessment.overall_compliance_score,
                "overall_risk_score": assessment.overall_risk_score,
                "completion_percentage": assessment.completion_percentage,
                "govern_score": assessment.govern_score,
                "map_score": assessment.map_score,
                "measure_score": assessment.measure_score,
                "manage_score": assessment.manage_score,
                "ai_system_name": assessment.ai_system_name,
                "target_completion_date": assessment.target_completion_date.isoformat() if assessment.target_completion_date else None
            },
            "category_progress": category_progress,
            "nist_progress": nist_progress,
            "total_controls": len(control_responses),
            "completed_controls": len([cr for cr in control_responses if cr.status == "completed"]),
            "in_progress_controls": len([cr for cr in control_responses if cr.status == "in_progress"])
        }

    def get_control_questionnaire(self, assessment_id: int, control_number: str) -> Dict[str, Any]:
        """Get questionnaire for a specific control"""
        # Get the control and its questions
        control = self.db.query(ISOControl).filter(
            ISOControl.control_number == control_number
        ).first()
        
        if not control:
            raise Exception("Control not found")

        # Get assessment response for this control
        assessment_response = self.db.query(AssessmentResponse).filter(
            and_(
                AssessmentResponse.assessment_id == assessment_id,
                AssessmentResponse.control_id == control.id
            )
        ).first()

        if not assessment_response:
            raise Exception("Assessment response not found")

        # Get questions and their responses
        questions_data = []
        for question in control.questions:
            question_response = self.db.query(QuestionResponse).filter(
                and_(
                    QuestionResponse.assessment_id == assessment_id,
                    QuestionResponse.question_id == question.id
                )
            ).first()

            questions_data.append({
                "id": question.id,
                "question_number": question.question_number,
                "question_text": question.question_text,
                "guidance": question.guidance,
                "weight": question.weight,
                "requires_evidence": question.requires_evidence,
                "evidence_description": question.evidence_description,
                "response": {
                    "id": question_response.id if question_response else None,
                    "response_value": question_response.response_value.value if question_response else None,
                    "comments": question_response.comments if question_response else None,
                    "confidence_level": question_response.confidence_level if question_response else 5,
                    "evidence_files": len(question_response.evidence_files) if question_response else 0
                }
            })

        return {
            "control": {
                "id": control.id,
                "control_number": control.control_number,
                "title": control.title,
                "description": control.description,
                "category": control.category.value,
                "nist_function": control.nist_function.value,
                "weight": control.weight
            },
            "assessment_response": {
                "id": assessment_response.id,
                "completion_percentage": assessment_response.completion_percentage,
                "compliance_score": assessment_response.compliance_score,
                "risk_score": assessment_response.risk_score,
                "status": assessment_response.status
            },
            "questions": questions_data
        }

    def submit_question_response(self, assessment_id: int, question_id: int, response_data: Dict[str, Any]) -> QuestionResponse:
        """Submit or update a response to a control question"""
        try:
            # Get or create question response
            question_response = self.db.query(QuestionResponse).filter(
                and_(
                    QuestionResponse.assessment_id == assessment_id,
                    QuestionResponse.question_id == question_id
                )
            ).first()

            if question_response:
                # Update existing response
                question_response.response_value = ResponseValue(response_data["response_value"])
                question_response.comments = response_data.get("comments")
                question_response.confidence_level = response_data.get("confidence_level", 5)
            else:
                # Create new response
                question_response = QuestionResponse(
                    assessment_id=assessment_id,
                    question_id=question_id,
                    response_value=ResponseValue(response_data["response_value"]),
                    comments=response_data.get("comments"),
                    confidence_level=response_data.get("confidence_level", 5)
                )
                self.db.add(question_response)

            self.db.flush()

            # Recalculate scores for the control
            self._recalculate_control_scores(assessment_id, question_response.question.control_id)
            
            # Recalculate overall assessment scores
            self._recalculate_assessment_scores(assessment_id)

            self.db.commit()
            return question_response

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to submit question response: {str(e)}")

    def _recalculate_control_scores(self, assessment_id: int, control_id: int):
        """Recalculate scores for a specific control"""
        # Get all question responses for this control
        question_responses = self.db.query(QuestionResponse).join(ControlQuestion).filter(
            and_(
                QuestionResponse.assessment_id == assessment_id,
                ControlQuestion.control_id == control_id
            )
        ).all()

        if not question_responses:
            return

        # Calculate compliance score
        total_weight = 0
        weighted_score = 0
        answered_questions = 0

        for qr in question_responses:
            if qr.response_value != ResponseValue.NOT_APPLICABLE:
                total_weight += qr.question.weight
                answered_questions += 1

                # Score calculation based on response and evidence
                if qr.response_value == ResponseValue.YES:
                    # Check if evidence is provided when required
                    has_evidence = len(qr.evidence_files) > 0
                    if qr.question.requires_evidence and has_evidence:
                        score = 100  # Full score
                    elif qr.question.requires_evidence and not has_evidence:
                        score = 75   # Reduced score for missing evidence
                    else:
                        score = 100  # Full score when evidence not required
                elif qr.response_value == ResponseValue.PARTIAL:
                    score = 50   # Partial implementation
                else:  # NO
                    score = 0    # No implementation

                weighted_score += score * qr.question.weight

        # Calculate final scores
        compliance_score = (weighted_score / total_weight) if total_weight > 0 else 0
        completion_percentage = (answered_questions / len(question_responses)) * 100 if question_responses else 0

        # Calculate risk score (inverse of compliance, adjusted by NIST function)
        control = self.db.query(ISOControl).filter(ISOControl.id == control_id).first()
        nist_weight = NIST_FUNCTION_WEIGHTS.get(control.nist_function.value, 1.0)
        risk_score = (100 - compliance_score) * nist_weight

        # Update assessment response
        assessment_response = self.db.query(AssessmentResponse).filter(
            and_(
                AssessmentResponse.assessment_id == assessment_id,
                AssessmentResponse.control_id == control_id
            )
        ).first()

        if assessment_response:
            assessment_response.compliance_score = compliance_score
            assessment_response.completion_percentage = completion_percentage
            assessment_response.risk_score = min(risk_score, 100)  # Cap at 100
            
            # Update status
            if completion_percentage == 100:
                assessment_response.status = "completed"
            elif completion_percentage > 0:
                assessment_response.status = "in_progress"
            else:
                assessment_response.status = "not_started"

    def _recalculate_assessment_scores(self, assessment_id: int):
        """Recalculate overall assessment scores"""
        assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            return

        # Get all control responses
        control_responses = self.db.query(AssessmentResponse).filter(
            AssessmentResponse.assessment_id == assessment_id
        ).all()

        if not control_responses:
            return

        # Calculate weighted overall scores
        total_weight = 0
        weighted_compliance = 0
        weighted_risk = 0
        completed_controls = 0

        for cr in control_responses:
            control_weight = cr.control.weight * CATEGORY_WEIGHTS.get(cr.control.category.value, 1.0)
            total_weight += control_weight
            weighted_compliance += cr.compliance_score * control_weight
            weighted_risk += cr.risk_score * control_weight
            
            if cr.status == "completed":
                completed_controls += 1

        # Update assessment scores
        if total_weight > 0:
            assessment.overall_compliance_score = weighted_compliance / total_weight
            assessment.overall_risk_score = weighted_risk / total_weight

        assessment.completion_percentage = (completed_controls / len(control_responses)) * 100 if control_responses else 0

        # Calculate NIST function scores
        self._calculate_nist_function_scores(assessment_id)

        # Update status
        if assessment.completion_percentage == 100:
            assessment.status = "completed"
        elif assessment.completion_percentage > 0:
            assessment.status = "in_progress"

    def _calculate_nist_function_scores(self, assessment_id: int):
        """Calculate scores for each NIST AI RMF function"""
        assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            return

        function_scores = {}
        
        for function in NISTFunction:
            # Get control responses for this NIST function
            control_responses = self.db.query(AssessmentResponse).join(ISOControl).filter(
                and_(
                    AssessmentResponse.assessment_id == assessment_id,
                    ISOControl.nist_function == function
                )
            ).all()

            if control_responses:
                total_weight = sum(cr.control.weight for cr in control_responses)
                weighted_score = sum(cr.compliance_score * cr.control.weight for cr in control_responses)
                function_scores[function.value] = weighted_score / total_weight if total_weight > 0 else 0
            else:
                function_scores[function.value] = 0

        # Update assessment with NIST function scores
        assessment.govern_score = function_scores.get("govern", 0)
        assessment.map_score = function_scores.get("map", 0)
        assessment.measure_score = function_scores.get("measure", 0)
        assessment.manage_score = function_scores.get("manage", 0)

    def get_gap_analysis(self, assessment_id: int) -> Dict[str, Any]:
        """Generate comprehensive gap analysis report"""
        assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise Exception("Assessment not found")

        # Get all control responses with details
        control_responses = self.db.query(AssessmentResponse).join(ISOControl).filter(
            AssessmentResponse.assessment_id == assessment_id
        ).all()

        gaps = []
        recommendations = []

        for cr in control_responses:
            if cr.compliance_score < 80:  # Consider anything below 80% as a gap
                # Get question responses to identify specific gaps
                question_responses = self.db.query(QuestionResponse).join(ControlQuestion).filter(
                    and_(
                        QuestionResponse.assessment_id == assessment_id,
                        ControlQuestion.control_id == cr.control_id
                    )
                ).all()

                gap_details = []
                for qr in question_responses:
                    if qr.response_value in [ResponseValue.NO, ResponseValue.PARTIAL]:
                        gap_details.append({
                            "question": qr.question.question_text,
                            "response": qr.response_value.value,
                            "guidance": qr.question.guidance,
                            "evidence_required": qr.question.requires_evidence,
                            "evidence_provided": len(qr.evidence_files) > 0
                        })

                gaps.append({
                    "control_number": cr.control.control_number,
                    "control_title": cr.control.title,
                    "category": cr.control.category.value,
                    "nist_function": cr.control.nist_function.value,
                    "compliance_score": cr.compliance_score,
                    "risk_score": cr.risk_score,
                    "gap_severity": self._calculate_gap_severity(cr.compliance_score, cr.control.weight),
                    "gap_details": gap_details
                })

                # Generate recommendations
                recommendations.extend(self._generate_recommendations(cr.control, gap_details))

        return {
            "assessment_summary": {
                "overall_compliance_score": assessment.overall_compliance_score,
                "overall_risk_score": assessment.overall_risk_score,
                "completion_percentage": assessment.completion_percentage,
                "total_gaps": len(gaps),
                "critical_gaps": len([g for g in gaps if g["gap_severity"] == "critical"]),
                "high_gaps": len([g for g in gaps if g["gap_severity"] == "high"]),
                "medium_gaps": len([g for g in gaps if g["gap_severity"] == "medium"]),
                "low_gaps": len([g for g in gaps if g["gap_severity"] == "low"])
            },
            "nist_function_scores": {
                "govern": assessment.govern_score,
                "map": assessment.map_score,
                "measure": assessment.measure_score,
                "manage": assessment.manage_score
            },
            "gaps": gaps,
            "recommendations": recommendations,
            "remediation_priority": self._prioritize_remediation(gaps)
        }

    def _calculate_gap_severity(self, compliance_score: float, control_weight: float) -> str:
        """Calculate gap severity based on compliance score and control weight"""
        impact_score = (100 - compliance_score) * control_weight
        
        if impact_score >= 80:
            return "critical"
        elif impact_score >= 60:
            return "high"
        elif impact_score >= 40:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, control: ISOControl, gap_details: List[Dict]) -> List[Dict]:
        """Generate specific recommendations for addressing gaps"""
        recommendations = []
        
        for gap in gap_details:
            if gap["response"] == "no":
                recommendations.append({
                    "control_number": control.control_number,
                    "priority": "high",
                    "recommendation": f"Implement {control.title.lower()} as required by control {control.control_number}",
                    "specific_action": gap["guidance"],
                    "evidence_needed": gap["evidence_required"]
                })
            elif gap["response"] == "partial":
                recommendations.append({
                    "control_number": control.control_number,
                    "priority": "medium",
                    "recommendation": f"Complete implementation of {control.title.lower()}",
                    "specific_action": gap["guidance"],
                    "evidence_needed": gap["evidence_required"]
                })

        return recommendations

    def _prioritize_remediation(self, gaps: List[Dict]) -> List[Dict]:
        """Prioritize remediation efforts based on risk and impact"""
        # Sort gaps by severity and NIST function importance
        nist_priority = {"govern": 4, "map": 3, "measure": 2, "manage": 1}
        
        prioritized = sorted(gaps, key=lambda x: (
            {"critical": 4, "high": 3, "medium": 2, "low": 1}[x["gap_severity"]],
            nist_priority.get(x["nist_function"], 0),
            x["risk_score"]
        ), reverse=True)

        return prioritized[:10]  # Return top 10 priority items

