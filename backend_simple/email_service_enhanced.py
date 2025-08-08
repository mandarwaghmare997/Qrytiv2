"""
Enhanced Email Service for Qrytiv2
Handles OTP generation and email sending with Amazon SES

Developed by: Qryti Dev Team
"""

import smtplib
import random
import string
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Amazon SES Configuration
        self.smtp_server = "email-smtp.us-east-1.amazonaws.com"
        self.smtp_port = 587
        self.sender_email = "no-reply@app.qryti.com"
        
        # AWS SES credentials (should be set as environment variables)
        self.smtp_username = os.environ.get('AWS_SES_SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('AWS_SES_SMTP_PASSWORD', '')
        
        # OTP storage (in production, use Redis or database)
        self.otp_storage: Dict[str, Dict] = {}
        
        # Demo mode flag
        self.demo_mode = not (self.smtp_username and self.smtp_password)
        
        if self.demo_mode:
            logger.info("Email service running in DEMO MODE - OTP codes will be logged to console")
        else:
            logger.info("Email service configured with Amazon SES")

    def generate_otp(self, email: str) -> str:
        """Generate a 6-digit OTP for the given email"""
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store OTP with expiration (5 minutes)
        self.otp_storage[email] = {
            'otp': otp,
            'expires_at': datetime.utcnow() + timedelta(minutes=5),
            'attempts': 0
        }
        
        logger.info(f"Generated OTP for {email}: {otp} (expires in 5 minutes)")
        return otp

    def verify_otp(self, email: str, otp: str) -> bool:
        """Verify the OTP for the given email"""
        if email not in self.otp_storage:
            logger.warning(f"No OTP found for email: {email}")
            return False
        
        stored_data = self.otp_storage[email]
        
        # Check if OTP has expired
        if datetime.utcnow() > stored_data['expires_at']:
            logger.warning(f"OTP expired for email: {email}")
            del self.otp_storage[email]
            return False
        
        # Check attempt limit
        if stored_data['attempts'] >= 3:
            logger.warning(f"Too many OTP attempts for email: {email}")
            del self.otp_storage[email]
            return False
        
        # Verify OTP
        if stored_data['otp'] == otp:
            logger.info(f"OTP verified successfully for email: {email}")
            del self.otp_storage[email]
            return True
        else:
            stored_data['attempts'] += 1
            logger.warning(f"Invalid OTP attempt for email: {email} (attempt {stored_data['attempts']}/3)")
            return False

    def create_otp_email_html(self, otp: str, email: str) -> str:
        """Create HTML email template for OTP"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Qryti - Email Verification</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
                .logo {{ color: white; font-size: 32px; font-weight: bold; margin-bottom: 10px; }}
                .header-text {{ color: white; font-size: 18px; margin: 0; }}
                .content {{ padding: 40px 20px; }}
                .otp-box {{ background: #f1f5f9; border: 2px solid #3b82f6; border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0; }}
                .otp-code {{ font-size: 36px; font-weight: bold; color: #3b82f6; letter-spacing: 8px; margin: 10px 0; }}
                .otp-label {{ color: #64748b; font-size: 14px; margin-bottom: 10px; }}
                .message {{ color: #374151; line-height: 1.6; margin: 20px 0; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; color: #92400e; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 12px; }}
                .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">QRYTI</div>
                    <p class="header-text">Email Verification Required</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #1e293b; margin-bottom: 20px;">Verify Your Email Address</h2>
                    
                    <p class="message">
                        Hello,<br><br>
                        You've requested to verify your email address for your Qryti account. 
                        Please use the verification code below to complete the process.
                    </p>
                    
                    <div class="otp-box">
                        <div class="otp-label">Your Verification Code</div>
                        <div class="otp-code">{otp}</div>
                        <div style="color: #64748b; font-size: 12px; margin-top: 10px;">
                            This code expires in 5 minutes
                        </div>
                    </div>
                    
                    <p class="message">
                        Enter this code in the verification page to complete your email verification.
                        If you didn't request this verification, please ignore this email.
                    </p>
                    
                    <div class="warning">
                        <strong>Security Notice:</strong> Never share this code with anyone. 
                        Qryti will never ask for your verification code via phone or email.
                    </div>
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

    def send_otp_email(self, email: str, otp: str) -> bool:
        """Send OTP email using Amazon SES"""
        try:
            if self.demo_mode:
                # Demo mode - just log the OTP
                logger.info(f"[DEMO MODE] OTP Email for {email}:")
                logger.info(f"[DEMO MODE] Verification Code: {otp}")
                logger.info(f"[DEMO MODE] Email would be sent from: {self.sender_email}")
                logger.info(f"[DEMO MODE] To enable real emails, set AWS_SES_SMTP_USERNAME and AWS_SES_SMTP_PASSWORD environment variables")
                return True
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Qryti - Email Verification Code"
            msg['From'] = self.sender_email
            msg['To'] = email
            
            # Create HTML content
            html_content = self.create_otp_email_html(otp, email)
            html_part = MIMEText(html_content, 'html')
            
            # Create plain text content
            text_content = f"""
Qryti - Email Verification

Hello,

You've requested to verify your email address for your Qryti account.

Your verification code is: {otp}

This code expires in 5 minutes.

Enter this code in the verification page to complete your email verification.
If you didn't request this verification, please ignore this email.

Security Notice: Never share this code with anyone. Qryti will never ask for your verification code via phone or email.

This email was sent to {email}
© 2025 Qryti. All rights reserved.
ISO 42001 AI Governance Platform
            """
            text_part = MIMEText(text_content, 'plain')
            
            # Attach parts
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email via Amazon SES
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"OTP email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {e}")
            return False

    def send_welcome_email(self, email: str, name: str, organization: str = "") -> bool:
        """Send welcome email to new users"""
        try:
            if self.demo_mode:
                logger.info(f"[DEMO MODE] Welcome email would be sent to {email} for {name}")
                logger.info(f"[DEMO MODE] Welcome to Qryti, {name}! Your account has been created successfully.")
                return True
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Welcome to Qryti - Your AI Governance Journey Begins!"
            msg['From'] = self.sender_email
            msg['To'] = email
            
            # Create HTML content
            html_content = self.create_welcome_email_html(name, email, organization)
            html_part = MIMEText(html_content, 'html')
            
            # Create plain text content
            text_content = f"""
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
            text_part = MIMEText(text_content, 'plain')
            
            # Attach parts
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email via Amazon SES
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Welcome email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return False

    def create_welcome_email_html(self, name: str, email: str, organization: str = "") -> str:
        """Create HTML email template for welcome email"""
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

# Global email service instance
email_service = EmailService()

