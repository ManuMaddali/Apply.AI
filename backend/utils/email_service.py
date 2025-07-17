import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from jinja2 import Template
from pathlib import Path
import logging
from datetime import datetime

from config.security import get_security_settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending verification, password reset, and notification emails"""
    
    def __init__(self):
        self.settings = get_security_settings()
        self.template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self._ensure_template_dir()
    
    def _ensure_template_dir(self):
        """Ensure the email templates directory exists"""
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_smtp_connection(self):
        """Get SMTP connection"""
        try:
            logger.info(f"🔗 Connecting to SMTP server: {self.settings.smtp_server}:{self.settings.smtp_port}")
            
            # Create SMTP connection
            server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port)
            
            if self.settings.smtp_use_tls:
                logger.info("🔐 Starting TLS encryption")
                server.starttls()
            
            if self.settings.smtp_username and self.settings.smtp_password:
                logger.info(f"🔑 Authenticating with username: {self.settings.smtp_username}")
                server.login(self.settings.smtp_username, self.settings.smtp_password)
                logger.info("✅ SMTP authentication successful")
            
            return server
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP authentication failed: {e}")
            logger.error(f"   Username: {self.settings.smtp_username}")
            logger.error(f"   Server: {self.settings.smtp_server}:{self.settings.smtp_port}")
            logger.error(f"   TLS: {self.settings.smtp_use_tls}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to connect to SMTP server: {e}")
            raise
    
    def _load_template(self, template_name: str) -> str:
        """Load email template"""
        template_path = self.template_dir / f"{template_name}.html"
        
        if not template_path.exists():
            # Return a default template if file doesn't exist
            return self._get_default_template(template_name)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_default_template(self, template_name: str) -> str:
        """Get default email template"""
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
                .content { padding: 30px; background: #f9f9f9; }
                .button { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ app_name }}</h1>
                </div>
                <div class="content">
                    {{ content }}
                </div>
                <div class="footer">
                    <p>{{ app_name }} - Streamline your job applications with AI-powered resume optimization</p>
                    <p>If you didn't request this email, please ignore it.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        if template_name == "verification":
            content = """
            <h2>Welcome to {{ app_name }}!</h2>
            <p>Hello {{ user_name }},</p>
            <p>Thank you for registering with ApplyAI. To complete your registration, please verify your email address by clicking the button below:</p>
            <p><a href="{{ verification_url }}" class="button">Verify Email Address</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p><a href="{{ verification_url }}">{{ verification_url }}</a></p>
            <p>This verification link will expire in 24 hours.</p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "password_reset":
            content = """
            <h2>Password Reset Request</h2>
            <p>Hello {{ user_name }},</p>
            <p>We received a request to reset your password for your ApplyAI account.</p>
            <p>Click the button below to reset your password:</p>
            <p><a href="{{ reset_url }}" class="button">Reset Password</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p><a href="{{ reset_url }}">{{ reset_url }}</a></p>
            <p>This reset link will expire in 1 hour.</p>
            <p>If you didn't request this password reset, please ignore this email.</p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        else:
            content = "{{ content }}"
        
        return base_template.replace("{{ content }}", content)
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        template_name: str, 
        template_data: Dict[str, Any],
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send email using template"""
        try:
            # Load and render template
            template_content = self._load_template(template_name)
            template = Template(template_content)
            
            # Add common template data
            template_data.update({
                'app_name': self.settings.email_from_name,
                'subject': subject,
                'current_year': datetime.now().year
            })
            
            html_body = template.render(**template_data)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.settings.email_from_name} <{self.settings.email_from}>"
            msg['To'] = to_email
            
            # Add HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            if self.settings.environment == "development" and (not self.settings.smtp_username or not self.settings.smtp_password):
                # In development without SMTP, just log the email
                logger.info(f"📧 Email would be sent to {to_email}")
                logger.info(f"📧 Subject: {subject}")
                logger.info(f"📧 Template: {template_name}")
                logger.info(f"📧 Data: {template_data}")
                return True
            
            try:
                with self._get_smtp_connection() as server:
                    server.send_message(msg)
                    logger.info(f"✅ Email sent successfully to {to_email}")
                    return True
            except Exception as smtp_error:
                logger.error(f"❌ SMTP send failed to {to_email}: {smtp_error}")
                # In development, we'll still return True to not block the flow
                if self.settings.environment == "development":
                    logger.info(f"📧 Development mode: Email would be sent to {to_email}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add attachment to email"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Failed to add attachment {file_path}: {e}")
    
    def send_verification_email(self, user_email: str, user_name: str, verification_token: str) -> bool:
        """Send email verification email"""
        # Use localhost:3000 for development, first CORS origin for production
        if self.settings.environment == "development":
            frontend_url = "http://localhost:3000"
        else:
            frontend_url = self.settings.get_cors_origins()[0] if self.settings.get_cors_origins() else "http://localhost:3000"
        verification_url = f"{frontend_url}/verify-email?token={verification_token}"
        
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'verification_url': verification_url,
            'verification_token': verification_token
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Verify your ApplyAI account",
            template_name="verification",
            template_data=template_data
        )
    
    def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        # Use localhost:3000 for development, first CORS origin for production
        if self.settings.environment == "development":
            frontend_url = "http://localhost:3000"
        else:
            frontend_url = self.settings.get_cors_origins()[0] if self.settings.get_cors_origins() else "http://localhost:3000"
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'reset_url': reset_url,
            'reset_token': reset_token
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Reset your ApplyAI password",
            template_name="password_reset",
            template_data=template_data
        )
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email after successful verification"""
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'app_url': self.settings.get_cors_origins()[0] if self.settings.get_cors_origins() else "http://localhost:3000"
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Welcome to ApplyAI! 🎉",
            template_name="welcome",
            template_data=template_data
        )
    
    def send_password_changed_notification(self, user_email: str, user_name: str) -> bool:
        """Send notification when password is changed"""
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'change_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Your ApplyAI password has been changed",
            template_name="password_changed",
            template_data=template_data
        )

# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service 