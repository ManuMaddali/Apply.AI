#!/usr/bin/env python3
"""
Integration test for SubscriptionService with existing models
Tests that the service can be imported and basic functionality works
"""

import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test model imports
        from models.user import (
            User, Subscription, UsageTracking, PaymentHistory,
            SubscriptionTier, SubscriptionStatus, UsageType, TailoringMode,
            UserRole, AuthProvider
        )
        print("✅ Model imports successful")
        
        # Test service import
        from services.subscription_service import SubscriptionService, UsageLimitResult
        print("✅ Service imports successful")
        
        # Test that enums have expected values
        assert SubscriptionTier.FREE.value == "free"
        assert SubscriptionTier.PRO.value == "pro"
        assert SubscriptionStatus.ACTIVE.value == "active"
        assert UsageType.RESUME_PROCESSING.value == "resume_processing"
        print("✅ Enum values correct")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_service_instantiation():
    """Test that the service can be instantiated with a mock database"""
    print("\nTesting service instantiation...")
    
    try:
        from services.subscription_service import SubscriptionService
        from unittest.mock import Mock
        
        # Create mock database session
        mock_db = Mock()
        
        # Instantiate service
        service = SubscriptionService(mock_db)
        
        # Verify service has database reference
        assert service.db == mock_db
        print("✅ Service instantiation successful")
        
        # Test that service methods exist and are callable
        methods_to_test = [
            'create_subscription',
            'check_usage_limits', 
            'track_usage',
            'validate_subscription_status',
            'calculate_next_billing_date'
        ]
        
        for method_name in methods_to_test:
            method = getattr(service, method_name)
            assert callable(method), f"Method {method_name} is not callable"
        
        print("✅ All key methods are callable")
        return True
        
    except Exception as e:
        print(f"❌ Service instantiation failed: {e}")
        return False


def test_usage_limit_result():
    """Test UsageLimitResult functionality"""
    print("\nTesting UsageLimitResult...")
    
    try:
        from services.subscription_service import UsageLimitResult
        
        # Test creating result objects
        success_result = UsageLimitResult(True, "Success", remaining=3, limit=5)
        failure_result = UsageLimitResult(False, "Limit exceeded")
        
        # Test properties
        assert success_result.can_use == True
        assert success_result.reason == "Success"
        assert success_result.remaining == 3
        assert success_result.limit == 5
        
        assert failure_result.can_use == False
        assert failure_result.reason == "Limit exceeded"
        assert failure_result.remaining == 0  # Default
        assert failure_result.limit == 0      # Default
        
        # Test serialization
        success_dict = success_result.to_dict()
        expected_keys = ["can_use", "reason", "remaining", "limit"]
        for key in expected_keys:
            assert key in success_dict, f"Missing key: {key}"
        
        print("✅ UsageLimitResult functionality works correctly")
        return True
        
    except Exception as e:
        print(f"❌ UsageLimitResult test failed: {e}")
        return False


def test_date_calculations():
    """Test date calculation methods work correctly"""
    print("\nTesting date calculations...")
    
    try:
        from services.subscription_service import SubscriptionService
        from unittest.mock import Mock
        
        service = SubscriptionService(Mock())
        
        # Test monthly billing calculation
        test_date = datetime(2024, 6, 15)
        next_month = service.calculate_next_billing_date(test_date, "monthly")
        expected = datetime(2024, 7, 15)
        assert next_month == expected, f"Expected {expected}, got {next_month}"
        
        # Test yearly billing calculation
        next_year = service.calculate_next_billing_date(test_date, "yearly")
        expected_year = datetime(2025, 6, 15)
        assert next_year == expected_year, f"Expected {expected_year}, got {next_year}"
        
        # Test prorated calculation
        prorated = service.calculate_prorated_amount(
            1000,  # $10.00
            datetime(2024, 1, 1),
            datetime(2024, 1, 31),
            datetime(2024, 1, 16)  # Halfway through month
        )
        # Should be roughly half the amount
        expected_prorated = int((15 / 30) * 1000)  # 15 days remaining out of 30
        assert prorated == expected_prorated, f"Expected {expected_prorated}, got {prorated}"
        
        print("✅ Date calculations work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Date calculation test failed: {e}")
        return False


def test_model_compatibility():
    """Test that the service is compatible with the User model structure"""
    print("\nTesting model compatibility...")
    
    try:
        from models.user import User, SubscriptionTier, SubscriptionStatus, AuthProvider
        
        # Test that User model has expected subscription fields
        user_fields = [
            'subscription_tier', 'subscription_status', 'stripe_customer_id',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'weekly_usage_count', 'weekly_usage_reset', 'total_usage_count',
            'preferred_tailoring_mode'
        ]
        
        # Create a test user instance (without database)
        user = User()
        
        for field in user_fields:
            assert hasattr(user, field), f"User model missing field: {field}"
        
        # Test that User model has expected methods
        user_methods = [
            'is_pro_active', 'get_active_subscription', 'reset_weekly_usage',
            'should_reset_weekly_usage', 'can_use_feature', 'get_usage_limits_new',
            'can_process_resume'
        ]
        
        for method in user_methods:
            assert hasattr(user, method), f"User model missing method: {method}"
            assert callable(getattr(user, method)), f"User method {method} not callable"
        
        print("✅ Model compatibility confirmed")
        return True
        
    except Exception as e:
        print(f"❌ Model compatibility test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🚀 Starting SubscriptionService Integration Tests")
    print("=" * 55)
    
    tests = [
        test_imports,
        test_service_instantiation,
        test_usage_limit_result,
        test_date_calculations,
        test_model_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 55)
    print(f"📊 Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All SubscriptionService integration tests passed!")
        print("✅ The subscription service is ready for use")
        return True
    else:
        print(f"❌ {failed} integration test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)