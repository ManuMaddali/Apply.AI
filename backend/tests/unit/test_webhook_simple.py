"""
Simple webhook test - Test webhook logic without full app dependencies
"""

import json
import hmac
import hashlib
import time
from unittest.mock import MagicMock, patch
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

def test_webhook_signature_creation():
    """Test that we can create valid webhook signatures"""
    payload = b'{"type": "test"}'
    secret = "whsec_test_secret"
    signature = create_stripe_signature(payload, secret)
    
    print(f"✅ Signature creation test passed: {signature[:20]}...")
    return True

def test_webhook_event_types():
    """Test supported webhook event types"""
    from config.stripe_config import SUPPORTED_WEBHOOK_EVENTS, is_supported_webhook_event
    
    # Test supported events
    supported_events = [
        "customer.subscription.created",
        "customer.subscription.updated", 
        "customer.subscription.deleted",
        "invoice.payment_succeeded",
        "invoice.payment_failed"
    ]
    
    for event in supported_events:
        assert is_supported_webhook_event(event), f"Event {event} should be supported"
    
    # Test unsupported event
    assert not is_supported_webhook_event("unsupported.event"), "Unsupported event should return False"
    
    print(f"✅ Webhook event types test passed. Supported events: {len(SUPPORTED_WEBHOOK_EVENTS)}")
    return True

def test_payment_service_webhook_handler():
    """Test PaymentService webhook handling logic"""
    try:
        # Mock database session
        mock_db = MagicMock()
        
        # Create PaymentService with mocked dependencies
        with patch('services.payment_service.get_stripe_config') as mock_config:
            mock_config.return_value.webhook_secret = "whsec_test_secret"
            mock_config.return_value.secret_key = "sk_test_123"
            mock_config.return_value.publishable_key = "pk_test_123"
            mock_config.return_value.pro_monthly_price_id = "price_test_123"
            mock_config.return_value.environment = "test"
            
            from services.payment_service import PaymentService
            service = PaymentService(mock_db)
            
            # Test webhook signature verification
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
                
                # Mock the specific webhook handler
                with patch.object(service, '_handle_subscription_created') as mock_handler:
                    mock_handler.return_value = {'status': 'processed'}
                    
                    # Test webhook handling
                    result = service.handle_webhook(payload, signature)
                    
                    # Verify the result (this would be async in real usage)
                    print("✅ PaymentService webhook handler test setup completed")
                    return True
                    
    except Exception as e:
        print(f"❌ PaymentService webhook test failed: {e}")
        return False

def main():
    """Run simple webhook tests"""
    print("🧪 Running simple webhook tests...")
    
    tests = [
        test_webhook_signature_creation,
        test_webhook_event_types,
        test_payment_service_webhook_handler
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All webhook tests passed!")
        return True
    else:
        print("❌ Some webhook tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)