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
        elif template_name == "payment_failure_reminder":
            content = """
            <h2>Payment Issue - Action Required</h2>
            <p>Hello {{ user_name }},</p>
            <p>We encountered an issue processing your payment for your ApplyAI Pro subscription.</p>
            <p>Your subscription is currently in a grace period and will expire on <strong>{{ period_end }}</strong> 
            ({{ days_remaining }} days remaining) if payment is not resolved.</p>
            <p>To continue enjoying Pro features, please update your payment method:</p>
            <p><a href="{{ update_payment_url }}" class="button">Update Payment Method</a></p>
            <p>If you have any questions, please contact our support team.</p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "final_grace_warning":
            content = """
            <h2>Final Notice - Subscription Cancellation</h2>
            <p>Hello {{ user_name }},</p>
            <p>This is your final notice regarding the payment issue with your ApplyAI Pro subscription.</p>
            <p>Your subscription will be canceled and downgraded to Free after <strong>{{ period_end }}</strong> 
            if payment is not resolved immediately.</p>
            <p><strong>Action Required:</strong> Update your payment method now to avoid service interruption:</p>
            <p><a href="{{ update_payment_url }}" class="button">Update Payment Method Now</a></p>
            <p>Once downgraded, you'll lose access to Pro features including unlimited resume processing, 
            advanced formatting, and premium templates.</p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "subscription_welcome":
            content = """
            <h2>Welcome to Pro! 🚀</h2>
            <p>Hello {{ user_name }},</p>
            <p>Congratulations! Your Pro subscription is now active. You now have access to all premium features:</p>
            <ul>
                {% for feature in features %}
                <li>{{ feature }}</li>
                {% endfor %}
            </ul>
            <p><strong>Subscription Details:</strong></p>
            <ul>
                <li>Plan: {{ subscription_tier }}</li>
                <li>Billing: {{ billing_amount }} {{ billing_cycle }}</li>
                <li>Next billing: {{ next_billing_date }}</li>
            </ul>
            <p><a href="{{ dashboard_url }}" class="button">Manage Subscription</a></p>
            <p>Need help? <a href="{{ support_url }}">Contact our support team</a></p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "payment_failed":
            content = """
            <h2>Action Required: Payment Failed</h2>
            <p>Hello {{ user_name }},</p>
            <p>We were unable to process your payment of {{ payment_amount }} for your Pro subscription.</p>
            <p><strong>Reason:</strong> {{ failure_reason }}</p>
            {% if retry_count > 0 %}
            <p>This is attempt #{{ retry_count }}. {% if next_retry_date %}We'll try again on {{ next_retry_date }}.{% endif %}</p>
            {% endif %}
            <p>To avoid service interruption, please:</p>
            <ul>
                {% for action in suggested_actions %}
                <li>{{ action }}</li>
                {% endfor %}
            </ul>
            <p><a href="{{ update_payment_url }}" class="button">Update Payment Method</a></p>
            <p>You have {{ grace_period_days }} days to resolve this before your account is downgraded to Free.</p>
            <p>Questions? <a href="{{ support_url }}">Contact support</a></p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "usage_limit_warning":
            content = """
            <h2>You're Almost at Your Limit</h2>
            <p>Hello {{ user_name }},</p>
            <p>You've used {{ current_usage }} of your {{ usage_limit }} weekly resume processing sessions.</p>
            <p>You have {{ remaining_sessions }} sessions remaining until {{ reset_date }}.</p>
            <p><strong>Upgrade to Pro for unlimited access:</strong></p>
            <ul>
                {% for benefit in pro_benefits %}
                <li>{{ benefit }}</li>
                {% endfor %}
            </ul>
            <p><a href="{{ upgrade_url }}" class="button">Upgrade to Pro</a></p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "usage_limit_exceeded":
            content = """
            <h2>Weekly Limit Reached</h2>
            <p>Hello {{ user_name }},</p>
            <p>You've reached your weekly limit of {{ usage_limit }} resume processing sessions.</p>
            <p>Your limit will reset on {{ reset_date }}.</p>
            <p><strong>Don't wait - upgrade to Pro for {{ pro_price }}:</strong></p>
            <ul>
                {% for benefit in pro_benefits %}
                <li>{{ benefit }}</li>
                {% endfor %}
            </ul>
            <p><a href="{{ upgrade_url }}" class="button">Upgrade Now</a></p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "subscription_canceled":
            content = """
            <h2>Subscription Canceled</h2>
            <p>Hello {{ user_name }},</p>
            <p>Your Pro subscription has been canceled.</p>
            {% if not cancellation_immediate %}
            <p>You'll continue to have Pro access until {{ access_until }}.</p>
            {% else %}
            <p>Your account has been downgraded to Free immediately.</p>
            {% endif %}
            <p><strong>You'll lose access to:</strong></p>
            <ul>
                {% for feature in features_lost %}
                <li>{{ feature }}</li>
                {% endfor %}
            </ul>
            <p>Changed your mind? <a href="{{ reactivate_url }}" class="button">Reactivate Subscription</a></p>
            <p>We'd love your feedback: <a href="{{ feedback_url }}">Tell us why you canceled</a></p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "grace_period_warning":
            content = """
            <h2>Urgent: Update Your Payment Method</h2>
            <p>Hello {{ user_name }},</p>
            <p><strong>Your Pro subscription will be downgraded in {{ days_remaining }} day(s).</strong></p>
            <p>We've been unable to process your payment of {{ payment_amount }}.</p>
            <p>To keep your Pro features, please update your payment method immediately:</p>
            <ul>
                {% for feature in features_at_risk %}
                <li>{{ feature }}</li>
                {% endfor %}
            </ul>
            <p><a href="{{ update_payment_url }}" class="button">Update Payment Method</a></p>
            <p>Your account will be downgraded on {{ downgrade_date }} if payment isn't resolved.</p>
            <p>Need help? <a href="{{ support_url }}">Contact support immediately</a></p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "subscription_error":
            content = """
            <h2>Important: Issue with Your Subscription</h2>
            <p>Hello {{ user_name }},</p>
            <p>We encountered an issue with your subscription:</p>
            <p><strong>{{ error_message }}</strong></p>
            {% if suggested_action %}
            <p>Recommended action: {{ suggested_action }}</p>
            {% endif %}
            <p>We're working to resolve this automatically, but if you continue to experience issues, please contact our support team.</p>
            <p><a href="mailto:{{ support_email }}" class="button">Contact Support</a></p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "downgrade_notification":
            content = """
            <h2>Account Downgraded to Free</h2>
            <p>Hello {{ user_name }},</p>
            <p>Your ApplyAI Pro subscription has been downgraded to Free due to payment issues.</p>
            <p>You now have access to:</p>
            <ul>
                <li>5 resume processing sessions per week</li>
                <li>Basic formatting options</li>
                <li>Standard templates</li>
            </ul>
            <p>To restore your Pro features, you can upgrade anytime:</p>
            <p><a href="{{ upgrade_url }}" class="button">Upgrade to Pro</a></p>
            <p>Thank you for using ApplyAI!</p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "subscription_expired":
            content = """
            <h2>Your Pro Subscription Has Expired</h2>
            <p>Hello {{ user_name }},</p>
            <p>Your ApplyAI Pro subscription has expired and your account has been downgraded to Free.</p>
            <p>You now have access to:</p>
            <ul>
                <li>5 resume processing sessions per week</li>
                <li>Basic formatting options</li>
                <li>Standard templates</li>
            </ul>
            <p>To restore unlimited access and Pro features:</p>
            <p><a href="{{ upgrade_url }}" class="button">Upgrade to Pro</a></p>
            <p>Thank you for using ApplyAI!</p>
            <p>Best regards,<br>The ApplyAI Team</p>
            """
        elif template_name == "renewal_reminder":
            content = """
            <h2>Subscription Renewal Reminder</h2>
            <p>Hello {{ user_name }},</p>
            <p>Your ApplyAI Pro subscription will automatically renew on <strong>{{ renewal_date }}</strong>.</p>
            <p>You'll continue to enjoy:</p>
            <ul>
                <li>Unlimited resume processing</li>
                <li>Advanced formatting options</li>
                <li>Premium templates and features</li>
                <li>Priority support</li>
            </ul>
            <p>If you need to make any changes to your subscription:</p>
            <p><a href="{{ manage_subscription_url }}" class="button">Manage Subscription</a></p>
            <p>Thank you for being a valued Pro member!</p>
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
    
    # Subscription Lifecycle Email Methods
    
    def send_payment_failure_reminder(self, user_email: str, user_name: str, period_end: datetime) -> bool:
        """Send payment failure reminder email"""
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'period_end': period_end.strftime("%B %d, %Y"),
            'days_remaining': max(0, (period_end - datetime.utcnow()).days),
            'update_payment_url': self._get_frontend_url() + "/subscription"
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Payment Issue - Action Required for Your ApplyAI Pro Subscription",
            template_name="payment_failure_reminder",
            template_data=template_data
        )
    
    def send_final_grace_warning(self, user_email: str, user_name: str, period_end: datetime) -> bool:
        """Send final grace period warning email"""
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'period_end': period_end.strftime("%B %d, %Y"),
            'update_payment_url': self._get_frontend_url() + "/subscription"
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Final Notice - Your ApplyAI Pro Subscription Will Be Canceled",
            template_name="final_grace_warning",
            template_data=template_data
        )
    
    def send_downgrade_notification(self, user_email: str, user_name: str) -> bool:
        """Send downgrade notification email"""
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'upgrade_url': self._get_frontend_url() + "/pricing"
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Your ApplyAI Account Has Been Downgraded to Free",
            template_name="downgrade_notification",
            template_data=template_data
        )
    
    def send_subscription_expired_notification(self, user_email: str, user_name: str) -> bool:
        """Send subscription expired notification email"""
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'upgrade_url': self._get_frontend_url() + "/pricing"
        }
        
        return self.send_email(
            to_email=user_email,
            subject="Your ApplyAI Pro Subscription Has Expired",
            template_name="subscription_expired",
            template_data=template_data
        )
    
    def send_renewal_reminder(self, user_email: str, user_name: str, renewal_date: datetime, 
                            days_before: int, reminder_type: str) -> bool:
        """Send renewal reminder email"""
        template_data = {
            'user_name': user_name or user_email.split('@')[0],
            'renewal_date': renewal_date.strftime("%B %d, %Y"),
            'days_before': days_before,
            'reminder_type': reminder_type,
            'manage_subscription_url': self._get_frontend_url() + "/subscription"
        }
        
        subject_map = {
            "week_before": "Your ApplyAI Pro Subscription Renews in 7 Days",
            "three_days": "Your ApplyAI Pro Subscription Renews in 3 Days", 
            "one_day": "Your ApplyAI Pro Subscription Renews Tomorrow"
        }
        
        return self.send_email(
            to_email=user_email,
            subject=subject_map.get(reminder_type, "ApplyAI Pro Subscription Renewal Reminder"),
            template_name="renewal_reminder",
            template_data=template_data
        )
    
    def _get_frontend_url(self) -> str:
        """Get frontend URL for email links"""
        if self.settings.environment == "development":
            return "http://localhost:3000"
        else:
            cors_origins = self.settings.get_cors_origins()
            return cors_origins[0] if cors_origins else "http://localhost:3000"

# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service 