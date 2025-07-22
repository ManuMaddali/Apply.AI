"""
Simple Error Handling Test

Test the core error handling functionality without complex dependencies.
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
import os

# Set test environment variables
os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake_key_for_testing"
os.environ["STRIPE_PUBLISHABLE_KEY"] = "pk_test_fake_key_for_testing"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_fake_secret"

# Test the error handling classes directly
from services.subscription_error_handler import (
    SubscriptionError, 
    ErrorCategory, 
    ErrorSeverity,
    SubscriptionErrorHandler
)
from utils.subscription_responses import SubscriptionResponseBuilder


def test_subscription_error_creation():
    """Test creating a subscription error"""
    error = SubscriptionError(
        code="test_error",
        message="Test error message",
        user_message="User-friendly error message",
        category=ErrorCategory.PAYMENT,
        severity=ErrorSeverity.MEDIUM,
        details={"test": "data"},
        timestamp=datetime.utcnow(),
        user_id="test-user-123",
        suggested_action="retry_payment"
    )
    
    assert error.code == "test_error"
    assert error.category == ErrorCategory.PAYMENT
    assert error.severity == ErrorSeverity.MEDIUM
    assert error.user_id == "test-user-123"
    assert error.suggested_action == "retry_payment"
    print("✅ SubscriptionError creation test passed")


def test_error_message_templates():
    """Test error message templates"""
    mock_db = Mock()
    error_handler = SubscriptionErrorHandler(mock_db)
    
    # Test that error messages are properly initialized
    assert "card_declined" in error_handler.error_messages
    assert "insufficient_funds" in error_handler.error_messages
    assert "subscription_not_found" in error_handler.error_messages
    
    # Test message structure
    card_declined_msg = error_handler.error_messages["card_declined"]
    assert "user_message" in card_declined_msg
    assert "suggested_action" in card_declined_msg
    assert "update_payment_method" == card_declined_msg["suggested_action"]
    
    print("✅ Error message templates test passed")


def test_response_builder():
    """Test response builder functionality"""
    # Test success response
    success_response = SubscriptionResponseBuilder.success(
        data={"test": "data"},
        message="Operation successful"
    )
    
    assert success_response["success"] is True
    assert success_response["code"] == "success"
    assert success_response["data"]["test"] == "data"
    
    # Test payment required response
    payment_response = SubscriptionResponseBuilder.payment_required(
        message="Pro subscription required",
        current_tier="free"
    )
    
    assert payment_response.status_code == 402
    
    # Test usage limit response
    usage_response = SubscriptionResponseBuilder.usage_limit_exceeded(
        limit=5,
        remaining=0
    )
    
    assert usage_response.status_code == 429
    
    print("✅ Response builder test passed")


def test_error_severity_mapping():
    """Test error severity mapping"""
    # Test different severity levels
    severities = [ErrorSeverity.LOW, ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
    
    for severity in severities:
        error = SubscriptionError(
            code="test_error",
            message="Test message",
            user_message="User message",
            category=ErrorCategory.PAYMENT,
            severity=severity,
            details={},
            timestamp=datetime.utcnow()
        )
        
        assert error.severity == severity
    
    print("✅ Error severity mapping test passed")


async def test_retry_config():
    """Test retry configuration"""
    from services.subscription_error_handler import RetryConfig
    
    config = RetryConfig(
        max_attempts=3,
        base_delay=2,
        max_delay=60,
        exponential_base=2.0,
        jitter=True
    )
    
    assert config.max_attempts == 3
    assert config.base_delay == 2
    assert config.max_delay == 60
    assert config.exponential_base == 2.0
    assert config.jitter is True
    
    print("✅ Retry configuration test passed")


def test_notification_types():
    """Test notification type enumeration"""
    from services.subscription_notification_service import NotificationType
    
    # Test that all expected notification types exist
    expected_types = [
        "subscription_created",
        "subscription_canceled", 
        "payment_failed",
        "usage_limit_exceeded",
        "grace_period_warning"
    ]
    
    for expected_type in expected_types:
        assert hasattr(NotificationType, expected_type.upper())
    
    print("✅ Notification types test passed")


def test_logging_integration():
    """Test logging integration"""
    from utils.subscription_logger import subscription_logger, EventCategory, LogLevel
    
    # Test that logger can be created
    assert subscription_logger is not None
    
    # Test event categories
    categories = [EventCategory.SUBSCRIPTION, EventCategory.PAYMENT, EventCategory.USAGE]
    for category in categories:
        assert category.value in ["subscription", "payment", "usage"]
    
    # Test log levels
    levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
    for level in levels:
        assert level.value in ["debug", "info", "warning", "error", "critical"]
    
    print("✅ Logging integration test passed")


def run_all_tests():
    """Run all tests"""
    print("🧪 Running comprehensive error handling tests...\n")
    
    try:
        test_subscription_error_creation()
        test_error_message_templates()
        test_response_builder()
        test_error_severity_mapping()
        asyncio.run(test_retry_config())
        test_notification_types()
        test_logging_integration()
        
        print("\n🎉 All error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)