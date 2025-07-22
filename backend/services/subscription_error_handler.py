"""
Subscription Error Handler - Comprehensive error handling and user feedback

This service provides:
- User-friendly error messages for subscription failures
- Payment failure handling with retry mechanisms
- Subscription status conflict resolution
- Graceful fallbacks for service unavailability
- Comprehensive logging for subscription events and errors
- User notification system for subscription changes
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
import stripe

from models.user import User, Subscription, SubscriptionTier, SubscriptionStatus
from services.payment_service import PaymentService, PaymentError
from services.subscription_service import SubscriptionService
from utils.email_service import EmailService

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization"""
    PAYMENT = "payment"
    SUBSCRIPTION = "subscription"
    USAGE = "usage"
    SYSTEM = "system"
    VALIDATION = "validation"


@dataclass
class SubscriptionError:
    """Structured error information"""
    code: str
    message: str
    user_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    retry_after: Optional[int] = None
    suggested_action: Optional[str] = None


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms"""
    max_attempts: int = 3
    base_delay: int = 2  # seconds
    max_delay: int = 60  # seconds
    exponential_base: float = 2.0
    jitter: bool = True


class SubscriptionErrorHandler:
    """Comprehensive error handling for subscription system"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.email_service = EmailService()
        self.payment_service = PaymentService(db_session)
        self.subscription_service = SubscriptionService(db_session)
        
        # Error message templates
        self.error_messages = self._initialize_error_messages()
        
        # Retry configurations for different operations
        self.retry_configs = {
            "payment_processing": RetryConfig(max_attempts=3, base_delay=2),
            "webhook_processing": RetryConfig(max_attempts=5, base_delay=1),
            "subscription_sync": RetryConfig(max_attempts=3, base_delay=5),
            "notification_sending": RetryConfig(max_attempts=3, base_delay=1)
        }
    
    def _initialize_error_messages(self) -> Dict[str, Dict[str, str]]:
        """Initialize user-friendly error messages"""
        return {
            # Payment errors
            "card_declined": {
                "user_message": "Your payment method was declined. Please check your card details or try a different payment method.",
                "suggested_action": "update_payment_method"
            },
            "insufficient_funds": {
                "user_message": "Your payment was declined due to insufficient funds. Please check your account balance or use a different payment method.",
                "suggested_action": "update_payment_method"
            },
            "expired_card": {
                "user_message": "Your payment method has expired. Please update your card information to continue your subscription.",
                "suggested_action": "update_payment_method"
            },
            "payment_processing_error": {
                "user_message": "We encountered an issue processing your payment. Please try again in a few minutes.",
                "suggested_action": "retry_payment"
            },
            "payment_method_invalid": {
                "user_message": "The payment method provided is invalid. Please check your card details and try again.",
                "suggested_action": "update_payment_method"
            },
            
            # Subscription errors
            "subscription_not_found": {
                "user_message": "We couldn't find your subscription. Please contact support if you believe this is an error.",
                "suggested_action": "contact_support"
            },
            "subscription_already_exists": {
                "user_message": "You already have an active subscription. Please cancel your current subscription before creating a new one.",
                "suggested_action": "manage_subscription"
            },
            "subscription_expired": {
                "user_message": "Your subscription has expired. Please renew to continue accessing Pro features.",
                "suggested_action": "renew_subscription"
            },
            "subscription_canceled": {
                "user_message": "Your subscription has been canceled. You can reactivate it anytime to regain access to Pro features.",
                "suggested_action": "reactivate_subscription"
            },
            "subscription_conflict": {
                "user_message": "There's a conflict with your subscription status. We're working to resolve this automatically.",
                "suggested_action": "wait_and_retry"
            },
            
            # Usage errors
            "usage_limit_exceeded": {
                "user_message": "You've reached your weekly usage limit. Upgrade to Pro for unlimited access or wait for your limit to reset.",
                "suggested_action": "upgrade_to_pro"
            },
            "feature_not_available": {
                "user_message": "This feature is only available to Pro subscribers. Upgrade now to unlock all features.",
                "suggested_action": "upgrade_to_pro"
            },
            
            # System errors
            "service_unavailable": {
                "user_message": "Our subscription service is temporarily unavailable. Please try again in a few minutes.",
                "suggested_action": "retry_later"
            },
            "database_error": {
                "user_message": "We're experiencing technical difficulties. Please try again shortly.",
                "suggested_action": "retry_later"
            },
            "stripe_service_error": {
                "user_message": "Our payment processor is temporarily unavailable. Please try again in a few minutes.",
                "suggested_action": "retry_later"
            },
            
            # Validation errors
            "invalid_subscription_tier": {
                "user_message": "The subscription plan you selected is not valid. Please choose a valid plan.",
                "suggested_action": "select_valid_plan"
            },
            "invalid_user_data": {
                "user_message": "Some of your account information is invalid. Please update your profile and try again.",
                "suggested_action": "update_profile"
            }
        }
    
    async def handle_payment_error(
        self,
        error: Exception,
        user_id: str,
        operation: str,
        context: Dict[str, Any] = None
    ) -> SubscriptionError:
        """Handle payment-related errors with user-friendly messages and retry logic"""
        try:
            context = context or {}
            
            # Determine error type and create structured error
            if isinstance(error, PaymentError) and error.stripe_error:
                subscription_error = await self._handle_stripe_error(error.stripe_error, user_id, operation, context)
            elif isinstance(error, PaymentError):
                subscription_error = self._create_subscription_error(
                    code="payment_processing_error",
                    message=str(error),
                    category=ErrorCategory.PAYMENT,
                    severity=ErrorSeverity.MEDIUM,
                    user_id=user_id,
                    details={"operation": operation, "context": context}
                )
            else:
                subscription_error = self._create_subscription_error(
                    code="payment_processing_error",
                    message=str(error),
                    category=ErrorCategory.PAYMENT,
                    severity=ErrorSeverity.MEDIUM,
                    user_id=user_id,
                    details={"operation": operation, "context": context, "error_type": type(error).__name__}
                )
            
            # Log the error
            await self._log_subscription_error(subscription_error)
            
            # Handle retry logic for certain operations
            if operation in ["create_subscription", "process_payment"]:
                await self._schedule_payment_retry(subscription_error, context)
            
            # Send user notification if appropriate
            if subscription_error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                await self._notify_user_of_error(subscription_error)
            
            return subscription_error
            
        except Exception as e:
            logger.error(f"Error in handle_payment_error: {e}")
            return self._create_subscription_error(
                code="error_handler_failure",
                message=f"Failed to handle payment error: {str(e)}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                user_id=user_id
            )
    
    async def _handle_stripe_error(
        self,
        stripe_error: stripe.error.StripeError,
        user_id: str,
        operation: str,
        context: Dict[str, Any]
    ) -> SubscriptionError:
        """Handle specific Stripe errors with appropriate user messages"""
        error_code = "payment_processing_error"
        severity = ErrorSeverity.MEDIUM
        
        if isinstance(stripe_error, stripe.error.CardError):
            # Card-specific errors
            decline_code = stripe_error.decline_code
            if decline_code == "insufficient_funds":
                error_code = "insufficient_funds"
            elif decline_code == "expired_card":
                error_code = "expired_card"
            elif decline_code in ["generic_decline", "card_declined"]:
                error_code = "card_declined"
            else:
                error_code = "payment_method_invalid"
            
            severity = ErrorSeverity.MEDIUM
            
        elif isinstance(stripe_error, stripe.error.RateLimitError):
            error_code = "stripe_service_error"
            severity = ErrorSeverity.HIGH
            
        elif isinstance(stripe_error, stripe.error.InvalidRequestError):
            error_code = "payment_method_invalid"
            severity = ErrorSeverity.MEDIUM
            
        elif isinstance(stripe_error, stripe.error.AuthenticationError):
            error_code = "stripe_service_error"
            severity = ErrorSeverity.CRITICAL
            
        elif isinstance(stripe_error, stripe.error.APIConnectionError):
            error_code = "stripe_service_error"
            severity = ErrorSeverity.HIGH
            
        elif isinstance(stripe_error, stripe.error.StripeError):
            error_code = "stripe_service_error"
            severity = ErrorSeverity.HIGH
        
        return self._create_subscription_error(
            code=error_code,
            message=str(stripe_error),
            category=ErrorCategory.PAYMENT,
            severity=severity,
            user_id=user_id,
            details={
                "operation": operation,
                "context": context,
                "stripe_error_type": type(stripe_error).__name__,
                "stripe_error_code": getattr(stripe_error, 'code', None),
                "stripe_decline_code": getattr(stripe_error, 'decline_code', None)
            }
        )
    
    async def handle_subscription_conflict(
        self,
        user_id: str,
        local_status: SubscriptionStatus,
        stripe_status: str,
        subscription_id: str
    ) -> Dict[str, Any]:
        """Resolve conflicts between local and Stripe subscription status"""
        try:
            logger.warning(f"Subscription conflict detected for user {user_id}: local={local_status.value}, stripe={stripe_status}")
            
            # Get user and subscription data
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Determine the authoritative source (Stripe is usually authoritative)
            resolution_action = await self._determine_conflict_resolution(local_status, stripe_status)
            
            # Apply resolution
            resolution_result = await self._apply_conflict_resolution(
                user, subscription_id, resolution_action, stripe_status
            )
            
            # Log the resolution
            await self._log_subscription_event(
                user_id=user_id,
                event_type="subscription_conflict_resolved",
                details={
                    "local_status": local_status.value,
                    "stripe_status": stripe_status,
                    "resolution_action": resolution_action,
                    "result": resolution_result
                }
            )
            
            # Notify user if significant change occurred
            if resolution_action in ["downgrade_to_free", "upgrade_to_pro"]:
                await self._notify_user_of_subscription_change(user, resolution_action, resolution_result)
            
            return {
                "resolved": True,
                "action_taken": resolution_action,
                "new_status": resolution_result.get("new_status"),
                "user_notified": resolution_action in ["downgrade_to_free", "upgrade_to_pro"]
            }
            
        except Exception as e:
            logger.error(f"Error resolving subscription conflict for user {user_id}: {e}")
            
            # Create error record
            error = self._create_subscription_error(
                code="subscription_conflict",
                message=f"Failed to resolve subscription conflict: {str(e)}",
                category=ErrorCategory.SUBSCRIPTION,
                severity=ErrorSeverity.HIGH,
                user_id=user_id,
                details={
                    "local_status": local_status.value if local_status else None,
                    "stripe_status": stripe_status,
                    "subscription_id": subscription_id
                }
            )
            
            await self._log_subscription_error(error)
            
            return {
                "resolved": False,
                "error": error.user_message,
                "retry_recommended": True
            }
    
    async def _determine_conflict_resolution(
        self,
        local_status: SubscriptionStatus,
        stripe_status: str
    ) -> str:
        """Determine how to resolve subscription status conflict"""
        # Stripe is generally the authoritative source
        if stripe_status == "active" and local_status != SubscriptionStatus.ACTIVE:
            return "sync_to_active"
        elif stripe_status == "canceled" and local_status == SubscriptionStatus.ACTIVE:
            return "downgrade_to_free"
        elif stripe_status in ["past_due", "unpaid"] and local_status == SubscriptionStatus.ACTIVE:
            return "mark_past_due"
        elif stripe_status == "incomplete" and local_status == SubscriptionStatus.ACTIVE:
            return "mark_incomplete"
        else:
            return "sync_to_stripe"
    
    async def _apply_conflict_resolution(
        self,
        user: User,
        subscription_id: str,
        action: str,
        stripe_status: str
    ) -> Dict[str, Any]:
        """Apply the determined conflict resolution"""
        try:
            if action == "sync_to_active":
                # Update local status to active
                user.subscription_tier = SubscriptionTier.PRO
                user.subscription_status = SubscriptionStatus.ACTIVE
                
                # Update subscription record
                subscription = self.db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription_id
                ).first()
                if subscription:
                    subscription.status = SubscriptionStatus.ACTIVE
                
                self.db.commit()
                return {"new_status": "active", "tier": "pro"}
                
            elif action == "downgrade_to_free":
                # Downgrade user to free
                user.subscription_tier = SubscriptionTier.FREE
                user.subscription_status = SubscriptionStatus.CANCELED
                
                # Update subscription record
                subscription = self.db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription_id
                ).first()
                if subscription:
                    subscription.status = SubscriptionStatus.CANCELED
                    subscription.canceled_at = datetime.utcnow()
                
                self.db.commit()
                return {"new_status": "canceled", "tier": "free"}
                
            elif action == "mark_past_due":
                # Mark as past due but keep Pro access temporarily
                user.subscription_status = SubscriptionStatus.PAST_DUE
                
                subscription = self.db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription_id
                ).first()
                if subscription:
                    subscription.status = SubscriptionStatus.PAST_DUE
                
                self.db.commit()
                return {"new_status": "past_due", "tier": "pro", "grace_period": True}
                
            elif action == "sync_to_stripe":
                # Sync local status to match Stripe
                new_status = self.payment_service._map_stripe_status(stripe_status)
                user.subscription_status = new_status
                
                if new_status in [SubscriptionStatus.CANCELED, SubscriptionStatus.UNPAID]:
                    user.subscription_tier = SubscriptionTier.FREE
                
                subscription = self.db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == subscription_id
                ).first()
                if subscription:
                    subscription.status = new_status
                
                self.db.commit()
                return {"new_status": new_status.value, "tier": user.subscription_tier.value}
            
            else:
                raise ValueError(f"Unknown resolution action: {action}")
                
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def handle_service_unavailability(
        self,
        service_name: str,
        error: Exception,
        user_id: Optional[str] = None,
        fallback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle service unavailability with graceful fallbacks"""
        try:
            logger.warning(f"Service unavailable: {service_name} - {str(error)}")
            
            # Create error record
            subscription_error = self._create_subscription_error(
                code="service_unavailable",
                message=f"{service_name} service unavailable: {str(error)}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                user_id=user_id,
                details={
                    "service": service_name,
                    "error_type": type(error).__name__,
                    "fallback_available": fallback_data is not None
                }
            )
            
            await self._log_subscription_error(subscription_error)
            
            # Determine fallback strategy
            fallback_result = await self._apply_service_fallback(service_name, fallback_data, user_id)
            
            return {
                "service_available": False,
                "fallback_applied": fallback_result["applied"],
                "fallback_data": fallback_result.get("data"),
                "user_message": subscription_error.user_message,
                "retry_after": 300,  # 5 minutes
                "error_code": subscription_error.code
            }
            
        except Exception as e:
            logger.error(f"Error handling service unavailability: {e}")
            return {
                "service_available": False,
                "fallback_applied": False,
                "user_message": "We're experiencing technical difficulties. Please try again later.",
                "retry_after": 600  # 10 minutes
            }
    
    async def _apply_service_fallback(
        self,
        service_name: str,
        fallback_data: Optional[Dict[str, Any]],
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Apply appropriate fallback for unavailable service"""
        if service_name == "stripe":
            # For Stripe unavailability, use cached subscription data
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        "applied": True,
                        "data": {
                            "subscription_tier": user.subscription_tier.value,
                            "subscription_status": user.subscription_status.value,
                            "is_pro_active": user.is_pro_active(),
                            "source": "cached_local_data"
                        }
                    }
            
        elif service_name == "database":
            # For database unavailability, use in-memory cache if available
            if fallback_data:
                return {
                    "applied": True,
                    "data": fallback_data
                }
        
        elif service_name == "email":
            # For email service unavailability, queue for later delivery
            return {
                "applied": True,
                "data": {"queued_for_retry": True}
            }
        
        return {"applied": False}
    
    async def retry_with_backoff(
        self,
        operation_func,
        operation_name: str,
        retry_config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Tuple[bool, Any, Optional[SubscriptionError]]:
        """Execute operation with exponential backoff retry logic"""
        config = retry_config or self.retry_configs.get(operation_name, RetryConfig())
        last_error = None
        
        for attempt in range(config.max_attempts):
            try:
                result = await operation_func(**kwargs)
                if attempt > 0:
                    logger.info(f"Operation {operation_name} succeeded on attempt {attempt + 1}")
                return True, result, None
                
            except Exception as e:
                last_error = e
                
                if attempt < config.max_attempts - 1:
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        import random
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Operation {operation_name} failed on attempt {attempt + 1}, retrying in {delay:.2f}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Operation {operation_name} failed after {config.max_attempts} attempts: {str(e)}")
        
        # Create error for final failure
        error = self._create_subscription_error(
            code=f"{operation_name}_retry_exhausted",
            message=f"Operation failed after {config.max_attempts} attempts: {str(last_error)}",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            details={
                "operation": operation_name,
                "attempts": config.max_attempts,
                "final_error": str(last_error)
            }
        )
        
        return False, None, error
    
    async def _schedule_payment_retry(
        self,
        error: SubscriptionError,
        context: Dict[str, Any]
    ) -> None:
        """Schedule payment retry for recoverable errors"""
        if error.code in ["card_declined", "insufficient_funds", "payment_processing_error"]:
            # Don't auto-retry user errors, but log for manual intervention
            logger.info(f"Payment error requires user action: {error.code}")
            return
        
        if error.code in ["stripe_service_error", "service_unavailable"]:
            # Schedule retry for service errors
            logger.info(f"Scheduling payment retry for service error: {error.code}")
            # In a production system, you might use a task queue like Celery
            # For now, we'll just log the intent
            await self._log_subscription_event(
                user_id=error.user_id,
                event_type="payment_retry_scheduled",
                details={
                    "error_code": error.code,
                    "retry_after": 300,  # 5 minutes
                    "context": context
                }
            )
    
    def _create_subscription_error(
        self,
        code: str,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> SubscriptionError:
        """Create a structured subscription error"""
        error_template = self.error_messages.get(code, {})
        
        return SubscriptionError(
            code=code,
            message=message,
            user_message=error_template.get("user_message", "An unexpected error occurred. Please try again."),
            category=category,
            severity=severity,
            details=details or {},
            timestamp=datetime.utcnow(),
            user_id=user_id,
            suggested_action=error_template.get("suggested_action")
        )
    
    async def _log_subscription_error(self, error: SubscriptionError) -> None:
        """Log subscription error with appropriate level"""
        log_data = {
            "code": error.code,
            "category": error.category.value,
            "severity": error.severity.value,
            "user_id": error.user_id,
            "details": error.details,
            "timestamp": error.timestamp.isoformat()
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL subscription error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH severity subscription error: {error.message}", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM severity subscription error: {error.message}", extra=log_data)
        else:
            logger.info(f"LOW severity subscription error: {error.message}", extra=log_data)
    
    async def _log_subscription_event(
        self,
        user_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Log subscription events for audit and monitoring"""
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Subscription event: {event_type}", extra=log_data)
    
    async def _notify_user_of_error(self, error: SubscriptionError) -> None:
        """Send user notification for significant errors"""
        if not error.user_id:
            return
        
        try:
            user = self.db.query(User).filter(User.id == error.user_id).first()
            if not user:
                return
            
            # Send email notification for critical errors
            if error.severity == ErrorSeverity.CRITICAL:
                await self.email_service.send_email(
                    to_email=user.email,
                    subject="Important: Issue with Your Subscription",
                    template_name="subscription_error",
                    template_data={
                        "user_name": user.full_name or user.username,
                        "error_message": error.user_message,
                        "suggested_action": error.suggested_action,
                        "support_email": "support@applyai.com"
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to notify user of error: {e}")
    
    async def _notify_user_of_subscription_change(
        self,
        user: User,
        change_type: str,
        change_details: Dict[str, Any]
    ) -> None:
        """Notify user of subscription status changes"""
        try:
            if change_type == "downgrade_to_free":
                await self.email_service.send_email(
                    to_email=user.email,
                    subject="Your Subscription Has Been Updated",
                    template_name="downgrade_notification",
                    template_data={
                        "user_name": user.full_name or user.username,
                        "new_tier": "Free",
                        "reason": "subscription_expired_or_canceled",
                        "reactivate_url": "https://applyai.com/upgrade"
                    }
                )
            elif change_type == "upgrade_to_pro":
                await self.email_service.send_email(
                    to_email=user.email,
                    subject="Welcome to Pro!",
                    template_name="upgrade_confirmation",
                    template_data={
                        "user_name": user.full_name or user.username,
                        "new_tier": "Pro",
                        "features": [
                            "Unlimited resume processing",
                            "Advanced formatting options",
                            "Premium cover letters",
                            "Analytics dashboard"
                        ]
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to notify user of subscription change: {e}")