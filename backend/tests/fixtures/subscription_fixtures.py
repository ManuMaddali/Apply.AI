"""
Test Fixtures for Subscription System

Provides reusable test data and scenarios for subscription testing.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from models.user import (
    User, Subscription, PaymentHistory, UsageTracking,
    SubscriptionTier, SubscriptionStatus, PaymentStatus, UsageType,
    TailoringMode, AuthProvider
)


class SubscriptionTestFixtures:
    """Factory class for creating test subscription scenarios"""
    
    @staticmethod
    def create_free_user(
        db_session: Session,
        email: str = "free@example.com",
        username: str = "freeuser",
        weekly_usage: int = 0
    ) -> User:
        """Create a Free tier user"""
        user = User(
            email=email,
            username=username,
            full_name=f"Free User {username}",
            subscription_tier=SubscriptionTier.FREE,
            subscription_status=SubscriptionStatus.ACTIVE,
            weekly_usage_count=weekly_usage,
            weekly_usage_reset=datetime.utcnow(),
            total_usage_count=weekly_usage,
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
    
    @staticmethod
    def create_pro_user(
        db_session: Session,
        email: str = "pro@example.com",
        username: str = "prouser",
        days_remaining: int = 30,
        stripe_customer_id: str = "cus_pro123",
        stripe_subscription_id: str = "sub_pro123"
    ) -> User:
        """Create a Pro tier user"""
        user = User(
            email=email,
            username=username,
            full_name=f"Pro User {username}",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            stripe_customer_id=stripe_customer_id,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=days_remaining),
            cancel_at_period_end=False,
            preferred_tailoring_mode=TailoringMode.LIGHT,
            auth_provider=AuthProvider.EMAIL,
            is_active=True,
            is_verified=True,
            email_verified=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Create subscription record
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id,
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=user.current_period_start,
            current_period_end=user.current_period_end,
            cancel_at_period_end=False
        )
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @staticmethod
    def create_expired_pro_user(
        db_session: Session,
        email: str = "expired@example.com",
        username: str = "expireduser",
        days_expired: int = 1
    ) -> User:
        """Create an expired Pro user"""
        user = User(
            email=email,
            username=username,
            full_name=f"Expired Pro User {username}",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            stripe_customer_id="cus_expired123",
            current_period_start=datetime.utcnow() - timedelta(days=30),
            current_period_end=datetime.utcnow() - timedelta(days=days_expired),
            cancel_at_period_end=False,
            auth_provider=AuthProvider.EMAIL,
            is_active=True,
            is_verified=True,
            email_verified=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Create expired subscription record
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_expired123",
            stripe_customer_id="cus_expired123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE,  # Will be updated by service
            current_period_start=user.current_period_start,
            current_period_end=user.current_period_end,
            cancel_at_period_end=False
        )
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @staticmethod
    def create_canceled_pro_user(
        db_session: Session,
        email: str = "canceled@example.com",
        username: str = "canceleduser",
        days_until_end: int = 15
    ) -> User:
        """Create a Pro user with canceled subscription (access until period end)"""
        user = User(
            email=email,
            username=username,
            full_name=f"Canceled Pro User {username}",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            stripe_customer_id="cus_canceled123",
            current_period_start=datetime.utcnow() - timedelta(days=15),
            current_period_end=datetime.utcnow() + timedelta(days=days_until_end),
            cancel_at_period_end=True,
            auth_provider=AuthProvider.EMAIL,
            is_active=True,
            is_verified=True,
            email_verified=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Create canceled subscription record
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_canceled123",
            stripe_customer_id="cus_canceled123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=user.current_period_start,
            current_period_end=user.current_period_end,
            cancel_at_period_end=True
        )
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @staticmethod
    def create_past_due_user(
        db_session: Session,
        email: str = "pastdue@example.com",
        username: str = "pastdueuser",
        days_past_due: int = 2
    ) -> User:
        """Create a Pro user with past due payment"""
        user = User(
            email=email,
            username=username,
            full_name=f"Past Due User {username}",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.PAST_DUE,
            stripe_customer_id="cus_pastdue123",
            current_period_start=datetime.utcnow() - timedelta(days=30),
            current_period_end=datetime.utcnow() - timedelta(days=days_past_due),
            cancel_at_period_end=False,
            auth_provider=AuthProvider.EMAIL,
            is_active=True,
            is_verified=True,
            email_verified=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Create past due subscription record
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_pastdue123",
            stripe_customer_id="cus_pastdue123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.PAST_DUE,
            current_period_start=user.current_period_start,
            current_period_end=user.current_period_end,
            cancel_at_period_end=False
        )
        db_session.add(subscription)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @staticmethod
    def create_usage_records(
        db_session: Session,
        user: User,
        usage_scenarios: List[Dict]
    ) -> List[UsageTracking]:
        """Create usage tracking records for a user
        
        Args:
            usage_scenarios: List of dicts with keys:
                - usage_type: UsageType
                - count: int
                - days_ago: int (optional, default 0)
                - session_id: str (optional)
                - extra_data: str (optional)
        """
        usage_records = []
        
        for scenario in usage_scenarios:
            usage_date = datetime.utcnow() - timedelta(days=scenario.get('days_ago', 0))
            
            record = UsageTracking(
                user_id=user.id,
                usage_type=scenario['usage_type'],
                count=scenario['count'],
                usage_date=usage_date,
                session_id=scenario.get('session_id'),
                extra_data=scenario.get('extra_data'),
                created_at=usage_date
            )
            usage_records.append(record)
        
        db_session.add_all(usage_records)
        
        # Update user counters
        total_usage = sum(r.count for r in usage_records)
        weekly_usage = sum(
            r.count for r in usage_records 
            if r.usage_date >= datetime.utcnow() - timedelta(days=7)
        )
        
        user.total_usage_count = (user.total_usage_count or 0) + total_usage
        user.weekly_usage_count = (user.weekly_usage_count or 0) + weekly_usage
        
        db_session.commit()
        return usage_records
    
    @staticmethod
    def create_payment_history(
        db_session: Session,
        user: User,
        payment_scenarios: List[Dict]
    ) -> List[PaymentHistory]:
        """Create payment history records for a user
        
        Args:
            payment_scenarios: List of dicts with keys:
                - amount: int (in cents)
                - status: PaymentStatus
                - days_ago: int (optional, default 0)
                - stripe_payment_intent_id: str (optional)
                - description: str (optional)
        """
        payment_records = []
        
        for scenario in payment_scenarios:
            payment_date = datetime.utcnow() - timedelta(days=scenario.get('days_ago', 0))
            
            record = PaymentHistory(
                user_id=user.id,
                stripe_payment_intent_id=scenario.get('stripe_payment_intent_id', f"pi_test_{len(payment_records)}"),
                amount=scenario['amount'],
                currency='usd',
                status=scenario['status'],
                description=scenario.get('description', f"Payment {scenario['status'].value}"),
                created_at=payment_date
            )
            payment_records.append(record)
        
        db_session.add_all(payment_records)
        db_session.commit()
        return payment_records


class SubscriptionScenarios:
    """Pre-defined subscription test scenarios"""
    
    @staticmethod
    def free_user_at_limit(db_session: Session) -> User:
        """Free user at weekly usage limit"""
        user = SubscriptionTestFixtures.create_free_user(
            db_session, 
            email="atlimit@example.com",
            username="atlimituser",
            weekly_usage=5
        )
        
        # Add usage records
        SubscriptionTestFixtures.create_usage_records(
            db_session, 
            user,
            [
                {'usage_type': UsageType.RESUME_PROCESSING, 'count': 1, 'days_ago': 6},
                {'usage_type': UsageType.RESUME_PROCESSING, 'count': 2, 'days_ago': 4},
                {'usage_type': UsageType.RESUME_PROCESSING, 'count': 2, 'days_ago': 1},
            ]
        )
        
        return user
    
    @staticmethod
    def free_user_near_limit(db_session: Session) -> User:
        """Free user near weekly usage limit"""
        user = SubscriptionTestFixtures.create_free_user(
            db_session,
            email="nearlimit@example.com", 
            username="nearlimituser",
            weekly_usage=4
        )
        
        SubscriptionTestFixtures.create_usage_records(
            db_session,
            user,
            [
                {'usage_type': UsageType.RESUME_PROCESSING, 'count': 2, 'days_ago': 3},
                {'usage_type': UsageType.RESUME_PROCESSING, 'count': 2, 'days_ago': 1},
            ]
        )
        
        return user
    
    @staticmethod
    def pro_user_heavy_usage(db_session: Session) -> User:
        """Pro user with heavy usage across all features"""
        user = SubscriptionTestFixtures.create_pro_user(
            db_session,
            email="heavyuser@example.com",
            username="heavyuser"
        )
        
        SubscriptionTestFixtures.create_usage_records(
            db_session,
            user,
            [
                {'usage_type': UsageType.RESUME_PROCESSING, 'count': 15, 'days_ago': 7},
                {'usage_type': UsageType.BULK_PROCESSING, 'count': 5, 'days_ago': 5},
                {'usage_type': UsageType.COVER_LETTER, 'count': 8, 'days_ago': 3},
                {'usage_type': UsageType.RESUME_PROCESSING, 'count': 10, 'days_ago': 1},
            ]
        )
        
        return user
    
    @staticmethod
    def pro_user_with_payment_history(db_session: Session) -> User:
        """Pro user with successful payment history"""
        user = SubscriptionTestFixtures.create_pro_user(
            db_session,
            email="paymenthistory@example.com",
            username="paymenthistoryuser"
        )
        
        SubscriptionTestFixtures.create_payment_history(
            db_session,
            user,
            [
                {
                    'amount': 999,
                    'status': PaymentStatus.SUCCEEDED,
                    'days_ago': 30,
                    'description': 'Pro subscription - January 2024'
                },
                {
                    'amount': 999,
                    'status': PaymentStatus.SUCCEEDED,
                    'days_ago': 0,
                    'description': 'Pro subscription - February 2024'
                }
            ]
        )
        
        return user
    
    @staticmethod
    def pro_user_with_failed_payments(db_session: Session) -> User:
        """Pro user with failed payment attempts"""
        user = SubscriptionTestFixtures.create_pro_user(
            db_session,
            email="failedpayments@example.com",
            username="failedpaymentsuser"
        )
        
        SubscriptionTestFixtures.create_payment_history(
            db_session,
            user,
            [
                {
                    'amount': 999,
                    'status': PaymentStatus.SUCCEEDED,
                    'days_ago': 60,
                    'description': 'Pro subscription - December 2023'
                },
                {
                    'amount': 999,
                    'status': PaymentStatus.FAILED,
                    'days_ago': 30,
                    'description': 'Failed payment - Card declined'
                },
                {
                    'amount': 999,
                    'status': PaymentStatus.FAILED,
                    'days_ago': 29,
                    'description': 'Failed payment retry - Insufficient funds'
                },
                {
                    'amount': 999,
                    'status': PaymentStatus.SUCCEEDED,
                    'days_ago': 28,
                    'description': 'Pro subscription - January 2024 (retry successful)'
                }
            ]
        )
        
        return user
    
    @staticmethod
    def mixed_user_cohort(db_session: Session) -> Dict[str, List[User]]:
        """Create a mixed cohort of users for analytics testing"""
        cohort = {
            'free_users': [],
            'pro_users': [],
            'expired_users': [],
            'canceled_users': []
        }
        
        # Create 10 free users with varying usage
        for i in range(10):
            user = SubscriptionTestFixtures.create_free_user(
                db_session,
                email=f"free{i}@example.com",
                username=f"free{i}",
                weekly_usage=i % 6  # 0-5 usage
            )
            cohort['free_users'].append(user)
        
        # Create 5 active pro users
        for i in range(5):
            user = SubscriptionTestFixtures.create_pro_user(
                db_session,
                email=f"pro{i}@example.com",
                username=f"pro{i}",
                days_remaining=30 - (i * 5)  # Varying renewal dates
            )
            cohort['pro_users'].append(user)
        
        # Create 3 expired users
        for i in range(3):
            user = SubscriptionTestFixtures.create_expired_pro_user(
                db_session,
                email=f"expired{i}@example.com",
                username=f"expired{i}",
                days_expired=i + 1
            )
            cohort['expired_users'].append(user)
        
        # Create 2 canceled users
        for i in range(2):
            user = SubscriptionTestFixtures.create_canceled_pro_user(
                db_session,
                email=f"canceled{i}@example.com",
                username=f"canceled{i}",
                days_until_end=15 - (i * 5)
            )
            cohort['canceled_users'].append(user)
        
        return cohort


# Pytest fixtures for easy use in tests
@pytest.fixture
def free_user(db_session):
    """Fixture for a basic free user"""
    return SubscriptionTestFixtures.create_free_user(db_session)


@pytest.fixture
def pro_user(db_session):
    """Fixture for a basic pro user"""
    return SubscriptionTestFixtures.create_pro_user(db_session)


@pytest.fixture
def expired_pro_user(db_session):
    """Fixture for an expired pro user"""
    return SubscriptionTestFixtures.create_expired_pro_user(db_session)


@pytest.fixture
def free_user_at_limit(db_session):
    """Fixture for a free user at usage limit"""
    return SubscriptionScenarios.free_user_at_limit(db_session)


@pytest.fixture
def pro_user_heavy_usage(db_session):
    """Fixture for a pro user with heavy usage"""
    return SubscriptionScenarios.pro_user_heavy_usage(db_session)


@pytest.fixture
def mixed_user_cohort(db_session):
    """Fixture for a mixed cohort of users"""
    return SubscriptionScenarios.mixed_user_cohort(db_session)