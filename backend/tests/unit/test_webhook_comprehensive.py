"""
Comprehensive webhook tests - Test all webhook event handlers

This test file verifies that all webhook event handlers work correctly
and handle various edge cases and error conditions.
"""

import asyncio
import json
import hmac
import hashlib
import time
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_stripe_signature(payload: bytes, secret: str) -> str:
    """Create a valid Stripe signature for testing"""
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode()}"
    signature = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"

class TestWebhookEventHandlers:
    """Test all webhook event handlers"""
    
    def __init__(self):
        self.mock_db = MagicMock()
        self.payment_service = None
        self.setup_payment_service()
    
    def setup_payment_service(self):
        """Set up PaymentService with mocked dependencies"""
        with patch('services.payment_service.get_stripe_config') as mock_config:
            mock_config.return_value.webhook_secret = "whsec_test_secret"
            mock_config.return_value.secret_key = "sk_test_123"
            mock_config.return_value.publishable_key = "pk_test_123"
            mock_config.return_value.pro_monthly_price_id = "price_test_123"
            mock_config.return_value.environment = "test"
            
            from services.payment_service import PaymentService
            self.payment_service = PaymentService(self.mock_db)
    
    async def test_subscription_created_webhook(self):
        """Test customer.subscription.created webhook"""
        try:
            # Mock user and database operations
            mock_user = MagicMock()
            mock_user.id = "user_123"
            mock_user.email = "test@example.com"
            
            self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
            self.mock_db.add = MagicMock()
            self.mock_db.commit = MagicMock()
            
            # Create test subscription data
            subscription_data = {
                "id": "sub_test123",
                "customer": "cus_test123",
                "status": "active",
                "current_period_start": int(time.time()),
                "current_period_end": int(time.time() + 2592000),  # 30 days
                "cancel_at_period_end": False,
                "metadata": {"user_id": "user_123"}
            }
            
            # Test the handler
            result = await self.payment_service._handle_subscription_created(subscription_data)
            
            assert result["status"] == "processed"
            assert result["action"] == "subscription_created"
            
            print("✅ Subscription created webhook test passed")
            return True
            
        except Exception as e:
            print(f"❌ Subscription created webhook test failed: {e}")
            return False
    
    async def test_subscription_updated_webhook(self):
        """Test customer.subscription.updated webhook"""
        try:
            # Mock subscription update
            with patch.object(self.payment_service, 'update_subscription_status') as mock_update:
                mock_update.return_value = MagicMock()
                
                subscription_data = {
                    "id": "sub_test123",
                    "status": "active"
                }
                
                result = await self.payment_service._handle_subscription_updated(subscription_data)
                
                assert result["status"] == "processed"
                assert result["action"] == "subscription_updated"
                mock_update.assert_called_once_with("sub_test123")
                
                print("✅ Subscription updated webhook test passed")
                return True
                
        except Exception as e:
            print(f"❌ Subscription updated webhook test failed: {e}")
            return False
    
    async def test_subscription_deleted_webhook(self):
        """Test customer.subscription.deleted webhook"""
        try:
            # Mock user
            mock_user = MagicMock()
            mock_user.id = "user_123"
            
            self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
            
            # Mock the cancellation handler
            with patch.object(self.payment_service, '_handle_subscription_cancellation') as mock_cancel:
                mock_cancel.return_value = None
                
                subscription_data = {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "metadata": {"user_id": "user_123"}
                }
                
                result = await self.payment_service._handle_subscription_deleted(subscription_data)
                
                assert result["status"] == "processed"
                assert result["action"] == "subscription_deleted"
                mock_cancel.assert_called_once()
                
                print("✅ Subscription deleted webhook test passed")
                return True
                
        except Exception as e:
            print(f"❌ Subscription deleted webhook test failed: {e}")
            return False
    
    async def test_payment_succeeded_webhook(self):
        """Test invoice.payment_succeeded webhook"""
        try:
            # Mock user
            mock_user = MagicMock()
            mock_user.id = "user_123"
            
            self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
            self.mock_db.add = MagicMock()
            self.mock_db.commit = MagicMock()
            
            invoice_data = {
                "id": "in_test123",
                "customer": "cus_test123",
                "payment_intent": "pi_test123",
                "amount_paid": 999,
                "currency": "usd"
            }
            
            result = await self.payment_service._handle_payment_succeeded(invoice_data)
            
            assert result["status"] == "processed"
            assert result["action"] == "payment_recorded"
            
            print("✅ Payment succeeded webhook test passed")
            return True
            
        except Exception as e:
            print(f"❌ Payment succeeded webhook test failed: {e}")
            return False
    
    async def test_payment_failed_webhook(self):
        """Test invoice.payment_failed webhook"""
        try:
            # Mock user
            mock_user = MagicMock()
            mock_user.id = "user_123"
            mock_user.subscription_tier = MagicMock()
            mock_user.subscription_tier.PRO = "pro"
            
            self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
            self.mock_db.commit = MagicMock()
            
            # Mock the payment failure recording
            with patch.object(self.payment_service, '_record_payment_failure') as mock_record:
                mock_record.return_value = MagicMock()
                
                invoice_data = {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "amount_due": 999,
                    "currency": "usd"
                }
                
                result = await self.payment_service._handle_payment_failed(invoice_data)
                
                assert result["status"] == "processed"
                assert result["action"] == "payment_failure_recorded"
                
                print("✅ Payment failed webhook test passed")
                return True
                
        except Exception as e:
            print(f"❌ Payment failed webhook test failed: {e}")
            return False
    
    async def test_trial_will_end_webhook(self):
        """Test customer.subscription.trial_will_end webhook"""
        try:
            subscription_data = {
                "id": "sub_test123",
                "metadata": {"user_id": "user_123"}
            }
            
            result = await self.payment_service._handle_trial_will_end(subscription_data)
            
            assert result["status"] == "processed"
            assert result["action"] == "trial_ending_noted"
            
            print("✅ Trial will end webhook test passed")
            return True
            
        except Exception as e:
            print(f"❌ Trial will end webhook test failed: {e}")
            return False
    
    async def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        try:
            payload = json.dumps({
                "type": "customer.subscription.created",
                "data": {"object": {"id": "sub_test"}}
            }).encode()
            
            signature = create_stripe_signature(payload, "whsec_test_secret")
            
            # Mock Stripe webhook verification
            with patch('stripe.Webhook.construct_event') as mock_construct:
                mock_event = {
                    'type': 'customer.subscription.created',
                    'data': {'object': {'id': 'sub_test', 'metadata': {'user_id': 'user_123'}}}
                }
                mock_construct.return_value = mock_event
                
                # Mock the handler
                with patch.object(self.payment_service, '_handle_subscription_created') as mock_handler:
                    mock_handler.return_value = {'status': 'processed'}
                    
                    result = await self.payment_service.handle_webhook(payload, signature)
                    
                    assert result["status"] == "processed"
                    mock_construct.assert_called_once()
                    
                    print("✅ Webhook signature verification test passed")
                    return True
                    
        except Exception as e:
            print(f"❌ Webhook signature verification test failed: {e}")
            return False
    
    async def test_webhook_invalid_signature(self):
        """Test webhook with invalid signature"""
        try:
            payload = b'{"type": "test"}'
            invalid_signature = "invalid_signature"
            
            # Mock Stripe to raise signature verification error
            with patch('stripe.Webhook.construct_event') as mock_construct:
                import stripe
                mock_construct.side_effect = stripe.error.SignatureVerificationError("Invalid signature", "sig")
                
                try:
                    await self.payment_service.handle_webhook(payload, invalid_signature)
                    # Should not reach here
                    return False
                except Exception as e:
                    # Should raise PaymentError
                    assert "Invalid webhook signature" in str(e)
                    print("✅ Invalid signature handling test passed")
                    return True
                    
        except Exception as e:
            print(f"❌ Invalid signature handling test failed: {e}")
            return False
    
    async def test_unsupported_webhook_event(self):
        """Test handling of unsupported webhook events"""
        try:
            payload = json.dumps({
                "type": "unsupported.event.type",
                "data": {"object": {"id": "test"}}
            }).encode()
            
            signature = create_stripe_signature(payload, "whsec_test_secret")
            
            # Mock Stripe webhook verification
            with patch('stripe.Webhook.construct_event') as mock_construct:
                mock_event = {
                    'type': 'unsupported.event.type',
                    'data': {'object': {'id': 'test'}}
                }
                mock_construct.return_value = mock_event
                
                result = await self.payment_service.handle_webhook(payload, signature)
                
                assert result["status"] == "ignored"
                assert result["event_type"] == "unsupported.event.type"
                
                print("✅ Unsupported webhook event test passed")
                return True
                
        except Exception as e:
            print(f"❌ Unsupported webhook event test failed: {e}")
            return False

async def run_all_tests():
    """Run all webhook tests"""
    print("🧪 Running comprehensive webhook tests...")
    
    tester = TestWebhookEventHandlers()
    
    tests = [
        tester.test_subscription_created_webhook,
        tester.test_subscription_updated_webhook,
        tester.test_subscription_deleted_webhook,
        tester.test_payment_succeeded_webhook,
        tester.test_payment_failed_webhook,
        tester.test_trial_will_end_webhook,
        tester.test_webhook_signature_verification,
        tester.test_webhook_invalid_signature,
        tester.test_unsupported_webhook_event
    ]
    
    passed = 0
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All comprehensive webhook tests passed!")
        return True
    else:
        print("❌ Some webhook tests failed")
        return False

def main():
    """Main test runner"""
    return asyncio.run(run_all_tests())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)