"""
Subscription Response Utilities - Standardized error responses and user feedback

This module provides:
- Standardized error response formats
- User-friendly error messages
- Consistent API response structure
- Error code mapping and categorization
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from enum import Enum

from services.subscription_error_handler import SubscriptionError, ErrorCategory, ErrorSeverity


class ResponseCode(Enum):
    """Standard response codes for subscription operations"""
    SUCCESS = "success"
    PAYMENT_REQUIRED = "payment_required"
    SUBSCRIPTION_REQUIRED = "subscription_required"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_CONFLICT = "subscription_conflict"
    SERVICE_UNAVAILABLE = "service_unavailable"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_REQUIRED = "authentication_required"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class SubscriptionResponseBuilder:
    """Builder for creating standardized subscription API responses"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a success response"""
        response = {
            "success": True,
            "code": ResponseCode.SUCCESS.value,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    @staticmethod
    def error(
        error: SubscriptionError,
        include_details: bool = False
    ) -> JSONResponse:
        """Create an error response from SubscriptionError"""
        status_code = SubscriptionResponseBuilder._get_http_status_code(error)
        
        response_data = {
            "success": False,
            "error": {
                "code": error.code,
                "message": error.user_message,
                "category": error.category.value,
                "severity": error.severity.value,
                "timestamp": error.timestamp.isoformat()
            }
        }
        
        # Add suggested action if available
        if error.suggested_action:
            response_data["error"]["suggested_action"] = error.suggested_action
            response_data["error"]["action_urls"] = SubscriptionResponseBuilder._get_action_urls(error.suggested_action)
        
        # Add retry information if applicable
        if error.retry_after:
            response_data["error"]["retry_after"] = error.retry_after
        
        # Include technical details for debugging (only in development)
        if include_details and error.details:
            response_data["error"]["details"] = error.details
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    @staticmethod
    def payment_required(
        message: str = "This feature requires a Pro subscription",
        current_tier: str = "free",
        required_tier: str = "pro",
        features: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a payment required response"""
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "success": False,
                "error": {
                    "code": ResponseCode.SUBSCRIPTION_REQUIRED.value,
                    "message": message,
                    "current_tier": current_tier,
                    "required_tier": required_tier,
                    "upgrade_url": "/upgrade",
                    "features": features or [
                        "Unlimited resume processing",
                        "Advanced formatting options",
                        "Premium cover letters",
                        "Analytics dashboard"
                    ]
                }
            }
        )
    
    @staticmethod
    def usage_limit_exceeded(
        limit: int,
        remaining: int = 0,
        reset_time: Optional[str] = None,
        upgrade_benefits: Optional[List[str]] = None
    ) -> JSONResponse:
        """Create a usage limit exceeded response"""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "error": {
                    "code": ResponseCode.USAGE_LIMIT_EXCEEDED.value,
                    "message": f"You've reached your weekly limit of {limit} sessions",
                    "limit": limit,
                    "remaining": remaining,
                    "reset_time": reset_time,
                    "upgrade_url": "/upgrade",
                    "upgrade_benefits": upgrade_benefits or [
                        "Unlimited weekly sessions",
                        "Bulk processing up to 10 jobs",
                        "Priority processing speed"
                    ]
                }
            }
        )
    
    @staticmethod
    def payment_failed(
        reason: str,
        suggested_action: str = "update_payment_method",
        retry_allowed: bool = True
    ) -> JSONResponse:
        """Create a payment failed response"""
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "success": False,
                "error": {
                    "code": ResponseCode.PAYMENT_FAILED.value,
                    "message": reason,
                    "suggested_action": suggested_action,
                    "retry_allowed": retry_allowed,
                    "action_urls": SubscriptionResponseBuilder._get_action_urls(suggested_action)
                }
            }
        )
    
    @staticmethod
    def service_unavailable(
        service_name: str,
        retry_after: int = 300,
        fallback_available: bool = False,
        fallback_message: Optional[str] = None
    ) -> JSONResponse:
        """Create a service unavailable response"""
        response_data = {
            "success": False,
            "error": {
                "code": ResponseCode.SERVICE_UNAVAILABLE.value,
                "message": f"The {service_name} service is temporarily unavailable. Please try again in a few minutes.",
                "service": service_name,
                "retry_after": retry_after
            }
        }
        
        if fallback_available and fallback_message:
            response_data["fallback"] = {
                "available": True,
                "message": fallback_message
            }
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response_data
        )
    
    @staticmethod
    def validation_error(
        field: str,
        message: str,
        value: Optional[Any] = None
    ) -> JSONResponse:
        """Create a validation error response"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": ResponseCode.VALIDATION_ERROR.value,
                    "message": f"Validation error: {message}",
                    "field": field,
                    "invalid_value": value
                }
            }
        )
    
    @staticmethod
    def subscription_conflict(
        local_status: str,
        remote_status: str,
        resolution_in_progress: bool = True
    ) -> JSONResponse:
        """Create a subscription conflict response"""
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error": {
                    "code": ResponseCode.SUBSCRIPTION_CONFLICT.value,
                    "message": "There's a conflict with your subscription status. We're working to resolve this automatically.",
                    "local_status": local_status,
                    "remote_status": remote_status,
                    "resolution_in_progress": resolution_in_progress,
                    "retry_after": 30  # 30 seconds
                }
            }
        )
    
    @staticmethod
    def _get_http_status_code(error: SubscriptionError) -> int:
        """Map SubscriptionError to appropriate HTTP status code"""
        status_mapping = {
            "card_declined": status.HTTP_402_PAYMENT_REQUIRED,
            "insufficient_funds": status.HTTP_402_PAYMENT_REQUIRED,
            "expired_card": status.HTTP_402_PAYMENT_REQUIRED,
            "payment_processing_error": status.HTTP_402_PAYMENT_REQUIRED,
            "payment_method_invalid": status.HTTP_400_BAD_REQUEST,
            "subscription_not_found": status.HTTP_404_NOT_FOUND,
            "subscription_already_exists": status.HTTP_409_CONFLICT,
            "subscription_expired": status.HTTP_402_PAYMENT_REQUIRED,
            "subscription_canceled": status.HTTP_402_PAYMENT_REQUIRED,
            "subscription_conflict": status.HTTP_409_CONFLICT,
            "usage_limit_exceeded": status.HTTP_429_TOO_MANY_REQUESTS,
            "feature_not_available": status.HTTP_402_PAYMENT_REQUIRED,
            "service_unavailable": status.HTTP_503_SERVICE_UNAVAILABLE,
            "database_error": status.HTTP_503_SERVICE_UNAVAILABLE,
            "stripe_service_error": status.HTTP_503_SERVICE_UNAVAILABLE,
            "invalid_subscription_tier": status.HTTP_400_BAD_REQUEST,
            "invalid_user_data": status.HTTP_400_BAD_REQUEST
        }
        
        return status_mapping.get(error.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def _get_action_urls(suggested_action: str) -> Dict[str, str]:
        """Get action URLs for suggested actions"""
        action_urls = {
            "update_payment_method": "/subscription/payment-methods",
            "retry_payment": "/subscription/retry-payment",
            "contact_support": "/support",
            "manage_subscription": "/subscription",
            "renew_subscription": "/upgrade",
            "reactivate_subscription": "/upgrade",
            "upgrade_to_pro": "/upgrade",
            "select_valid_plan": "/pricing",
            "update_profile": "/profile",
            "wait_and_retry": None,
            "retry_later": None
        }
        
        urls = {}
        if suggested_action in action_urls:
            url = action_urls[suggested_action]
            if url:
                urls["primary"] = url
        
        # Always include support URL as fallback
        urls["support"] = "/support"
        
        return urls


class SubscriptionExceptionHandler:
    """Exception handler for subscription-related errors"""
    
    @staticmethod
    def handle_subscription_error(error: SubscriptionError) -> JSONResponse:
        """Handle SubscriptionError and return appropriate response"""
        return SubscriptionResponseBuilder.error(error)
    
    @staticmethod
    def handle_payment_error(error: Exception, user_id: Optional[str] = None) -> JSONResponse:
        """Handle payment-related exceptions"""
        from services.subscription_error_handler import SubscriptionErrorHandler, ErrorCategory, ErrorSeverity
        
        # Create a basic error response for payment failures
        subscription_error = SubscriptionError(
            code="payment_processing_error",
            message=str(error),
            user_message="We encountered an issue processing your payment. Please try again.",
            category=ErrorCategory.PAYMENT,
            severity=ErrorSeverity.MEDIUM,
            details={"error_type": type(error).__name__},
            timestamp=datetime.utcnow(),
            user_id=user_id,
            suggested_action="retry_payment"
        )
        
        return SubscriptionResponseBuilder.error(subscription_error)
    
    @staticmethod
    def handle_stripe_webhook_error(error: Exception, event_type: str) -> JSONResponse:
        """Handle Stripe webhook processing errors"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "webhook_processing_error",
                    "message": "Failed to process webhook event",
                    "event_type": event_type,
                    "retry_recommended": True
                }
            }
        )


# Utility functions for common response patterns

def create_subscription_status_response(user) -> Dict[str, Any]:
    """Create standardized subscription status response"""
    return SubscriptionResponseBuilder.success(
        data={
            "user_id": str(user.id),
            "subscription_tier": user.subscription_tier.value,
            "subscription_status": user.subscription_status.value,
            "is_pro_active": user.is_pro_active(),
            "current_period_end": user.current_period_end.isoformat() if user.current_period_end else None,
            "cancel_at_period_end": user.cancel_at_period_end,
            "usage_limits": user.get_usage_limits_new(),
            "features": {
                "bulk_processing": user.is_pro_active(),
                "advanced_formatting": user.is_pro_active(),
                "premium_templates": user.is_pro_active(),
                "cover_letters": user.is_pro_active(),
                "analytics": user.is_pro_active(),
                "heavy_tailoring": user.is_pro_active()
            }
        },
        message="Subscription status retrieved successfully"
    )


def create_usage_status_response(usage_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized usage status response"""
    return SubscriptionResponseBuilder.success(
        data=usage_stats,
        message="Usage statistics retrieved successfully"
    )


def create_payment_success_response(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized payment success response"""
    return SubscriptionResponseBuilder.success(
        data=payment_data,
        message="Payment processed successfully"
    )


def create_subscription_upgrade_response(subscription_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized subscription upgrade response"""
    return SubscriptionResponseBuilder.success(
        data=subscription_data,
        message="Subscription upgraded successfully"
    )


def create_subscription_cancellation_response(cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create standardized subscription cancellation response"""
    return SubscriptionResponseBuilder.success(
        data=cancellation_data,
        message="Subscription cancellation processed successfully"
    )