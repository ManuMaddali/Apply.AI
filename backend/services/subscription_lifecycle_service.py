"""
Subscription Lifecycle Management Service

This service handles automated subscription lifecycle management including:
- Scheduled tasks for subscription status synchronization
- Automatic weekly usage reset for Free users
- Grace period handling for failed payments
- Automated downgrade process for expired subscriptions
- Subscription renewal reminders and notifications
- Cleanup tasks for expired sessions and old usage data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from enum import Enum

from models.user import (
    User, Subscription, UsageTracking, PaymentHistory, UserSession,
    SubscriptionTier, SubscriptionStatus, UsageType, PaymentStatus
)
from services.subscription_service import SubscriptionService
from services.payment_service import PaymentService
from utils.email_service import EmailService
from config.database import SessionLocal

logger = logging.getLogger(__name__)


class LifecycleTaskType(Enum):
    """Types of lifecycle tasks"""
    SUBSCRIPTION_SYNC = "subscription_sync"
    USAGE_RESET = "usage_reset"
    GRACE_PERIOD_CHECK = "grace_period_check"
    EXPIRED_DOWNGRADE = "expired_downgrade"
    RENEWAL_REMINDERS = "renewal_reminders"
    DATA_CLEANUP = "data_cleanup"


class LifecycleTaskResult:
    """Result object for lifecycle tasks"""
    def __init__(self, task_type: LifecycleTaskType, success: bool, 
                 processed_count: int = 0, error_message: str = "", 
                 details: Dict = None):
        self.task_type = task_type
        self.success = success
        self.processed_count = processed_count
        self.error_message = error_message
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        return {
            "task_type": self.task_type.value,
            "success": self.success,
            "processed_count": self.processed_count,
            "error_message": self.error_message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class SubscriptionLifecycleService:
    """Service for managing subscription lifecycle automation"""
    
    def __init__(self):
        self.subscription_service = None
        self.payment_service = None
        self.email_service = None
        self._running_tasks = set()
    
    def _get_services(self, db_session: Session):
        """Initialize services with database session"""
        if not self.subscription_service:
            self.subscription_service = SubscriptionService(db_session)
        if not self.payment_service:
            self.payment_service = PaymentService(db_session)
        if not self.email_service:
            self.email_service = EmailService()
    
    # Subscription Status Synchronization
    
    async def sync_subscription_status(self) -> LifecycleTaskResult:
        """
        Synchronize subscription status with Stripe
        Checks for discrepancies between local and Stripe subscription status
        """
        db = SessionLocal()
        try:
            self._get_services(db)
            
            # Get all active subscriptions with Stripe IDs
            active_subscriptions = db.query(Subscription).filter(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.stripe_subscription_id.isnot(None)
                )
            ).all()
            
            synced_count = 0
            sync_errors = []
            
            for subscription in active_subscriptions:
                try:
                    # Get subscription status from Stripe
                    stripe_subscription = await self.payment_service.get_subscription(
                        subscription.stripe_subscription_id
                    )
                    
                    if stripe_subscription:
                        # Check if status needs updating
                        stripe_status = self._map_stripe_status(stripe_subscription.status)
                        
                        if stripe_status != subscription.status:
                            # Update local subscription status
                            await self.subscription_service.update_subscription(
                                str(subscription.id),
                                status=stripe_status,
                                current_period_start=datetime.fromtimestamp(
                                    stripe_subscription.current_period_start
                                ),
                                current_period_end=datetime.fromtimestamp(
                                    stripe_subscription.current_period_end
                                ),
                                cancel_at_period_end=stripe_subscription.cancel_at_period_end
                            )
                            
                            logger.info(f"Synced subscription {subscription.id}: "
                                      f"{subscription.status.value} -> {stripe_status.value}")
                            synced_count += 1
                    
                except Exception as e:
                    error_msg = f"Error syncing subscription {subscription.id}: {str(e)}"
                    logger.error(error_msg)
                    sync_errors.append(error_msg)
            
            return LifecycleTaskResult(
                LifecycleTaskType.SUBSCRIPTION_SYNC,
                success=len(sync_errors) == 0,
                processed_count=synced_count,
                error_message="; ".join(sync_errors) if sync_errors else "",
                details={
                    "total_checked": len(active_subscriptions),
                    "synced": synced_count,
                    "errors": len(sync_errors)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in subscription sync task: {e}")
            return LifecycleTaskResult(
                LifecycleTaskType.SUBSCRIPTION_SYNC,
                success=False,
                error_message=str(e)
            )
        finally:
            db.close()
    
    def _map_stripe_status(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe subscription status to local status"""
        status_mapping = {
            "active": SubscriptionStatus.ACTIVE,
            "canceled": SubscriptionStatus.CANCELED,
            "past_due": SubscriptionStatus.PAST_DUE,
            "unpaid": SubscriptionStatus.UNPAID,
            "incomplete": SubscriptionStatus.INCOMPLETE,
            "incomplete_expired": SubscriptionStatus.INCOMPLETE_EXPIRED,
            "trialing": SubscriptionStatus.TRIALING
        }
        return status_mapping.get(stripe_status, SubscriptionStatus.CANCELED)
    
    # Weekly Usage Reset
    
    async def reset_weekly_usage(self) -> LifecycleTaskResult:
        """
        Reset weekly usage counters for all users
        Runs weekly to reset Free user session limits
        """
        db = SessionLocal()
        try:
            self._get_services(db)
            
            # Find users whose weekly usage should be reset
            users_to_reset = db.query(User).filter(
                or_(
                    User.weekly_usage_reset.is_(None),
                    User.weekly_usage_reset <= datetime.utcnow() - timedelta(days=7)
                )
            ).all()
            
            reset_count = 0
            reset_errors = []
            
            for user in users_to_reset:
                try:
                    # Reset weekly usage
                    user.reset_weekly_usage()
                    reset_count += 1
                    
                    logger.info(f"Reset weekly usage for user {user.id}")
                    
                except Exception as e:
                    error_msg = f"Error resetting usage for user {user.id}: {str(e)}"
                    logger.error(error_msg)
                    reset_errors.append(error_msg)
            
            db.commit()
            
            return LifecycleTaskResult(
                LifecycleTaskType.USAGE_RESET,
                success=len(reset_errors) == 0,
                processed_count=reset_count,
                error_message="; ".join(reset_errors) if reset_errors else "",
                details={
                    "total_users_checked": len(users_to_reset),
                    "reset_count": reset_count,
                    "errors": len(reset_errors)
                }
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in weekly usage reset task: {e}")
            return LifecycleTaskResult(
                LifecycleTaskType.USAGE_RESET,
                success=False,
                error_message=str(e)
            )
        finally:
            db.close()
    
    # Grace Period Handling
    
    async def handle_grace_periods(self, grace_days: int = 3) -> LifecycleTaskResult:
        """
        Handle grace periods for failed payments
        Checks users in PAST_DUE status and manages grace period
        """
        db = SessionLocal()
        try:
            self._get_services(db)
            
            # Find users in past due status
            past_due_users = db.query(User).filter(
                and_(
                    User.subscription_status == SubscriptionStatus.PAST_DUE,
                    User.current_period_end.isnot(None)
                )
            ).all()
            
            processed_count = 0
            grace_actions = []
            
            for user in past_due_users:
                try:
                    days_past_due = (datetime.utcnow() - user.current_period_end).days
                    
                    if days_past_due <= grace_days:
                        # Still in grace period - send reminder if needed
                        if days_past_due == 1:  # Send reminder on day 1
                            await self._send_payment_failure_reminder(user)
                            grace_actions.append(f"Sent reminder to user {user.id}")
                        elif days_past_due == grace_days:  # Final warning
                            await self._send_final_grace_warning(user)
                            grace_actions.append(f"Sent final warning to user {user.id}")
                    else:
                        # Grace period expired - downgrade to Free
                        await self._downgrade_expired_grace_period(user)
                        grace_actions.append(f"Downgraded user {user.id} after grace period")
                    
                    processed_count += 1
                    
                except Exception as e:
                    error_msg = f"Error handling grace period for user {user.id}: {str(e)}"
                    logger.error(error_msg)
                    grace_actions.append(error_msg)
            
            return LifecycleTaskResult(
                LifecycleTaskType.GRACE_PERIOD_CHECK,
                success=True,
                processed_count=processed_count,
                details={
                    "total_past_due": len(past_due_users),
                    "actions_taken": grace_actions,
                    "grace_days": grace_days
                }
            )
            
        except Exception as e:
            logger.error(f"Error in grace period handling task: {e}")
            return LifecycleTaskResult(
                LifecycleTaskType.GRACE_PERIOD_CHECK,
                success=False,
                error_message=str(e)
            )
        finally:
            db.close()
    
    async def _send_payment_failure_reminder(self, user: User):
        """Send payment failure reminder email"""
        try:
            await self.email_service.send_payment_failure_reminder(
                user.email,
                user.full_name or user.username,
                user.current_period_end
            )
            logger.info(f"Sent payment failure reminder to user {user.id}")
        except Exception as e:
            logger.error(f"Error sending payment reminder to user {user.id}: {e}")
    
    async def _send_final_grace_warning(self, user: User):
        """Send final grace period warning email"""
        try:
            await self.email_service.send_final_grace_warning(
                user.email,
                user.full_name or user.username,
                user.current_period_end
            )
            logger.info(f"Sent final grace warning to user {user.id}")
        except Exception as e:
            logger.error(f"Error sending final warning to user {user.id}: {e}")
    
    async def _downgrade_expired_grace_period(self, user: User):
        """Downgrade user after grace period expires"""
        db = SessionLocal()
        try:
            # Update user to Free tier
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_status = SubscriptionStatus.CANCELED
            
            # Update subscription record
            subscription = db.query(Subscription).filter(
                and_(
                    Subscription.user_id == user.id,
                    Subscription.status == SubscriptionStatus.PAST_DUE
                )
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.utcnow()
            
            db.commit()
            
            # Send downgrade notification
            await self.email_service.send_downgrade_notification(
                user.email,
                user.full_name or user.username
            )
            
            logger.info(f"Downgraded user {user.id} after grace period expiry")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error downgrading user {user.id} after grace period: {e}")
            raise
        finally:
            db.close()
    
    # Expired Subscription Downgrade
    
    async def process_expired_subscriptions(self) -> LifecycleTaskResult:
        """
        Process expired subscriptions and downgrade users
        Handles subscriptions that have passed their end date
        """
        db = SessionLocal()
        try:
            self._get_services(db)
            
            # Find users with expired Pro subscriptions
            expired_users = db.query(User).filter(
                and_(
                    User.subscription_tier == SubscriptionTier.PRO,
                    User.current_period_end < datetime.utcnow(),
                    User.subscription_status.in_([
                        SubscriptionStatus.ACTIVE,
                        SubscriptionStatus.CANCELED
                    ])
                )
            ).all()
            
            downgraded_count = 0
            downgrade_errors = []
            
            for user in expired_users:
                try:
                    # Check if user should be downgraded
                    if user.cancel_at_period_end or user.subscription_status == SubscriptionStatus.CANCELED:
                        # Downgrade to Free tier
                        user.subscription_tier = SubscriptionTier.FREE
                        user.subscription_status = SubscriptionStatus.CANCELED
                        
                        # Update subscription record
                        subscription = db.query(Subscription).filter(
                            and_(
                                Subscription.user_id == user.id,
                                Subscription.status.in_([
                                    SubscriptionStatus.ACTIVE,
                                    SubscriptionStatus.CANCELED
                                ])
                            )
                        ).first()
                        
                        if subscription:
                            subscription.status = SubscriptionStatus.CANCELED
                            if not subscription.canceled_at:
                                subscription.canceled_at = datetime.utcnow()
                        
                        # Send downgrade notification
                        await self.email_service.send_subscription_expired_notification(
                            user.email,
                            user.full_name or user.username
                        )
                        
                        downgraded_count += 1
                        logger.info(f"Downgraded expired subscription for user {user.id}")
                
                except Exception as e:
                    error_msg = f"Error downgrading user {user.id}: {str(e)}"
                    logger.error(error_msg)
                    downgrade_errors.append(error_msg)
            
            db.commit()
            
            return LifecycleTaskResult(
                LifecycleTaskType.EXPIRED_DOWNGRADE,
                success=len(downgrade_errors) == 0,
                processed_count=downgraded_count,
                error_message="; ".join(downgrade_errors) if downgrade_errors else "",
                details={
                    "total_expired": len(expired_users),
                    "downgraded": downgraded_count,
                    "errors": len(downgrade_errors)
                }
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in expired subscription processing: {e}")
            return LifecycleTaskResult(
                LifecycleTaskType.EXPIRED_DOWNGRADE,
                success=False,
                error_message=str(e)
            )
        finally:
            db.close()
    
    # Renewal Reminders
    
    async def send_renewal_reminders(self) -> LifecycleTaskResult:
        """
        Send renewal reminders to users approaching subscription end
        Sends reminders at 7 days, 3 days, and 1 day before renewal
        """
        db = SessionLocal()
        try:
            self._get_services(db)
            
            now = datetime.utcnow()
            reminder_periods = [
                (7, "week_before"),
                (3, "three_days"),
                (1, "one_day")
            ]
            
            sent_count = 0
            reminder_details = []
            
            for days_before, reminder_type in reminder_periods:
                target_date = now + timedelta(days=days_before)
                
                # Find users with renewals on target date
                users_to_remind = db.query(User).filter(
                    and_(
                        User.subscription_tier == SubscriptionTier.PRO,
                        User.subscription_status == SubscriptionStatus.ACTIVE,
                        User.current_period_end >= target_date,
                        User.current_period_end < target_date + timedelta(days=1),
                        User.cancel_at_period_end == False  # Only remind users who aren't canceling
                    )
                ).all()
                
                for user in users_to_remind:
                    try:
                        await self._send_renewal_reminder(user, days_before, reminder_type)
                        sent_count += 1
                        reminder_details.append(f"Sent {reminder_type} reminder to user {user.id}")
                        
                    except Exception as e:
                        error_msg = f"Error sending {reminder_type} reminder to user {user.id}: {str(e)}"
                        logger.error(error_msg)
                        reminder_details.append(error_msg)
            
            return LifecycleTaskResult(
                LifecycleTaskType.RENEWAL_REMINDERS,
                success=True,
                processed_count=sent_count,
                details={
                    "reminders_sent": sent_count,
                    "reminder_details": reminder_details
                }
            )
            
        except Exception as e:
            logger.error(f"Error in renewal reminders task: {e}")
            return LifecycleTaskResult(
                LifecycleTaskType.RENEWAL_REMINDERS,
                success=False,
                error_message=str(e)
            )
        finally:
            db.close()
    
    async def _send_renewal_reminder(self, user: User, days_before: int, reminder_type: str):
        """Send renewal reminder email"""
        try:
            await self.email_service.send_renewal_reminder(
                user.email,
                user.full_name or user.username,
                user.current_period_end,
                days_before,
                reminder_type
            )
            logger.info(f"Sent {reminder_type} renewal reminder to user {user.id}")
        except Exception as e:
            logger.error(f"Error sending renewal reminder to user {user.id}: {e}")
    
    # Data Cleanup
    
    async def cleanup_old_data(self, retention_days: int = 90) -> LifecycleTaskResult:
        """
        Clean up old data including expired sessions and old usage data
        Removes data older than retention_days to maintain database performance
        """
        db = SessionLocal()
        try:
            cleanup_date = datetime.utcnow() - timedelta(days=retention_days)
            cleanup_details = []
            total_cleaned = 0
            
            # Clean up expired sessions
            expired_sessions = db.query(UserSession).filter(
                or_(
                    UserSession.expires_at < datetime.utcnow(),
                    UserSession.created_at < cleanup_date
                )
            ).all()
            
            for session in expired_sessions:
                db.delete(session)
            
            session_count = len(expired_sessions)
            total_cleaned += session_count
            cleanup_details.append(f"Cleaned {session_count} expired sessions")
            
            # Clean up old usage tracking data (keep recent data for analytics)
            old_usage_data = db.query(UsageTracking).filter(
                UsageTracking.usage_date < cleanup_date
            ).all()
            
            for usage in old_usage_data:
                db.delete(usage)
            
            usage_count = len(old_usage_data)
            total_cleaned += usage_count
            cleanup_details.append(f"Cleaned {usage_count} old usage records")
            
            # Clean up old payment history (keep for longer period - 2 years)
            payment_cleanup_date = datetime.utcnow() - timedelta(days=730)
            old_payments = db.query(PaymentHistory).filter(
                and_(
                    PaymentHistory.created_at < payment_cleanup_date,
                    PaymentHistory.status.in_([
                        PaymentStatus.FAILED,
                        PaymentStatus.CANCELED
                    ])
                )
            ).all()
            
            for payment in old_payments:
                db.delete(payment)
            
            payment_count = len(old_payments)
            total_cleaned += payment_count
            cleanup_details.append(f"Cleaned {payment_count} old failed payment records")
            
            # Optimize database (SQLite specific)
            try:
                db.execute(text("VACUUM"))
                cleanup_details.append("Database optimized with VACUUM")
            except Exception as e:
                logger.warning(f"Could not run VACUUM: {e}")
            
            db.commit()
            
            return LifecycleTaskResult(
                LifecycleTaskType.DATA_CLEANUP,
                success=True,
                processed_count=total_cleaned,
                details={
                    "retention_days": retention_days,
                    "cleanup_details": cleanup_details,
                    "sessions_cleaned": session_count,
                    "usage_records_cleaned": usage_count,
                    "payment_records_cleaned": payment_count
                }
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in data cleanup task: {e}")
            return LifecycleTaskResult(
                LifecycleTaskType.DATA_CLEANUP,
                success=False,
                error_message=str(e)
            )
        finally:
            db.close()
    
    # Task Orchestration
    
    async def run_all_lifecycle_tasks(self) -> List[LifecycleTaskResult]:
        """
        Run all lifecycle management tasks
        Returns list of results for each task
        """
        logger.info("Starting subscription lifecycle management tasks")
        
        tasks = [
            ("Subscription Status Sync", self.sync_subscription_status()),
            ("Weekly Usage Reset", self.reset_weekly_usage()),
            ("Grace Period Handling", self.handle_grace_periods()),
            ("Expired Subscription Processing", self.process_expired_subscriptions()),
            ("Renewal Reminders", self.send_renewal_reminders()),
            ("Data Cleanup", self.cleanup_old_data())
        ]
        
        results = []
        
        for task_name, task_coro in tasks:
            try:
                logger.info(f"Running {task_name}...")
                result = await task_coro
                results.append(result)
                
                if result.success:
                    logger.info(f"✅ {task_name} completed successfully: "
                              f"{result.processed_count} items processed")
                else:
                    logger.error(f"❌ {task_name} failed: {result.error_message}")
                    
            except Exception as e:
                logger.error(f"❌ {task_name} crashed: {e}")
                results.append(LifecycleTaskResult(
                    LifecycleTaskType.SUBSCRIPTION_SYNC,  # Default type
                    success=False,
                    error_message=f"Task crashed: {str(e)}"
                ))
        
        logger.info("Subscription lifecycle management tasks completed")
        return results
    
    async def run_single_task(self, task_type: LifecycleTaskType) -> LifecycleTaskResult:
        """Run a single lifecycle task"""
        task_map = {
            LifecycleTaskType.SUBSCRIPTION_SYNC: self.sync_subscription_status,
            LifecycleTaskType.USAGE_RESET: self.reset_weekly_usage,
            LifecycleTaskType.GRACE_PERIOD_CHECK: self.handle_grace_periods,
            LifecycleTaskType.EXPIRED_DOWNGRADE: self.process_expired_subscriptions,
            LifecycleTaskType.RENEWAL_REMINDERS: self.send_renewal_reminders,
            LifecycleTaskType.DATA_CLEANUP: self.cleanup_old_data
        }
        
        if task_type not in task_map:
            return LifecycleTaskResult(
                task_type,
                success=False,
                error_message=f"Unknown task type: {task_type.value}"
            )
        
        try:
            return await task_map[task_type]()
        except Exception as e:
            logger.error(f"Error running task {task_type.value}: {e}")
            return LifecycleTaskResult(
                task_type,
                success=False,
                error_message=str(e)
            )


# Global instance for use in scheduled tasks
lifecycle_service = SubscriptionLifecycleService()