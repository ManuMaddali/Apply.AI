#!/usr/bin/env python3
"""
Payment Service Validation Script

This script validates the PaymentService implementation without requiring
actual Stripe API keys or making real API calls.
"""

import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_payment_service_imports():
    """Test that all required modules can be imported"""
    try:
        from services.payment_service import PaymentService, PaymentError
        from config.stripe_config import StripeConfig, get_stripe_config
        print("✓ All PaymentService modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_stripe_config():
    """Test Stripe configuration validation"""
    try:
        from config.stripe_config import StripeConfig
        
        # Test valid configuration
        config = StripeConfig(
            secret_key="sk_test_123",
            publishable_key="pk_test_123",
            webhook_secret="whsec_123",
            pro_monthly_price_id="price_123",
            environment="test"
        )
        
        assert config.is_configured
        assert not config.is_production
        print("✓ StripeConfig validation works correctly")
        
        # Test invalid configuration
        try:
            invalid_config = StripeConfig(
                secret_key="",
                publishable_key="pk_test_123"
            )
            print("✗ Should have failed validation")
            return False
        except ValueError:
            print("✓ Invalid configuration properly rejected")
        
        return True
    except Exception as e:
        print(f"✗ StripeConfig test failed: {e}")
        return False

def test_payment_service_initialization():
    """Test PaymentService initialization with mocked dependencies"""
    try:
        from services.payment_service import PaymentService
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models.user import Base
        
        # Create in-memory database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Mock Stripe configuration
        with patch('services.payment_service.get_stripe_config') as mock_config:
            mock_config.return_value = Mock(
                secret_key="sk_test_123",
                publishable_key="pk_test_123",
                webhook_secret="whsec_123",
                pro_monthly_price_id="price_123",
                environment="test"
            )
            
            with patch('stripe.api_key'):
                service = PaymentService(db)
                assert service.stripe_secret_key == "sk_test_123"
                assert service.pro_monthly_price_id == "price_123"
                print("✓ PaymentService initializes correctly")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ PaymentService initialization failed: {e}")
        return False

def test_payment_error_handling():
    """Test PaymentError exception handling"""
    try:
        from services.payment_service import PaymentError
        import stripe
        
        # Test basic PaymentError
        error = PaymentError("Test error")
        assert str(error) == "Test error"
        
        # Test PaymentError with Stripe error
        stripe_error = stripe.error.StripeError("Stripe error")
        error_with_stripe = PaymentError("Payment failed", stripe_error)
        assert error_with_stripe.stripe_error == stripe_error
        
        print("✓ PaymentError handling works correctly")
        return True
    except Exception as e:
        print(f"✗ PaymentError test failed: {e}")
        return False

def test_method_signatures():
    """Test that all required methods exist with correct signatures"""
    try:
        from services.payment_service import PaymentService
        import inspect
        
        # Required methods from the task specification
        required_methods = [
            'create_customer',
            'create_subscription', 
            'cancel_subscription',
            'get_payment_methods',
            'add_payment_method',
            'create_payment_intent',
            'handle_webhook',
            'retry_failed_payment'
        ]
        
        for method_name in required_methods:
            if not hasattr(PaymentService, method_name):
                print(f"✗ Missing method: {method_name}")
                return False
            
            method = getattr(PaymentService, method_name)
            if not callable(method):
                print(f"✗ {method_name} is not callable")
                return False
            
            # Check if method is async
            if not inspect.iscoroutinefunction(method):
                print(f"✗ {method_name} should be async")
                return False
        
        print("✓ All required methods exist and are async")
        return True
    except Exception as e:
        print(f"✗ Method signature test failed: {e}")
        return False

def test_webhook_event_types():
    """Test webhook event type support"""
    try:
        from config.stripe_config import SUPPORTED_WEBHOOK_EVENTS, is_supported_webhook_event
        
        # Test supported events
        expected_events = [
            "customer.subscription.created",
            "customer.subscription.updated", 
            "customer.subscription.deleted",
            "invoice.payment_succeeded",
            "invoice.payment_failed"
        ]
        
        for event in expected_events:
            if event not in SUPPORTED_WEBHOOK_EVENTS:
                print(f"✗ Missing webhook event: {event}")
                return False
            
            if not is_supported_webhook_event(event):
                print(f"✗ Event not recognized as supported: {event}")
                return False
        
        # Test unsupported event
        if is_supported_webhook_event("unsupported.event"):
            print("✗ Should not support unsupported.event")
            return False
        
        print("✓ Webhook event types configured correctly")
        return True
    except Exception as e:
        print(f"✗ Webhook event test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=== PaymentService Validation ===\n")
    
    tests = [
        ("Import Tests", test_payment_service_imports),
        ("Stripe Configuration", test_stripe_config),
        ("Service Initialization", test_payment_service_initialization),
        ("Error Handling", test_payment_error_handling),
        ("Method Signatures", test_method_signatures),
        ("Webhook Events", test_webhook_event_types)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"✗ {test_name} failed")
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All validation tests passed!")
        print("\nPaymentService implementation is ready for integration.")
        print("\nNext steps:")
        print("1. Set up Stripe API keys in environment variables")
        print("2. Configure webhook endpoints")
        print("3. Test with Stripe test mode")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)