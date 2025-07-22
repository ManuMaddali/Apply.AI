"""
Demonstration of Comprehensive Error Handling System

This script demonstrates the comprehensive error handling and user feedback system
implemented for the subscription service, including:

1. User-friendly error messages for subscription failures
2. Payment failure handling with retry mechanisms  
3. Subscription status conflict resolution
4. Graceful fallbacks for service unavailability
5. Comprehensive logging for subscription events and errors
6. User notification system for subscription changes
"""

import asyncio
import os
from datetime import datetime
from unittest.mock import Mock
import stripe

# Set up test environment
os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake_key_for_testing"
os.environ["STRIPE_PUBLISHABLE_KEY"] = "pk_test_fake_key_for_testing"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_fake_secret"

from services.subscription_error_handler import (
    SubscriptionErrorHandler, 
    SubscriptionError, 
    ErrorCategory, 
    ErrorSeverity
)
from services.subscription_notification_service import (
    SubscriptionNotificationService,
    NotificationType
)
from services.service_availability_monitor import ServiceAvailabilityMonitor
from utils.subscription_responses import SubscriptionResponseBuilder
from utils.subscription_logger import subscription_logger
from services.payment_service import PaymentError
from models.user import User, SubscriptionTier, SubscriptionStatus


async def demo_payment_error_handling():
    """Demonstrate payment error handling with user-friendly messages"""
    print("🔧 Demo 1: Payment Error Handling")
    print("=" * 50)
    
    # Mock database session
    mock_db = Mock()
    error_handler = SubscriptionErrorHandler(mock_db)
    
    # Simulate different types of payment errors
    payment_errors = [
        {
            "name": "Card Declined",
            "stripe_error": stripe.error.CardError(
                message="Your card was declined.",
                param="card",
                code="card_declined"
            )
        },
        {
            "name": "Insufficient Funds", 
            "stripe_error": stripe.error.CardError(
                message="Your card has insufficient funds.",
                param="card", 
                code="card_declined"
            )
        },
        {
            "name": "Expired Card",
            "stripe_error": stripe.error.CardError(
                message="Your card has expired.",
                param="card",
                code="expired_card"
            )
        }
    ]
    
    for error_info in payment_errors:
        print(f"\n📋 Handling: {error_info['name']}")
        
        payment_error = PaymentError("Payment failed", error_info["stripe_error"])
        
        # Handle the error
        result = await error_handler.handle_payment_error(
            error=payment_error,
            user_id="demo-user-123",
            operation="create_subscription",
            context={"payment_method_id": "pm_demo_123"}
        )
        
        print(f"   Error Code: {result.code}")
        print(f"   User Message: {result.user_message}")
        print(f"   Suggested Action: {result.suggested_action}")
        print(f"   Severity: {result.severity.value}")
        
        # Create API response
        response = SubscriptionResponseBuilder.error(result)
        print(f"   HTTP Status: {response.status_code}")
    
    print("\n✅ Payment error handling demo completed")


async def demo_subscription_conflict_resolution():
    """Demonstrate subscription status conflict resolution"""
    print("\n🔧 Demo 2: Subscription Conflict Resolution")
    print("=" * 50)
    
    mock_db = Mock()
    error_handler = SubscriptionErrorHandler(mock_db)
    
    # Mock user
    mock_user = Mock(spec=User)
    mock_user.id = "demo-user-123"
    mock_user.subscription_tier = SubscriptionTier.PRO
    mock_user.subscription_status = SubscriptionStatus.ACTIVE
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Mock subscription
    mock_subscription = Mock()
    mock_subscription.status = SubscriptionStatus.ACTIVE
    
    conflicts = [
        {
            "name": "Local Active, Stripe Canceled",
            "local_status": SubscriptionStatus.ACTIVE,
            "stripe_status": "canceled"
        },
        {
            "name": "Local Active, Stripe Past Due",
            "local_status": SubscriptionStatus.ACTIVE,
            "stripe_status": "past_due"
        }
    ]
    
    for conflict in conflicts:
        print(f"\n📋 Resolving: {conflict['name']}")
        
        result = await error_handler.handle_subscription_conflict(
            user_id="demo-user-123",
            local_status=conflict["local_status"],
            stripe_status=conflict["stripe_status"],
            subscription_id="sub_demo_123"
        )
        
        print(f"   Resolved: {result['resolved']}")
        print(f"   Action Taken: {result.get('action_taken', 'N/A')}")
        print(f"   User Notified: {result.get('user_notified', False)}")
    
    print("\n✅ Subscription conflict resolution demo completed")


async def demo_service_unavailability_handling():
    """Demonstrate graceful fallbacks for service unavailability"""
    print("\n🔧 Demo 3: Service Unavailability Handling")
    print("=" * 50)
    
    mock_db = Mock()
    error_handler = SubscriptionErrorHandler(mock_db)
    
    services = [
        {
            "name": "stripe",
            "error": Exception("Stripe API timeout"),
            "fallback_data": None
        },
        {
            "name": "database", 
            "error": Exception("Database connection lost"),
            "fallback_data": {"cached_subscription": "pro"}
        },
        {
            "name": "email",
            "error": Exception("SMTP server unavailable"),
            "fallback_data": None
        }
    ]
    
    for service in services:
        print(f"\n📋 Service: {service['name']}")
        
        result = await error_handler.handle_service_unavailability(
            service_name=service["name"],
            error=service["error"],
            user_id="demo-user-123",
            fallback_data=service["fallback_data"]
        )
        
        print(f"   Service Available: {result['service_available']}")
        print(f"   Fallback Applied: {result['fallback_applied']}")
        print(f"   User Message: {result['user_message']}")
        print(f"   Retry After: {result['retry_after']} seconds")
    
    print("\n✅ Service unavailability handling demo completed")


async def demo_retry_mechanism():
    """Demonstrate retry mechanism with exponential backoff"""
    print("\n🔧 Demo 4: Retry Mechanism")
    print("=" * 50)
    
    mock_db = Mock()
    error_handler = SubscriptionErrorHandler(mock_db)
    
    # Simulate operation that succeeds after 2 failures
    call_count = 0
    
    async def flaky_operation():
        nonlocal call_count
        call_count += 1
        print(f"   Attempt {call_count}")
        
        if call_count < 3:
            raise Exception(f"Temporary failure #{call_count}")
        return {"success": True, "data": "Operation completed"}
    
    print("📋 Testing retry with eventual success:")
    
    from services.subscription_error_handler import RetryConfig
    config = RetryConfig(max_attempts=5, base_delay=0.1)  # Fast for demo
    
    success, result, error = await error_handler.retry_with_backoff(
        flaky_operation,
        "demo_operation",
        config
    )
    
    print(f"   Final Result: Success={success}")
    if success:
        print(f"   Data: {result}")
    else:
        print(f"   Error: {error.user_message}")
    
    print("\n✅ Retry mechanism demo completed")


async def demo_notification_system():
    """Demonstrate user notification system"""
    print("\n🔧 Demo 5: User Notification System")
    print("=" * 50)
    
    mock_db = Mock()
    
    # Mock user
    mock_user = Mock(spec=User)
    mock_user.id = "demo-user-123"
    mock_user.email = "demo@example.com"
    mock_user.full_name = "Demo User"
    mock_user.username = "demouser"
    
    # Create notification service with mocked email service
    with patch('services.subscription_notification_service.EmailService') as mock_email_service:
        notification_service = SubscriptionNotificationService(mock_db)
        notification_service.email_service.send_email = Mock(return_value=True)
        
        notifications = [
            {
                "name": "Subscription Created",
                "func": notification_service.notify_subscription_created,
                "data": {
                    "tier": "Pro",
                    "amount": "$9.99",
                    "cycle": "monthly",
                    "next_billing_date": "2024-02-01"
                }
            },
            {
                "name": "Payment Failed",
                "func": notification_service.notify_payment_failed,
                "data": {
                    "amount": "$9.99",
                    "user_friendly_reason": "Your card was declined",
                    "next_retry_date": "2024-01-15"
                }
            },
            {
                "name": "Usage Limit Exceeded",
                "func": notification_service.notify_usage_limit_exceeded,
                "data": {
                    "limit": 5,
                    "reset_date": "2024-01-20"
                }
            }
        ]
        
        for notification in notifications:
            print(f"\n📋 Sending: {notification['name']}")
            
            if notification["name"] == "Payment Failed":
                result = await notification["func"](mock_user, notification["data"], retry_count=1)
            else:
                result = await notification["func"](mock_user, notification["data"])
            
            print(f"   Notification Sent: {result}")
            
            if notification_service.email_service.send_email.called:
                call_args = notification_service.email_service.send_email.call_args
                print(f"   Email To: {call_args[1]['to_email']}")
                print(f"   Subject: {call_args[1]['subject']}")
                print(f"   Template: {call_args[1]['template_name']}")
    
    print("\n✅ User notification system demo completed")


async def demo_comprehensive_logging():
    """Demonstrate comprehensive logging system"""
    print("\n🔧 Demo 6: Comprehensive Logging")
    print("=" * 50)
    
    # Log different types of events
    events = [
        {
            "name": "Subscription Created",
            "func": subscription_logger.log_subscription_created,
            "args": ("demo-user-123", "sub_demo_123", "Pro", "card", 9.99, 0.5)
        },
        {
            "name": "Payment Success",
            "func": subscription_logger.log_payment_success,
            "args": ("demo-user-123", "pi_demo_123", 9.99)
        },
        {
            "name": "Payment Failure",
            "func": subscription_logger.log_payment_failure,
            "args": ("demo-user-123", "card_declined", "Your card was declined")
        },
        {
            "name": "Usage Tracking",
            "func": subscription_logger.log_usage_tracking,
            "args": ("demo-user-123", "resume_processing", 1, "/api/resumes/tailor", 0.3)
        },
        {
            "name": "Usage Limit Exceeded",
            "func": subscription_logger.log_usage_limit_exceeded,
            "args": ("demo-user-123", "resume_processing", 6, 5)
        }
    ]
    
    for event in events:
        print(f"\n📋 Logging: {event['name']}")
        event["func"](*event["args"])
        print(f"   ✅ Event logged successfully")
    
    print("\n✅ Comprehensive logging demo completed")


async def demo_response_building():
    """Demonstrate standardized response building"""
    print("\n🔧 Demo 7: Response Building")
    print("=" * 50)
    
    responses = [
        {
            "name": "Success Response",
            "func": SubscriptionResponseBuilder.success,
            "args": ({"subscription_id": "sub_123"}, "Subscription created successfully")
        },
        {
            "name": "Payment Required",
            "func": SubscriptionResponseBuilder.payment_required,
            "args": ("Pro subscription required",)
        },
        {
            "name": "Usage Limit Exceeded",
            "func": SubscriptionResponseBuilder.usage_limit_exceeded,
            "args": (5, 0, "2024-01-20T00:00:00Z")
        },
        {
            "name": "Service Unavailable",
            "func": SubscriptionResponseBuilder.service_unavailable,
            "args": ("stripe", 300, True, "Using cached data")
        }
    ]
    
    for response_info in responses:
        print(f"\n📋 Building: {response_info['name']}")
        
        if response_info["name"] == "Success Response":
            response = response_info["func"](*response_info["args"])
            print(f"   Type: Dictionary")
            print(f"   Success: {response['success']}")
            print(f"   Code: {response['code']}")
        else:
            response = response_info["func"](*response_info["args"])
            print(f"   Type: JSONResponse")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content Type: {response.headers.get('content-type', 'application/json')}")
    
    print("\n✅ Response building demo completed")


async def main():
    """Run all demonstrations"""
    print("🎯 Comprehensive Error Handling System Demonstration")
    print("=" * 60)
    print("This demo showcases the complete error handling and user feedback system")
    print("implemented for the subscription service.\n")
    
    try:
        await demo_payment_error_handling()
        await demo_subscription_conflict_resolution()
        await demo_service_unavailability_handling()
        await demo_retry_mechanism()
        await demo_notification_system()
        await demo_comprehensive_logging()
        await demo_response_building()
        
        print("\n" + "=" * 60)
        print("🎉 All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ User-friendly error messages for subscription failures")
        print("✅ Payment failure handling with retry mechanisms")
        print("✅ Subscription status conflict resolution")
        print("✅ Graceful fallbacks for service unavailability")
        print("✅ Comprehensive logging for subscription events and errors")
        print("✅ User notification system for subscription changes")
        print("✅ Standardized API response building")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Import patch here to avoid issues
    from unittest.mock import patch
    
    asyncio.run(main())