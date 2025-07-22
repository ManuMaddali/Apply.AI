"""
Subscription Logger - Comprehensive logging for subscription events and errors

This module provides:
- Structured logging for subscription events
- Error tracking and monitoring
- Performance metrics logging
- Audit trail for subscription changes
- Integration with monitoring systems
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
import os

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LogLevel(Enum):
    """Log levels for subscription events"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventCategory(Enum):
    """Categories for subscription events"""
    SUBSCRIPTION = "subscription"
    PAYMENT = "payment"
    USAGE = "usage"
    NOTIFICATION = "notification"
    WEBHOOK = "webhook"
    ERROR = "error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    AUDIT = "audit"


@dataclass
class SubscriptionLogEvent:
    """Structured log event for subscription system"""
    timestamp: str
    event_type: str
    category: EventCategory
    level: LogLevel
    user_id: Optional[str] = None
    subscription_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, float]] = None
    error_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


class SubscriptionLogger:
    """Comprehensive logger for subscription system"""
    
    def __init__(self, logger_name: str = "subscription"):
        self.logger = logging.getLogger(logger_name)
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Configure different handlers for different environments
        self._configure_handlers()
    
    def _configure_handlers(self):
        """Configure logging handlers based on environment"""
        if self.environment == "production":
            # In production, you might want to add:
            # - File handlers for persistent logging
            # - External logging services (e.g., CloudWatch, Datadog)
            # - Error tracking services (e.g., Sentry)
            pass
        elif self.environment == "development":
            # Development logging is already configured via basicConfig
            pass
    
    def log_subscription_event(
        self,
        event_type: str,
        category: EventCategory,
        level: LogLevel = LogLevel.INFO,
        user_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
        **kwargs
    ) -> None:
        """Log a subscription event with structured data"""
        try:
            event = SubscriptionLogEvent(
                timestamp=datetime.utcnow().isoformat(),
                event_type=event_type,
                category=category,
                level=level,
                user_id=user_id,
                subscription_id=subscription_id,
                details=details or {},
                metrics=metrics or {},
                **kwargs
            )
            
            # Log with appropriate level
            log_method = getattr(self.logger, level.value)
            log_method(
                f"[{category.value.upper()}] {event_type}",
                extra={"structured_data": event.to_dict()}
            )
            
            # Send to external monitoring if configured
            self._send_to_monitoring(event)
            
        except Exception as e:
            self.logger.error(f"Error logging subscription event: {e}")
    
    def log_subscription_created(
        self,
        user_id: str,
        subscription_id: str,
        tier: str,
        payment_method: str,
        amount: float,
        processing_time: float
    ) -> None:
        """Log subscription creation event"""
        self.log_subscription_event(
            event_type="subscription_created",
            category=EventCategory.SUBSCRIPTION,
            level=LogLevel.INFO,
            user_id=user_id,
            subscription_id=subscription_id,
            details={
                "tier": tier,
                "payment_method": payment_method,
                "amount": amount
            },
            metrics={
                "processing_time_ms": processing_time * 1000,
                "amount_cents": int(amount * 100)
            }
        )
    
    def log_subscription_canceled(
        self,
        user_id: str,
        subscription_id: str,
        reason: Optional[str] = None,
        immediate: bool = False
    ) -> None:
        """Log subscription cancellation event"""
        self.log_subscription_event(
            event_type="subscription_canceled",
            category=EventCategory.SUBSCRIPTION,
            level=LogLevel.INFO,
            user_id=user_id,
            subscription_id=subscription_id,
            details={
                "reason": reason,
                "immediate": immediate,
                "canceled_at": datetime.utcnow().isoformat()
            }
        )
    
    def log_payment_success(
        self,
        user_id: str,
        payment_intent_id: str,
        amount: float,
        currency: str = "usd",
        processing_time: float = 0
    ) -> None:
        """Log successful payment event"""
        self.log_subscription_event(
            event_type="payment_succeeded",
            category=EventCategory.PAYMENT,
            level=LogLevel.INFO,
            user_id=user_id,
            details={
                "payment_intent_id": payment_intent_id,
                "amount": amount,
                "currency": currency
            },
            metrics={
                "processing_time_ms": processing_time * 1000,
                "amount_cents": int(amount * 100)
            }
        )
    
    def log_payment_failure(
        self,
        user_id: str,
        error_code: str,
        error_message: str,
        payment_method_id: Optional[str] = None,
        amount: Optional[float] = None,
        retry_count: int = 0
    ) -> None:
        """Log payment failure event"""
        self.log_subscription_event(
            event_type="payment_failed",
            category=EventCategory.PAYMENT,
            level=LogLevel.ERROR,
            user_id=user_id,
            details={
                "error_code": error_code,
                "error_message": error_message,
                "payment_method_id": payment_method_id,
                "amount": amount,
                "retry_count": retry_count
            },
            error_info={
                "error_code": error_code,
                "error_message": error_message,
                "retry_count": retry_count
            }
        )
    
    def log_usage_tracking(
        self,
        user_id: str,
        usage_type: str,
        count: int = 1,
        endpoint: Optional[str] = None,
        processing_time: Optional[float] = None
    ) -> None:
        """Log usage tracking event"""
        self.log_subscription_event(
            event_type="usage_tracked",
            category=EventCategory.USAGE,
            level=LogLevel.INFO,
            user_id=user_id,
            details={
                "usage_type": usage_type,
                "count": count,
                "endpoint": endpoint
            },
            metrics={
                "processing_time_ms": processing_time * 1000 if processing_time else 0,
                "usage_count": count
            }
        )
    
    def log_usage_limit_exceeded(
        self,
        user_id: str,
        usage_type: str,
        current_usage: int,
        limit: int
    ) -> None:
        """Log usage limit exceeded event"""
        self.log_subscription_event(
            event_type="usage_limit_exceeded",
            category=EventCategory.USAGE,
            level=LogLevel.WARNING,
            user_id=user_id,
            details={
                "usage_type": usage_type,
                "current_usage": current_usage,
                "limit": limit,
                "exceeded_by": current_usage - limit
            }
        )
    
    def log_webhook_received(
        self,
        event_type: str,
        event_id: str,
        processing_time: float,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """Log webhook processing event"""
        self.log_subscription_event(
            event_type="webhook_processed",
            category=EventCategory.WEBHOOK,
            level=LogLevel.INFO if success else LogLevel.ERROR,
            details={
                "webhook_event_type": event_type,
                "webhook_event_id": event_id,
                "success": success,
                "error": error
            },
            metrics={
                "processing_time_ms": processing_time * 1000
            },
            error_info={"error": error} if error else None
        )
    
    def log_notification_sent(
        self,
        user_id: str,
        notification_type: str,
        channel: str = "email",
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """Log notification sending event"""
        self.log_subscription_event(
            event_type="notification_sent",
            category=EventCategory.NOTIFICATION,
            level=LogLevel.INFO if success else LogLevel.ERROR,
            user_id=user_id,
            details={
                "notification_type": notification_type,
                "channel": channel,
                "success": success,
                "error": error
            },
            error_info={"error": error} if error else None
        )
    
    def log_subscription_error(
        self,
        error_code: str,
        error_message: str,
        user_id: Optional[str] = None,
        subscription_id: Optional[str] = None,
        operation: Optional[str] = None,
        severity: str = "medium",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log subscription system error"""
        level_mapping = {
            "low": LogLevel.INFO,
            "medium": LogLevel.WARNING,
            "high": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL
        }
        
        self.log_subscription_event(
            event_type="subscription_error",
            category=EventCategory.ERROR,
            level=level_mapping.get(severity, LogLevel.ERROR),
            user_id=user_id,
            subscription_id=subscription_id,
            details={
                "operation": operation,
                "severity": severity,
                **(details or {})
            },
            error_info={
                "error_code": error_code,
                "error_message": error_message,
                "severity": severity
            }
        )
    
    def log_performance_metric(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        user_id: Optional[str] = None,
        additional_metrics: Optional[Dict[str, float]] = None
    ) -> None:
        """Log performance metrics"""
        metrics = {
            "duration_ms": duration_ms,
            "success": 1 if success else 0,
            **(additional_metrics or {})
        }
        
        self.log_subscription_event(
            event_type="performance_metric",
            category=EventCategory.PERFORMANCE,
            level=LogLevel.INFO,
            user_id=user_id,
            details={
                "operation": operation,
                "success": success
            },
            metrics=metrics
        )
    
    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "medium"
    ) -> None:
        """Log security-related events"""
        level_mapping = {
            "low": LogLevel.INFO,
            "medium": LogLevel.WARNING,
            "high": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL
        }
        
        self.log_subscription_event(
            event_type=event_type,
            category=EventCategory.SECURITY,
            level=level_mapping.get(severity, LogLevel.WARNING),
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "severity": severity,
                **(details or {})
            }
        )
    
    def log_audit_event(
        self,
        action: str,
        user_id: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """Log audit trail events"""
        self.log_subscription_event(
            event_type="audit_event",
            category=EventCategory.AUDIT,
            level=LogLevel.INFO,
            user_id=user_id,
            ip_address=ip_address,
            details={
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "changes": changes or {}
            }
        )
    
    def _send_to_monitoring(self, event: SubscriptionLogEvent) -> None:
        """Send event to external monitoring systems"""
        try:
            # In production, you might send to:
            # - CloudWatch Logs
            # - Datadog
            # - New Relic
            # - Custom monitoring endpoints
            
            if self.environment == "production":
                # Example: Send critical errors to monitoring
                if event.level == LogLevel.CRITICAL:
                    self._send_alert(event)
                
                # Example: Send metrics to monitoring
                if event.metrics:
                    self._send_metrics(event)
                    
        except Exception as e:
            self.logger.error(f"Error sending to monitoring: {e}")
    
    def _send_alert(self, event: SubscriptionLogEvent) -> None:
        """Send alert for critical events"""
        # Implement alerting logic (e.g., PagerDuty, Slack, email)
        pass
    
    def _send_metrics(self, event: SubscriptionLogEvent) -> None:
        """Send metrics to monitoring system"""
        # Implement metrics sending (e.g., StatsD, CloudWatch Metrics)
        pass
    
    # Context managers for operation logging
    
    def log_operation(self, operation_name: str, user_id: Optional[str] = None):
        """Context manager for logging operations with timing"""
        return OperationLogger(self, operation_name, user_id)


class OperationLogger:
    """Context manager for logging operations with automatic timing"""
    
    def __init__(self, logger: SubscriptionLogger, operation_name: str, user_id: Optional[str] = None):
        self.logger = logger
        self.operation_name = operation_name
        self.user_id = user_id
        self.start_time = None
        self.success = True
        self.error = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
            
            if exc_type is not None:
                self.success = False
                self.error = str(exc_val)
            
            self.logger.log_performance_metric(
                operation=self.operation_name,
                duration_ms=duration,
                success=self.success,
                user_id=self.user_id
            )
            
            if not self.success:
                self.logger.log_subscription_error(
                    error_code=f"{self.operation_name}_failed",
                    error_message=self.error,
                    user_id=self.user_id,
                    operation=self.operation_name,
                    severity="high"
                )


# Global logger instance
subscription_logger = SubscriptionLogger()


# Convenience functions for common logging patterns

def log_subscription_created(user_id: str, subscription_id: str, **kwargs):
    """Convenience function for logging subscription creation"""
    subscription_logger.log_subscription_created(user_id, subscription_id, **kwargs)


def log_payment_success(user_id: str, payment_intent_id: str, amount: float, **kwargs):
    """Convenience function for logging payment success"""
    subscription_logger.log_payment_success(user_id, payment_intent_id, amount, **kwargs)


def log_payment_failure(user_id: str, error_code: str, error_message: str, **kwargs):
    """Convenience function for logging payment failure"""
    subscription_logger.log_payment_failure(user_id, error_code, error_message, **kwargs)


def log_usage_event(user_id: str, usage_type: str, **kwargs):
    """Convenience function for logging usage events"""
    subscription_logger.log_usage_tracking(user_id, usage_type, **kwargs)


def log_error(error_code: str, error_message: str, **kwargs):
    """Convenience function for logging errors"""
    subscription_logger.log_subscription_error(error_code, error_message, **kwargs)