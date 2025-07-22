#!/usr/bin/env python3
"""
Simple validation script for SubscriptionService without pytest
Tests core functionality to ensure the service works correctly
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from models.user import (
    Base, User, Subscription, UsageTracking,
    SubscriptionTier, SubscriptionStatus, UsageType,
    UserRole, AuthProvider
)
from services.subscription_service import SubscriptionService


# Test database setup - use in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_test_db():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def cleanup_test_db():
    """Clean up test database"""
    Base.metadata.drop_all(bind=engine)


def create_test_user(db_session, email="test@example.com", tier=SubscriptionTier.FREE):
    """Create a test user"""
    user = User(
        email=email,
        username=email.split('@')[0],
        full_name="Test User",
        subscription_tier=tier,
        subscription_status=SubscriptionStatus.ACTIVE,
        auth_provider=AuthProvider.EMAIL,
        is_active=True,
        is_verified=True,
        email_verified=True
    )
    if tier == SubscriptionTier.PRO:
        user.current_period_start = datetime.utcnow()
        user.current_period_end = datetime.utcnow() + timedelta(days=30)
    
    user.set_password("testpass123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


async def test_subscription_crud():
    """Test CRUD operations for subscriptions"""
    print("Testing Subscription CRUD operations...")
    
    db_session = setup_test_db()
    service = SubscriptionService(db_session)
    
    try:
        # Create test user
        user = create_test_user(db_session)
        
        # Test creating subscription
        subscription = await service.create_subscription(
            user_id=str(user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        assert subscription is not None, "Subscription creation failed"
        assert subscription.tier == SubscriptionTier.PRO, "Subscription tier incorrect"
        assert subscription.status == SubscriptionStatus.ACTIVE, "Subscription status incorrect"
        print("✅ Subscription creation successful")
        
        # Test getting active subscription
        active_sub = service.get_active_subscription(str(user.id))
        assert active_sub is not None, "Failed to get active subscription"
        assert active_sub.id == subscription.id, "Wrong subscription returned"
        print("✅ Get active subscription successful")
        
        # Test updating subscription
        updated_sub = await service.update_subscription(
            subscription_id=str(subscription.id),
            cancel_at_period_end=True
        )
        assert updated_sub.cancel_at_period_end == True, "Subscription update failed"
        print("✅ Subscription update successful")
        
        # Test canceling subscription
        canceled_sub = await service.cancel_subscription(
            user_id=str(user.id),
            cancel_immediately=True
        )
        assert canceled_sub.status == SubscriptionStatus.CANCELED, "Subscription cancellation failed"
        print("✅ Subscription cancellation successful")
        
        print("✅ All CRUD tests passed!")
        
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        raise
    finally:
        db_session.close()
        cleanup_test_db()


async def test_usage_limits():
    """Test usage limit checking"""
    print("\nTesting Usage Limits...")
    
    db_session = setup_test_db()
    service = SubscriptionService(db_session)
    
    try:
        # Create Free and Pro users
        free_user = create_test_user(db_session, "free@example.com", SubscriptionTier.FREE)
        pro_user = create_test_user(db_session, "pro@example.com", SubscriptionTier.PRO)
        
        # Test Pro user unlimited access
        result = await service.check_usage_limits(str(pro_user.id), UsageType.RESUME_PROCESSING)
        assert result.can_use == True, "Pro user should have unlimited access"
        print("✅ Pro user unlimited access confirmed")
        
        # Test Free user weekly limit
        result = await service.check_usage_limits(str(free_user.id), UsageType.RESUME_PROCESSING)
        assert result.can_use == True, "Free user should be able to use initially"
        assert result.limit == 5, "Free user limit should be 5"
        print("✅ Free user initial access confirmed")
        
        # Test Free user bulk processing blocked
        result = await service.check_usage_limits(str(free_user.id), UsageType.BULK_PROCESSING)
        assert result.can_use == False, "Free user should not be able to use bulk processing"
        print("✅ Free user bulk processing restriction confirmed")
        
        # Test Free user cover letter blocked
        result = await service.check_usage_limits(str(free_user.id), UsageType.COVER_LETTER)
        assert result.can_use == False, "Free user should not be able to use cover letters"
        print("✅ Free user cover letter restriction confirmed")
        
        # Test bulk processing limits
        free_limit = await service.get_bulk_processing_limit(str(free_user.id))
        pro_limit = await service.get_bulk_processing_limit(str(pro_user.id))
        assert free_limit == 1, "Free user bulk limit should be 1"
        assert pro_limit == 10, "Pro user bulk limit should be 10"
        print("✅ Bulk processing limits confirmed")
        
        print("✅ All usage limit tests passed!")
        
    except Exception as e:
        print(f"❌ Usage limit test failed: {e}")
        raise
    finally:
        db_session.close()
        cleanup_test_db()


async def test_usage_tracking():
    """Test usage tracking functionality"""
    print("\nTesting Usage Tracking...")
    
    db_session = setup_test_db()
    service = SubscriptionService(db_session)
    
    try:
        # Create test user
        user = create_test_user(db_session)
        
        # Test tracking usage
        usage_record = await service.track_usage(
            user_id=str(user.id),
            usage_type=UsageType.RESUME_PROCESSING,
            count=2,
            extra_data="test metadata"
        )
        
        assert usage_record is not None, "Usage tracking failed"
        assert usage_record.count == 2, "Usage count incorrect"
        print("✅ Usage tracking successful")
        
        # Check user counters were updated
        updated_user = db_session.query(User).filter(User.id == user.id).first()
        assert updated_user.total_usage_count == 2, "Total usage count not updated"
        assert updated_user.weekly_usage_count == 2, "Weekly usage count not updated"
        print("✅ User counters updated correctly")
        
        # Test weekly usage reset
        result = await service.reset_weekly_usage(str(user.id))
        assert result == True, "Weekly usage reset failed"
        
        updated_user = db_session.query(User).filter(User.id == user.id).first()
        assert updated_user.weekly_usage_count == 0, "Weekly usage not reset"
        print("✅ Weekly usage reset successful")
        
        # Test usage statistics
        stats = await service.get_usage_statistics(str(user.id))
        assert "user_id" in stats, "Usage statistics missing user_id"
        assert "subscription_tier" in stats, "Usage statistics missing subscription_tier"
        assert stats["subscription_tier"] == "free", "Incorrect subscription tier in stats"
        print("✅ Usage statistics retrieval successful")
        
        print("✅ All usage tracking tests passed!")
        
    except Exception as e:
        print(f"❌ Usage tracking test failed: {e}")
        raise
    finally:
        db_session.close()
        cleanup_test_db()


async def test_subscription_validation():
    """Test subscription status validation"""
    print("\nTesting Subscription Validation...")
    
    db_session = setup_test_db()
    service = SubscriptionService(db_session)
    
    try:
        # Create Pro user
        pro_user = create_test_user(db_session, "pro@example.com", SubscriptionTier.PRO)
        
        # Test validating active subscription
        result = await service.validate_subscription_status(str(pro_user.id))
        assert result["valid"] == True, "Active subscription validation failed"
        assert result["subscription_tier"] == "pro", "Incorrect tier in validation"
        print("✅ Active subscription validation successful")
        
        # Create expired Pro user
        expired_user = create_test_user(db_session, "expired@example.com", SubscriptionTier.PRO)
        expired_user.current_period_end = datetime.utcnow() - timedelta(days=1)
        db_session.commit()
        
        # Test validating expired subscription
        result = await service.validate_subscription_status(str(expired_user.id))
        assert result["valid"] == False, "Expired subscription should be invalid"
        assert "expired" in result["reason"].lower(), "Should indicate expiration"
        print("✅ Expired subscription validation successful")
        
        print("✅ All subscription validation tests passed!")
        
    except Exception as e:
        print(f"❌ Subscription validation test failed: {e}")
        raise
    finally:
        db_session.close()
        cleanup_test_db()


async def test_date_calculations():
    """Test date calculation helper methods"""
    print("\nTesting Date Calculations...")
    
    db_session = setup_test_db()
    service = SubscriptionService(db_session)
    
    try:
        # Test monthly billing date calculation
        current_date = datetime(2024, 1, 15)
        next_date = service.calculate_next_billing_date(current_date, "monthly")
        expected_date = datetime(2024, 2, 15)
        assert next_date == expected_date, f"Monthly billing calculation failed: {next_date} != {expected_date}"
        print("✅ Monthly billing date calculation successful")
        
        # Test yearly billing date calculation
        next_date = service.calculate_next_billing_date(current_date, "yearly")
        expected_date = datetime(2025, 1, 15)
        assert next_date == expected_date, f"Yearly billing calculation failed: {next_date} != {expected_date}"
        print("✅ Yearly billing date calculation successful")
        
        # Test prorated amount calculation
        full_amount = 999  # $9.99 in cents
        period_start = datetime(2024, 1, 1)
        period_end = datetime(2024, 1, 31)  # 30 days
        upgrade_date = datetime(2024, 1, 16)  # 15 days remaining
        
        prorated = service.calculate_prorated_amount(
            full_amount, period_start, period_end, upgrade_date
        )
        expected = int((15 / 30) * 999)  # Should be roughly half
        assert prorated == expected, f"Prorated calculation failed: {prorated} != {expected}"
        print("✅ Prorated amount calculation successful")
        
        # Test grace period check
        user = create_test_user(db_session)
        user.subscription_status = SubscriptionStatus.PAST_DUE
        user.current_period_end = datetime.utcnow() - timedelta(days=2)
        db_session.commit()
        
        in_grace = service.is_in_grace_period(str(user.id))
        assert in_grace == True, "Should be in grace period"
        print("✅ Grace period check successful")
        
        print("✅ All date calculation tests passed!")
        
    except Exception as e:
        print(f"❌ Date calculation test failed: {e}")
        raise
    finally:
        db_session.close()
        cleanup_test_db()


async def main():
    """Run all tests"""
    print("🚀 Starting SubscriptionService Validation Tests")
    print("=" * 50)
    
    try:
        await test_subscription_crud()
        await test_usage_limits()
        await test_usage_tracking()
        await test_subscription_validation()
        await test_date_calculations()
        
        print("\n" + "=" * 50)
        print("🎉 All SubscriptionService tests passed successfully!")
        print("✅ The subscription service is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())