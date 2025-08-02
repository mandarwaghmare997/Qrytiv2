"""
Email Service using Amazon SES
Handles OTP emails, notifications, and compliance reminders
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Amazon SES SMTP Configuration
        self.smtp_server = "email-smtp.us-east-1.amazonaws.com"
        self.smtp_port = 587
        self.sender_email = "no-reply@app.qryti.com"
        self.sender_name = "Qryti ISO 42001 Platform"
        
        # Get SES credentials from environment variables
        self.smtp_username = os.environ.get('AWS_SES_SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('AWS_SES_SMTP_PASSWORD', '')
        
        # For demo/development, we'll simulate email sending
        self.demo_mode = not (self.smtp_username and self.smtp_password)
        
        if self.demo_mode:
            logger.info("Email service running in demo mode - emails will be logged instead of sent")
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """Send an email using Amazon SES SMTP"""
        
        # In demo mode, just log the email
        if self.demo_mode:
            logger.info(f"""
            ===========================================
            EMAIL WOULD BE SENT TO: {to_email}
            SUBJECT: {subject}
            ===========================================
            {text_body or 'HTML email body (see logs for full content)'}
            ===========================================
            """)
            return True
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email
            
            # Add text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, "plain")
                message.attach(text_part)
            
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_otp_email(self, to_email: str, otp_code: str, user_name: str = None) -> bool:
        """Send OTP verification email"""
        subject = "Qryti - Verification Code for New Device Login"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verification Code</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 10px;
                }}
                .otp-code {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    font-size: 32px;
                    font-weight: bold;
                    text-align: center;
                    padding: 20px;
                    border-radius: 12px;
                    letter-spacing: 8px;
                    margin: 30px 0;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">QRYTI</div>
                    <h2>New Device Login Verification</h2>
                </div>
                
                <p>Hello{f" {user_name}" if user_name else ""},</p>
                
                <p>We detected a login attempt from a new device. To ensure the security of your account, please use the verification code below:</p>
                
                <div class="otp-code">{otp_code}</div>
                
                <p>This code will expire in <strong>5 minutes</strong>.</p>
                
                <div class="warning">
                    <strong>Security Notice:</strong> If you didn't attempt to log in, please ignore this email and consider changing your password.
                </div>
                
                <p>If you have any questions, please contact our support team.</p>
                
                <div class="footer">
                    <p>© 2025 Qryti ISO 42001 Platform. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text version for email clients that don't support HTML
        text_body = f"""
        QRYTI - New Device Login Verification
        
        Hello{f" {user_name}" if user_name else ""},
        
        We detected a login attempt from a new device. To ensure the security of your account, please use the verification code below:
        
        Verification Code: {otp_code}
        
        This code will expire in 5 minutes.
        
        Security Notice: If you didn't attempt to log in, please ignore this email and consider changing your password.
        
        © 2025 Qryti ISO 42001 Platform. All rights reserved.
        """
        
        return self.send_email(to_email, subject, html_body, text_body)
    
    def send_welcome_email(self, to_email: str, user_name: str, organization: str) -> bool:
        """Send welcome email to new clients"""
        subject = f"Welcome to Qryti ISO 42001 Platform - {organization}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Qryti</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 10px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    text-decoration: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .features {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .feature-item {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">QRYTI</div>
                    <h2>Welcome to ISO 42001 Compliance Platform</h2>
                </div>
                
                <p>Dear {user_name},</p>
                
                <p>Welcome to Qryti! We're excited to help {organization} achieve ISO 42001 compliance for your AI management systems.</p>
                
                <div class="features">
                    <h3>What you can do with Qryti:</h3>
                    <div class="feature-item">✅ Conduct comprehensive gap assessments</div>
                    <div class="feature-item">📊 Track compliance progress in real-time</div>
                    <div class="feature-item">📋 Manage evidence and documentation</div>
                    <div class="feature-item">🏆 Generate compliance certificates</div>
                    <div class="feature-item">🔍 Monitor AI system governance</div>
                </div>
                
                <p>Your compliance project has been automatically created and is ready for you to begin the assessment process.</p>
                
                <div style="text-align: center;">
                    <a href="https://app.qryti.com" class="cta-button">Start Your Assessment</a>
                </div>
                
                <p>If you have any questions or need assistance, our support team is here to help.</p>
                
                <div class="footer">
                    <p>© 2025 Qryti ISO 42001 Platform. All rights reserved.</p>
                    <p>Contact us: support@qryti.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to Qryti ISO 42001 Platform
        
        Dear {user_name},
        
        Welcome to Qryti! We're excited to help {organization} achieve ISO 42001 compliance for your AI management systems.
        
        What you can do with Qryti:
        - Conduct comprehensive gap assessments
        - Track compliance progress in real-time
        - Manage evidence and documentation
        - Generate compliance certificates
        - Monitor AI system governance
        
        Your compliance project has been automatically created and is ready for you to begin the assessment process.
        
        Visit: https://app.qryti.com
        
        If you have any questions or need assistance, our support team is here to help.
        
        © 2025 Qryti ISO 42001 Platform. All rights reserved.
        Contact us: support@qryti.com
        """
        
        return self.send_email(to_email, subject, html_body, text_body)
    
    def send_compliance_reminder(self, to_email: str, user_name: str, project_name: str, days_remaining: int) -> bool:
        """Send compliance deadline reminder"""
        subject = f"Compliance Reminder: {project_name} - {days_remaining} days remaining"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Compliance Reminder</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 10px;
                }}
                .reminder-box {{
                    background: linear-gradient(135deg, #f59e0b, #d97706);
                    color: white;
                    text-align: center;
                    padding: 20px;
                    border-radius: 12px;
                    margin: 20px 0;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    text-decoration: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">QRYTI</div>
                    <h2>Compliance Deadline Reminder</h2>
                </div>
                
                <p>Dear {user_name},</p>
                
                <p>This is a friendly reminder about your upcoming compliance deadline for:</p>
                
                <div class="reminder-box">
                    <h3>{project_name}</h3>
                    <p style="font-size: 24px; margin: 10px 0;"><strong>{days_remaining} days remaining</strong></p>
                </div>
                
                <p>To ensure you meet your compliance deadline, we recommend:</p>
                <ul>
                    <li>Complete any pending gap assessment items</li>
                    <li>Upload required evidence and documentation</li>
                    <li>Review and validate all compliance controls</li>
                    <li>Schedule final compliance review</li>
                </ul>
                
                <div style="text-align: center;">
                    <a href="https://app.qryti.com" class="cta-button">Continue Assessment</a>
                </div>
                
                <p>If you need assistance or have questions about your compliance project, please don't hesitate to contact our support team.</p>
                
                <div class="footer">
                    <p>© 2025 Qryti ISO 42001 Platform. All rights reserved.</p>
                    <p>Contact us: support@qryti.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Qryti - Compliance Deadline Reminder
        
        Dear {user_name},
        
        This is a friendly reminder about your upcoming compliance deadline for:
        
        Project: {project_name}
        Days Remaining: {days_remaining}
        
        To ensure you meet your compliance deadline, we recommend:
        - Complete any pending gap assessment items
        - Upload required evidence and documentation
        - Review and validate all compliance controls
        - Schedule final compliance review
        
        Visit: https://app.qryti.com
        
        If you need assistance or have questions about your compliance project, please don't hesitate to contact our support team.
        
        © 2025 Qryti ISO 42001 Platform. All rights reserved.
        Contact us: support@qryti.com
        """
        
        return self.send_email(to_email, subject, html_body, text_body)

# Global email service instance
email_service = EmailService()

