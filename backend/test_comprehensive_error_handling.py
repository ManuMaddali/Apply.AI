"""
Comprehensive Error Handling Test Suite

This test suite verifies:
- User-friendly error messages for subscription failures
- Payment failure handling with retry mechanisms
- Subscription status conflict resolution
- Graceful fallbacks for service unavailability
- Comprehensive logging for subscription events and errors
- User notification system for subscription changes
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from services.subscription_error_handler import (
    SubscriptionErrorHandler, 
    SubscriptionError, 
    ErrorCategory, 
    ErrorSeverity,
    RetryConfig
)
from services.subscription_notification_service import (
    SubscriptionNotificationService,
    NotificationType
)
from services.service_availability_monitor import (
    ServiceAvailabilityMonitor,
    ServiceStatus,
    CircuitState
)
from utils.subscription_responses import SubscriptionResponseBuilder
from utils.subscription_logger import subscription_logger
from models.user import User, SubscriptionTier, SubscriptionStatus
from services.payment_service import PaymentError
import stripe


class TestSubscriptionErrorHandler:
    """Test subscription error handling functionality"""
    
    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def error_handler(self, mock_db_session):
        return SubscriptionErrorHandler(mock_db_session)
    
    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = "test-user-123"
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.subscription_tier = SubscriptionTier.FREE
        return user
    
    @pytest.mark.asyncio
    async def test_handle_payment_error_card_declined(self, error_handler, mock_user):
        """Test handling of card declined errors"""
        # Create a mock Stripe card error
        stripe_error = stripe.error.CardError(
            message="Your card was declined.",
            param="card",
            code="card_declined",
            decline_code="generic_decline"
        )
        payment_error = PaymentError("Payment failed", stripe_error)
        
        # Handle the error
        result = await error_handler.handle_payment_error(
            error=payment_error,
            user_id=str(mock_user.id),
            operation="create_subscription",
            context={"payment_method_id": "pm_test_123"}
        )
        
        # Verify error structure
        assert isinstance(result, SubscriptionError)
        assert result.code == "card_declined"
        assert result.category == ErrorCategory.PAYMENT
        assert result.severity == ErrorSeverity.MEDIUM
        assert "declined" in result.user_message.lower()
        assert result.suggested_action == "update_payment_method"
    
    @pytest.mark.asyncio
    async def test_handle_payment_error_insufficient_funds(self, error_handler, mock_user):
        """Test handling of insufficient funds errors"""
        stripe_error = stripe.error.CardError(
            message="Your card has insufficient funds.",
            param="card",
            code="card_declined",
            decline_code="insufficient_funds"
        )
        payment_error = PaymentError("Payment failed", stripe_error)
        
        result = await error_handler.handle_payment_error(
            error=payment_error,
            user_id=str(mock_user.id),
            operation="create_subscription"
        )
        
        assert result.code == "insufficient_funds"
        assert "insufficient funds" in result.user_message.lower()
        assert result.suggested_action == "update_payment_method"
    
    @pytest.mark.asyncio
    async def test_handle_subscription_conflict_resolution(self, error_handler, mock_db_session):
        """Test subscription conflict resolution"""
        user_id = "test-user-123"
        local_status = SubscriptionStatus.ACTIVE
        stripe_status = "canceled"
        subscription_id = "sub_test_123"
        
        # Mock user query
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.subscription_tier = SubscriptionTier.PRO
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock subscription query
        mock_subscription = Mock()
        mock_subscription.status = SubscriptionStatus.ACTIVE
        
        result = await error_handler.handle_subscription_conflict(
            user_id=user_id,
            local_status=local_status,
            stripe_status=stripe_status,
            subscription_id=subscription_id
        )
        
        assert result["resolved"] is True
        assert result["action_taken"] == "downgrade_to_free"
    
    @pytest.mark.asyncio
    async def test_service_unavailability_handling(self, error_handler):
        """Test handling of service unavailability"""
        service_name = "stripe"
        error = Exception("Connection timeout")
        user_id = "test-user-123"
        fallback_data = {"cached_status": "pro"}
        
        result = await error_handler.handle_service_unavailability(
            service_name=service_name,
            error=error,
            user_id=user_id,
            fallback_data=fallback_data
        )
        
        assert result["service_available"] is False
        assert result["fallback_applied"] is True
        assert result["retry_after"] == 300
        assert "temporarily unavailable" in result["user_message"].lower()
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_success(self, error_handler):
        """Test retry mechanism with eventual success"""
        call_count = 0
        
        async def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"success": True}
        
        config = RetryConfig(max_attempts=3, base_delay=0.1)  # Fast retry for testing
        
        success, result, error = await error_handler.retry_with_backoff(
            failing_operation,
            "test_operation",
            config
        )
        
        assert success is True
        assert result == {"success": True}
        assert error is None
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_exhausted(self, error_handler):
        """Test retry mechanism with all attempts failing"""
        async def always_failing_operation():
            raise Exception("Persistent failure")
        
        config = RetryConfig(max_attempts=2, base_delay=0.1)
        
        success, result, error = await error_handler.retry_with_backoff(
            always_failing_operation,
            "test_operation",
            config
        )
        
        assert success is False
        assert result is None
        assert isinstance(error, SubscriptionError)
        assert "retry_exhausted" in error.code


class TestSubscriptionNotificationService:
    """Test subscription notification functionality"""
    
    @pytest.fixture
    def mock_db_session(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def notification_service(self, mock_db_session):
        with patch('services.subscription_notification_service.EmailService'):
            return SubscriptionNotificationService(mock_db_session)
    
    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = "test-user-123"
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.username = "testuser"
        return user
    
    @pytest.mark.asyncio
    async def test_notify_subscription_created(self, notification_service, mock_user):
        """Test subscription creation notification"""
        subscription_data = {
            "tier": "Pro",
            "amount": "$9.99",
            "cycle": "monthly",
            "next_billing_date": "2024-02-01"
        }
        
        # Mock email service
        notification_service.email_service.send_email = AsyncMock(return_value=True)
        
        result = await notification_service.notify_subscription_created(
            user=mock_user,
            subscription_data=subscription_data
        )
        
        assert result is True
        notification_service.email_service.send_email.assert_called_once()
        
        # Verify email content
        call_args = notification_service.email_service.send_email.call_args
        assert call_args[1]["to_email"] == mock_user.email
        assert "Welcome to Pro" in call_args[1]["subject"]
        assert call_args[1]["template_name"] == "subscription_welcome"
    
    @pytest.mark.asyncio
    async def test_notify_payment_failed(self, notification_service, mock_user):
        """Test payment failure notification"""
        payment_error = {
            "amount": "$9.99",
            "user_friendly_reason": "Your card was declined",
            "next_retry_date": "2024-01-15"
        }
        
        notification_service.email_service.send_email = AsyncMock(return_value=True)
        
        result = await notification_service.notify_payment_failed(
            user=mock_user,
            payment_error=payment_error,
            retry_count=1
        )
        
        assert result is True
        
        # Verify retry failure notification was sent
        call_args = notification_service.email_service.send_email.call_args
        assert "Action required" in call_args[1]["subject"]
        assert call_args[1]["template_name"] == "payment_retry_failed"
    
    @pytest.mark.asyncio
    async def test_notify_usage_limit_warning(self, notification_service, mock_user):
        """Test usage limit warning notification"""
        usage_data = {
            "current_usage": 4,
            "limit": 5,
            "reset_date": "2024-01-20"
        }
        
        notification_service.email_service.send_email = AsyncMock(return_value=True)
        
        result = await notification_service.notify_usage_limit_warning(
            user=mock_user,
            usage_data=usage_data
        )
        
        assert result is True
        
        call_args = notification_service.email_service.send_email.call_args
        assert "approaching your usage limit" in call_args[1]["subject"]
        assert call_args[1]["template_name"] == "usage_limit_warning"
    
    @pytest.mark.asyncio
    async def test_notify_usage_limit_exceeded(self, notification_service, mock_user):
        """Test usage limit exceeded notification"""
        usage_data = {
            "limit": 5,
            "reset_date": "2024-01-20"
        }
        
        notification_service.email_service.send_email = AsyncMock(return_value=True)
        
        result = await notification_service.notify_usage_limit_exceeded(
            user=mock_user,
            usage_data=usage_data
        )
        
        assert result is True
        
        call_args = notification_service.email_service.send_email.call_args
        assert "limit reached" in call_args[1]["subject"].lower()
        assert call_args[1]["template_name"] == "usage_limit_exceeded"


class TestServiceAvailabilityMonitor:
    """Test service availability monitoring"""
    
    @pytest.fixture
    def monitor(self):
        return ServiceAvailabilityMonitor()
    
    @pytest.mark.asyncio
    async def test_service_health_check_success(self, monitor):
        """Test successful service health check"""
        # Mock successful database check
        with patch('services.service_availability_monitor.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.execute.return_value.fetchone.return_value = (1,)
            mock_get_db.return_value = iter([mock_db])
            
            health = await monitor._check_service_health("database")
            
            assert health.status == ServiceStatus.HEALTHY
            assert health.error_count == 0
            assert health.last_error is None
    
    @pytest.mark.asyncio
    async def test_service_health_check_failure(self, monitor):
        """Test failed service health check"""
        # Mock database failure
        with patch('services.service_availability_monitor.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            health = await monitor._check_service_health("database")
            
            assert health.status == ServiceStatus.UNHEALTHY
            assert health.error_count > 0
            assert health.last_error is not None
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self, monitor):
        """Test circuit breaker opens after threshold failures"""
        service_name = "test_service"
        monitor.circuit_configs[service_name] = RetryConfig(failure_threshold=2)
        monitor._initialize_services()
        
        # Simulate failures
        await monitor._handle_service_failure(service_name, "Error 1")
        assert monitor.circuit_breakers[service_name]["state"] == CircuitState.CLOSED
        
        await monitor._handle_service_failure(service_name, "Error 2")
        assert monitor.circuit_breakers[service_name]["state"] == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self, monitor):
        """Test circuit breaker recovery after timeout"""
        service_name = "test_service"
        monitor.circuit_configs[service_name] = RetryConfig(
            failure_threshold=1,
            recovery_timeout=0.1,  # Short timeout for testing
            success_threshold=1
        )
        monitor._initialize_services()
        
        # Open circuit
        await monitor._handle_service_failure(service_name, "Error")
        assert monitor.circuit_breakers[service_name]["state"] == CircuitState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Check availability (should move to half-open)
        available = await monitor.is_service_available(service_name)
        assert available is True
        assert monitor.circuit_breakers[service_name]["state"] == CircuitState.HALF_OPEN
        
        # Successful call should close circuit
        await monitor._handle_service_success(service_name)
        assert monitor.circuit_breakers[service_name]["state"] == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback_success(self, monitor):
        """Test successful execution without fallback"""
        async def primary_func(value):
            return {"result": value * 2}
        
        result = await monitor.execute_with_fallback(
            "test_service",
            primary_func,
            None,
            5
        )
        
        assert result["success"] is True
        assert result["data"]["result"] == 10
        assert result["fallback_used"] is False
        assert result["service_available"] is True
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback_failure_with_fallback(self, monitor):
        """Test execution with fallback when primary fails"""
        async def primary_func(value):
            raise Exception("Primary function failed")
        
        async def fallback_func(value):
            return {"result": value, "fallback": True}
        
        result = await monitor.execute_with_fallback(
            "test_service",
            primary_func,
            fallback_func,
            5
        )
        
        assert result["success"] is True
        assert result["data"]["result"] == 5
        assert result["data"]["fallback"] is True
        assert result["fallback_used"] is True
        assert result["service_available"] is False


class TestSubscriptionResponseBuilder:
    """Test subscription response building"""
    
    def test_success_response(self):
        """Test success response creation"""
        data = {"subscription_id": "sub_123", "status": "active"}
        response = SubscriptionResponseBuilder.success(
            data=data,
            message="Subscription created successfully"
        )
        
        assert response["success"] is True
        assert response["code"] == "success"
        assert response["data"] == data
        assert "created successfully" in response["message"]
    
    def test_payment_required_response(self):
        """Test payment required response"""
        response = SubscriptionResponseBuilder.payment_required(
            message="Pro subscription required",
            current_tier="free",
            required_tier="pro"
        )
        
        assert response.status_code == 402
        content = response.body.decode()
        assert "subscription_required" in content
        assert "Pro subscription required" in content
    
    def test_usage_limit_exceeded_response(self):
        """Test usage limit exceeded response"""
        response = SubscriptionResponseBuilder.usage_limit_exceeded(
            limit=5,
            remaining=0,
            reset_time="2024-01-20T00:00:00Z"
        )
        
        assert response.status_code == 429
        content = response.body.decode()
        assert "usage_limit_exceeded" in content
        assert "weekly limit of 5" in content
    
    def test_service_unavailable_response(self):
        """Test service unavailable response"""
        response = SubscriptionResponseBuilder.service_unavailable(
            service_name="stripe",
            retry_after=300,
            fallback_available=True,
            fallback_message="Using cached data"
        )
        
        assert response.status_code == 503
        content = response.body.decode()
        assert "service_unavailable" in content
        assert "stripe service" in content
        assert "retry_after" in content


# Integration test
@pytest.mark.asyncio
async def test_end_to_end_error_handling():
    """Test end-to-end error handling flow"""
    # This test would simulate a complete error handling flow
    # from error occurrence to user notification
    
    # Mock database session
    mock_db = Mock(spec=Session)
    
    # Create error handler
    error_handler = SubscriptionErrorHandler(mock_db)
    
    # Simulate a payment error
    stripe_error = stripe.error.CardError(
        message="Your card was declined.",
        param="card",
        code="card_declined"
    )
    payment_error = PaymentError("Payment failed", stripe_error)
    
    # Handle the error
    result = await error_handler.handle_payment_error(
        error=payment_error,
        user_id="test-user-123",
        operation="create_subscription"
    )
    
    # Verify error was properly structured
    assert isinstance(result, SubscriptionError)
    assert result.code == "card_declined"
    assert result.user_message is not None
    assert result.suggested_action == "update_payment_method"
    
    # Create response from error
    response = SubscriptionResponseBuilder.error(result)
    
    # Verify response structure
    assert response.status_code == 402
    content = response.body.decode()
    assert "card_declined" in content
    assert "update_payment_method" in content


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])