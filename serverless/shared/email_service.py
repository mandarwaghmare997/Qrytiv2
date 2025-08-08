"""
AWS SES Email Service for Qrytiv2 Serverless
Handles email sending using Amazon SES

Developed by: Qryti Dev Team
"""

import boto3
import os
import logging
from typing import Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.ses_client = boto3.client('ses')
        self.sender_email = os.environ.get('SENDER_EMAIL', 'no-reply@qryti.com')
        self.sender_name = os.environ.get('SENDER_NAME', 'Qryti Team')
        
    def send_email(self, to_email: str, subject: str, html_body: str, 
                   text_body: str = None) -> bool:
        """Send email using AWS SES"""
        try:
            # Prepare the email
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
            
            if text_body:
                message['Body']['Text'] = {'Data': text_body, 'Charset': 'UTF-8'}
            
            # Send the email
            response = self.ses_client.send_email(
                Source=f"{self.sender_name} <{self.sender_email}>",
                Destination={'ToAddresses': [to_email]},
                Message=message
            )
            
            logger.info(f"Email sent successfully to {to_email}. Message ID: {response['MessageId']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_welcome_email(self, to_email: str, full_name: str, 
                          organization: str = "") -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to Qryti - Your AI Governance Journey Begins!"
        
        html_body = self._create_welcome_email_html(full_name, to_email, organization)
        text_body = self._create_welcome_email_text(full_name, to_email, organization)
        
        return self.send_email(to_email, subject, html_body, text_body)

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        subject = "Qryti - Password Reset Request"
        
        reset_url = f"https://app.qryti.com/reset-password?token={reset_token}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 8px;">
                <h1 style="color: #333; text-align: center;">Password Reset Request</h1>
                <p>You requested a password reset for your Qryti account.</p>
                <p>Click the button below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Reset Password</a>
                </div>
                <p>If you didn't request this reset, please ignore this email.</p>
                <p>This link will expire in 1 hour.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        You requested a password reset for your Qryti account.
        
        Click this link to reset your password: {reset_url}
        
        If you didn't request this reset, please ignore this email.
        This link will expire in 1 hour.
        """
        
        return self.send_email(to_email, subject, html_body, text_body)

    def _create_welcome_email_html(self, name: str, email: str, organization: str = "") -> str:
        """Create HTML welcome email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Qryti</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
                .logo {{ color: white; font-size: 32px; font-weight: bold; margin-bottom: 10px; }}
                .header-text {{ color: white; font-size: 18px; margin: 0; }}
                .content {{ padding: 40px 20px; }}
                .welcome-box {{ background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0; }}
                .welcome-title {{ font-size: 24px; font-weight: bold; color: #0ea5e9; margin-bottom: 10px; }}
                .message {{ color: #374151; line-height: 1.6; margin: 20px 0; }}
                .steps {{ background: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .step {{ margin: 10px 0; padding: 10px; background: white; border-radius: 6px; border-left: 4px solid #3b82f6; }}
                .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 12px; }}
                .account-details {{ background: #f1f5f9; border-radius: 8px; padding: 20px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">QRYTI</div>
                    <p class="header-text">ISO 42001 AI Governance Platform</p>
                </div>
                
                <div class="content">
                    <div class="welcome-box">
                        <div class="welcome-title">Welcome to Qryti!</div>
                        <p style="color: #64748b; margin: 0;">Your AI governance journey starts here</p>
                    </div>
                    
                    <p class="message">
                        Hello <strong>{name}</strong>,<br><br>
                        Welcome to Qryti! Your account has been successfully created and you're now ready to begin your ISO 42001 AI governance journey.
                    </p>
                    
                    <div class="steps">
                        <h3 style="color: #1e293b; margin-bottom: 15px;">Getting Started:</h3>
                        <div class="step">
                            <strong>1. Access Your Dashboard</strong><br>
                            Log in to your personalized dashboard to get started
                        </div>
                        <div class="step">
                            <strong>2. Register AI Models</strong><br>
                            Add your organization's AI models to the registry
                        </div>
                        <div class="step">
                            <strong>3. Track Compliance</strong><br>
                            Monitor your ISO 42001 compliance progress
                        </div>
                        <div class="step">
                            <strong>4. Generate Reports</strong><br>
                            Create professional compliance reports
                        </div>
                    </div>
                    
                    <div class="account-details">
                        <h3 style="color: #1e293b; margin-bottom: 15px;">Your Account Details:</h3>
                        <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
                        <p style="margin: 5px 0;"><strong>Organization:</strong> {organization}</p>
                        <p style="margin: 5px 0;"><strong>Account Type:</strong> Standard User</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://app.qryti.com" class="button">Access Your Dashboard</a>
                    </div>
                    
                    <p class="message">
                        Need help getting started? Our comprehensive documentation and support team are here to assist you every step of the way.
                    </p>
                </div>
                
                <div class="footer">
                    <p>
                        This email was sent to {email}<br>
                        © 2025 Qryti. All rights reserved.<br>
                        ISO 42001 AI Governance Platform
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_welcome_email_text(self, name: str, email: str, organization: str = "") -> str:
        """Create plain text welcome email"""
        return f"""
Welcome to Qryti - ISO 42001 AI Governance Platform

Hello {name},

Welcome to Qryti! Your account has been successfully created.

Getting Started:
1. Log in to your dashboard at https://app.qryti.com
2. Complete your organization profile
3. Start registering your AI models
4. Begin your ISO 42001 compliance journey

Your Account Details:
- Email: {email}
- Organization: {organization}
- Account Type: Standard User

Need Help?
Visit our documentation or contact our support team.

Best regards,
The Qryti Team

© 2025 Qryti. All rights reserved.
ISO 42001 AI Governance Platform
        """

# Global email service instance
email_service = EmailService()

