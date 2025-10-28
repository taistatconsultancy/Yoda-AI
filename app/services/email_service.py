"""
Email service for sending notifications, invitations, and verifications
"""

from typing import Optional, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
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
        text_content: Optional[str] = None,
        attachments: Optional[List[tuple]] = None
    ) -> bool:
        """
        Send an email with optional attachments
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content
            attachments: List of tuples (filename, content, mime_type)
        """
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
            
            # Add attachments
            if attachments:
                for filename, content, mime_type in attachments:
                    # Handle different content types
                    if isinstance(content, bytes):
                        # For binary content like .ics files
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(content)
                        encoders.encode_base64(part)
                    else:
                        # For text content
                        part = MIMEBase('application', mime_type)
                        part.set_payload(content)
                        encoders.encode_base64(part)
                    
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    part.add_header('Content-Type', f'{mime_type}; name="{filename}"')
                    msg.attach(part)
            
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
        subject = "Please verify your email to activate your YodaAI account"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email - YodaAI</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .email-wrapper {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
                .content {{ padding: 40px 30px; }}
                .greeting {{ font-size: 20px; font-weight: 600; color: #333; margin-bottom: 15px; }}
                .message {{ color: #555; margin-bottom: 20px; font-size: 16px; }}
                .verify-button-wrapper {{ text-align: center; margin: 35px 0; }}
                .verify-button {{ display: inline-block; padding: 18px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); transition: transform 0.2s; }}
                .verify-button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5); }}
                .link-box {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 25px 0; border-radius: 4px; }}
                .link-text {{ font-family: 'Courier New', monospace; font-size: 12px; word-break: break-all; color: #666; }}
                .important-note {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 25px 0; border-radius: 4px; }}
                .important-note strong {{ color: #856404; }}
                .security-note {{ background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 25px 0; border-radius: 4px; }}
                .features {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; }}
                .features-title {{ font-weight: 600; color: #667eea; margin-bottom: 12px; font-size: 16px; }}
                .features ul {{ margin: 0; padding-left: 20px; color: #555; }}
                .features li {{ margin: 8px 0; }}
                .footer {{ background: #f8f9fa; padding: 25px; text-align: center; color: #666; font-size: 13px; border-top: 1px solid #e0e0e0; }}
                .footer p {{ margin: 5px 0; }}
                .help-link {{ color: #667eea; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="header">
                    <h1>🎯 YodaAI</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.95; font-size: 16px;">AI-Powered Retrospective Assistant</p>
                </div>
                
                <div class="content">
                    <div class="greeting">Hello {full_name}!</div>
                    
                    <div class="message">
                        Thank you for creating your YodaAI account! We're excited to have you on board and help you run effective retrospectives with AI-powered insights.
                    </div>
                    
                    <div class="security-note">
                        <strong>🔒 Security Notice:</strong><br>
                        To ensure the security of your account and protect your data, please verify your email address by clicking the button below. This helps us confirm that you own this email address and prevent unauthorized account access.
                    </div>
                    
                    <div class="verify-button-wrapper">
                        <a href="{verification_link}" class="verify-button">✓ Verify My Email Address</a>
                    </div>
                    
                    <div class="link-box">
                        <div style="font-size: 12px; color: #666; margin-bottom: 8px; font-weight: 600;">Or copy and paste this link into your browser:</div>
                        <div class="link-text">{verification_link}</div>
                    </div>
                    
                    <div class="important-note">
                        <strong>⏰ Important:</strong> This verification link will expire in <strong>24 hours</strong>. If you didn't create a YodaAI account, you can safely ignore this email - no action is needed.
                    </div>
                    
                    <div class="message">
                        Didn't expect this email? No worries - if you didn't sign up for YodaAI, you can safely ignore this message. Your email will not be added to any mailing lists.
                    </div>
                    
                    <div class="features">
                        <div class="features-title">✨ Once verified, you'll be able to:</div>
                        <ul>
                            <li>Create and manage workspaces for your team</li>
                            <li>Run AI-guided 4Ls retrospectives</li>
                            <li>Track action items and insights</li>
                            <li>Collaborate with team members in real-time</li>
                            <li>Get AI-powered recommendations for improvement</li>
                        </ul>
                    </div>
                    
                    <div class="message" style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        If you're having trouble verifying your account, please <a href="mailto:support@yodaai.com" class="help-link">contact our support team</a> and we'll be happy to help.
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>YodaAI</strong></p>
                    <p>AI-Powered Retrospective Assistant for Agile Teams</p>
                    <p style="margin-top: 15px; font-size: 11px; color: #999;">
                        © 2025 YodaAI. All rights reserved.<br>
                        This is an automated message. Please do not reply to this email.
                    </p>
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

    def send_calendar_invite_email(
        self,
        to_email: str,
        full_name: str,
        retrospective_title: str,
        sprint_name: str,
        start_time: datetime,
        end_time: datetime,
        workspace_name: str,
        facilitator_name: str,
        ics_content: bytes,
        retro_link: str
    ) -> bool:
        """Send calendar invite email with .ics attachment"""
        
        # Convert to Kenya time for display
        from app.services.timezone_utils import format_kenya_datetime, utc_to_kenya_time
        
        kenya_start = utc_to_kenya_time(start_time)
        kenya_end = utc_to_kenya_time(end_time)
        
        # Format dates in Kenya time
        start_date = format_kenya_datetime(start_time, "%B %d, %Y")
        start_time_str = format_kenya_datetime(start_time, "%I:%M %p EAT")
        end_time_str = format_kenya_datetime(end_time, "%I:%M %p EAT")
        
        subject = f"📅 {retrospective_title} - Retrospective Scheduled for {start_date}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Retrospective Calendar Invite</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .email-wrapper {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
                .content {{ padding: 40px 30px; }}
                .event-info {{ background: #f8f9fa; border-radius: 8px; padding: 25px; margin: 25px 0; }}
                .event-row {{ display: flex; margin: 15px 0; align-items: flex-start; }}
                .event-icon {{ font-size: 24px; margin-right: 15px; min-width: 30px; }}
                .event-details {{ flex: 1; }}
                .event-label {{ font-weight: 600; color: #667eea; margin-bottom: 5px; font-size: 13px; text-transform: uppercase; }}
                .event-value {{ font-size: 16px; color: #333; }}
                .calendar-buttons {{ margin: 30px 0; text-align: center; }}
                .calendar-button {{ display: inline-block; margin: 8px; padding: 14px 28px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px; }}
                .calendar-button:hover {{ background: #5568d3; }}
                .note {{ background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 25px 0; border-radius: 4px; font-size: 14px; color: #0c5460; }}
                .footer {{ background: #f8f9fa; padding: 25px; text-align: center; color: #666; font-size: 13px; border-top: 1px solid #e0e0e0; }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="header">
                    <h1>📅 Retrospective Scheduled</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.95;">Add to your calendar</p>
                </div>
                
                <div class="content">
                    <p style="font-size: 18px; font-weight: 600; color: #333;">Hello {full_name}!</p>
                    
                    <p style="color: #555; font-size: 16px;">
                        A new retrospective has been scheduled for your workspace. Add it to your calendar to receive reminders!
                    </p>
                    
                    <div class="event-info">
                        <div class="event-row">
                            <div class="event-icon">📋</div>
                            <div class="event-details">
                                <div class="event-label">Title</div>
                                <div class="event-value"><strong>{retrospective_title}</strong></div>
                            </div>
                        </div>
                        
                        <div class="event-row">
                            <div class="event-icon">🏃</div>
                            <div class="event-details">
                                <div class="event-label">Sprint</div>
                                <div class="event-value">{sprint_name}</div>
                            </div>
                        </div>
                        
                        <div class="event-row">
                            <div class="event-icon">👥</div>
                            <div class="event-details">
                                <div class="event-label">Workspace</div>
                                <div class="event-value">{workspace_name}</div>
                            </div>
                        </div>
                        
                        <div class="event-row">
                            <div class="event-icon">👤</div>
                            <div class="event-details">
                                <div class="event-label">Facilitator</div>
                                <div class="event-value">{facilitator_name}</div>
                            </div>
                        </div>
                        
                        <div class="event-row">
                            <div class="event-icon">📅</div>
                            <div class="event-details">
                                <div class="event-label">Date</div>
                                <div class="event-value">{start_date}</div>
                            </div>
                        </div>
                        
                        <div class="event-row">
                            <div class="event-icon">🕐</div>
                            <div class="event-details">
                                <div class="event-label">Time</div>
                                <div class="event-value">{start_time_str} - {end_time_str}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="calendar-buttons">
                        <a href="{retro_link}" class="calendar-button" style="background: #667eea;">View in YodaAI</a>
                    </div>
                    
                    <div class="note">
                        <strong>📎 Calendar Attachment:</strong> We've attached a calendar file (.ics) to this email. Simply double-click the attachment to add this event to your calendar, or drag it into your calendar app. The event includes a 15-minute reminder!
                    </div>
                    
                    <p style="color: #555; font-size: 14px; margin-top: 25px;">
                        <strong>What to expect:</strong> This retrospective will help your team reflect on the sprint using the 4Ls framework (Liked, Learned, Lacked, Longed for). AI will help facilitate the discussion and capture insights.
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>YodaAI</strong></p>
                    <p>AI-Powered Retrospective Assistant for Agile Teams</p>
                    <p style="margin-top: 15px; font-size: 11px; color: #999;">
                        © 2025 YodaAI. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email with .ics attachment
        try:
            print(f"📧 Sending calendar invite to {to_email}")
            print(f"   iCal content size: {len(ics_content)} bytes")
            print(f"   iCal content type: {type(ics_content)}")
            
            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                attachments=[('retrospective.ics', ics_content, 'text/calendar')]
            )
        except Exception as e:
            print(f"❌ Error sending calendar invite: {e}")
            print(f"   iCal content preview: {ics_content[:100]}...")
            return False


# Singleton instance
email_service = EmailService()

