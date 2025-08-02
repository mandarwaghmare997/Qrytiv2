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
            logger.info("📧 Email service running in demo mode - emails will be logged instead of sent")
        else:
            logger.info(f"📧 Email service configured with Amazon SES for {self.sender_email}")
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """Send an email using Amazon SES SMTP"""
        
        # In demo mode, just log the email
        if self.demo_mode:
            logger.info(f"""
            ===========================================
            📧 EMAIL WOULD BE SENT TO: {to_email}
            📋 SUBJECT: {subject}
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
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def send_otp_email(self, to_email: str, otp_code: str, user_name: str = None) -> bool:
        """Send OTP verification email"""
        subject = "🔐 Qryti - Verification Code for New Device Login"
        
        # Text version for fallback
        text_body = f"""
        Qryti - Verification Code
        
        Hello{' ' + user_name if user_name else ''},
        
        You're trying to sign in to your Qryti account from a new device.
        
        Your verification code is: {otp_code}
        
        This code will expire in 5 minutes.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        The Qryti Team
        """
        
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
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 2rem;
                    font-weight: bold;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                .otp-code {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-size: 2rem;
                    font-weight: bold;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 30px 0;
                    letter-spacing: 0.5rem;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #6c757d;
                    font-size: 0.875rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">QRYTI</div>
                    <h1>🔐 Device Verification</h1>
                    <p>Hello{' ' + user_name if user_name else ''},</p>
                    <p>You're trying to sign in to your Qryti account from a new device.</p>
                </div>
                
                <div class="otp-code">
                    {otp_code}
                </div>
                
                <p style="text-align: center; margin: 20px 0;">
                    Enter this 6-digit code to complete your sign-in.
                </p>
                
                <div class="warning">
                    <strong>⏰ Important:</strong> This code will expire in 5 minutes for security reasons.
                </div>
                
                <p style="text-align: center;">
                    If you didn't request this code, please ignore this email and ensure your account is secure.
                </p>
                
                <div class="footer">
                    <p>Best regards,<br>The Qryti Team</p>
                    <p>ISO 42001 AI Governance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body, text_body)
    
    def send_welcome_email(self, to_email: str, user_name: str, organization: str) -> bool:
        """Send welcome email to new clients"""
        subject = f"🎉 Welcome to Qryti ISO 42001 Platform - {organization}"
        
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
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 2rem;
                    font-weight: bold;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #6c757d;
                    font-size: 0.875rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">QRYTI</div>
                    <h1>🎉 Welcome to ISO 42001 Compliance Platform</h1>
                </div>
                
                <p>Dear {user_name},</p>
                
                <p>Welcome to Qryti! We're excited to help <strong>{organization}</strong> achieve ISO 42001 compliance for your AI management systems.</p>
                
                <div class="features">
                    <h3>What you can do with Qryti:</h3>
                    <p>✅ Conduct comprehensive gap assessments<br>
                    📊 Track compliance progress in real-time<br>
                    📋 Manage evidence and documentation<br>
                    🏆 Generate compliance certificates<br>
                    🔍 Monitor AI system governance</p>
                </div>
                
                <p>Your compliance project has been automatically created and is ready for you to begin the assessment process.</p>
                
                <div style="text-align: center;">
                    <a href="https://app.qryti.com" class="cta-button">Start Your Assessment</a>
                </div>
                
                <p>If you have any questions or need assistance, our support team is here to help.</p>
                
                <div class="footer">
                    <p>Best regards,<br>The Qryti Team</p>
                    <p>© 2025 Qryti ISO 42001 Platform. All rights reserved.</p>
                    <p>Contact us: support@qryti.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body, text_body)

# Global email service instance
email_service = EmailService()

