"""
Report Generation Lambda Function
Generates compliance reports and uploads to S3

Developed by: Qryti Dev Team
"""

import json
import sys
import os
import uuid
from datetime import datetime, timezone
from io import BytesIO

# Add shared modules to path
sys.path.append('/opt/python')
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from database import db
from auth import require_auth
from utils import lambda_handler_wrapper, parse_json_body, validation_error_response, success_response, error_response, upload_to_s3, generate_presigned_url

# For PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except ImportError:
    print("ReportLab not available - PDF generation will be disabled")

@require_auth
@lambda_handler_wrapper
def lambda_handler(event, context):
    """Generate compliance reports"""
    try:
        user = event['user']
        user_id = user['user_id']
        
        # Parse request body
        body = parse_json_body(event)
        
        # Validate required fields
        report_type = body.get('type', 'compliance')
        title = body.get('title', f'Compliance Report - {datetime.now().strftime("%Y-%m-%d")}')
        
        # Validate report type
        valid_types = ['compliance', 'model_inventory', 'risk_assessment', 'audit_trail']
        if report_type not in valid_types:
            return error_response(400, f"Invalid report type. Must be one of: {', '.join(valid_types)}")
        
        # Generate report content based on type
        if report_type == 'compliance':
            report_content = generate_compliance_report(user_id)
        elif report_type == 'model_inventory':
            report_content = generate_model_inventory_report(user_id)
        elif report_type == 'risk_assessment':
            report_content = generate_risk_assessment_report(user_id)
        elif report_type == 'audit_trail':
            report_content = generate_audit_trail_report(user_id)
        else:
            return error_response(400, "Unsupported report type")
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(report_content, title)
        
        # Upload to S3
        report_id = str(uuid.uuid4())
        s3_key = f"reports/{user_id}/{report_id}.pdf"
        bucket_name = os.environ.get('S3_BUCKET', 'qryti-reports-dev')
        
        upload_success = upload_to_s3(bucket_name, s3_key, pdf_buffer.getvalue(), 'application/pdf')
        
        if not upload_success:
            return error_response(500, "Failed to upload report to storage")
        
        # Save report metadata to database
        report_data = db.create_report(
            user_id=user_id,
            report_type=report_type,
            title=title,
            s3_key=s3_key
        )
        
        # Generate presigned URL for download
        try:
            download_url = generate_presigned_url(bucket_name, s3_key, 3600)  # 1 hour expiry
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            download_url = None
        
        # Format response
        response_data = {
            'report_id': report_data['report_id'],
            'type': report_data['type'],
            'title': report_data['title'],
            'status': report_data['status'],
            'created_at': report_data['created_at'],
            'download_url': download_url,
            'expires_in': 3600 if download_url else None
        }
        
        return success_response(response_data, "Report generated successfully")
        
    except Exception as e:
        print(f"Report generation error: {e}")
        return error_response(500, "Internal server error")

def generate_compliance_report(user_id):
    """Generate compliance report content"""
    # Get user data
    user = db.get_user_by_id(user_id)
    
    # Get all models for the user's organization
    all_models = db.get_all_models()
    
    # Calculate compliance metrics
    total_models = len(all_models)
    high_risk_models = len([m for m in all_models if m.get('risk_level') == 'high'])
    monitored_models = len([m for m in all_models if m.get('monitoring_enabled')])
    
    compliance_score = calculate_compliance_score(all_models)
    
    return {
        'title': 'ISO 42001 Compliance Report',
        'user': user,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_models': total_models,
            'high_risk_models': high_risk_models,
            'monitored_models': monitored_models,
            'compliance_score': compliance_score
        },
        'models': all_models,
        'recommendations': generate_recommendations(all_models)
    }

def generate_model_inventory_report(user_id):
    """Generate model inventory report content"""
    user = db.get_user_by_id(user_id)
    all_models = db.get_all_models()
    clients = db.get_all_clients()
    
    # Group models by client
    models_by_client = {}
    for model in all_models:
        client_id = model.get('client_id')
        if client_id not in models_by_client:
            models_by_client[client_id] = []
        models_by_client[client_id].append(model)
    
    return {
        'title': 'AI Model Inventory Report',
        'user': user,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'total_models': len(all_models),
        'total_clients': len(clients),
        'models_by_client': models_by_client,
        'clients': {client['client_id']: client for client in clients}
    }

def generate_risk_assessment_report(user_id):
    """Generate risk assessment report content"""
    user = db.get_user_by_id(user_id)
    all_models = db.get_all_models()
    
    # Categorize by risk level
    risk_categories = {
        'low': [],
        'medium': [],
        'high': [],
        'critical': []
    }
    
    for model in all_models:
        risk_level = model.get('risk_level', 'medium')
        if risk_level in risk_categories:
            risk_categories[risk_level].append(model)
    
    return {
        'title': 'AI Risk Assessment Report',
        'user': user,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'risk_distribution': {level: len(models) for level, models in risk_categories.items()},
        'risk_categories': risk_categories,
        'risk_mitigation_recommendations': generate_risk_recommendations(risk_categories)
    }

def generate_audit_trail_report(user_id):
    """Generate audit trail report content"""
    user = db.get_user_by_id(user_id)
    
    return {
        'title': 'Audit Trail Report',
        'user': user,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'note': 'Audit trail functionality will be implemented with DynamoDB Streams'
    }

def calculate_compliance_score(models):
    """Calculate overall compliance score"""
    if not models:
        return 0
    
    score = 0
    total_points = len(models) * 100
    
    for model in models:
        # Points for having description
        if model.get('description'):
            score += 20
        
        # Points for having business purpose
        if model.get('business_purpose'):
            score += 20
        
        # Points for monitoring
        if model.get('monitoring_enabled'):
            score += 30
        
        # Points for proper risk classification
        if model.get('risk_level') in ['low', 'medium', 'high', 'critical']:
            score += 20
        
        # Points for framework specification
        if model.get('framework'):
            score += 10
    
    return min(100, (score / total_points) * 100) if total_points > 0 else 0

def generate_recommendations(models):
    """Generate compliance recommendations"""
    recommendations = []
    
    models_without_monitoring = [m for m in models if not m.get('monitoring_enabled')]
    if models_without_monitoring:
        recommendations.append({
            'priority': 'high',
            'category': 'monitoring',
            'description': f'{len(models_without_monitoring)} models lack monitoring. Enable monitoring for better compliance.',
            'affected_models': len(models_without_monitoring)
        })
    
    models_without_description = [m for m in models if not m.get('description')]
    if models_without_description:
        recommendations.append({
            'priority': 'medium',
            'category': 'documentation',
            'description': f'{len(models_without_description)} models lack proper description. Add detailed descriptions.',
            'affected_models': len(models_without_description)
        })
    
    return recommendations

def generate_risk_recommendations(risk_categories):
    """Generate risk mitigation recommendations"""
    recommendations = []
    
    if risk_categories['critical']:
        recommendations.append({
            'priority': 'critical',
            'description': f'{len(risk_categories["critical"])} critical risk models require immediate attention and enhanced controls.'
        })
    
    if risk_categories['high']:
        recommendations.append({
            'priority': 'high',
            'description': f'{len(risk_categories["high"])} high risk models need regular monitoring and risk mitigation measures.'
        })
    
    return recommendations

def generate_pdf_report(content, title):
    """Generate PDF report from content"""
    buffer = BytesIO()
    
    try:
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Generated info
        story.append(Paragraph(f"Generated: {content.get('generated_at', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Organization: {content.get('user', {}).get('organization', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary section
        if 'summary' in content:
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            summary = content['summary']
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total AI Models', str(summary.get('total_models', 0))],
                ['High Risk Models', str(summary.get('high_risk_models', 0))],
                ['Monitored Models', str(summary.get('monitored_models', 0))],
                ['Compliance Score', f"{summary.get('compliance_score', 0):.1f}%"]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # Recommendations section
        if 'recommendations' in content and content['recommendations']:
            story.append(Paragraph("Recommendations", styles['Heading2']))
            for i, rec in enumerate(content['recommendations'], 1):
                story.append(Paragraph(f"{i}. {rec.get('description', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Return a simple text-based PDF if ReportLab fails
        buffer.write(b"PDF generation failed. Report content available via API.")
        buffer.seek(0)
        return buffer

# For local testing
if __name__ == "__main__":
    test_event = {
        'httpMethod': 'POST',
        'headers': {
            'Authorization': 'Bearer your-test-token-here'
        },
        'body': json.dumps({
            'type': 'compliance',
            'title': 'Test Compliance Report'
        }),
        'user': {
            'user_id': 'test-user-id',
            'email': 'test@example.com',
            'role': 'user'
        }
    }
    
    class TestContext:
        aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, TestContext())
    print(json.dumps(result, indent=2))

