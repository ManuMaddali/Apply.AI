"""
Webhook Routes - Stripe webhook handling endpoints

This module handles:
- Stripe webhook endpoint for subscription events
- Webhook signature verification for security
- Automatic subscription status synchronization
- Graceful error handling and retry logic for webhook failures
"""

import logging
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import asyncio
from typing import Dict, Any

from config.database import get_db
from services.payment_service import PaymentService, PaymentError
from services.webhook_logger import WebhookLogger, WebhookEventStatus
from services.subscription_error_handler import SubscriptionErrorHandler, SubscriptionError, ErrorCategory, ErrorSeverity
from config.stripe_config import get_stripe_config, is_supported_webhook_event
from utils.subscription_responses import SubscriptionExceptionHandler
from utils.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stripe")
@limiter.limit("100/minute")  # Allow high rate for webhook events
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events
    
    This endpoint receives webhook events from Stripe and processes them
    to keep subscription status synchronized.
    
    Supported events:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.trial_will_end
    """
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            logger.error("Missing Stripe signature header")
            raise HTTPException(
                status_code=400,
                detail="Missing Stripe signature header"
            )
        
        # Initialize payment service
        payment_service = PaymentService(db)
        
        # Process webhook in background to avoid timeout
        background_tasks.add_task(
            process_webhook_with_retry,
            payment_service,
            payload,
            signature
        )
        
        # Return immediate success to Stripe
        return JSONResponse(
            status_code=200,
            content={"received": True}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in webhook endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


async def process_webhook_with_retry(
    payment_service: PaymentService,
    payload: bytes,
    signature: str,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Process webhook with retry logic and exponential backoff
    
    Args:
        payment_service: PaymentService instance
        payload: Raw webhook payload
        signature: Stripe signature header
        max_retries: Maximum number of retry attempts
    
    Returns:
        Dict containing processing result
    """
    webhook_logger = WebhookLogger(payment_service.db)
    webhook_event = None
    last_error = None
    
    try:
        # Parse event type from payload for logging
        import json
        try:
            payload_data = json.loads(payload.decode('utf-8'))
            event_type = payload_data.get('type', 'unknown')
            stripe_event_id = payload_data.get('id')
        except:
            event_type = 'unknown'
            stripe_event_id = None
        
        # Log webhook received
        webhook_event = webhook_logger.log_webhook_received(
            event_type=event_type,
            payload=payload,
            signature=signature,
            stripe_event_id=stripe_event_id
        )
        
        for attempt in range(max_retries):
            try:
                # Log processing start
                if webhook_event:
                    webhook_logger.log_processing_start(str(webhook_event.id))
                
                # Wait before retry (exponential backoff)
                if attempt > 0:
                    wait_time = 2 ** attempt  # 2, 4, 8 seconds
                    logger.info(f"Retrying webhook processing in {wait_time} seconds (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                
                # Process webhook
                result = await payment_service.handle_webhook(payload, signature)
                
                # Log successful processing
                if webhook_event:
                    webhook_logger.log_processing_success(str(webhook_event.id), result)
                
                logger.info(f"Webhook processed successfully on attempt {attempt + 1}: {result}")
                return result
                
            except PaymentError as e:
                last_error = e
                logger.warning(f"Webhook processing attempt {attempt + 1} failed: {e.message}")
                
                # Use enhanced error handler for payment errors
                error_handler = SubscriptionErrorHandler(db)
                subscription_error = await error_handler.handle_payment_error(
                    error=e,
                    user_id=None,  # Webhook may not have specific user context
                    operation="webhook_processing",
                    context={
                        "event_type": event_type,
                        "attempt": attempt + 1,
                        "max_retries": max_retries
                    }
                )
                
                # Don't retry signature verification errors
                if "signature" in e.message.lower():
                    logger.error(f"Webhook signature verification failed - not retrying: {e.message}")
                    if webhook_event:
                        webhook_logger.log_processing_failure(
                            str(webhook_event.id), 
                            e.message, 
                            will_retry=False
                        )
                    break
                else:
                    # Log retry attempt
                    if webhook_event:
                        will_retry = attempt < max_retries - 1
                        webhook_logger.log_processing_failure(
                            str(webhook_event.id), 
                            e.message, 
                            will_retry=will_retry
                        )
                    
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error in webhook processing attempt {attempt + 1}: {e}")
                
                # Create structured error for unexpected exceptions
                error_handler = SubscriptionErrorHandler(db)
                subscription_error = SubscriptionError(
                    code="webhook_processing_error",
                    message=f"Unexpected webhook processing error: {str(e)}",
                    user_message="We encountered an issue processing a payment notification. This will be retried automatically.",
                    category=ErrorCategory.SYSTEM,
                    severity=ErrorSeverity.HIGH,
                    details={
                        "error_type": type(e).__name__,
                        "event_type": event_type,
                        "attempt": attempt + 1,
                        "max_retries": max_retries
                    },
                    timestamp=datetime.utcnow(),
                    suggested_action="wait_and_retry"
                )
                
                await error_handler._log_subscription_error(subscription_error)
                
                # Log retry attempt
                if webhook_event:
                    will_retry = attempt < max_retries - 1
                    webhook_logger.log_processing_failure(
                        str(webhook_event.id), 
                        str(e), 
                        will_retry=will_retry
                    )
        
        # All retries failed
        error_msg = f"Webhook processing failed after {max_retries} attempts"
        if last_error:
            error_msg += f": {str(last_error)}"
        
        logger.error(error_msg)
        
        # Return error result
        return {
            "status": "error",
            "error": error_msg,
            "attempts": max_retries
        }
        
    except Exception as e:
        logger.error(f"Critical error in webhook processing: {e}")
        return {
            "status": "error",
            "error": f"Critical processing error: {str(e)}",
            "attempts": 0
        }


@router.get("/stripe/test")
@limiter.limit("10/minute")
async def test_webhook_endpoint(request: Request):
    """
    Test endpoint to verify webhook configuration
    
    This endpoint can be used to test that the webhook route is accessible
    and properly configured. It should only be available in development.
    """
    try:
        config = get_stripe_config()
        
        if config.is_production:
            raise HTTPException(
                status_code=404,
                detail="Test endpoint not available in production"
            )
        
        return {
            "status": "ok",
            "message": "Webhook endpoint is accessible",
            "environment": config.environment,
            "supported_events": [
                "customer.subscription.created",
                "customer.subscription.updated", 
                "customer.subscription.deleted",
                "invoice.payment_succeeded",
                "invoice.payment_failed",
                "customer.subscription.trial_will_end"
            ],
            "webhook_configured": bool(config.webhook_secret)
        }
        
    except Exception as e:
        logger.error(f"Error in webhook test endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )


@router.post("/stripe/manual-sync/{user_id}")
@limiter.limit("5/minute")
async def manual_subscription_sync(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Manually sync subscription status for a user
    
    This endpoint allows manual synchronization of subscription status
    from Stripe. Useful for debugging or handling missed webhooks.
    
    Args:
        user_id: User ID to sync subscription for
    """
    try:
        config = get_stripe_config()
        
        # Only allow in development or with proper authentication
        if config.is_production:
            # In production, this would require admin authentication
            # For now, we'll disable it in production
            raise HTTPException(
                status_code=404,
                detail="Manual sync not available in production"
            )
        
        payment_service = PaymentService(db)
        
        # Find user's subscription
        from models.user import User, Subscription
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()
        
        if not subscription or not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=404,
                detail="No Stripe subscription found for user"
            )
        
        # Sync subscription status
        updated_subscription = await payment_service.update_subscription_status(
            subscription.stripe_subscription_id
        )
        
        if updated_subscription:
            return {
                "status": "success",
                "message": "Subscription synced successfully",
                "subscription": {
                    "id": updated_subscription.id,
                    "status": updated_subscription.status.value,
                    "tier": updated_subscription.tier.value,
                    "current_period_end": updated_subscription.current_period_end.isoformat() if updated_subscription.current_period_end else None
                }
            }
        else:
            return {
                "status": "error",
                "message": "Failed to sync subscription"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in manual subscription sync: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )


# Health check for webhook processing
@router.get("/health")
@limiter.limit("30/minute")
async def webhook_health_check(request: Request):
    """
    Health check for webhook processing system
    
    Returns status of webhook configuration and dependencies
    """
    try:
        config = get_stripe_config()
        
        health_status = {
            "status": "healthy",
            "webhook_configured": bool(config.webhook_secret),
            "stripe_configured": config.is_configured,
            "environment": config.environment,
            "supported_events_count": len([
                "customer.subscription.created",
                "customer.subscription.updated", 
                "customer.subscription.deleted",
                "invoice.payment_succeeded",
                "invoice.payment_failed",
                "customer.subscription.trial_will_end"
            ])
        }
        
        # Check if any critical configuration is missing
        if not config.webhook_secret:
            health_status["warnings"] = ["Webhook secret not configured"]
        
        if not config.is_configured:
            health_status["status"] = "unhealthy"
            health_status["errors"] = ["Stripe not properly configured"]
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in webhook health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/events")
@limiter.limit("20/minute")
async def get_webhook_events(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 50,
    event_type: str = None,
    status: str = None,
    hours_back: int = 24
):
    """
    Get recent webhook events for monitoring and debugging
    
    Args:
        limit: Maximum number of events to return (default: 50, max: 100)
        event_type: Filter by specific event type
        status: Filter by event status
        hours_back: How many hours back to look (default: 24)
    """
    try:
        config = get_stripe_config()
        
        # Only allow in development or with proper authentication
        if config.is_production:
            raise HTTPException(
                status_code=404,
                detail="Event monitoring not available in production without authentication"
            )
        
        # Validate parameters
        limit = min(limit, 100)  # Cap at 100
        hours_back = min(hours_back, 168)  # Cap at 1 week
        
        # Parse status enum if provided
        status_enum = None
        if status:
            try:
                status_enum = WebhookEventStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Valid options: {[s.value for s in WebhookEventStatus]}"
                )
        
        webhook_logger = WebhookLogger(db)
        events = webhook_logger.get_webhook_events(
            limit=limit,
            event_type=event_type,
            status=status_enum,
            hours_back=hours_back
        )
        
        return {
            "events": [event.to_dict() for event in events],
            "count": len(events),
            "filters": {
                "limit": limit,
                "event_type": event_type,
                "status": status,
                "hours_back": hours_back
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook events: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get events: {str(e)}"
        )


@router.get("/statistics")
@limiter.limit("10/minute")
async def get_webhook_statistics(
    request: Request,
    db: Session = Depends(get_db),
    hours_back: int = 24
):
    """
    Get webhook processing statistics
    
    Args:
        hours_back: How many hours back to analyze (default: 24, max: 168)
    """
    try:
        config = get_stripe_config()
        
        # Only allow in development or with proper authentication
        if config.is_production:
            raise HTTPException(
                status_code=404,
                detail="Statistics not available in production without authentication"
            )
        
        # Validate parameters
        hours_back = min(hours_back, 168)  # Cap at 1 week
        
        webhook_logger = WebhookLogger(db)
        stats = webhook_logger.get_webhook_statistics(hours_back=hours_back)
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.post("/cleanup")
@limiter.limit("2/hour")
async def cleanup_old_webhook_events(
    request: Request,
    db: Session = Depends(get_db),
    days_to_keep: int = 30
):
    """
    Clean up old webhook events
    
    Args:
        days_to_keep: Number of days of events to keep (default: 30, min: 7)
    """
    try:
        config = get_stripe_config()
        
        # Only allow in development or with proper authentication
        if config.is_production:
            raise HTTPException(
                status_code=404,
                detail="Cleanup not available in production without authentication"
            )
        
        # Validate parameters
        days_to_keep = max(days_to_keep, 7)  # Keep at least 7 days
        
        webhook_logger = WebhookLogger(db)
        deleted_count = webhook_logger.cleanup_old_events(days_to_keep=days_to_keep)
        
        return {
            "status": "success",
            "message": f"Cleaned up {deleted_count} old webhook events",
            "deleted_count": deleted_count,
            "days_kept": days_to_keep
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up webhook events: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cleanup failed: {str(e)}"
        )