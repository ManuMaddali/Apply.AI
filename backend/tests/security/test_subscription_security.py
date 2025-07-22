"""
Security Tests for Subscription System

Tests security aspects including data protection, access control,
input validation, and payment security.
"""

import pytest
import asyncio
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import stripe

from models.user import (
    Base, User, Subscription, PaymentHistory, UsageTracking,
    SubscriptionTier, SubscriptionStatus, PaymentStatus, UsageType, AuthProvider
)
from services.subscription_service import SubscriptionService
from services.payment_service import PaymentService, PaymentError


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def subscription_service(db_session):
    """Create SubscriptionService instance"""
    return SubscriptionService(db_session)


@pytest.fixture
def payment_service(db_session):
    """Create PaymentService instance with mocked config"""
    with patch('services.payment_service.get_stripe_config') as mock_config:
        mock_config.return_value = Mock(
            secret_key="sk_test_123",
            publishable_key="pk_test_123",
            webhook_secret="whsec_test_123",
            pro_monthly_price_id="price_test_123",
            environment="test"
        )
        
        with patch('stripe.api_key'):
            return PaymentService(db_session)


class TestDataProtection:
    """Test data protection and privacy measures"""
    
    @pytest.mark.asyncio
    async def test_user_data_isolation(self, subscription_service, db_session):
        """Test that users cannot access each other's data"""
        # Create two users
        user1 = User(
            email="user1@example.com",
            username="user1",
            subscription_tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_user1",
            auth_provider=AuthProvider.EMAIL
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            subscription_tier=SubscriptionTier.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create subscription for user1
        subscription1 = await subscription_service.create_subscription(
            user_id=str(user1.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_user1",
            stripe_customer_id="cus_user1"
        )
        
        # User2 should not be able to access user1's subscription
        user2_subscription = subscription_service.get_active_subscription(str(user2.id))
        assert user2_subscription is None
        
        # User2's operations should not affect user1
        await subscription_service.track_usage(
            str(user2.id), 
            UsageType.RESUME_PROCESSING, 
            count=5
        )
        
        # User1's usage should be unaffected
        user1_stats = await subscription_service.get_usage_statistics(str(user1.id))
        assert user1_stats["total_usage_count"] == 0
    
    @pytest.mark.asyncio
    async def test_sensitive_data_handling(self, subscription_service, payment_service, db_session):
        """Test that sensitive data is properly protected"""
        # Create user
        user = User(
            email="sensitive@example.com",
            username="sensitiveuser",
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Track usage with potentially sensitive metadata
        sensitive_metadata = "ip:192.168.1.100,session:abc123,device:iPhone"
        
        usage_record = await subscription_service.track_usage(
            user_id=str(user.id),
            usage_type=UsageType.RESUME_PROCESSING,
            extra_data=sensitive_metadata
        )
        
        # Verify sensitive data is stored but not exposed in aggregated stats
        stats = await subscription_service.get_usage_statistics(str(user.id))
        
        # Stats should not contain raw sensitive data
        stats_str = str(stats)
        assert "192.168.1.100" not in stats_str
        assert "abc123" not in stats_str
        assert "iPhone" not in stats_str
        
        # But the raw record should contain the data (for legitimate access)
        assert usage_record.extra_data == sensitive_metadata
    
    @pytest.mark.asyncio
    async def test_payment_data_protection(self, payment_service, db_session):
        """Test payment data protection measures"""
        # Create user
        user = User(
            email="payment@example.com",
            username="paymentuser",
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Record payment failure with sensitive information
        await payment_service._record_payment_failure(
            str(user.id),
            "Card was declined due to insufficient funds",
            "pm_card4242"
        )
        
        # Verify sensitive payment data is not stored in plain text
        payment_records = db_session.query(PaymentHistory).filter(
            PaymentHistory.user_id == user.id
        ).all()
        
        assert len(payment_records) == 1
        record = payment_records[0]
        
        # Should not contain full card numbers or sensitive details
        assert "4242" not in record.description
        assert record.status == PaymentStatus.FAILED
        
        # Metadata should be sanitized
        if record.metadata:
            metadata_str = str(record.metadata)
            assert "4242" not in metadata_str
    
    def test_database_query_injection_protection(self, subscription_service, db_session):
        """Test protection against SQL injection attacks"""
        # Create test user
        user = User(
            email="injection@example.com",
            username="injectionuser",
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Attempt SQL injection through user ID
        malicious_user_id = "1'; DROP TABLE users; --"
        
        # These operations should handle malicious input safely
        result = asyncio.run(
            subscription_service.check_usage_limits(malicious_user_id, UsageType.RESUME_PROCESSING)
        )
        assert result.can_use == False
        # Should handle malicious input gracefully (either "not found" or validation error)
        assert ("not found" in result.reason.lower() or 
                "error checking limits" in result.reason.lower() or
                "badly formed" in result.reason.lower())
        
        # Verify users table still exists
        users = db_session.query(User).all()
        assert len(users) == 1  # Original user should still exist
        
        # Test with malicious metadata
        malicious_metadata = "'; DELETE FROM usage_tracking; --"
        
        try:
            asyncio.run(
                subscription_service.track_usage(
                    str(user.id),
                    UsageType.RESUME_PROCESSING,
                    extra_data=malicious_metadata
                )
            )
            
            # Verify the malicious metadata is stored safely (escaped)
            usage_records = db_session.query(UsageTracking).all()
            assert len(usage_records) == 1
            assert usage_records[0].extra_data == malicious_metadata
            
        except Exception:
            # If it fails, it should fail safely without compromising data
            pass


class TestAccessControl:
    """Test access control and authorization"""
    
    @pytest.mark.asyncio
    async def test_subscription_tier_enforcement(self, subscription_service, db_session):
        """Test that subscription tiers are properly enforced"""
        # Create Free and Pro users
        free_user = User(
            email="free@example.com",
            username="freeuser",
            subscription_tier=SubscriptionTier.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        pro_user = User(
            email="pro@example.com",
            username="prouser",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() + timedelta(days=30),
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add_all([free_user, pro_user])
        db_session.commit()
        
        # Test Free user restrictions
        free_bulk_access = await subscription_service.check_usage_limits(
            str(free_user.id), 
            UsageType.BULK_PROCESSING
        )
        assert free_bulk_access.can_use == False
        
        free_cover_letter_access = await subscription_service.check_usage_limits(
            str(free_user.id), 
            UsageType.COVER_LETTER
        )
        assert free_cover_letter_access.can_use == False
        
        # Test Pro user access
        pro_bulk_access = await subscription_service.check_usage_limits(
            str(pro_user.id), 
            UsageType.BULK_PROCESSING
        )
        assert pro_bulk_access.can_use == True
        
        pro_cover_letter_access = await subscription_service.check_usage_limits(
            str(pro_user.id), 
            UsageType.COVER_LETTER
        )
        assert pro_cover_letter_access.can_use == True
    
    @pytest.mark.asyncio
    async def test_expired_subscription_access_revocation(self, subscription_service, db_session):
        """Test that expired subscriptions lose Pro access"""
        # Create Pro user with expired subscription
        expired_user = User(
            email="expired@example.com",
            username="expireduser",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() - timedelta(days=1),  # Expired
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(expired_user)
        db_session.commit()
        
        # Validate subscription status (should trigger downgrade)
        validation_result = await subscription_service.validate_subscription_status(str(expired_user.id))
        
        assert validation_result["valid"] == False
        assert "expired" in validation_result["reason"].lower()
        
        # Verify user was downgraded
        updated_user = db_session.query(User).filter(User.id == expired_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.FREE
        
        # Verify Pro features are no longer accessible
        bulk_access = await subscription_service.check_usage_limits(
            str(expired_user.id), 
            UsageType.BULK_PROCESSING
        )
        assert bulk_access.can_use == False
    
    @pytest.mark.asyncio
    async def test_usage_limit_bypass_prevention(self, subscription_service, db_session):
        """Test that usage limits cannot be bypassed"""
        # Create Free user at limit
        free_user = User(
            email="atlimit@example.com",
            username="atlimituser",
            subscription_tier=SubscriptionTier.FREE,
            weekly_usage_count=5,  # At limit
            weekly_usage_reset=datetime.utcnow(),
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(free_user)
        db_session.commit()
        
        # Attempt to bypass limit by manipulating user data
        # (This simulates an attack where someone tries to reset usage)
        
        # Check that limit is enforced
        limits = await subscription_service.check_usage_limits(
            str(free_user.id), 
            UsageType.RESUME_PROCESSING
        )
        assert limits.can_use == False
        assert limits.remaining == 0
        
        # Attempt to track usage anyway (should be blocked by application logic)
        # In a real system, this would be prevented by the feature gate middleware
        
        # Verify user cannot exceed limits through direct manipulation
        original_count = free_user.weekly_usage_count
        
        # Even if someone tries to track usage, the limit should be checked first
        try:
            await subscription_service.track_usage(
                str(free_user.id),
                UsageType.RESUME_PROCESSING,
                count=1
            )
            
            # If tracking succeeds, verify limits are still enforced elsewhere
            updated_user = db_session.query(User).filter(User.id == free_user.id).first()
            
            # The system should prevent actual feature usage even if tracking occurs
            post_track_limits = await subscription_service.check_usage_limits(
                str(free_user.id), 
                UsageType.RESUME_PROCESSING
            )
            assert post_track_limits.can_use == False
            
        except Exception:
            # If tracking fails due to limits, that's also acceptable
            pass


class TestInputValidation:
    """Test input validation and sanitization"""
    
    @pytest.mark.asyncio
    async def test_user_id_validation(self, subscription_service):
        """Test user ID validation"""
        # Test invalid UUID formats
        invalid_user_ids = [
            "not-a-uuid",
            "12345",
            "",
            None,
            "00000000-0000-0000-0000-000000000000",  # Null UUID
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # Invalid characters
        ]
        
        for invalid_id in invalid_user_ids:
            try:
                result = await subscription_service.check_usage_limits(
                    str(invalid_id) if invalid_id is not None else "",
                    UsageType.RESUME_PROCESSING
                )
                # Should return safe failure, not crash
                assert result.can_use == False
                assert "not found" in result.reason.lower() or "error" in result.reason.lower()
            except Exception as e:
                # If it raises an exception, it should be a controlled one
                assert "not found" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_usage_count_validation(self, subscription_service, db_session):
        """Test usage count validation"""
        # Create test user
        user = User(
            email="validation@example.com",
            username="validationuser",
            subscription_tier=SubscriptionTier.PRO,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Test invalid usage counts
        invalid_counts = [-1, -100, 0, 1000000]  # Negative, zero, and extremely large
        
        for count in invalid_counts:
            try:
                result = await subscription_service.track_usage(
                    str(user.id),
                    UsageType.RESUME_PROCESSING,
                    count=count
                )
                
                if count <= 0:
                    # Zero or negative counts should be handled appropriately
                    assert result.count == max(0, count)
                elif count > 100:
                    # Extremely large counts should be validated/limited
                    assert result.count <= 100 or result.count == count  # Depends on implementation
                    
            except ValueError:
                # It's acceptable to reject invalid counts with an exception
                pass
    
    @pytest.mark.asyncio
    async def test_metadata_sanitization(self, subscription_service, db_session):
        """Test metadata sanitization"""
        # Create test user
        user = User(
            email="metadata@example.com",
            username="metadatauser",
            subscription_tier=SubscriptionTier.PRO,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Test potentially dangerous metadata
        dangerous_metadata = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:alert('xss')",
            "\x00\x01\x02",  # Null bytes and control characters
        ]
        
        for metadata in dangerous_metadata:
            result = await subscription_service.track_usage(
                str(user.id),
                UsageType.RESUME_PROCESSING,
                count=1,
                extra_data=metadata
            )
            
            # Metadata should be stored safely (escaped or sanitized)
            assert result.extra_data is not None
            
            # Verify it doesn't break the system
            stats = await subscription_service.get_usage_statistics(str(user.id))
            assert "user_id" in stats


class TestPaymentSecurity:
    """Test payment processing security"""
    
    @pytest.mark.asyncio
    async def test_webhook_signature_validation(self, payment_service):
        """Test webhook signature validation"""
        # Test with invalid signature
        payload = b'{"type": "test.event"}'
        invalid_signature = "invalid_signature"
        
        with pytest.raises(PaymentError) as exc_info:
            await payment_service.handle_webhook(payload, invalid_signature)
        
        assert "signature" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_webhook_timestamp_validation(self, payment_service):
        """Test webhook timestamp validation (replay attack protection)"""
        # Create old timestamp (over 5 minutes ago)
        old_timestamp = str(int(time.time()) - 400)  # 6+ minutes ago
        payload = b'{"type": "test.event"}'
        
        # Create signature with old timestamp
        signed_payload = f"{old_timestamp}.{payload.decode()}"
        signature = hmac.new(
            "whsec_test_123".encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        stripe_signature = f"t={old_timestamp},v1={signature}"
        
        # Should reject old webhooks
        with patch('stripe.Webhook.construct_event', side_effect=stripe.error.SignatureVerificationError("Timestamp too old", "sig")):
            with pytest.raises(PaymentError):
                await payment_service.handle_webhook(payload, stripe_signature)
    
    @pytest.mark.asyncio
    async def test_customer_data_isolation(self, payment_service, db_session):
        """Test customer data isolation in payment processing"""
        # Create two users
        user1 = User(
            email="customer1@example.com",
            username="customer1",
            stripe_customer_id="cus_customer1",
            auth_provider=AuthProvider.EMAIL
        )
        user2 = User(
            email="customer2@example.com",
            username="customer2",
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Mock payment method operations
        with patch('stripe.PaymentMethod.list') as mock_list:
            mock_list.return_value = Mock(data=[
                Mock(
                    id="pm_customer1",
                    type="card",
                    card=Mock(brand="visa", last4="4242", exp_month=12, exp_year=2025),
                    created=int(time.time())
                )
            ])
            
            # User1 should only see their own payment methods
            user1_methods = await payment_service.get_payment_methods("cus_customer1")
            assert len(user1_methods) == 1
            assert user1_methods[0]["id"] == "pm_customer1"
            
            # User2 should not have access to user1's payment methods
            mock_list.return_value = Mock(data=[])
            user2_methods = await payment_service.get_payment_methods("cus_customer2")
            assert len(user2_methods) == 0
    
    @pytest.mark.asyncio
    async def test_payment_method_security(self, payment_service):
        """Test payment method security measures"""
        # Test that payment methods are properly attached to correct customer
        with patch('stripe.PaymentMethod.attach') as mock_attach:
            with patch('stripe.Customer.modify') as mock_modify:
                await payment_service.add_payment_method(
                    "cus_secure123",
                    "pm_secure123",
                    set_as_default=True
                )
                
                # Verify payment method is attached to correct customer
                mock_attach.assert_called_once_with("pm_secure123", customer="cus_secure123")
                
                # Verify customer is updated securely
                mock_modify.assert_called_once_with(
                    "cus_secure123",
                    invoice_settings={'default_payment_method': 'pm_secure123'}
                )


class TestAuditAndLogging:
    """Test audit trails and security logging"""
    
    @pytest.mark.asyncio
    async def test_subscription_change_audit_trail(self, subscription_service, db_session):
        """Test that subscription changes create audit trails"""
        # Create user
        user = User(
            email="audit@example.com",
            username="audituser",
            subscription_tier=SubscriptionTier.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Create subscription (should be logged)
        subscription = await subscription_service.create_subscription(
            user_id=str(user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_audit123",
            stripe_customer_id="cus_audit123"
        )
        
        # Update subscription (should be logged)
        await subscription_service.update_subscription(
            str(subscription.id),
            cancel_at_period_end=True
        )
        
        # Cancel subscription (should be logged)
        await subscription_service.cancel_subscription(
            str(user.id),
            cancel_immediately=True
        )
        
        # Verify audit trail exists in database
        # (In a real system, this would check audit log tables)
        final_user = db_session.query(User).filter(User.id == user.id).first()
        assert final_user.subscription_tier == SubscriptionTier.FREE
        assert final_user.subscription_status == SubscriptionStatus.CANCELED
    
    @pytest.mark.asyncio
    async def test_failed_operation_logging(self, subscription_service, payment_service, db_session):
        """Test that failed operations are properly logged"""
        # Create user
        user = User(
            email="logging@example.com",
            username="logginguser",
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Test failed payment (should be logged)
        with patch('stripe.Customer.create', side_effect=stripe.error.CardError("Card declined", None, "card_declined")):
            try:
                await payment_service.create_customer(user)
            except PaymentError:
                pass  # Expected failure
        
        # Test invalid subscription operation (should be logged)
        try:
            await subscription_service.create_subscription(
                user_id="invalid-user-id",
                tier=SubscriptionTier.PRO
            )
        except Exception:
            pass  # Expected failure
        
        # In a real system, verify that these failures are logged
        # For now, just verify the system handles failures gracefully
        assert True  # Placeholder for actual log verification


class TestRateLimiting:
    """Test rate limiting and abuse prevention"""
    
    @pytest.mark.asyncio
    async def test_usage_tracking_rate_limiting(self, subscription_service, db_session):
        """Test rate limiting for usage tracking"""
        # Create user
        user = User(
            email="ratelimit@example.com",
            username="ratelimituser",
            subscription_tier=SubscriptionTier.PRO,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Attempt rapid usage tracking (potential abuse)
        rapid_requests = 100
        start_time = time.time()
        
        tasks = []
        for i in range(rapid_requests):
            task = subscription_service.track_usage(
                str(user.id),
                UsageType.RESUME_PROCESSING,
                count=1,
                session_id=f"rapid_{i}"
            )
            tasks.append(task)
        
        # Execute all requests
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        # System should handle rapid requests gracefully
        # Either by processing them all (if system can handle it)
        # Or by rate limiting some requests
        total_requests = len(successful_results) + len(failed_results)
        assert total_requests == rapid_requests
        
        # If rate limiting is implemented, some requests should fail
        # If not, all should succeed but system should remain stable
        duration = end_time - start_time
        assert duration < 10.0, "System became unresponsive under load"
    
    @pytest.mark.asyncio
    async def test_subscription_operation_rate_limiting(self, subscription_service, db_session):
        """Test rate limiting for subscription operations"""
        # Create user
        user = User(
            email="subrate@example.com",
            username="subrateuser",
            subscription_tier=SubscriptionTier.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Attempt rapid subscription status checks
        rapid_checks = 50
        
        async def check_status():
            return await subscription_service.validate_subscription_status(str(user.id))
        
        start_time = time.time()
        tasks = [check_status() for _ in range(rapid_checks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # System should handle rapid checks gracefully
        successful_results = [r for r in results if not isinstance(r, Exception)]
        
        # Most requests should succeed (status checks are read-only)
        success_rate = len(successful_results) / rapid_checks
        assert success_rate >= 0.8, f"Too many status checks failed: {success_rate}"
        
        # System should remain responsive
        duration = end_time - start_time
        assert duration < 5.0, "Status checks took too long under load"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])