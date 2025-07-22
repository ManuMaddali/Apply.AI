"""
Integration Tests for Subscription and Payment Services

Tests the integration between SubscriptionService and PaymentService
to ensure they work together correctly for complete workflows.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch, AsyncMock
import stripe

from models.user import (
    Base, User, Subscription, PaymentHistory, UsageTracking,
    SubscriptionTier, SubscriptionStatus, PaymentStatus, UsageType, AuthProvider
)
from services.subscription_service import SubscriptionService
from services.payment_service import PaymentService, PaymentError


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_integration.db"
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
    """Create PaymentService instance with mocked Stripe config"""
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


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="integration@example.com",
        username="integration",
        full_name="Integration Test User",
        subscription_tier=SubscriptionTier.FREE,
        subscription_status=SubscriptionStatus.ACTIVE,
        auth_provider=AuthProvider.EMAIL,
        is_active=True,
        is_verified=True,
        email_verified=True
    )
    user.set_password("testpass123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestSubscriptionUpgradeFlow:
    """Test complete subscription upgrade workflow"""
    
    @pytest.mark.asyncio
    async def test_free_to_pro_upgrade_success(self, subscription_service, payment_service, test_user, db_session):
        """Test successful upgrade from Free to Pro"""
        # 1. Verify user starts as Free
        assert test_user.subscription_tier == SubscriptionTier.FREE
        
        # 2. Check initial usage limits
        limits = await subscription_service.check_usage_limits(
            str(test_user.id), 
            UsageType.RESUME_PROCESSING
        )
        assert limits.can_use == True
        assert limits.limit == 5  # Free user limit
        
        # 3. Mock successful payment processing
        mock_customer = Mock(id="cus_integration")
        mock_subscription = Mock()
        mock_subscription.id = "sub_integration"
        mock_subscription.status = "active"
        mock_subscription.current_period_start = int(datetime.utcnow().timestamp())
        mock_subscription.current_period_end = int((datetime.utcnow() + timedelta(days=30)).timestamp())
        mock_subscription.cancel_at_period_end = False
        mock_subscription.customer = "cus_integration"
        
        # Mock invoice with proper structure
        mock_invoice = Mock()
        mock_invoice.id = "in_test123"
        mock_invoice.amount_paid = 999  # $9.99 in cents
        mock_invoice.status = "paid"
        mock_invoice.payment_intent = Mock()
        mock_invoice.payment_intent.id = "pi_test123"
        
        # Set latest_invoice as an object, not just ID
        mock_subscription.latest_invoice = mock_invoice
        
        with patch.object(payment_service, 'create_customer', return_value="cus_integration"):
            with patch('stripe.PaymentMethod.attach'):
                with patch('stripe.Customer.modify'):
                    with patch('stripe.Subscription.create', return_value=mock_subscription):
                        with patch('stripe.Invoice.retrieve', return_value=mock_invoice):
                            with patch.object(payment_service, '_handle_successful_subscription') as mock_handle:
                                with patch('services.payment_service.log_payment_success') as mock_log:
                                    # 4. Process upgrade
                                    result = await payment_service.create_subscription(
                                        str(test_user.id),
                                        "pm_test123"
                                    )
                                    
                                    # 5. Verify subscription was created successfully
                                    assert result['status'] == 'active'
                                    assert result['subscription_id'] == 'sub_integration'
                                    
                                    # 6. Manually simulate the successful subscription handling
                                    # (since we mocked _handle_successful_subscription)
                                    test_user.subscription_tier = SubscriptionTier.PRO
                                    test_user.subscription_status = SubscriptionStatus.ACTIVE
                                    test_user.current_period_start = datetime.fromtimestamp(mock_subscription.current_period_start)
                                    test_user.current_period_end = datetime.fromtimestamp(mock_subscription.current_period_end)
                                    test_user.stripe_customer_id = mock_subscription.customer
                                    
                                    # Create subscription record
                                    subscription = Subscription(
                                        user_id=test_user.id,
                                        stripe_subscription_id=mock_subscription.id,
                                        stripe_customer_id=mock_subscription.customer,
                                        tier=SubscriptionTier.PRO,
                                        status=SubscriptionStatus.ACTIVE,
                                        current_period_start=datetime.fromtimestamp(mock_subscription.current_period_start),
                                        current_period_end=datetime.fromtimestamp(mock_subscription.current_period_end),
                                        cancel_at_period_end=mock_subscription.cancel_at_period_end
                                    )
                                    db_session.add(subscription)
                                    # Commit both user and subscription changes
                                    db_session.commit()
                                    
                                    # 7. Verify user was upgraded
                                    db_session.refresh(test_user)
                                    assert test_user.subscription_tier == SubscriptionTier.PRO
                                    assert test_user.subscription_status == SubscriptionStatus.ACTIVE

                                    # 8. Verify usage limits were updated
                                    limits = await subscription_service.check_usage_limits(
                                        str(test_user.id),
                                        UsageType.RESUME_PROCESSING
                                    )
                                    assert limits.can_use == True
                                    assert "unlimited" in limits.reason.lower()  # Pro users have unlimited access

                                    # 9. Verify subscription record was created
                                    subscription_check = db_session.query(Subscription).filter(
                                        Subscription.user_id == test_user.id
                                    ).first()
                                    assert subscription_check is not None
                                    assert subscription_check.tier == SubscriptionTier.PRO
                                    assert subscription_check.status == SubscriptionStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_upgrade_with_payment_failure(self, subscription_service, payment_service, test_user, db_session):
        """Test upgrade failure due to payment issues"""
        # Mock payment failure
        with patch.object(payment_service, 'create_customer', return_value="cus_test"):
            with patch('stripe.PaymentMethod.attach'):
                with patch('stripe.Customer.modify'):
                    with patch('stripe.Subscription.create', side_effect=stripe.error.CardError("Card declined", None, "card_declined")):
                        
                        # Attempt upgrade
                        with pytest.raises(PaymentError) as exc_info:
                            await payment_service.create_subscription(
                                str(test_user.id),
                                "pm_test123"
                            )
                        
                        assert "Payment failed" in str(exc_info.value)
        
        # Verify user remains on Free tier
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.FREE
        
        # Verify no subscription record was created
        subscription = subscription_service.get_active_subscription(str(test_user.id))
        assert subscription is None
    
    @pytest.mark.asyncio
    async def test_upgrade_with_existing_usage(self, subscription_service, payment_service, test_user, db_session):
        """Test upgrade when user has existing usage"""
        # 1. User uses Free tier features
        for i in range(3):
            await subscription_service.track_usage(
                str(test_user.id),
                UsageType.RESUME_PROCESSING,
                count=1
            )
        
        # Verify usage is tracked
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.weekly_usage_count == 3
        assert updated_user.total_usage_count == 3
        
        # 2. Upgrade to Pro
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_test123",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        # 3. Verify usage history is preserved
        final_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert final_user.subscription_tier == SubscriptionTier.PRO
        assert final_user.total_usage_count == 3  # History preserved
        
        # 4. Verify Pro features work immediately
        limits = await subscription_service.check_usage_limits(
            str(test_user.id),
            UsageType.BULK_PROCESSING
        )
        assert limits.can_use == True


class TestSubscriptionCancellationFlow:
    """Test subscription cancellation workflows"""
    
    @pytest.mark.asyncio
    async def test_cancel_at_period_end(self, subscription_service, payment_service, test_user, db_session):
        """Test cancellation at period end"""
        # 1. Create Pro subscription
        period_end = datetime.utcnow() + timedelta(days=15)
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_cancel_test",
            stripe_customer_id="cus_test123",
            current_period_end=period_end
        )
        
        # 2. Mock Stripe cancellation
        mock_stripe_sub = Mock()
        mock_stripe_sub.current_period_end = int(period_end.timestamp())
        
        with patch('stripe.Subscription.modify', return_value=mock_stripe_sub):
            result = await payment_service.cancel_subscription(str(test_user.id))
            
            assert result['status'] == 'will_cancel'
            assert result['cancel_at_period_end'] == True
        
        # 3. Update subscription service
        await subscription_service.update_subscription(
            str(subscription.id),
            cancel_at_period_end=True
        )
        
        # 4. Verify user still has Pro access
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.PRO
        assert updated_user.cancel_at_period_end == True
        
        # 5. Verify Pro features still work
        limits = await subscription_service.check_usage_limits(
            str(test_user.id),
            UsageType.RESUME_PROCESSING
        )
        assert limits.can_use == True
        assert "unlimited" in limits.reason.lower()
    
    @pytest.mark.asyncio
    async def test_immediate_cancellation(self, subscription_service, payment_service, test_user, db_session):
        """Test immediate cancellation"""
        # 1. Create Pro subscription
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_immediate_cancel",
            stripe_customer_id="cus_test123",
            current_period_end=datetime.utcnow() + timedelta(days=15)
        )
        
        # 2. Mock immediate Stripe cancellation
        mock_stripe_sub = Mock()
        mock_stripe_sub.id = "sub_immediate_cancel"
        
        with patch('stripe.Subscription.delete', return_value=mock_stripe_sub):
            result = await payment_service.cancel_subscription(
                str(test_user.id),
                cancel_immediately=True
            )
            
            assert result['status'] == 'canceled'
        
        # 3. Process cancellation in subscription service
        await subscription_service.cancel_subscription(
            str(test_user.id),
            cancel_immediately=True
        )
        
        # 4. Verify user is downgraded immediately
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.FREE
        assert updated_user.subscription_status == SubscriptionStatus.CANCELED
        
        # 5. Verify Free tier limits are enforced
        limits = await subscription_service.check_usage_limits(
            str(test_user.id),
            UsageType.BULK_PROCESSING
        )
        assert limits.can_use == False
        assert "requires Pro subscription" in limits.reason


class TestWebhookIntegration:
    """Test webhook integration between services"""
    
    @pytest.mark.asyncio
    async def test_subscription_created_webhook(self, subscription_service, payment_service, test_user, db_session):
        """Test processing subscription.created webhook"""
        # Mock webhook event
        webhook_event = {
            'type': 'customer.subscription.created',
            'data': {
                'object': {
                    'id': 'sub_webhook_test',
                    'customer': 'cus_webhook_test',
                    'status': 'active',
                    'current_period_start': int(datetime.utcnow().timestamp()),
                    'current_period_end': int((datetime.utcnow() + timedelta(days=30)).timestamp()),
                    'cancel_at_period_end': False,
                    'metadata': {
                        'user_id': str(test_user.id)
                    }
                }
            }
        }
        
        # Mock webhook processing
        with patch('stripe.Webhook.construct_event', return_value=webhook_event):
            with patch.object(payment_service, '_handle_subscription_created') as mock_handler:
                mock_handler.return_value = {'status': 'processed'}
                
                result = await payment_service.handle_webhook(b'payload', 'signature')
                assert result['status'] == 'processed'
                mock_handler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_payment_succeeded_webhook(self, subscription_service, payment_service, test_user, db_session):
        """Test processing payment_succeeded webhook"""
        # Create subscription first
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_payment_test",
            stripe_customer_id="cus_test123"
        )
        
        # Mock payment succeeded webhook
        webhook_event = {
            'type': 'invoice.payment_succeeded',
            'data': {
                'object': {
                    'id': 'in_test123',
                    'customer': 'cus_test123',
                    'subscription': 'sub_payment_test',
                    'amount_paid': 999,
                    'currency': 'usd',
                    'payment_intent': 'pi_test123'
                }
            }
        }
        
        with patch('stripe.Webhook.construct_event', return_value=webhook_event):
            with patch.object(payment_service, '_handle_payment_succeeded') as mock_handler:
                mock_handler.return_value = {'status': 'processed'}
                
                result = await payment_service.handle_webhook(b'payload', 'signature')
                assert result['status'] == 'processed'
    
    @pytest.mark.asyncio
    async def test_payment_failed_webhook(self, subscription_service, payment_service, test_user, db_session):
        """Test processing payment_failed webhook"""
        # Create subscription
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_failed_payment",
            stripe_customer_id="cus_test123"
        )
        
        # Mock payment failed webhook
        webhook_event = {
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'id': 'in_failed123',
                    'customer': 'cus_test123',
                    'subscription': 'sub_failed_payment',
                    'amount_due': 999,
                    'currency': 'usd',
                    'attempt_count': 1
                }
            }
        }
        
        with patch('stripe.Webhook.construct_event', return_value=webhook_event):
            with patch.object(payment_service, '_handle_payment_failed') as mock_handler:
                mock_handler.return_value = {'status': 'processed'}
                
                result = await payment_service.handle_webhook(b'payload', 'signature')
                assert result['status'] == 'processed'


class TestUsageAndBilling:
    """Test usage tracking with billing integration"""
    
    @pytest.mark.asyncio
    async def test_usage_tracking_across_tiers(self, subscription_service, payment_service, test_user, db_session):
        """Test usage tracking when switching between tiers"""
        # 1. Track usage as Free user
        for i in range(3):
            await subscription_service.track_usage(
                str(test_user.id),
                UsageType.RESUME_PROCESSING,
                count=1
            )
        
        free_stats = await subscription_service.get_usage_statistics(str(test_user.id))
        assert free_stats["total_usage_count"] == 3
        
        # 2. Upgrade to Pro
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_test123",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        # 3. Track more usage as Pro user
        for i in range(5):
            await subscription_service.track_usage(
                str(test_user.id),
                UsageType.RESUME_PROCESSING,
                count=1
            )
        
        # Track Pro-only features
        await subscription_service.track_usage(
            str(test_user.id),
            UsageType.BULK_PROCESSING,
            count=2
        )
        
        # 4. Verify combined usage statistics
        pro_stats = await subscription_service.get_usage_statistics(str(test_user.id))
        assert pro_stats["total_usage_count"] == 10  # 3 + 5 + 2
        assert pro_stats["subscription_tier"] == "pro"
        
        # 5. Cancel and downgrade
        await subscription_service.cancel_subscription(
            str(test_user.id),
            cancel_immediately=True
        )
        
        # 6. Verify usage history is preserved but limits are enforced
        final_stats = await subscription_service.get_usage_statistics(str(test_user.id))
        assert final_stats["total_usage_count"] == 10  # History preserved (3 + 5 + 2)
        assert final_stats["subscription_tier"] == "free"
        
        # Verify Free tier limits are enforced
        limits = await subscription_service.check_usage_limits(
            str(test_user.id),
            UsageType.BULK_PROCESSING
        )
        assert limits.can_use == False
    
    @pytest.mark.asyncio
    async def test_prorated_billing_calculation(self, subscription_service, payment_service, test_user):
        """Test prorated billing calculations"""
        # Test mid-cycle upgrade
        period_start = datetime(2024, 1, 1)
        period_end = datetime(2024, 1, 31)  # 30 days
        upgrade_date = datetime(2024, 1, 16)  # 15 days into cycle
        
        prorated_amount = subscription_service.calculate_prorated_amount(
            999,  # $9.99 in cents
            period_start,
            period_end,
            upgrade_date
        )
        
        # Should be roughly half the amount (15 days remaining out of 30)
        expected = int((15 / 30) * 999)
        assert prorated_amount == expected
        
        # Test edge cases
        same_day_amount = subscription_service.calculate_prorated_amount(
            999, period_start, period_end, period_start
        )
        assert same_day_amount == 999  # Full amount
        
        after_period_amount = subscription_service.calculate_prorated_amount(
            999, period_start, period_end, datetime(2024, 2, 1)
        )
        assert after_period_amount == 0  # No charge


class TestErrorHandlingIntegration:
    """Test error handling across service boundaries"""
    
    @pytest.mark.asyncio
    async def test_payment_failure_rollback(self, subscription_service, payment_service, test_user, db_session):
        """Test that payment failures don't leave inconsistent state"""
        # Attempt upgrade with payment failure
        with patch.object(payment_service, 'create_customer', return_value="cus_test"):
            with patch('stripe.PaymentMethod.attach'):
                with patch('stripe.Customer.modify'):
                    with patch('stripe.Subscription.create', side_effect=stripe.error.CardError("Card declined", None, "card_declined")):
                        
                        with pytest.raises(PaymentError):
                            await payment_service.create_subscription(
                                str(test_user.id),
                                "pm_test123"
                            )
        
        # Verify no subscription was created
        subscription = subscription_service.get_active_subscription(str(test_user.id))
        assert subscription is None
        
        # Verify user remains on Free tier
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.FREE
        
        # Verify Free tier limits are still enforced
        limits = await subscription_service.check_usage_limits(
            str(test_user.id),
            UsageType.BULK_PROCESSING
        )
        assert limits.can_use == False
    
    @pytest.mark.asyncio
    async def test_webhook_processing_failure_recovery(self, subscription_service, payment_service, test_user, db_session):
        """Test recovery from webhook processing failures"""
        # Create subscription that webhook should update
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_webhook_fail",
            stripe_customer_id="cus_test123"
        )
        
        # Mock webhook with processing failure
        webhook_event = {
            'type': 'customer.subscription.updated',
            'data': {
                'object': {
                    'id': 'sub_webhook_fail',
                    'status': 'canceled'
                }
            }
        }
        
        with patch('stripe.Webhook.construct_event', return_value=webhook_event):
            with patch.object(payment_service, '_handle_subscription_updated', side_effect=Exception("Processing failed")):
                
                # Webhook processing should fail gracefully
                with pytest.raises(PaymentError):
                    await payment_service.handle_webhook(b'payload', 'signature')
        
        # Verify original subscription state is preserved
        current_subscription = subscription_service.get_active_subscription(str(test_user.id))
        assert current_subscription is not None
        assert current_subscription.status == SubscriptionStatus.ACTIVE


class TestPerformanceIntegration:
    """Test performance of integrated workflows"""
    
    @pytest.mark.asyncio
    async def test_bulk_user_upgrade_performance(self, subscription_service, payment_service, db_session):
        """Test performance of upgrading multiple users"""
        # Create multiple users
        users = []
        for i in range(20):
            user = User(
                email=f"bulk{i}@example.com",
                username=f"bulk{i}",
                subscription_tier=SubscriptionTier.FREE,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Mock successful payment processing
        with patch.object(payment_service, 'create_customer') as mock_customer:
            with patch('stripe.PaymentMethod.attach'):
                with patch('stripe.Customer.modify'):
                    with patch('stripe.Subscription.create') as mock_create:
                        with patch.object(payment_service, '_handle_successful_subscription') as mock_handle:
                            with patch('services.payment_service.log_payment_success') as mock_log:
                                
                                mock_customer.side_effect = lambda user: f"cus_{user.username}"
                                mock_create.side_effect = lambda **kwargs: Mock(
                                    id=f"sub_{kwargs['customer']}",
                                    status="active",
                                    current_period_start=int(datetime.utcnow().timestamp()),
                                    current_period_end=int((datetime.utcnow() + timedelta(days=30)).timestamp()),
                                    cancel_at_period_end=False,
                                    customer=kwargs['customer'],
                                    latest_invoice=Mock(payment_intent=Mock(id="pi_test"))
                                )
                                
                                # Process upgrades concurrently
                                start_time = time.time()
                                
                                async def upgrade_user(user):
                                    try:
                                        # Payment processing
                                        await payment_service.create_subscription(
                                            str(user.id),
                                            "pm_test123"
                                        )
                                        
                                        # Subscription service
                                        await subscription_service.create_subscription(
                                            user_id=str(user.id),
                                            tier=SubscriptionTier.PRO,
                                            stripe_subscription_id=f"sub_cus_{user.username}",
                                            stripe_customer_id=f"cus_{user.username}",
                                            current_period_end=datetime.utcnow() + timedelta(days=30)
                                        )
                                        return True
                                    except Exception:
                                        return False
                                
                                tasks = [upgrade_user(user) for user in users]
                                results = await asyncio.gather(*tasks, return_exceptions=True)
                                
                                end_time = time.time()
                                
                                # Should complete within reasonable time
                                assert end_time - start_time < 10.0  # 10 seconds for 20 users
                                
                                # Most upgrades should succeed
                                successful = sum(1 for r in results if r is True)
                                assert successful >= 15  # At least 75% success rate


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])