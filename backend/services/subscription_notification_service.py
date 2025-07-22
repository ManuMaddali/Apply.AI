"""
Subscription Notification Service - User notifications for subscription changes

This service handles:
- Email notifications for subscription events
- In-app notifications for subscription changes
- User communication for payment issues
- Proactive notifications for upcoming renewals
- Cancellation retention communications
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from enum import Enum

from models.user import User, Subscription, SubscriptionTier, SubscriptionStatus
from utils.email_service import EmailService
from services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of subscription notifications"""
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPGRADED = "subscription_upgraded"
    SUBSCRIPTION_DOWNGRADED = "subscription_downgraded"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_RETRY_FAILED = "payment_retry_failed"
    USAGE_LIMIT_WARNING = "usage_limit_warning"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    RENEWAL_REMINDER = "renewal_reminder"
    CANCELLATION_RETENTION = "cancellation_retention"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    GRACE_PERIOD_WARNING = "grace_period_warning"


class SubscriptionNotificationService:
    """Service for handling subscription-related notifications"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.email_service = EmailService()
        self.subscription_service = SubscriptionService(db_session)
        
        # Notification templates and settings
        self.notification_settings = self._initialize_notification_settings()
    
    def _initialize_notification_settings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize notification settings and templates"""
        return {
            NotificationType.SUBSCRIPTION_CREATED.value: {
                "email_template": "subscription_welcome",
                "subject": "Welcome to Pro! Your subscription is now active",
                "priority": "high",
                "immediate": True
            },
            NotificationType.SUBSCRIPTION_UPGRADED.value: {
                "email_template": "subscription_upgraded",
                "subject": "Your subscription has been upgraded",
                "priority": "high",
                "immediate": True
            },
            NotificationType.SUBSCRIPTION_DOWNGRADED.value: {
                "email_template": "subscription_downgraded",
                "subject": "Your subscription has been updated",
                "priority": "medium",
                "immediate": True
            },
            NotificationType.SUBSCRIPTION_CANCELED.value: {
                "email_template": "subscription_canceled",
                "subject": "Your subscription has been canceled",
                "priority": "medium",
                "immediate": True
            },
            NotificationType.PAYMENT_SUCCEEDED.value: {
                "email_template": "payment_success",
                "subject": "Payment received - Thank you!",
                "priority": "low",
                "immediate": False
            },
            NotificationType.PAYMENT_FAILED.value: {
                "email_template": "payment_failed",
                "subject": "Action required: Payment failed",
                "priority": "high",
                "immediate": True
            },
            NotificationType.PAYMENT_RETRY_FAILED.value: {
                "email_template": "payment_retry_failed",
                "subject": "Urgent: Multiple payment attempts failed",
                "priority": "critical",
                "immediate": True
            },
            NotificationType.USAGE_LIMIT_WARNING.value: {
                "email_template": "usage_limit_warning",
                "subject": "You're approaching your usage limit",
                "priority": "medium",
                "immediate": False
            },
            NotificationType.USAGE_LIMIT_EXCEEDED.value: {
                "email_template": "usage_limit_exceeded",
                "subject": "Usage limit reached - Upgrade to continue",
                "priority": "medium",
                "immediate": True
            },
            NotificationType.RENEWAL_REMINDER.value: {
                "email_template": "renewal_reminder",
                "subject": "Your subscription renews soon",
                "priority": "low",
                "immediate": False
            },
            NotificationType.CANCELLATION_RETENTION.value: {
                "email_template": "cancellation_retention",
                "subject": "We'd love to keep you - Special offer inside",
                "priority": "medium",
                "immediate": False
            },
            NotificationType.SUBSCRIPTION_EXPIRED.value: {
                "email_template": "subscription_expired",
                "subject": "Your subscription has expired",
                "priority": "high",
                "immediate": True
            },
            NotificationType.GRACE_PERIOD_WARNING.value: {
                "email_template": "grace_period_warning",
                "subject": "Action required: Update your payment method",
                "priority": "critical",
                "immediate": True
            }
        }
    
    async def notify_subscription_created(
        self,
        user: User,
        subscription_data: Dict[str, Any]
    ) -> bool:
        """Notify user of successful subscription creation"""
        try:
            template_data = {
                "user_name": user.full_name or user.username,
                "subscription_tier": subscription_data.get("tier", "Pro"),
                "billing_amount": subscription_data.get("amount", "$9.99"),
                "billing_cycle": subscription_data.get("cycle", "monthly"),
                "next_billing_date": subscription_data.get("next_billing_date"),
                "features": [
                    "Unlimited resume processing",
                    "Advanced formatting options",
                    "Premium cover letter templates",
                    "Analytics dashboard",
                    "Priority support"
                ],
                "dashboard_url": "https://applyai.com/subscription",
                "support_url": "https://applyai.com/support"
            }
            
            return await self._send_notification(
                user=user,
                notification_type=NotificationType.SUBSCRIPTION_CREATED,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending subscription created notification to user {user.id}: {e}")
            return False
    
    async def notify_subscription_canceled(
        self,
        user: User,
        cancellation_data: Dict[str, Any]
    ) -> bool:
        """Notify user of subscription cancellation"""
        try:
            access_until = cancellation_data.get("access_until")
            immediate = cancellation_data.get("immediate", False)
            
            template_data = {
                "user_name": user.full_name or user.username,
                "cancellation_immediate": immediate,
                "access_until": access_until,
                "reason": cancellation_data.get("reason", "User requested"),
                "reactivate_url": "https://applyai.com/upgrade",
                "feedback_url": "https://applyai.com/feedback",
                "features_lost": [
                    "Unlimited resume processing",
                    "Advanced formatting options",
                    "Premium cover letter templates",
                    "Analytics dashboard"
                ]
            }
            
            success = await self._send_notification(
                user=user,
                notification_type=NotificationType.SUBSCRIPTION_CANCELED,
                template_data=template_data
            )
            
            # Schedule retention email for later (if not immediate cancellation)
            if not immediate and access_until:
                await self._schedule_retention_communication(user, access_until)
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending subscription canceled notification to user {user.id}: {e}")
            return False
    
    async def notify_payment_failed(
        self,
        user: User,
        payment_error: Dict[str, Any],
        retry_count: int = 0
    ) -> bool:
        """Notify user of payment failure"""
        try:
            is_retry_failure = retry_count > 0
            notification_type = (
                NotificationType.PAYMENT_RETRY_FAILED if is_retry_failure 
                else NotificationType.PAYMENT_FAILED
            )
            
            template_data = {
                "user_name": user.full_name or user.username,
                "payment_amount": payment_error.get("amount", "$9.99"),
                "failure_reason": payment_error.get("user_friendly_reason", "Payment method declined"),
                "retry_count": retry_count,
                "next_retry_date": payment_error.get("next_retry_date"),
                "update_payment_url": "https://applyai.com/subscription/payment-methods",
                "grace_period_days": 3,
                "support_url": "https://applyai.com/support",
                "suggested_actions": [
                    "Update your payment method",
                    "Check your card balance",
                    "Contact your bank if needed",
                    "Reach out to our support team"
                ]
            }
            
            return await self._send_notification(
                user=user,
                notification_type=notification_type,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending payment failed notification to user {user.id}: {e}")
            return False
    
    async def notify_usage_limit_warning(
        self,
        user: User,
        usage_data: Dict[str, Any]
    ) -> bool:
        """Notify user when approaching usage limits"""
        try:
            current_usage = usage_data.get("current_usage", 0)
            limit = usage_data.get("limit", 5)
            remaining = limit - current_usage
            
            # Only send warning when user has 1-2 sessions remaining
            if remaining > 2:
                return True  # Don't send warning yet
            
            template_data = {
                "user_name": user.full_name or user.username,
                "current_usage": current_usage,
                "usage_limit": limit,
                "remaining_sessions": remaining,
                "reset_date": usage_data.get("reset_date"),
                "upgrade_url": "https://applyai.com/upgrade",
                "pro_benefits": [
                    "Unlimited weekly sessions",
                    "Bulk processing up to 10 jobs",
                    "Advanced formatting options",
                    "Premium cover letter templates"
                ]
            }
            
            return await self._send_notification(
                user=user,
                notification_type=NotificationType.USAGE_LIMIT_WARNING,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending usage limit warning to user {user.id}: {e}")
            return False
    
    async def notify_usage_limit_exceeded(
        self,
        user: User,
        usage_data: Dict[str, Any]
    ) -> bool:
        """Notify user when usage limit is exceeded"""
        try:
            template_data = {
                "user_name": user.full_name or user.username,
                "usage_limit": usage_data.get("limit", 5),
                "reset_date": usage_data.get("reset_date"),
                "upgrade_url": "https://applyai.com/upgrade",
                "pro_price": "$9.99/month",
                "pro_benefits": [
                    "Unlimited resume processing",
                    "No weekly limits",
                    "Bulk processing capability",
                    "Advanced formatting options",
                    "Premium templates and analytics"
                ]
            }
            
            return await self._send_notification(
                user=user,
                notification_type=NotificationType.USAGE_LIMIT_EXCEEDED,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending usage limit exceeded notification to user {user.id}: {e}")
            return False
    
    async def notify_subscription_renewal(
        self,
        user: User,
        renewal_data: Dict[str, Any]
    ) -> bool:
        """Notify user of successful subscription renewal"""
        try:
            template_data = {
                "user_name": user.full_name or user.username,
                "renewal_amount": renewal_data.get("amount", "$9.99"),
                "billing_period": renewal_data.get("period", "monthly"),
                "next_billing_date": renewal_data.get("next_billing_date"),
                "invoice_url": renewal_data.get("invoice_url"),
                "manage_subscription_url": "https://applyai.com/subscription"
            }
            
            return await self._send_notification(
                user=user,
                notification_type=NotificationType.SUBSCRIPTION_RENEWED,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending subscription renewal notification to user {user.id}: {e}")
            return False
    
    async def notify_grace_period_warning(
        self,
        user: User,
        grace_period_data: Dict[str, Any]
    ) -> bool:
        """Notify user during grace period after payment failure"""
        try:
            template_data = {
                "user_name": user.full_name or user.username,
                "days_remaining": grace_period_data.get("days_remaining", 1),
                "downgrade_date": grace_period_data.get("downgrade_date"),
                "payment_amount": grace_period_data.get("amount", "$9.99"),
                "update_payment_url": "https://applyai.com/subscription/payment-methods",
                "support_url": "https://applyai.com/support",
                "features_at_risk": [
                    "Unlimited resume processing",
                    "Advanced formatting options",
                    "Premium cover letter templates",
                    "Analytics dashboard"
                ]
            }
            
            return await self._send_notification(
                user=user,
                notification_type=NotificationType.GRACE_PERIOD_WARNING,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending grace period warning to user {user.id}: {e}")
            return False
    
    async def _send_notification(
        self,
        user: User,
        notification_type: NotificationType,
        template_data: Dict[str, Any]
    ) -> bool:
        """Send notification using configured settings"""
        try:
            settings = self.notification_settings.get(notification_type.value)
            if not settings:
                logger.warning(f"No notification settings found for type: {notification_type.value}")
                return False
            
            # Send email notification
            success = await self.email_service.send_email(
                to_email=user.email,
                subject=settings["subject"],
                template_name=settings["email_template"],
                template_data=template_data
            )
            
            if success:
                logger.info(f"Sent {notification_type.value} notification to user {user.id}")
                
                # Log notification for audit trail
                await self._log_notification_sent(
                    user_id=str(user.id),
                    notification_type=notification_type.value,
                    success=True
                )
            else:
                logger.error(f"Failed to send {notification_type.value} notification to user {user.id}")
                await self._log_notification_sent(
                    user_id=str(user.id),
                    notification_type=notification_type.value,
                    success=False
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification {notification_type.value} to user {user.id}: {e}")
            await self._log_notification_sent(
                user_id=str(user.id),
                notification_type=notification_type.value,
                success=False,
                error=str(e)
            )
            return False
    
    async def _schedule_retention_communication(
        self,
        user: User,
        access_until: str
    ) -> None:
        """Schedule retention communication for canceled subscriptions"""
        try:
            # In a production system, you would use a task queue like Celery
            # For now, we'll just log the intent to schedule
            logger.info(f"Scheduling retention communication for user {user.id} until {access_until}")
            
            # You could implement this with:
            # 1. A task queue (Celery, RQ, etc.)
            # 2. A scheduled job system
            # 3. Database-based scheduling with periodic checks
            
        except Exception as e:
            logger.error(f"Error scheduling retention communication for user {user.id}: {e}")
    
    async def _log_notification_sent(
        self,
        user_id: str,
        notification_type: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log notification attempts for audit and monitoring"""
        log_data = {
            "user_id": user_id,
            "notification_type": notification_type,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error:
            log_data["error"] = error
        
        if success:
            logger.info(f"Notification sent successfully: {notification_type}", extra=log_data)
        else:
            logger.error(f"Notification failed: {notification_type}", extra=log_data)
    
    # Batch notification methods for administrative tasks
    
    async def send_renewal_reminders(self, days_before: int = 3) -> int:
        """Send renewal reminders to users whose subscriptions renew soon"""
        try:
            # Find users whose subscriptions renew in the specified number of days
            reminder_date = datetime.utcnow() + timedelta(days=days_before)
            
            users_to_remind = self.db.query(User).filter(
                User.subscription_tier == SubscriptionTier.PRO,
                User.subscription_status == SubscriptionStatus.ACTIVE,
                User.current_period_end <= reminder_date,
                User.current_period_end > datetime.utcnow()
            ).all()
            
            sent_count = 0
            for user in users_to_remind:
                template_data = {
                    "user_name": user.full_name or user.username,
                    "renewal_date": user.current_period_end.strftime("%B %d, %Y"),
                    "billing_amount": "$9.99",
                    "manage_subscription_url": "https://applyai.com/subscription"
                }
                
                if await self._send_notification(
                    user=user,
                    notification_type=NotificationType.RENEWAL_REMINDER,
                    template_data=template_data
                ):
                    sent_count += 1
            
            logger.info(f"Sent renewal reminders to {sent_count} users")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending renewal reminders: {e}")
            return 0
    
    async def send_usage_warnings(self) -> int:
        """Send usage warnings to Free users approaching their limits"""
        try:
            # Find Free users who are approaching their usage limits
            free_users = self.db.query(User).filter(
                User.subscription_tier == SubscriptionTier.FREE
            ).all()
            
            sent_count = 0
            for user in free_users:
                # Check if user is approaching limit (4 out of 5 sessions used)
                if user.weekly_usage_count >= 4:
                    usage_data = {
                        "current_usage": user.weekly_usage_count,
                        "limit": 5,
                        "reset_date": (user.weekly_usage_reset + timedelta(days=7)).strftime("%B %d, %Y")
                    }
                    
                    if await self.notify_usage_limit_warning(user, usage_data):
                        sent_count += 1
            
            logger.info(f"Sent usage warnings to {sent_count} users")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending usage warnings: {e}")
            return 0