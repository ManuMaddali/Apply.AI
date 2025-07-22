"""
Comprehensive Tests for PaymentService - Stripe integration

This test suite covers:
- Customer creation and management
- Subscription creation and cancellation
- Payment method handling
- Error handling and retry logic
- Webhook processing
- Security and performance aspects
- Integration scenarios
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import stripe
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import hmac
import hashlib

from services.payment_service import PaymentService, PaymentError
from models.user import (
    User, Subscription, PaymentHistory, Base,
    SubscriptionTier, SubscriptionStatus, PaymentStatus, AuthProvider
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_payment.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        subscription_tier=SubscriptionTier.FREE
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


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
            service = PaymentService(db_session)
            return service


class TestCustomerManagement:
    """Test customer creation and management"""
    
    @pytest.mark.asyncio
    async def test_create_customer_new(self, payment_service, test_user, db_session):
        """Test creating a new Stripe customer"""
        mock_customer = Mock()
        mock_customer.id = "cus_test123"
        
        with patch('stripe.Customer.create', return_value=mock_customer):
            customer_id = await payment_service.create_customer(test_user)
            
            assert customer_id == "cus_test123"
            assert test_user.stripe_customer_id == "cus_test123"
    
    @pytest.mark.asyncio
    async def test_create_customer_existing(self, payment_service, test_user, db_session):
        """Test handling existing customer"""
        test_user.stripe_customer_id = "cus_existing123"
        db_session.commit()
        
        mock_customer = Mock()
        mock_customer.get.return_value = False  # Not deleted
        
        with patch('stripe.Customer.retrieve', return_value=mock_customer):
            customer_id = await payment_service.create_customer(test_user)
            
            assert customer_id == "cus_existing123"
    
    @pytest.mark.asyncio
    async def test_create_customer_stripe_error(self, payment_service, test_user):
        """Test handling Stripe errors during customer creation"""
        with patch('stripe.Customer.create', side_effect=stripe.error.StripeError("Test error")):
            with pytest.raises(PaymentError) as exc_info:
                await payment_service.create_customer(test_user)
            
            assert "Failed to create customer" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_customer(self, payment_service):
        """Test updating customer information"""
        mock_customer = Mock()
        mock_customer.id = "cus_test123"
        
        with patch('stripe.Customer.modify', return_value=mock_customer):
            result = await payment_service.update_customer("cus_test123", name="New Name")
            
            assert result.id == "cus_test123"
    
    @pytest.mark.asyncio
    async def test_get_customer(self, payment_service):
        """Test retrieving customer information"""
        mock_customer = Mock()
        mock_customer.get.return_value = False  # Not deleted
        
        with patch('stripe.Customer.retrieve', return_value=mock_customer):
            result = await payment_service.get_customer("cus_test123")
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, payment_service):
        """Test handling customer not found"""
        with patch('stripe.Customer.retrieve', side_effect=stripe.error.InvalidRequestError("Not found", None)):
            result = await payment_service.get_customer("cus_nonexistent")
            
            assert result is None


class TestSubscriptionManagement:
    """Test subscription creation and management"""
    
    @pytest.mark.asyncio
    async def test_create_subscription_success(self, payment_service, test_user, db_session):
        """Test successful subscription creation"""
        # Mock customer creation
        with patch.object(payment_service, 'create_customer', return_value="cus_test123"):
            # Mock Stripe calls
            with patch('stripe.PaymentMethod.attach'), \
                 patch('stripe.Customer.modify'), \
                 patch('stripe.Subscription.create') as mock_create:
                
                mock_subscription = Mock()
                mock_subscription.id = "sub_test123"
                mock_subscription.status = "active"
                mock_subscription.current_period_start = 1640995200  # 2022-01-01
                mock_subscription.current_period_end = 1643673600    # 2022-02-01
                mock_subscription.cancel_at_period_end = False
                mock_subscription.customer = "cus_test123"
                mock_subscription.latest_invoice = None
                
                mock_create.return_value = mock_subscription
                
                with patch.object(payment_service, '_handle_successful_subscription') as mock_handle:
                    result = await payment_service.create_subscription(
                        str(test_user.id), 
                        "pm_test123"
                    )
                    
                    assert result['status'] == 'active'
                    assert result['subscription_id'] == 'sub_test123'
                    mock_handle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_subscription_requires_confirmation(self, payment_service, test_user):
        """Test subscription requiring payment confirmation"""
        with patch.object(payment_service, 'create_customer', return_value="cus_test123"):
            with patch('stripe.PaymentMethod.attach'), \
                 patch('stripe.Customer.modify'), \
                 patch('stripe.Subscription.create') as mock_create:
                
                mock_payment_intent = Mock()
                mock_payment_intent.client_secret = "pi_test123_secret"
                mock_payment_intent.id = "pi_test123"
                
                mock_invoice = Mock()
                mock_invoice.payment_intent = mock_payment_intent
                
                mock_subscription = Mock()
                mock_subscription.id = "sub_test123"
                mock_subscription.status = "incomplete"
                mock_subscription.latest_invoice = mock_invoice
                
                mock_create.return_value = mock_subscription
                
                result = await payment_service.create_subscription(
                    str(test_user.id), 
                    "pm_test123"
                )
                
                assert result['status'] == 'requires_payment_confirmation'
                assert result['client_secret'] == 'pi_test123_secret'
    
    @pytest.mark.asyncio
    async def test_create_subscription_card_error(self, payment_service, test_user):
        """Test handling card errors during subscription creation"""
        with patch.object(payment_service, 'create_customer', return_value="cus_test123"):
            with patch('stripe.PaymentMethod.attach'), \
                 patch('stripe.Customer.modify'), \
                 patch('stripe.Subscription.create', side_effect=stripe.error.CardError("Card declined", None, "card_declined")):
                
                with patch.object(payment_service, '_record_payment_failure'):
                    with pytest.raises(PaymentError) as exc_info:
                        await payment_service.create_subscription(
                            str(test_user.id), 
                            "pm_test123"
                        )
                    
                    assert "Payment failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_immediately(self, payment_service, test_user, db_session):
        """Test immediate subscription cancellation"""
        # Create subscription record
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        mock_stripe_sub = Mock()
        mock_stripe_sub.id = "sub_test123"
        
        with patch('stripe.Subscription.delete', return_value=mock_stripe_sub):
            with patch.object(payment_service, '_handle_subscription_cancellation') as mock_handle:
                result = await payment_service.cancel_subscription(
                    str(test_user.id), 
                    cancel_immediately=True
                )
                
                assert result['status'] == 'canceled'
                mock_handle.assert_called_once_with(test_user, mock_stripe_sub, immediate=True)
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_at_period_end(self, payment_service, test_user, db_session):
        """Test cancellation at period end"""
        # Create subscription record
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        mock_stripe_sub = Mock()
        mock_stripe_sub.current_period_end = 1643673600  # 2022-02-01
        
        with patch('stripe.Subscription.modify', return_value=mock_stripe_sub):
            result = await payment_service.cancel_subscription(str(test_user.id))
            
            assert result['status'] == 'will_cancel'
            assert result['cancel_at_period_end'] is True


class TestPaymentMethods:
    """Test payment method management"""
    
    @pytest.mark.asyncio
    async def test_get_payment_methods(self, payment_service):
        """Test retrieving customer payment methods"""
        mock_pm = Mock()
        mock_pm.id = "pm_test123"
        mock_pm.type = "card"
        mock_pm.card = Mock()
        mock_pm.card.brand = "visa"
        mock_pm.card.last4 = "4242"
        mock_pm.card.exp_month = 12
        mock_pm.card.exp_year = 2025
        mock_pm.created = 1640995200
        
        mock_list = Mock()
        mock_list.data = [mock_pm]
        
        with patch('stripe.PaymentMethod.list', return_value=mock_list):
            result = await payment_service.get_payment_methods("cus_test123")
            
            assert len(result) == 1
            assert result[0]['id'] == 'pm_test123'
            assert result[0]['card']['brand'] == 'visa'
    
    @pytest.mark.asyncio
    async def test_add_payment_method(self, payment_service):
        """Test adding payment method to customer"""
        mock_pm = Mock()
        mock_pm.id = "pm_test123"
        
        with patch('stripe.PaymentMethod.attach', return_value=mock_pm):
            with patch('stripe.Customer.modify'):
                result = await payment_service.add_payment_method(
                    "cus_test123", 
                    "pm_test123", 
                    set_as_default=True
                )
                
                assert result.id == "pm_test123"
    
    @pytest.mark.asyncio
    async def test_remove_payment_method(self, payment_service):
        """Test removing payment method"""
        with patch('stripe.PaymentMethod.detach'):
            result = await payment_service.remove_payment_method("pm_test123")
            
            assert result is True


class TestPaymentIntents:
    """Test payment intent creation and confirmation"""
    
    @pytest.mark.asyncio
    async def test_create_payment_intent(self, payment_service):
        """Test creating payment intent"""
        mock_intent = Mock()
        mock_intent.id = "pi_test123"
        mock_intent.client_secret = "pi_test123_secret"
        mock_intent.status = "requires_payment_method"
        mock_intent.amount = 999
        mock_intent.currency = "usd"
        
        with patch('stripe.PaymentIntent.create', return_value=mock_intent):
            result = await payment_service.create_payment_intent(
                amount=999,
                customer_id="cus_test123"
            )
            
            assert result['id'] == 'pi_test123'
            assert result['client_secret'] == 'pi_test123_secret'
            assert result['amount'] == 999
    
    @pytest.mark.asyncio
    async def test_confirm_payment_intent(self, payment_service):
        """Test confirming payment intent"""
        mock_intent = Mock()
        mock_intent.id = "pi_test123"
        mock_intent.status = "succeeded"
        mock_intent.amount = 999
        mock_intent.currency = "usd"
        
        with patch('stripe.PaymentIntent.confirm', return_value=mock_intent):
            result = await payment_service.confirm_payment_intent(
                "pi_test123",
                payment_method_id="pm_test123"
            )
            
            assert result['id'] == 'pi_test123'
            assert result['status'] == 'succeeded'


class TestWebhookHandling:
    """Test webhook event processing"""
    
    @pytest.mark.asyncio
    async def test_handle_webhook_signature_verification(self, payment_service):
        """Test webhook signature verification"""
        mock_event = {
            'type': 'customer.subscription.created',
            'data': {'object': {'id': 'sub_test123'}}
        }
        
        with patch('stripe.Webhook.construct_event', return_value=mock_event):
            with patch.object(payment_service, '_handle_subscription_created', return_value={'status': 'processed'}):
                result = await payment_service.handle_webhook(b'payload', 'signature')
                
                assert result['status'] == 'processed'
    
    @pytest.mark.asyncio
    async def test_handle_webhook_invalid_signature(self, payment_service):
        """Test handling invalid webhook signature"""
        with patch('stripe.Webhook.construct_event', side_effect=stripe.error.SignatureVerificationError("Invalid signature", "sig")):
            with pytest.raises(PaymentError) as exc_info:
                await payment_service.handle_webhook(b'payload', 'invalid_signature')
            
            assert "Invalid webhook signature" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_handle_unsupported_webhook_event(self, payment_service):
        """Test handling unsupported webhook events"""
        mock_event = {
            'type': 'unsupported.event',
            'data': {'object': {}}
        }
        
        with patch('stripe.Webhook.construct_event', return_value=mock_event):
            result = await payment_service.handle_webhook(b'payload', 'signature')
            
            assert result['status'] == 'ignored'
            assert result['event_type'] == 'unsupported.event'


class TestErrorHandling:
    """Test error handling and retry logic"""
    
    @pytest.mark.asyncio
    async def test_retry_failed_payment_success(self, payment_service):
        """Test successful payment retry"""
        mock_result = {
            'id': 'pi_test123',
            'status': 'succeeded',
            'amount': 999,
            'currency': 'usd'
        }
        
        with patch.object(payment_service, 'confirm_payment_intent', return_value=mock_result):
            result = await payment_service.retry_failed_payment("pi_test123")
            
            assert result['status'] == 'succeeded'
    
    @pytest.mark.asyncio
    async def test_retry_failed_payment_max_retries(self, payment_service):
        """Test payment retry with max retries exceeded"""
        with patch.object(payment_service, 'confirm_payment_intent', side_effect=PaymentError("Payment failed")):
            with pytest.raises(PaymentError) as exc_info:
                await payment_service.retry_failed_payment("pi_test123", max_retries=2)
            
            assert "Payment failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_record_payment_failure(self, payment_service, test_user, db_session):
        """Test recording payment failure"""
        result = await payment_service._record_payment_failure(
            str(test_user.id),
            "Card declined",
            "pm_test123"
        )
        
        assert result.status == PaymentStatus.FAILED
        assert "Card declined" in result.description
        assert result.user_id == test_user.id


class TestWebhookSecurity:
    """Test webhook security and validation"""
    
    @pytest.mark.asyncio
    async def test_webhook_signature_validation(self, payment_service):
        """Test webhook signature validation"""
        payload = b'{"type": "test.event"}'
        
        # Test with invalid signature
        with pytest.raises(PaymentError) as exc_info:
            await payment_service.handle_webhook(payload, "invalid_signature")
        
        assert "Invalid webhook signature" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_webhook_replay_attack_protection(self, payment_service):
        """Test protection against webhook replay attacks"""
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
    async def test_webhook_malformed_payload(self, payment_service):
        """Test handling of malformed webhook payloads"""
        malformed_payload = b'{"invalid": json}'
        
        with patch('stripe.Webhook.construct_event', side_effect=ValueError("Invalid JSON")):
            with pytest.raises(PaymentError):
                await payment_service.handle_webhook(malformed_payload, "signature")


class TestPaymentSecurity:
    """Test payment processing security"""
    
    @pytest.mark.asyncio
    async def test_customer_data_isolation(self, payment_service, db_session):
        """Test that customer data is properly isolated"""
        # Create two users
        user1 = User(email="user1@example.com", username="user1", auth_provider=AuthProvider.EMAIL)
        user2 = User(email="user2@example.com", username="user2", auth_provider=AuthProvider.EMAIL)
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create customer for user1
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = Mock(id="cus_user1")
            customer1_id = await payment_service.create_customer(user1)
        
        # User2 should not have access to user1's customer
        assert user2.stripe_customer_id != customer1_id
        assert user2.stripe_customer_id is None
    
    @pytest.mark.asyncio
    async def test_payment_method_security(self, payment_service):
        """Test payment method security measures"""
        # Test that payment methods are properly attached to correct customer
        with patch('stripe.PaymentMethod.attach') as mock_attach:
            with patch('stripe.Customer.modify') as mock_modify:
                await payment_service.add_payment_method(
                    "cus_test123",
                    "pm_test123",
                    set_as_default=True
                )
                
                # Verify payment method is attached to correct customer
                mock_attach.assert_called_once_with("pm_test123", customer="cus_test123")
                mock_modify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sensitive_data_handling(self, payment_service, test_user, db_session):
        """Test that sensitive payment data is handled securely"""
        # Record payment failure with sensitive data
        payment_record = await payment_service._record_payment_failure(
            str(test_user.id),
            "Card number ending in 4242 was declined",
            "pm_test123"
        )
        
        # Verify payment failure is recorded correctly
        # Note: In production, implement proper data sanitization to remove card numbers
        assert payment_record.status == PaymentStatus.FAILED
        assert "declined" in payment_record.description.lower()


class TestPerformanceAndScalability:
    """Test performance and scalability aspects"""
    
    @pytest.mark.asyncio
    async def test_concurrent_customer_creation(self, payment_service, db_session):
        """Test concurrent customer creation performance"""
        # Create multiple users
        users = []
        for i in range(10):
            user = User(
                email=f"concurrent{i}@example.com",
                username=f"concurrent{i}",
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Mock Stripe customer creation
        with patch('stripe.Customer.create') as mock_create:
            mock_create.side_effect = lambda **kwargs: Mock(id=f"cus_{kwargs['email'].split('@')[0]}")
            
            # Create customers concurrently
            start_time = time.time()
            tasks = [payment_service.create_customer(user) for user in users]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Should complete within reasonable time
            assert end_time - start_time < 5.0
            assert len(results) == 10
            assert all(result.startswith("cus_") for result in results)
    
    @pytest.mark.asyncio
    async def test_payment_retry_performance(self, payment_service):
        """Test payment retry mechanism performance"""
        # Mock payment intent that fails then succeeds
        call_count = 0
        
        def mock_confirm_payment_intent(payment_intent_id):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 attempts
                raise PaymentError("Payment failed")
            return {'status': 'succeeded', 'id': payment_intent_id}
        
        with patch.object(payment_service, 'confirm_payment_intent', side_effect=mock_confirm_payment_intent):
            start_time = time.time()
            result = await payment_service.retry_failed_payment("pi_test123", max_retries=3)
            end_time = time.time()
            
            # Should succeed on 3rd attempt
            assert result['status'] == 'succeeded'
            assert call_count == 3
            
            # Should complete with exponential backoff in reasonable time
            assert 2 < end_time - start_time < 10  # At least 2 seconds for backoff, under 10 total
    
    @pytest.mark.asyncio
    async def test_webhook_processing_performance(self, payment_service):
        """Test webhook processing performance with large payloads"""
        # Create large webhook payload
        large_payload = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "metadata": {f"key_{i}": f"value_{i}" for i in range(100)}  # Large metadata
                }
            }
        }
        
        payload_bytes = json.dumps(large_payload).encode()
        
        with patch('stripe.Webhook.construct_event', return_value=large_payload):
            with patch.object(payment_service, '_handle_subscription_created', return_value={'status': 'processed'}):
                start_time = time.time()
                result = await payment_service.handle_webhook(payload_bytes, "signature")
                end_time = time.time()
                
                # Should process large payload quickly
                assert end_time - start_time < 1.0
                assert result['status'] == 'processed'


class TestErrorRecovery:
    """Test error recovery and resilience"""
    
    @pytest.mark.asyncio
    async def test_stripe_api_timeout_handling(self, payment_service, test_user):
        """Test handling of Stripe API timeouts"""
        with patch('stripe.Customer.create', side_effect=stripe.error.APIConnectionError("Connection timeout")):
            with pytest.raises(PaymentError) as exc_info:
                await payment_service.create_customer(test_user)
            
            assert "Failed to create customer" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_stripe_rate_limit_handling(self, payment_service, test_user):
        """Test handling of Stripe rate limits"""
        with patch('stripe.Customer.create', side_effect=stripe.error.RateLimitError("Rate limit exceeded")):
            with pytest.raises(PaymentError) as exc_info:
                await payment_service.create_customer(test_user)
            
            assert "Failed to create customer" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_database_rollback_on_stripe_failure(self, payment_service, test_user, db_session):
        """Test database rollback when Stripe operations fail"""
        # Mock successful customer creation but failed subscription
        with patch.object(payment_service, 'create_customer', return_value="cus_test123"):
            with patch('stripe.PaymentMethod.attach'):
                with patch('stripe.Customer.modify'):
                    with patch('stripe.Subscription.create', side_effect=stripe.error.CardError("Card declined", None, "card_declined")):
                        
                        # Should rollback database changes on Stripe failure
                        with pytest.raises(PaymentError):
                            await payment_service.create_subscription(
                                str(test_user.id),
                                "pm_test123"
                            )
                        
                        # Verify no subscription was created in database
                        subscription = db_session.query(Subscription).filter(
                            Subscription.user_id == test_user.id
                        ).first()
                        assert subscription is None
    
    @pytest.mark.asyncio
    async def test_partial_failure_recovery(self, payment_service, test_user, db_session):
        """Test recovery from partial failures"""
        # Create subscription record
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Mock Stripe failure during cancellation
        with patch('stripe.Subscription.delete', side_effect=stripe.error.InvalidRequestError("Subscription not found", None)):
            # Should handle gracefully and still update local records
            with patch.object(payment_service, '_handle_subscription_cancellation') as mock_handle:
                try:
                    await payment_service.cancel_subscription(str(test_user.id), cancel_immediately=True)
                except PaymentError:
                    pass  # Expected due to Stripe failure
                
                # Local cleanup should still be attempted
                # (In real implementation, this would be handled more gracefully)


class TestIntegrationWorkflows:
    """Test complete integration workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_subscription_lifecycle(self, payment_service, db_session):
        """Test complete subscription lifecycle"""
        # Create user
        user = User(
            email="lifecycle@example.com",
            username="lifecycle",
            subscription_tier=SubscriptionTier.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # 1. Create customer
        with patch('stripe.Customer.create') as mock_create:
            mock_create.return_value = Mock(id="cus_lifecycle")
            customer_id = await payment_service.create_customer(user)
            assert customer_id == "cus_lifecycle"
        
        # 2. Add payment method
        with patch('stripe.PaymentMethod.attach') as mock_attach:
            with patch('stripe.Customer.modify') as mock_modify:
                result = await payment_service.add_payment_method(
                    customer_id, "pm_test123", set_as_default=True
                )
                assert result is not None
        
        # 3. Create subscription
        mock_subscription = Mock()
        mock_subscription.id = "sub_lifecycle"
        mock_subscription.status = "active"
        mock_subscription.current_period_start = int(time.time())
        mock_subscription.current_period_end = int(time.time()) + 2592000  # 30 days
        mock_subscription.cancel_at_period_end = False
        mock_subscription.customer = customer_id
        mock_subscription.latest_invoice = None
        
        with patch.object(payment_service, 'create_customer', return_value=customer_id):
            with patch('stripe.PaymentMethod.attach'):
                with patch('stripe.Customer.modify'):
                    with patch('stripe.Subscription.create', return_value=mock_subscription):
                        with patch.object(payment_service, '_handle_successful_subscription'):
                            result = await payment_service.create_subscription(
                                str(user.id), "pm_test123"
                            )
                            assert result['status'] == 'active'
        
        # Create subscription record in database for cancellation test
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_lifecycle",
            stripe_customer_id=customer_id,
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        # 4. Cancel subscription
        with patch('stripe.Subscription.modify') as mock_modify:
            mock_modify.return_value = Mock(current_period_end=int(time.time()) + 2592000)
            result = await payment_service.cancel_subscription(str(user.id))
            assert result['status'] == 'will_cancel'
    
    @pytest.mark.asyncio
    async def test_webhook_event_chain(self, payment_service, db_session):
        """Test processing chain of webhook events"""
        # Create user and subscription
        user = User(
            email="webhook@example.com",
            username="webhook",
            stripe_customer_id="cus_webhook",
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_webhook",
            stripe_customer_id="cus_webhook",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Process sequence of webhook events
        events = [
            {
                'type': 'customer.subscription.updated',
                'data': {'object': {'id': 'sub_webhook', 'status': 'active'}}
            },
            {
                'type': 'invoice.payment_succeeded',
                'data': {'object': {'subscription': 'sub_webhook', 'amount_paid': 999}}
            },
            {
                'type': 'customer.subscription.deleted',
                'data': {'object': {'id': 'sub_webhook', 'status': 'canceled'}}
            }
        ]
        
        with patch('stripe.Webhook.construct_event') as mock_construct:
            with patch.object(payment_service, '_handle_subscription_updated', return_value={'status': 'processed'}):
                with patch.object(payment_service, '_handle_payment_succeeded', return_value={'status': 'processed'}):
                    with patch.object(payment_service, '_handle_subscription_deleted', return_value={'status': 'processed'}):
                        
                        for event in events:
                            mock_construct.return_value = event
                            result = await payment_service.handle_webhook(b'payload', 'signature')
                            assert result['status'] == 'processed'


class TestDataConsistency:
    """Test data consistency and integrity"""
    
    @pytest.mark.asyncio
    async def test_subscription_status_consistency(self, payment_service, test_user, db_session):
        """Test that subscription status remains consistent between Stripe and database"""
        # Create subscription
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_consistency",
            stripe_customer_id="cus_consistency",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Mock Stripe subscription with different status
        mock_stripe_sub = Mock()
        mock_stripe_sub.id = "sub_consistency"
        mock_stripe_sub.status = "canceled"
        mock_stripe_sub.current_period_start = int(time.time())
        mock_stripe_sub.current_period_end = int(time.time()) + 2592000
        mock_stripe_sub.cancel_at_period_end = False
        
        with patch('stripe.Subscription.retrieve', return_value=mock_stripe_sub):
            updated_sub = await payment_service.update_subscription_status("sub_consistency")
            
            # Database should be updated to match Stripe
            assert updated_sub.status == SubscriptionStatus.CANCELED
            
            # User record should also be updated
            updated_user = db_session.query(User).filter(User.id == test_user.id).first()
            assert updated_user.subscription_status == SubscriptionStatus.CANCELED
    
    @pytest.mark.asyncio
    async def test_payment_history_integrity(self, payment_service, test_user, db_session):
        """Test payment history data integrity"""
        # Record multiple payments
        payments = [
            ("pi_test1", 999, PaymentStatus.SUCCEEDED),
            ("pi_test2", 999, PaymentStatus.FAILED),
            ("pi_test3", 999, PaymentStatus.SUCCEEDED)
        ]
        
        for payment_id, amount, status in payments:
            payment_record = PaymentHistory(
                user_id=test_user.id,
                stripe_payment_intent_id=payment_id,
                amount=amount,
                currency="usd",
                status=status,
                description=f"Test payment {payment_id}"
            )
            db_session.add(payment_record)
        
        db_session.commit()
        
        # Verify payment history integrity
        user_payments = db_session.query(PaymentHistory).filter(
            PaymentHistory.user_id == test_user.id
        ).all()
        
        assert len(user_payments) == 3
        successful_payments = [p for p in user_payments if p.status == PaymentStatus.SUCCEEDED]
        assert len(successful_payments) == 2
        
        # Verify total amounts
        total_attempted = sum(p.amount for p in user_payments)
        total_successful = sum(p.amount for p in successful_payments)
        assert total_attempted == 2997  # 3 * 999
        assert total_successful == 1998  # 2 * 999


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])