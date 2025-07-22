"""
Subscription Management API Routes

This module provides API endpoints for subscription management including:
- GET /api/subscription/status - Get current subscription info
- POST /api/subscription/upgrade - Create Pro subscription
- POST /api/subscription/cancel - Cancel subscription
- GET /api/subscription/usage - Get usage statistics
- PUT /api/subscription/preferences - Update Pro user settings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from config.database import get_db
from models.user import User, SubscriptionTier, SubscriptionStatus, TailoringMode
from services.subscription_service import SubscriptionService
from services.payment_service import PaymentService, PaymentError
from services.subscription_error_handler import SubscriptionErrorHandler, SubscriptionError, ErrorCategory, ErrorSeverity
from utils.auth import AuthManager
from utils.rate_limiter import limiter, RateLimits
from utils.subscription_responses import (
    SubscriptionResponseBuilder, 
    SubscriptionExceptionHandler,
    create_subscription_status_response,
    create_usage_status_response,
    create_payment_success_response,
    create_subscription_upgrade_response,
    create_subscription_cancellation_response
)

router = APIRouter(prefix="/api/subscription", tags=["subscription"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class SubscriptionStatusResponse(BaseModel):
    user_id: str
    subscription_tier: str
    subscription_status: str
    is_pro_active: bool
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False
    stripe_customer_id: Optional[str] = None
    usage_limits: Dict[str, Any]
    subscription_details: Optional[Dict[str, Any]] = None

class UpgradeSubscriptionRequest(BaseModel):
    payment_method_id: str
    price_id: Optional[str] = None
    
    @validator('payment_method_id')
    def validate_payment_method(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Payment method ID is required')
        return v.strip()

class UpgradeSubscriptionResponse(BaseModel):
    success: bool
    message: str
    subscription_id: Optional[str] = None
    client_secret: Optional[str] = None
    status: Optional[str] = None

class CancelSubscriptionRequest(BaseModel):
    cancel_immediately: bool = False
    reason: Optional[str] = None

class CancelSubscriptionResponse(BaseModel):
    success: bool
    message: str
    status: str
    cancel_at_period_end: Optional[bool] = None
    access_until: Optional[str] = None

class UsageStatisticsResponse(BaseModel):
    user_id: str
    subscription_tier: str
    weekly_usage: Dict[str, int]
    monthly_usage: Dict[str, int]
    total_usage: Dict[str, int]
    current_limits: Dict[str, Any]
    weekly_usage_count: int
    weekly_usage_reset: Optional[str] = None
    total_usage_count: int
    usage_percentage: Dict[str, float]

class UserPreferencesRequest(BaseModel):
    default_tailoring_mode: Optional[str] = None
    email_notifications: Optional[bool] = None
    analytics_consent: Optional[bool] = None
    
    @validator('default_tailoring_mode')
    def validate_tailoring_mode(cls, v):
        if v and v not in ['light', 'heavy']:
            raise ValueError('Tailoring mode must be "light" or "heavy"')
        return v

class UserPreferencesResponse(BaseModel):
    success: bool
    message: str
    preferences: Dict[str, Any]

# Helper functions
def get_subscription_service(db: Session) -> SubscriptionService:
    """Get subscription service instance"""
    return SubscriptionService(db)

def get_payment_service(db: Session) -> PaymentService:
    """Get payment service instance"""
    return PaymentService(db)

def calculate_usage_percentage(usage: Dict[str, int], limits: Dict[str, Any]) -> Dict[str, float]:
    """Calculate usage percentage for each usage type"""
    percentages = {}
    for usage_type, count in usage.items():
        limit = limits.get(usage_type, 0)
        if limit > 0:
            percentages[usage_type] = min((count / limit) * 100, 100.0)
        else:
            percentages[usage_type] = 0.0
    return percentages

# Subscription Management Endpoints

@router.get("/status", response_model=SubscriptionStatusResponse)
@limiter.limit(RateLimits.SUBSCRIPTION_STATUS)
async def get_subscription_status(
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Get current subscription status and information
    
    Returns detailed subscription information including:
    - Current subscription tier and status
    - Pro subscription active status
    - Current period dates
    - Usage limits
    - Subscription details
    """
    try:
        subscription_service = get_subscription_service(db)
        
        # Validate and get current subscription status
        status_info = await subscription_service.validate_subscription_status(user.id)
        
        if not status_info.get("valid", False):
            logger.warning(f"Invalid subscription status for user {user.id}: {status_info.get('reason')}")
        
        # Get subscription details
        active_subscription = subscription_service.get_active_subscription(user.id)
        subscription_details = None
        if active_subscription:
            subscription_details = {
                "id": active_subscription.id,
                "created_at": active_subscription.created_at.isoformat(),
                "stripe_subscription_id": active_subscription.stripe_subscription_id,
                "current_period_start": active_subscription.current_period_start.isoformat() if active_subscription.current_period_start else None,
                "current_period_end": active_subscription.current_period_end.isoformat() if active_subscription.current_period_end else None,
            }
        
        # Get usage limits
        usage_limits = user.get_usage_limits_new() if hasattr(user, 'get_usage_limits_new') else {}
        
        response_data = SubscriptionStatusResponse(
            user_id=str(user.id),
            subscription_tier=user.subscription_tier.value,
            subscription_status=user.subscription_status.value,
            is_pro_active=user.is_pro_active(),
            current_period_start=user.current_period_start.isoformat() if user.current_period_start else None,
            current_period_end=user.current_period_end.isoformat() if user.current_period_end else None,
            cancel_at_period_end=user.cancel_at_period_end or False,
            stripe_customer_id=user.stripe_customer_id,
            usage_limits=usage_limits,
            subscription_details=subscription_details
        )
        
        logger.info(f"Retrieved subscription status for user {user.id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error getting subscription status for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription status"
        )

@router.post("/upgrade", response_model=UpgradeSubscriptionResponse)
@limiter.limit(RateLimits.SUBSCRIPTION_UPGRADE)
async def upgrade_subscription(
    request: Request,
    upgrade_data: UpgradeSubscriptionRequest,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Upgrade user to Pro subscription
    
    Creates a new Pro subscription using Stripe payment processing.
    Requires valid payment method and handles payment failures gracefully.
    """
    try:
        # Check if user already has Pro subscription
        if user.subscription_tier == SubscriptionTier.PRO and user.is_pro_active():
            return UpgradeSubscriptionResponse(
                success=False,
                message="User already has an active Pro subscription",
                status="already_pro"
            )
        
        payment_service = get_payment_service(db)
        
        # Create subscription through payment service
        result = await payment_service.create_subscription(
            user_id=user.id,
            payment_method_id=upgrade_data.payment_method_id,
            price_id=upgrade_data.price_id
        )
        
        logger.info(f"Successfully upgraded user {user.id} to Pro subscription")
        
        return UpgradeSubscriptionResponse(
            success=True,
            message="Successfully upgraded to Pro subscription",
            subscription_id=result.get("subscription_id"),
            client_secret=result.get("client_secret"),
            status=result.get("status", "active")
        )
        
    except PaymentError as e:
        logger.error(f"Payment error upgrading user {user.id}: {e}")
        
        # Use enhanced error handler
        error_handler = SubscriptionErrorHandler(db)
        subscription_error = await error_handler.handle_payment_error(
            error=e,
            user_id=str(user.id),
            operation="create_subscription",
            context={"payment_method_id": upgrade_data.payment_method_id}
        )
        
        return SubscriptionExceptionHandler.handle_subscription_error(subscription_error)
        
    except Exception as e:
        logger.error(f"Error upgrading subscription for user {user.id}: {e}")
        
        # Create structured error for unexpected exceptions
        error_handler = SubscriptionErrorHandler(db)
        subscription_error = SubscriptionError(
            code="subscription_upgrade_error",
            message=f"Unexpected error during subscription upgrade: {str(e)}",
            user_message="We encountered an unexpected issue while upgrading your subscription. Please try again or contact support.",
            category=ErrorCategory.SUBSCRIPTION,
            severity=ErrorSeverity.HIGH,
            details={"error_type": type(e).__name__, "operation": "upgrade_subscription"},
            timestamp=datetime.utcnow(),
            user_id=str(user.id),
            suggested_action="retry_payment"
        )
        
        await error_handler._log_subscription_error(subscription_error)
        return SubscriptionExceptionHandler.handle_subscription_error(subscription_error)

@router.post("/cancel", response_model=CancelSubscriptionResponse)
@limiter.limit(RateLimits.SUBSCRIPTION_CANCEL)
async def cancel_subscription(
    request: Request,
    cancel_data: CancelSubscriptionRequest,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription
    
    Cancels the user's Pro subscription either immediately or at the end
    of the current billing period. Handles both Stripe and local cancellation.
    """
    try:
        # Check if user has an active subscription to cancel
        if user.subscription_tier != SubscriptionTier.PRO or not user.is_pro_active():
            return CancelSubscriptionResponse(
                success=False,
                message="No active Pro subscription to cancel",
                status="no_subscription"
            )
        
        payment_service = get_payment_service(db)
        
        # Cancel subscription through payment service
        result = await payment_service.cancel_subscription(
            user_id=user.id,
            cancel_immediately=cancel_data.cancel_immediately
        )
        
        # Log cancellation reason if provided
        if cancel_data.reason:
            logger.info(f"Subscription canceled for user {user.id} - Reason: {cancel_data.reason}")
        
        logger.info(f"Successfully canceled subscription for user {user.id} (immediate: {cancel_data.cancel_immediately})")
        
        return CancelSubscriptionResponse(
            success=True,
            message="Subscription canceled successfully",
            status=result.get("status", "canceled"),
            cancel_at_period_end=result.get("cancel_at_period_end"),
            access_until=result.get("access_until")
        )
        
    except PaymentError as e:
        logger.error(f"Payment error canceling subscription for user {user.id}: {e}")
        
        # Use enhanced error handler
        error_handler = SubscriptionErrorHandler(db)
        subscription_error = await error_handler.handle_payment_error(
            error=e,
            user_id=str(user.id),
            operation="cancel_subscription",
            context={"cancel_immediately": cancel_data.cancel_immediately, "reason": cancel_data.reason}
        )
        
        return SubscriptionExceptionHandler.handle_subscription_error(subscription_error)
        
    except Exception as e:
        logger.error(f"Error canceling subscription for user {user.id}: {e}")
        
        # Create structured error for unexpected exceptions
        error_handler = SubscriptionErrorHandler(db)
        subscription_error = SubscriptionError(
            code="subscription_cancellation_error",
            message=f"Unexpected error during subscription cancellation: {str(e)}",
            user_message="We encountered an issue while canceling your subscription. Please try again or contact support.",
            category=ErrorCategory.SUBSCRIPTION,
            severity=ErrorSeverity.HIGH,
            details={"error_type": type(e).__name__, "operation": "cancel_subscription"},
            timestamp=datetime.utcnow(),
            user_id=str(user.id),
            suggested_action="contact_support"
        )
        
        await error_handler._log_subscription_error(subscription_error)
        return SubscriptionExceptionHandler.handle_subscription_error(subscription_error)

@router.get("/usage", response_model=UsageStatisticsResponse)
@limiter.limit(RateLimits.SUBSCRIPTION_USAGE)
async def get_usage_statistics(
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for the current user
    
    Returns detailed usage information including:
    - Weekly, monthly, and total usage by type
    - Current usage limits
    - Usage percentages
    - Weekly usage reset date
    """
    try:
        subscription_service = get_subscription_service(db)
        
        # Get usage statistics
        usage_stats = await subscription_service.get_usage_statistics(user.id)
        
        if not usage_stats:
            # Return default empty stats if no data found
            usage_stats = {
                "weekly_usage": {},
                "monthly_usage": {},
                "total_usage": {},
                "current_limits": user.get_usage_limits_new() if hasattr(user, 'get_usage_limits_new') else {},
                "weekly_usage_count": user.weekly_usage_count or 0,
                "weekly_usage_reset": user.weekly_usage_reset.isoformat() if user.weekly_usage_reset else None,
                "total_usage_count": user.total_usage_count or 0
            }
        
        # Calculate usage percentages
        usage_percentage = calculate_usage_percentage(
            usage_stats.get("weekly_usage", {}),
            usage_stats.get("current_limits", {})
        )
        
        response_data = UsageStatisticsResponse(
            user_id=str(user.id),
            subscription_tier=user.subscription_tier.value,
            weekly_usage=usage_stats.get("weekly_usage", {}),
            monthly_usage=usage_stats.get("monthly_usage", {}),
            total_usage=usage_stats.get("total_usage", {}),
            current_limits=usage_stats.get("current_limits", {}),
            weekly_usage_count=usage_stats.get("weekly_usage_count", 0),
            weekly_usage_reset=usage_stats.get("weekly_usage_reset"),
            total_usage_count=usage_stats.get("total_usage_count", 0),
            usage_percentage=usage_percentage
        )
        
        logger.info(f"Retrieved usage statistics for user {user.id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error getting usage statistics for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics"
        )

@router.put("/preferences", response_model=UserPreferencesResponse)
@limiter.limit(RateLimits.USER_PREFERENCES)
async def update_user_preferences(
    request: Request,
    preferences_data: UserPreferencesRequest,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Update Pro user preferences and settings
    
    Allows Pro users to update their preferences including:
    - Default tailoring mode (light/heavy)
    - Email notification settings
    - Analytics consent
    
    Note: Some preferences may require Pro subscription
    """
    try:
        updated_preferences = {}
        
        # Update default tailoring mode (Pro users only)
        if preferences_data.default_tailoring_mode is not None:
            if user.subscription_tier != SubscriptionTier.PRO or not user.is_pro_active():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tailoring mode preferences require Pro subscription"
                )
            
            # Convert string to enum
            tailoring_mode = TailoringMode.LIGHT if preferences_data.default_tailoring_mode == 'light' else TailoringMode.HEAVY
            
            # Update user's preferred tailoring mode
            user.preferred_tailoring_mode = tailoring_mode
            updated_preferences['default_tailoring_mode'] = preferences_data.default_tailoring_mode
        
        # Update email notifications
        if preferences_data.email_notifications is not None:
            if hasattr(user, 'email_notifications'):
                user.email_notifications = preferences_data.email_notifications
                updated_preferences['email_notifications'] = preferences_data.email_notifications
        
        # Update analytics consent
        if preferences_data.analytics_consent is not None:
            if hasattr(user, 'analytics_consent'):
                user.analytics_consent = preferences_data.analytics_consent
                updated_preferences['analytics_consent'] = preferences_data.analytics_consent
        
        # Save changes to database
        if updated_preferences:
            db.commit()
            db.refresh(user)
            
            logger.info(f"Updated preferences for user {user.id}: {updated_preferences}")
            
            return UserPreferencesResponse(
                success=True,
                message="Preferences updated successfully",
                preferences=updated_preferences
            )
        else:
            return UserPreferencesResponse(
                success=True,
                message="No preferences to update",
                preferences={}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating preferences for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences"
        )

# Additional helper endpoints

@router.get("/renewal-date")
@limiter.limit(RateLimits.SUBSCRIPTION_INFO)
async def get_subscription_renewal_date(
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """Get next subscription renewal date"""
    try:
        subscription_service = get_subscription_service(db)
        renewal_date = subscription_service.get_subscription_renewal_date(user.id)
        
        return {
            "user_id": user.id,
            "renewal_date": renewal_date.isoformat() if renewal_date else None,
            "has_renewal": renewal_date is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting renewal date for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve renewal date"
        )

@router.get("/history")
@limiter.limit(RateLimits.SUBSCRIPTION_INFO)
async def get_subscription_history(
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """Get user's subscription history"""
    try:
        subscription_service = get_subscription_service(db)
        subscriptions = subscription_service.get_user_subscriptions(user.id)
        
        history = []
        for sub in subscriptions:
            history.append({
                "id": sub.id,
                "tier": sub.tier.value,
                "status": sub.status.value,
                "created_at": sub.created_at.isoformat(),
                "current_period_start": sub.current_period_start.isoformat() if sub.current_period_start else None,
                "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
                "canceled_at": sub.canceled_at.isoformat() if sub.canceled_at else None,
                "cancel_at_period_end": sub.cancel_at_period_end or False
            })
        
        return {
            "user_id": user.id,
            "subscription_history": history,
            "total_subscriptions": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting subscription history for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription history"
        )

@router.get("/billing-history")
@limiter.limit(RateLimits.SUBSCRIPTION_INFO)
async def get_billing_history(
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    Get user's billing history with downloadable receipts
    
    Returns payment history including successful payments, failed attempts,
    and downloadable receipt information for Pro users.
    """
    try:
        from models.user import PaymentHistory
        
        # Query payment history for the user
        payment_query = db.query(PaymentHistory).filter(
            PaymentHistory.user_id == user.id
        ).order_by(PaymentHistory.payment_date.desc())
        
        # Apply pagination
        total_payments = payment_query.count()
        payments = payment_query.offset(offset).limit(limit).all()
        
        # Format payment history
        billing_history = []
        for payment in payments:
            payment_data = payment.to_dict()
            
            # Add receipt download URL if available
            if payment.stripe_invoice_id and payment.is_successful():
                payment_data["receipt_url"] = f"/api/subscription/receipt/{payment.stripe_invoice_id}"
                payment_data["downloadable"] = True
            else:
                payment_data["downloadable"] = False
            
            billing_history.append(payment_data)
        
        return {
            "user_id": user.id,
            "billing_history": billing_history,
            "pagination": {
                "total": total_payments,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_payments
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting billing history for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing history"
        )

@router.get("/receipt/{invoice_id}")
@limiter.limit("10/minute")
async def download_receipt(
    invoice_id: str,
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Download receipt for a specific invoice
    
    Provides secure access to Stripe-hosted receipts for user's payments.
    """
    try:
        from models.user import PaymentHistory
        
        # Verify the invoice belongs to the user
        payment = db.query(PaymentHistory).filter(
            PaymentHistory.stripe_invoice_id == invoice_id,
            PaymentHistory.user_id == user.id
        ).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        if not payment.is_successful():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receipt not available for failed payments"
            )
        
        # Get receipt URL from Stripe
        payment_service = get_payment_service(db)
        receipt_url = await payment_service.get_receipt_url(invoice_id)
        
        if not receipt_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not available"
            )
        
        return {
            "invoice_id": invoice_id,
            "receipt_url": receipt_url,
            "payment_date": payment.payment_date.isoformat(),
            "amount": payment.amount_in_dollars(),
            "currency": payment.currency.upper(),
            "description": payment.description
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading receipt {invoice_id} for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipt"
        )

@router.get("/payment-methods")
@limiter.limit(RateLimits.SUBSCRIPTION_INFO)
async def get_payment_methods(
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Get user's saved payment methods
    
    Returns list of payment methods associated with the user's Stripe customer.
    """
    try:
        if not user.stripe_customer_id:
            return {
                "user_id": user.id,
                "payment_methods": [],
                "default_payment_method": None
            }
        
        payment_service = get_payment_service(db)
        payment_methods = await payment_service.get_payment_methods(user.stripe_customer_id)
        
        return {
            "user_id": user.id,
            "payment_methods": payment_methods,
            "default_payment_method": payment_methods[0] if payment_methods else None
        }
        
    except Exception as e:
        logger.error(f"Error getting payment methods for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment methods"
        )

@router.post("/payment-methods/{payment_method_id}/set-default")
@limiter.limit("10/minute")
async def set_default_payment_method(
    payment_method_id: str,
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Set default payment method for user
    
    Updates the default payment method for the user's subscription.
    """
    try:
        if not user.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe customer found"
            )
        
        payment_service = get_payment_service(db)
        result = await payment_service.set_default_payment_method(
            user.stripe_customer_id, 
            payment_method_id
        )
        
        return {
            "success": True,
            "message": "Default payment method updated successfully",
            "payment_method_id": payment_method_id
        }
        
    except PaymentError as e:
        logger.error(f"Payment error setting default method for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error setting default payment method for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update default payment method"
        )

@router.delete("/payment-methods/{payment_method_id}")
@limiter.limit("10/minute")
async def remove_payment_method(
    payment_method_id: str,
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """
    Remove a payment method
    
    Detaches the payment method from the user's Stripe customer.
    """
    try:
        if not user.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe customer found"
            )
        
        payment_service = get_payment_service(db)
        result = await payment_service.remove_payment_method(payment_method_id)
        
        return {
            "success": True,
            "message": "Payment method removed successfully",
            "payment_method_id": payment_method_id
        }
        
    except PaymentError as e:
        logger.error(f"Payment error removing method for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing payment method for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove payment method"
        )

@router.get("/analytics-dashboard")
@limiter.limit(RateLimits.SUBSCRIPTION_INFO)
async def get_analytics_dashboard(
    request: Request,
    user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db),
    time_range: str = "30d"
):
    """
    Get analytics dashboard data for Pro users
    
    Returns comprehensive analytics including success rates, keyword optimization,
    and usage patterns for Pro subscribers.
    """
    try:
        # Check if user has Pro subscription
        if user.subscription_tier != SubscriptionTier.PRO or not user.is_pro_active():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Analytics dashboard requires active Pro subscription"
            )
        
        from services.analytics_service import AnalyticsService
        analytics_service = AnalyticsService(db)
        
        # Get dashboard data
        dashboard_data = await analytics_service.get_user_analytics_dashboard(
            user.id, 
            time_range
        )
        
        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )
        
        return dashboard_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics dashboard for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics dashboard"
        )
