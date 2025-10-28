"""
Email service for sending notifications, invitations, and verifications
"""

from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email"""
        try:
            if not settings.ENABLE_EMAIL_NOTIFICATIONS:
                logger.info(f"📧 Email notifications disabled. Would send to {to_email}: {subject}")
                # Print verification link to console for testing
                if "verify" in subject.lower() or "Verify" in subject:
                    logger.info("="*60)
                    logger.info("EMAIL VERIFICATION LINK (check console):")
                    logger.info("="*60)
                    # Extract link from HTML
                    import re
                    links = re.findall(r'href="([^"]+verify[^"]+)"', html_content)
                    if links:
                        logger.info(f"Click here to verify: {links[0]}")
                    logger.info("="*60)
                return True
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def send_verification_email(self, to_email: str, verification_link: str, full_name: str) -> bool:
        """Send email verification link"""
        subject = "Verify your YodaAI email address"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .code-box {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; font-family: monospace; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Welcome to YodaAI!</h1>
                </div>
                <div class="content">
                    <h2>Hi {full_name},</h2>
                    <p>Thank you for signing up for YodaAI - your AI-powered retrospective assistant!</p>
                    <p>To complete your registration and start using YodaAI, please verify your email address by clicking the button below:</p>
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">✓ Verify Email Address</a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <div class="code-box">{verification_link}</div>
                    <p><strong>⏰ This link will expire in 24 hours.</strong></p>
                    <p>If you didn't create an account with YodaAI, you can safely ignore this email.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 14px;">
                        Once verified, you'll be able to:
                        <ul>
                            <li>Create and manage workspaces</li>
                            <li>Run AI-guided retrospectives</li>
                            <li>Track action items and insights</li>
                            <li>Collaborate with your team</li>
                        </ul>
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 YodaAI. All rights reserved.</p>
                    <p>AI-Powered Retrospective Assistant for Agile Teams</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to YodaAI!
        
        Hi {full_name},
        
        Thank you for signing up! Please verify your email by visiting:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create this account, please ignore this email.
        
        ---
        YodaAI - AI-Powered Retrospective Assistant
        © 2025 All rights reserved
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_invitation_token() -> str:
        """Generate a secure invitation token"""
        return secrets.token_urlsafe(32)


# Singleton instance
email_service = EmailService()

