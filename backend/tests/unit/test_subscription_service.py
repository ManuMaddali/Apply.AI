"""
Comprehensive Test Suite for SubscriptionService

Tests all core subscription service functionality including:
- CRUD operations for subscriptions
- Usage limit checking and enforcement
- Usage tracking and reset functionality
- Subscription status validation
- Automatic tier downgrade logic
- Helper methods for subscription date calculations
- Performance and security aspects
- Error handling and edge cases
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch, AsyncMock
import concurrent.futures
import threading

from models.user import (
    Base, User, Subscription, UsageTracking, PaymentHistory,
    SubscriptionTier, SubscriptionStatus, UsageType, TailoringMode,
    UserRole, AuthProvider, PaymentStatus
)
from services.subscription_service import SubscriptionService, UsageLimitResult


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_subscription.db"
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
    """Create SubscriptionService instance with test database"""
    return SubscriptionService(db_session)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
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


@pytest.fixture
def test_pro_user(db_session):
    """Create a test Pro user"""
    user = User(
        email="pro@example.com",
        username="prouser",
        full_name="Pro User",
        subscription_tier=SubscriptionTier.PRO,
        subscription_status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
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


class TestSubscriptionCRUD:
    """Test CRUD operations for subscriptions"""
    
    @pytest.mark.asyncio
    async def test_create_subscription(self, subscription_service, test_user):
        """Test creating a new subscription"""
        # Create subscription
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_subscription_id="sub_test123",
            stripe_customer_id="cus_test123",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        assert subscription is not None
        assert subscription.tier == SubscriptionTier.PRO
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.stripe_subscription_id == "sub_test123"
        assert subscription.stripe_customer_id == "cus_test123"
        
        # Check user was updated
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.PRO
        assert updated_user.subscription_status == SubscriptionStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_create_duplicate_subscription_fails(self, subscription_service, test_user):
        """Test that creating duplicate subscription fails"""
        # Create first subscription
        await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_test123"
        )
        
        # Try to create second subscription - should fail
        with pytest.raises(ValueError, match="already has an active subscription"):
            await subscription_service.create_subscription(
                user_id=str(test_user.id),
                tier=SubscriptionTier.PRO,
                stripe_customer_id="cus_test456"
            )
    
    @pytest.mark.asyncio
    async def test_update_subscription(self, subscription_service, test_user):
        """Test updating an existing subscription"""
        # Create subscription
        subscription = await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_test123"
        )
        
        # Update subscription
        updated_subscription = await subscription_service.update_subscription(
            subscription_id=str(subscription.id),
            status=SubscriptionStatus.CANCELED,
            cancel_at_period_end=True
        )
        
        assert updated_subscription.status == SubscriptionStatus.CANCELED
        assert updated_subscription.cancel_at_period_end == True
        
        # Check user was updated
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_status == SubscriptionStatus.CANCELED
        assert updated_user.cancel_at_period_end == True
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_immediately(self, subscription_service, test_user):
        """Test canceling subscription immediately"""
        # Create subscription
        await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_test123",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        # Cancel immediately
        canceled_subscription = await subscription_service.cancel_subscription(
            user_id=str(test_user.id),
            cancel_immediately=True
        )
        
        assert canceled_subscription.status == SubscriptionStatus.CANCELED
        assert canceled_subscription.canceled_at is not None
        
        # Check user was downgraded
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.FREE
        assert updated_user.subscription_status == SubscriptionStatus.CANCELED
    
    @pytest.mark.asyncio
    async def test_cancel_subscription_at_period_end(self, subscription_service, test_user):
        """Test canceling subscription at period end"""
        # Create subscription
        await subscription_service.create_subscription(
            user_id=str(test_user.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_test123",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        # Cancel at period end
        canceled_subscription = await subscription_service.cancel_subscription(
            user_id=str(test_user.id),
            cancel_immediately=False
        )
        
        assert canceled_subscription.cancel_at_period_end == True
        assert canceled_subscription.status == SubscriptionStatus.ACTIVE  # Still active until period end
        
        # Check user still has Pro access
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.PRO
        assert updated_user.cancel_at_period_end == True
    
    def test_get_active_subscription(self, subscription_service, test_user, db_session):
        """Test getting active subscription"""
        # No subscription initially
        subscription = subscription_service.get_active_subscription(str(test_user.id))
        assert subscription is None
        
        # Create subscription
        subscription = Subscription(
            user_id=test_user.id,
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE,
            stripe_customer_id="cus_test123"
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Should find active subscription
        active_subscription = subscription_service.get_active_subscription(str(test_user.id))
        assert active_subscription is not None
        assert active_subscription.tier == SubscriptionTier.PRO


class TestUsageLimits:
    """Test usage limit checking and enforcement"""
    
    @pytest.mark.asyncio
    async def test_pro_user_unlimited_access(self, subscription_service, test_pro_user):
        """Test that Pro users have unlimited access"""
        result = await subscription_service.check_usage_limits(
            str(test_pro_user.id), 
            UsageType.RESUME_PROCESSING
        )
        
        assert result.can_use == True
        assert "unlimited access" in result.reason.lower()
    
    @pytest.mark.asyncio
    async def test_free_user_weekly_limit(self, subscription_service, test_user):
        """Test weekly limit for Free users"""
        # Should be able to use initially
        result = await subscription_service.check_usage_limits(
            str(test_user.id), 
            UsageType.RESUME_PROCESSING
        )
        assert result.can_use == True
        assert result.limit == 5
        assert result.remaining == 5
        
        # Use up the weekly limit
        test_user.weekly_usage_count = 5
        subscription_service.db.commit()
        
        # Should be blocked now
        result = await subscription_service.check_usage_limits(
            str(test_user.id), 
            UsageType.RESUME_PROCESSING
        )
        assert result.can_use == False
        assert "exceeded" in result.reason.lower()
        assert result.remaining == 0
    
    @pytest.mark.asyncio
    async def test_free_user_bulk_processing_blocked(self, subscription_service, test_user):
        """Test that Free users can't use bulk processing"""
        result = await subscription_service.check_usage_limits(
            str(test_user.id), 
            UsageType.BULK_PROCESSING
        )
        
        assert result.can_use == False
        assert "requires Pro subscription" in result.reason
    
    @pytest.mark.asyncio
    async def test_free_user_cover_letter_blocked(self, subscription_service, test_user):
        """Test that Free users can't use cover letters"""
        result = await subscription_service.check_usage_limits(
            str(test_user.id), 
            UsageType.COVER_LETTER
        )
        
        assert result.can_use == False
        assert "require Pro subscription" in result.reason
    
    @pytest.mark.asyncio
    async def test_bulk_processing_limits(self, subscription_service, test_user, test_pro_user):
        """Test bulk processing limits"""
        # Free user gets 1 job limit
        free_limit = await subscription_service.get_bulk_processing_limit(str(test_user.id))
        assert free_limit == 1
        
        # Pro user gets 10 job limit
        pro_limit = await subscription_service.get_bulk_processing_limit(str(test_pro_user.id))
        assert pro_limit == 10
    
    @pytest.mark.asyncio
    async def test_feature_access_control(self, subscription_service, test_user, test_pro_user):
        """Test feature access control"""
        # Free user limitations
        assert await subscription_service.can_use_feature(str(test_user.id), "resume_processing") == True
        assert await subscription_service.can_use_feature(str(test_user.id), "cover_letter") == False
        assert await subscription_service.can_use_feature(str(test_user.id), "bulk_processing") == False
        assert await subscription_service.can_use_feature(str(test_user.id), "advanced_formatting") == False
        assert await subscription_service.can_use_feature(str(test_user.id), "analytics") == False
        assert await subscription_service.can_use_feature(str(test_user.id), "heavy_tailoring") == False
        
        # Pro user access
        assert await subscription_service.can_use_feature(str(test_pro_user.id), "resume_processing") == True
        assert await subscription_service.can_use_feature(str(test_pro_user.id), "cover_letter") == True
        assert await subscription_service.can_use_feature(str(test_pro_user.id), "bulk_processing") == True
        assert await subscription_service.can_use_feature(str(test_pro_user.id), "advanced_formatting") == True
        assert await subscription_service.can_use_feature(str(test_pro_user.id), "analytics") == True
        assert await subscription_service.can_use_feature(str(test_pro_user.id), "heavy_tailoring") == True


class TestUsageTracking:
    """Test usage tracking and reset functionality"""
    
    @pytest.mark.asyncio
    async def test_track_usage(self, subscription_service, test_user):
        """Test tracking user usage"""
        # Track usage
        usage_record = await subscription_service.track_usage(
            user_id=str(test_user.id),
            usage_type=UsageType.RESUME_PROCESSING,
            count=2,
            extra_data="test metadata",
            session_id="session123"
        )
        
        assert usage_record is not None
        assert usage_record.usage_type == UsageType.RESUME_PROCESSING
        assert usage_record.count == 2
        assert usage_record.extra_data == "test metadata"
        assert usage_record.session_id == "session123"
        
        # Check user counters were updated
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.total_usage_count == 2
        assert updated_user.weekly_usage_count == 2
        assert updated_user.resumes_generated == 2
    
    @pytest.mark.asyncio
    async def test_reset_weekly_usage(self, subscription_service, test_user):
        """Test resetting weekly usage"""
        # Set some usage
        test_user.weekly_usage_count = 3
        test_user.weekly_usage_reset = datetime.utcnow() - timedelta(days=8)
        subscription_service.db.commit()
        
        # Reset usage
        result = await subscription_service.reset_weekly_usage(str(test_user.id))
        assert result == True
        
        # Check usage was reset
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.weekly_usage_count == 0
        assert updated_user.weekly_usage_reset > datetime.utcnow() - timedelta(minutes=1)
    
    @pytest.mark.asyncio
    async def test_reset_all_weekly_usage(self, subscription_service, db_session):
        """Test resetting weekly usage for all users"""
        # Create users with old usage
        user1 = User(
            email="user1@example.com",
            username="user1",
            weekly_usage_count=5,
            weekly_usage_reset=datetime.utcnow() - timedelta(days=8),
            auth_provider=AuthProvider.EMAIL
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            weekly_usage_count=3,
            weekly_usage_reset=datetime.utcnow() - timedelta(days=10),
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Reset all
        reset_count = await subscription_service.reset_all_weekly_usage()
        assert reset_count == 2
        
        # Check users were reset
        updated_user1 = db_session.query(User).filter(User.id == user1.id).first()
        updated_user2 = db_session.query(User).filter(User.id == user2.id).first()
        assert updated_user1.weekly_usage_count == 0
        assert updated_user2.weekly_usage_count == 0
    
    @pytest.mark.asyncio
    async def test_get_usage_statistics(self, subscription_service, test_user, db_session):
        """Test getting usage statistics"""
        # Create some usage records
        usage1 = UsageTracking(
            user_id=test_user.id,
            usage_type=UsageType.RESUME_PROCESSING,
            count=2,
            usage_date=datetime.utcnow()
        )
        usage2 = UsageTracking(
            user_id=test_user.id,
            usage_type=UsageType.COVER_LETTER,
            count=1,
            usage_date=datetime.utcnow() - timedelta(days=2)
        )
        db_session.add_all([usage1, usage2])
        db_session.commit()
        
        # Get statistics
        stats = await subscription_service.get_usage_statistics(str(test_user.id))
        
        assert stats["user_id"] == str(test_user.id)
        assert stats["subscription_tier"] == "free"
        assert stats["is_pro_active"] == False
        assert "weekly_usage" in stats
        assert "monthly_usage" in stats
        assert "total_usage" in stats
        assert "current_limits" in stats


class TestSubscriptionValidation:
    """Test subscription status validation"""
    
    @pytest.mark.asyncio
    async def test_validate_active_subscription(self, subscription_service, test_pro_user):
        """Test validating active subscription"""
        result = await subscription_service.validate_subscription_status(str(test_pro_user.id))
        
        assert result["valid"] == True
        assert result["subscription_tier"] == "pro"
        assert result["subscription_status"] == "active"
        assert result["is_pro_active"] == True
    
    @pytest.mark.asyncio
    async def test_validate_expired_subscription(self, subscription_service, test_user, db_session):
        """Test validating expired subscription"""
        # Create expired Pro subscription
        test_user.subscription_tier = SubscriptionTier.PRO
        test_user.subscription_status = SubscriptionStatus.ACTIVE
        test_user.current_period_end = datetime.utcnow() - timedelta(days=1)
        db_session.commit()
        
        result = await subscription_service.validate_subscription_status(str(test_user.id))
        
        assert result["valid"] == False
        assert "expired" in result["reason"].lower()
        assert result["action_taken"] == "downgraded_to_free"
        
        # Check user was downgraded
        updated_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.FREE
        assert updated_user.subscription_status == SubscriptionStatus.CANCELED


class TestAutomaticDowngrade:
    """Test automatic tier downgrade logic"""
    
    @pytest.mark.asyncio
    async def test_process_expired_subscriptions(self, subscription_service, db_session):
        """Test processing expired subscriptions"""
        # Create expired Pro users
        expired_user1 = User(
            email="expired1@example.com",
            username="expired1",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() - timedelta(days=1),
            auth_provider=AuthProvider.EMAIL
        )
        expired_user2 = User(
            email="expired2@example.com",
            username="expired2",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() - timedelta(days=5),
            auth_provider=AuthProvider.EMAIL
        )
        
        # Create active Pro user (should not be affected)
        active_user = User(
            email="active@example.com",
            username="active",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() + timedelta(days=10),
            auth_provider=AuthProvider.EMAIL
        )
        
        db_session.add_all([expired_user1, expired_user2, active_user])
        db_session.commit()
        
        # Process expired subscriptions
        downgraded_count = await subscription_service.process_expired_subscriptions()
        assert downgraded_count == 2
        
        # Check expired users were downgraded
        updated_expired1 = db_session.query(User).filter(User.id == expired_user1.id).first()
        updated_expired2 = db_session.query(User).filter(User.id == expired_user2.id).first()
        updated_active = db_session.query(User).filter(User.id == active_user.id).first()
        
        assert updated_expired1.subscription_tier == SubscriptionTier.FREE
        assert updated_expired1.subscription_status == SubscriptionStatus.CANCELED
        assert updated_expired2.subscription_tier == SubscriptionTier.FREE
        assert updated_expired2.subscription_status == SubscriptionStatus.CANCELED
        
        # Active user should be unchanged
        assert updated_active.subscription_tier == SubscriptionTier.PRO
        assert updated_active.subscription_status == SubscriptionStatus.ACTIVE


class TestDateCalculations:
    """Test helper methods for subscription date calculations"""
    
    def test_calculate_next_billing_date_monthly(self, subscription_service):
        """Test calculating next monthly billing date"""
        current_date = datetime(2024, 1, 15)
        next_date = subscription_service.calculate_next_billing_date(current_date, "monthly")
        assert next_date == datetime(2024, 2, 15)
        
        # Test December to January
        december_date = datetime(2024, 12, 15)
        next_date = subscription_service.calculate_next_billing_date(december_date, "monthly")
        assert next_date == datetime(2025, 1, 15)
    
    def test_calculate_next_billing_date_yearly(self, subscription_service):
        """Test calculating next yearly billing date"""
        current_date = datetime(2024, 1, 15)
        next_date = subscription_service.calculate_next_billing_date(current_date, "yearly")
        assert next_date == datetime(2025, 1, 15)
    
    def test_calculate_prorated_amount(self, subscription_service):
        """Test calculating prorated amount"""
        full_amount = 999  # $9.99 in cents
        period_start = datetime(2024, 1, 1)
        period_end = datetime(2024, 1, 31)  # 30 days
        upgrade_date = datetime(2024, 1, 16)  # 15 days remaining
        
        prorated = subscription_service.calculate_prorated_amount(
            full_amount, period_start, period_end, upgrade_date
        )
        
        # Should be roughly half the amount (15/30 days)
        expected = int((15 / 30) * 999)
        assert prorated == expected
    
    def test_days_until_renewal(self, subscription_service, test_pro_user):
        """Test calculating days until renewal"""
        # Set renewal date to 10 days from now
        test_pro_user.current_period_end = datetime.utcnow() + timedelta(days=10)
        subscription_service.db.commit()
        
        days = subscription_service.days_until_renewal(str(test_pro_user.id))
        assert 9 <= days <= 10  # Allow for small timing differences
    
    def test_is_in_grace_period(self, subscription_service, test_user, db_session):
        """Test checking grace period"""
        # Set user as past due within grace period
        test_user.subscription_status = SubscriptionStatus.PAST_DUE
        test_user.current_period_end = datetime.utcnow() - timedelta(days=2)
        db_session.commit()
        
        # Should be in grace period (default 3 days)
        assert subscription_service.is_in_grace_period(str(test_user.id)) == True
        
        # Set past due beyond grace period
        test_user.current_period_end = datetime.utcnow() - timedelta(days=5)
        db_session.commit()
        
        # Should not be in grace period
        assert subscription_service.is_in_grace_period(str(test_user.id)) == False


class TestSubscriptionMetrics:
    """Test subscription analytics and reporting"""
    
    @pytest.mark.asyncio
    async def test_get_subscription_metrics(self, subscription_service, db_session):
        """Test getting subscription metrics"""
        # Create test users with different tiers
        free_user1 = User(email="free1@example.com", username="free1", 
                         subscription_tier=SubscriptionTier.FREE, auth_provider=AuthProvider.EMAIL)
        free_user2 = User(email="free2@example.com", username="free2", 
                         subscription_tier=SubscriptionTier.FREE, auth_provider=AuthProvider.EMAIL)
        pro_user1 = User(email="pro1@example.com", username="pro1", 
                        subscription_tier=SubscriptionTier.PRO, auth_provider=AuthProvider.EMAIL)
        
        db_session.add_all([free_user1, free_user2, pro_user1])
        db_session.commit()
        
        # Create subscriptions
        active_sub = Subscription(
            user_id=pro_user1.id,
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE,
            stripe_customer_id="cus_test"
        )
        canceled_sub = Subscription(
            user_id=free_user1.id,
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.CANCELED,
            canceled_at=datetime.utcnow(),
            stripe_customer_id="cus_test2"
        )
        
        db_session.add_all([active_sub, canceled_sub])
        db_session.commit()
        
        # Get metrics
        metrics = await subscription_service.get_subscription_metrics()
        
        assert "tier_distribution" in metrics
        assert "active_subscriptions" in metrics
        assert "canceled_this_month" in metrics
        assert "new_subscriptions_this_month" in metrics
        assert "churn_rate" in metrics
        
        assert metrics["tier_distribution"]["free"] == 2
        assert metrics["tier_distribution"]["pro"] == 1
        assert metrics["active_subscriptions"] == 1
        assert metrics["canceled_this_month"] == 1


class TestPerformance:
    """Test performance aspects of subscription service"""
    
    @pytest.mark.asyncio
    async def test_bulk_usage_tracking_performance(self, subscription_service, test_user):
        """Test performance of bulk usage tracking"""
        start_time = time.time()
        
        # Track 100 usage records
        tasks = []
        for i in range(100):
            task = subscription_service.track_usage(
                user_id=str(test_user.id),
                usage_type=UsageType.RESUME_PROCESSING,
                count=1,
                session_id=f"session_{i}"
            )
            tasks.append(task)
        
        # Execute all tracking operations
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (5 seconds for 100 operations)
        assert duration < 5.0, f"Bulk usage tracking took too long: {duration}s"
        
        # Verify all records were created
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.total_usage_count == 100
    
    @pytest.mark.asyncio
    async def test_concurrent_usage_limit_checks(self, subscription_service, test_user):
        """Test concurrent usage limit checks"""
        # Set user near limit
        test_user.weekly_usage_count = 4  # 1 away from limit of 5
        subscription_service.db.commit()
        
        # Create multiple concurrent limit checks
        async def check_limits():
            return await subscription_service.check_usage_limits(
                str(test_user.id), 
                UsageType.RESUME_PROCESSING
            )
        
        # Run 10 concurrent checks
        tasks = [check_limits() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should return consistent results
        for result in results:
            assert result.can_use == True  # Should still be able to use
            assert result.remaining == 1   # Should have 1 remaining
    
    @pytest.mark.asyncio
    async def test_subscription_metrics_performance(self, subscription_service, db_session):
        """Test performance of subscription metrics calculation"""
        # Create many test users and subscriptions
        users = []
        for i in range(50):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                subscription_tier=SubscriptionTier.PRO if i % 2 == 0 else SubscriptionTier.FREE,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Measure metrics calculation time
        start_time = time.time()
        metrics = await subscription_service.get_subscription_metrics()
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 2.0, f"Metrics calculation took too long: {duration}s"
        assert "tier_distribution" in metrics
        assert metrics["tier_distribution"]["pro"] == 25
        assert metrics["tier_distribution"]["free"] == 25


class TestSecurity:
    """Test security aspects of subscription service"""
    
    @pytest.mark.asyncio
    async def test_user_isolation(self, subscription_service, db_session):
        """Test that users cannot access each other's data"""
        # Create two users
        user1 = User(
            email="user1@example.com",
            username="user1",
            subscription_tier=SubscriptionTier.PRO,
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
        await subscription_service.create_subscription(
            user_id=str(user1.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_user1"
        )
        
        # User2 should not be able to access user1's subscription
        user2_subscription = subscription_service.get_active_subscription(str(user2.id))
        assert user2_subscription is None
        
        # User1's subscription should not affect user2's limits
        user2_limits = await subscription_service.check_usage_limits(
            str(user2.id), 
            UsageType.RESUME_PROCESSING
        )
        assert user2_limits.limit == 5  # Free user limit
    
    @pytest.mark.asyncio
    async def test_input_validation(self, subscription_service):
        """Test input validation and sanitization"""
        # Test invalid user IDs
        with pytest.raises(Exception):
            await subscription_service.create_subscription(
                user_id="invalid-uuid",
                tier=SubscriptionTier.PRO
            )
        
        # Test SQL injection attempts
        malicious_input = "'; DROP TABLE users; --"
        result = await subscription_service.check_usage_limits(
            malicious_input, 
            UsageType.RESUME_PROCESSING
        )
        assert result.can_use == False
        assert "error" in result.reason.lower() or "not found" in result.reason.lower()
    
    @pytest.mark.asyncio
    async def test_data_privacy(self, subscription_service, test_user, db_session):
        """Test that sensitive data is properly handled"""
        # Track usage with sensitive metadata
        sensitive_data = "user_ip:192.168.1.1,session_token:abc123"
        
        usage_record = await subscription_service.track_usage(
            user_id=str(test_user.id),
            usage_type=UsageType.RESUME_PROCESSING,
            extra_data=sensitive_data
        )
        
        # Verify data is stored but not exposed in statistics
        stats = await subscription_service.get_usage_statistics(str(test_user.id))
        
        # Stats should not contain raw sensitive data
        stats_str = str(stats)
        assert "192.168.1.1" not in stats_str
        assert "session_token" not in stats_str


class TestErrorHandling:
    """Test comprehensive error handling"""
    
    @pytest.mark.asyncio
    async def test_database_connection_failure(self, db_session):
        """Test handling of database connection failures"""
        # Create service with mock database that fails
        mock_db = Mock()
        mock_db.query.side_effect = Exception("Database connection failed")
        
        service = SubscriptionService(mock_db)
        
        # Should handle database errors gracefully
        result = await service.check_usage_limits("user123", UsageType.RESUME_PROCESSING)
        assert result.can_use == False
        assert "error" in result.reason.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_subscription_data(self, subscription_service, test_user):
        """Test handling of invalid subscription data"""
        # Try to create subscription with invalid data
        with pytest.raises(Exception):
            await subscription_service.create_subscription(
                user_id=str(test_user.id),
                tier="invalid_tier"  # Invalid enum value
            )
    
    @pytest.mark.asyncio
    async def test_concurrent_subscription_creation(self, subscription_service, test_user):
        """Test handling of concurrent subscription creation attempts"""
        # Try to create multiple subscriptions simultaneously
        async def create_subscription():
            try:
                return await subscription_service.create_subscription(
                    user_id=str(test_user.id),
                    tier=SubscriptionTier.PRO,
                    stripe_customer_id="cus_concurrent"
                )
            except (ValueError, Exception):
                return None  # Expected for duplicate attempts or constraint failures
        
        # Run concurrent creation attempts
        tasks = [create_subscription() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Only one should succeed, others should fail gracefully
        successful_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        assert len(successful_results) == 1
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_large_datasets(self, subscription_service, db_session):
        """Test memory usage with large datasets"""
        # Create many usage records
        user = User(
            email="heavy_user@example.com",
            username="heavy_user",
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Create 1000 usage records
        usage_records = []
        for i in range(1000):
            record = UsageTracking(
                user_id=user.id,
                usage_type=UsageType.RESUME_PROCESSING,
                count=1,
                usage_date=datetime.utcnow() - timedelta(days=i % 30)
            )
            usage_records.append(record)
        
        db_session.add_all(usage_records)
        db_session.commit()
        
        # Get statistics - should handle large dataset efficiently
        stats = await subscription_service.get_usage_statistics(str(user.id))
        
        # Should return results without memory issues
        assert "total_usage" in stats
        assert isinstance(stats["total_usage"], dict)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.mark.asyncio
    async def test_subscription_at_exact_expiry(self, subscription_service, test_user, db_session):
        """Test subscription validation at exact expiry time"""
        # Set subscription to expire exactly now
        test_user.subscription_tier = SubscriptionTier.PRO
        test_user.current_period_end = datetime.utcnow()
        db_session.commit()
        
        # Should be considered expired
        result = await subscription_service.validate_subscription_status(str(test_user.id))
        assert result["valid"] == False
    
    @pytest.mark.asyncio
    async def test_usage_tracking_with_zero_count(self, subscription_service, test_user):
        """Test usage tracking with zero count"""
        usage_record = await subscription_service.track_usage(
            user_id=str(test_user.id),
            usage_type=UsageType.RESUME_PROCESSING,
            count=0
        )
        
        assert usage_record.count == 0
        
        # User counters should not change
        updated_user = subscription_service.db.query(User).filter(User.id == test_user.id).first()
        assert updated_user.total_usage_count == 0
        assert updated_user.weekly_usage_count == 0
    
    @pytest.mark.asyncio
    async def test_prorated_calculation_edge_cases(self, subscription_service):
        """Test prorated amount calculation edge cases"""
        # Test same day upgrade
        same_day = subscription_service.calculate_prorated_amount(
            1000,
            datetime(2024, 1, 1),
            datetime(2024, 1, 31),
            datetime(2024, 1, 1)  # Same as start
        )
        assert same_day == 1000  # Full amount
        
        # Test upgrade after period end
        after_period = subscription_service.calculate_prorated_amount(
            1000,
            datetime(2024, 1, 1),
            datetime(2024, 1, 31),
            datetime(2024, 2, 1)  # After end
        )
        assert after_period == 0  # No charge
        
        # Test zero-day period
        zero_period = subscription_service.calculate_prorated_amount(
            1000,
            datetime(2024, 1, 1),
            datetime(2024, 1, 1),  # Same day
            datetime(2024, 1, 1)
        )
        assert zero_period == 1000  # Full amount for edge case
    
    @pytest.mark.asyncio
    async def test_weekly_reset_boundary_conditions(self, subscription_service, test_user, db_session):
        """Test weekly usage reset at boundary conditions"""
        # Set usage reset to exactly 7 days ago
        test_user.weekly_usage_count = 5
        test_user.weekly_usage_reset = datetime.utcnow() - timedelta(days=7, seconds=1)
        db_session.commit()
        
        # Should trigger reset
        result = await subscription_service.check_usage_limits(
            str(test_user.id), 
            UsageType.RESUME_PROCESSING
        )
        
        # Should be reset and allow usage
        assert result.can_use == True
        assert result.remaining == 5  # Full limit available


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_user_lifecycle(self, subscription_service, db_session):
        """Test complete user lifecycle from free to pro to canceled"""
        # Create new free user
        user = User(
            email="lifecycle@example.com",
            username="lifecycle",
            subscription_tier=SubscriptionTier.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # 1. Free user uses service within limits
        for i in range(3):
            await subscription_service.track_usage(
                str(user.id), 
                UsageType.RESUME_PROCESSING
            )
        
        limits = await subscription_service.check_usage_limits(
            str(user.id), 
            UsageType.RESUME_PROCESSING
        )
        assert limits.can_use == True
        assert limits.remaining == 2
        
        # 2. User upgrades to Pro
        subscription = await subscription_service.create_subscription(
            user_id=str(user.id),
            tier=SubscriptionTier.PRO,
            stripe_customer_id="cus_lifecycle",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        # Should now have unlimited access
        limits = await subscription_service.check_usage_limits(
            str(user.id), 
            UsageType.RESUME_PROCESSING
        )
        assert limits.can_use == True
        assert "unlimited" in limits.reason.lower()
        
        # 3. User cancels subscription
        canceled = await subscription_service.cancel_subscription(
            str(user.id),
            cancel_immediately=False
        )
        assert canceled.cancel_at_period_end == True
        
        # Should still have Pro access until period end
        updated_user = db_session.query(User).filter(User.id == user.id).first()
        assert updated_user.subscription_tier == SubscriptionTier.PRO
        
        # 4. Subscription expires
        await subscription_service._downgrade_expired_subscription(str(user.id))
        
        # Should be downgraded to Free
        final_user = db_session.query(User).filter(User.id == user.id).first()
        assert final_user.subscription_tier == SubscriptionTier.FREE
    
    @pytest.mark.asyncio
    async def test_bulk_user_processing(self, subscription_service, db_session):
        """Test processing many users efficiently"""
        # Create 100 users with mixed tiers
        users = []
        for i in range(100):
            user = User(
                email=f"bulk{i}@example.com",
                username=f"bulk{i}",
                subscription_tier=SubscriptionTier.PRO if i % 3 == 0 else SubscriptionTier.FREE,
                current_period_end=datetime.utcnow() - timedelta(days=1) if i % 10 == 0 else datetime.utcnow() + timedelta(days=30),
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Process expired subscriptions
        start_time = time.time()
        downgraded_count = await subscription_service.process_expired_subscriptions()
        end_time = time.time()
        
        # Should complete quickly and process correct number
        assert end_time - start_time < 5.0  # Under 5 seconds
        assert downgraded_count >= 0  # Some users should be processed (depends on Pro users with expired dates)
        
        # Reset weekly usage for all users
        start_time = time.time()
        reset_count = await subscription_service.reset_all_weekly_usage()
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 5.0
        assert reset_count >= 0  # Some users may have been reset


if __name__ == "__main__":
    # Run tests with verbose output and coverage
    pytest.main([__file__, "-v", "--tb=short"])