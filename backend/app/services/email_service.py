"""
Email service for sending notifications
Handles verification emails, password resets, and other notifications

Developed by: Qryti Dev Team
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import security_utils

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.FROM_EMAIL
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email using SMTP"""
        try:
            # Skip email sending if SMTP is not configured
            if not self.smtp_host or not self.smtp_username:
                logger.warning("SMTP not configured - email sending skipped")
                logger.info(f"Would send email to {to_email}: {subject}")
                return True
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_verification_email(self, email: str, full_name: str) -> bool:
        """Send email verification email"""
        try:
            # Create verification token
            verification_token = security_utils.create_access_token(
                data={"sub": email, "type": "verification"},
                expires_delta=timedelta(hours=24)
            )
            
            # Create verification URL
            verification_url = f"https://app.qryti.com/verify-email?token={verification_token}"
            
            # Email content
            subject = "Verify your Qrytiv2 account"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Verify Your Email</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Qrytiv2!</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {full_name},</h2>
                        <p>Thank you for registering with Qrytiv2, your ISO 42001 AI Governance Platform.</p>
                        <p>To complete your registration, please verify your email address by clicking the button below:</p>
                        <p style="text-align: center;">
                            <a href="{verification_url}" class="button">Verify Email Address</a>
                        </p>
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p><a href="{verification_url}">{verification_url}</a></p>
                        <p>This verification link will expire in 24 hours.</p>
                        <p>If you didn't create an account with Qrytiv2, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 Qrytiv2. All rights reserved.</p>
                        <p>This is an automated email. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Welcome to Qrytiv2!
            
            Hi {full_name},
            
            Thank you for registering with Qrytiv2, your ISO 42001 AI Governance Platform.
            
            To complete your registration, please verify your email address by visiting:
            {verification_url}
            
            This verification link will expire in 24 hours.
            
            If you didn't create an account with Qrytiv2, please ignore this email.
            
            © 2025 Qrytiv2. All rights reserved.
            """
            
            return self._send_email(email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {e}")
            return False
    
    def send_password_reset_email(self, email: str, full_name: str) -> bool:
        """Send password reset email"""
        try:
            # Create reset token
            reset_token = security_utils.create_access_token(
                data={"sub": email, "type": "reset"},
                expires_delta=timedelta(hours=1)
            )
            
            # Create reset URL
            reset_url = f"https://app.qryti.com/reset-password?token={reset_token}"
            
            # Email content
            subject = "Reset your Qrytiv2 password"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Reset Your Password</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #ef4444; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #ef4444; color: white; text-decoration: none; border-radius: 5px; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <h2>Hi {full_name},</h2>
                        <p>We received a request to reset your password for your Qrytiv2 account.</p>
                        <p>To reset your password, click the button below:</p>
                        <p style="text-align: center;">
                            <a href="{reset_url}" class="button">Reset Password</a>
                        </p>
                        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                        <p><a href="{reset_url}">{reset_url}</a></p>
                        <p>This reset link will expire in 1 hour.</p>
                        <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 Qrytiv2. All rights reserved.</p>
                        <p>This is an automated email. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Password Reset Request
            
            Hi {full_name},
            
            We received a request to reset your password for your Qrytiv2 account.
            
            To reset your password, visit:
            {reset_url}
            
            This reset link will expire in 1 hour.
            
            If you didn't request a password reset, please ignore this email.
            
            © 2025 Qrytiv2. All rights reserved.
            """
            
            return self._send_email(email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return False
    
    def send_welcome_email(self, email: str, full_name: str, organization_name: str) -> bool:
        """Send welcome email after successful verification"""
        try:
            subject = "Welcome to Qrytiv2 - Your AI Governance Journey Begins!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to Qrytiv2</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                    .feature {{ margin: 15px 0; padding: 15px; background: white; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Qrytiv2!</h1>
                        <p>Your ISO 42001 AI Governance Platform</p>
                    </div>
                    <div class="content">
                        <h2>Hi {full_name},</h2>
                        <p>Congratulations! Your Qrytiv2 account for <strong>{organization_name}</strong> is now active.</p>
                        
                        <h3>What's Next?</h3>
                        <div class="feature">
                            <h4>🎯 Start Your Compliance Journey</h4>
                            <p>Begin with our Requirements Analysis module to map your AI inventory and identify stakeholders.</p>
                        </div>
                        
                        <div class="feature">
                            <h4>📊 Track Your Progress</h4>
                            <p>Monitor your ISO 42001 compliance score in real-time with our automated scoring system.</p>
                        </div>
                        
                        <div class="feature">
                            <h4>🤖 Manage AI Models</h4>
                            <p>Register and track your AI models with our comprehensive model registry.</p>
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="https://app.qryti.com/dashboard" class="button">Access Your Dashboard</a>
                        </p>
                        
                        <p>Need help getting started? Check out our <a href="https://app.qryti.com/guides">Quick Start Guide</a> or contact our support team.</p>
                    </div>
                    <div class="footer">
                        <p>© 2025 Qrytiv2. All rights reserved.</p>
                        <p>Questions? Contact us at support@qryti.com</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return False

# Global email service instance
email_service = EmailService()

# Convenience functions
def send_verification_email(email: str, full_name: str) -> bool:
    """Send verification email"""
    return email_service.send_verification_email(email, full_name)

def send_password_reset_email(email: str, full_name: str) -> bool:
    """Send password reset email"""
    return email_service.send_password_reset_email(email, full_name)

def send_welcome_email(email: str, full_name: str, organization_name: str) -> bool:
    """Send welcome email"""
    return email_service.send_welcome_email(email, full_name, organization_name)

