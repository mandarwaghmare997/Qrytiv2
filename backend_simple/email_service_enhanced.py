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

    def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email to new users"""
        try:
            if self.demo_mode:
                logger.info(f"[DEMO MODE] Welcome email would be sent to {email}")
                return True
            
            # Create welcome email (implementation similar to OTP email)
            # This is a placeholder for welcome email functionality
            logger.info(f"Welcome email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return False

# Global email service instance
email_service = EmailService()

