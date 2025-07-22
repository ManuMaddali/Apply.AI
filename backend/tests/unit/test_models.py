#!/usr/bin/env python3
"""
Test script to validate subscription models
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_model_imports():
    """Test that all models can be imported correctly"""
    try:
        print("Testing model imports...")
        
        # Test enum imports
        from models.user import (
            SubscriptionTier, SubscriptionStatus, TailoringMode, 
            UsageType, PaymentStatus
        )
        print("✅ Enums imported successfully")
        
        # Test that enums have correct values
        assert SubscriptionTier.FREE.value == "free"
        assert SubscriptionTier.PRO.value == "pro"
        assert SubscriptionStatus.ACTIVE.value == "active"
        assert TailoringMode.LIGHT.value == "light"
        assert TailoringMode.HEAVY.value == "heavy"
        assert UsageType.RESUME_PROCESSING.value == "resume_processing"
        assert PaymentStatus.SUCCEEDED.value == "succeeded"
        print("✅ Enum values are correct")
        
        # Test model imports (without database connection)
        from models.user import User, Subscription, UsageTracking, PaymentHistory
        print("✅ Models imported successfully")
        
        # Test that models have required attributes
        user_attrs = ['subscription_tier', 'stripe_customer_id', 'subscription_status', 
                     'weekly_usage_count', 'preferred_tailoring_mode']
        for attr in user_attrs:
            assert hasattr(User, attr), f"User model missing attribute: {attr}"
        print("✅ User model has all required subscription attributes")
        
        subscription_attrs = ['user_id', 'stripe_subscription_id', 'status', 'tier']
        for attr in subscription_attrs:
            assert hasattr(Subscription, attr), f"Subscription model missing attribute: {attr}"
        print("✅ Subscription model has all required attributes")
        
        usage_attrs = ['user_id', 'usage_type', 'usage_date', 'count']
        for attr in usage_attrs:
            assert hasattr(UsageTracking, attr), f"UsageTracking model missing attribute: {attr}"
        print("✅ UsageTracking model has all required attributes")
        
        payment_attrs = ['user_id', 'amount', 'currency', 'status']
        for attr in payment_attrs:
            assert hasattr(PaymentHistory, attr), f"PaymentHistory model missing attribute: {attr}"
        print("✅ PaymentHistory model has all required attributes")
        
        print("\n🎉 All model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_model_methods():
    """Test model methods without database connection"""
    try:
        print("\nTesting model methods...")
        
        from models.user import User, SubscriptionTier, SubscriptionStatus
        
        # Create a mock user instance (without saving to database)
        user = User()
        user.subscription_tier = SubscriptionTier.PRO
        user.subscription_status = SubscriptionStatus.ACTIVE
        user.weekly_usage_count = 3
        
        # Test methods
        assert user.is_pro_active() == True, "is_pro_active should return True for active Pro user"
        print("✅ is_pro_active method works")
        
        limits = user.get_usage_limits_new()
        assert limits['weekly_sessions'] == -1, "Pro users should have unlimited sessions"
        print("✅ get_usage_limits_new method works")
        
        assert user.can_use_feature('heavy_tailoring') == True, "Pro users should access heavy tailoring"
        print("✅ can_use_feature method works")
        
        # Test Free user
        user.subscription_tier = SubscriptionTier.FREE
        assert user.is_pro_active() == False, "is_pro_active should return False for Free user"
        assert user.can_use_feature('heavy_tailoring') == False, "Free users should not access heavy tailoring"
        print("✅ Free user restrictions work correctly")
        
        print("✅ All method tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Method test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Testing Subscription System Models")
    print("=" * 60)
    
    success = True
    
    # Test imports
    if not test_model_imports():
        success = False
    
    # Test methods
    if not test_model_methods():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Subscription models are correctly implemented.")
    else:
        print("❌ Some tests failed. Please check the model implementation.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)