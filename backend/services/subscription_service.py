"""
Subscription Service - Core subscription management logic

This service handles all subscription-related operations including:
- CRUD operations for subscriptions
- Usage limit checking and enforcement
- Usage tracking and reset functionality
- Subscription status validation
- Automatic tier downgrade logic
- Helper methods for subscription date calculations
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging
from enum import Enum

from models.user import (
    User, Subscription, UsageTracking, PaymentHistory,
    SubscriptionTier, SubscriptionStatus, UsageType, TailoringMode
)

logger = logging.getLogger(__name__)


class UsageLimitResult:
    """Result object for usage limit checks"""
    def __init__(self, can_use: bool, reason: str = "", remaining: int = 0, limit: int = 0):
        self.can_use = can_use
        self.reason = reason
        self.remaining = remaining
        self.limit = limit
        
    def to_dict(self) -> Dict:
        return {
            "can_use": self.can_use,
            "reason": self.reason,
            "remaining": self.remaining,
            "limit": self.limit
        }


class SubscriptionService:
    """Core subscription service for managing user subscriptions and usage"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
    # CRUD Operations for Subscriptions
    
    async def create_subscription(
        self, 
        user_id: str, 
        tier: SubscriptionTier,
        stripe_subscription_id: Optional[str] = None,
        stripe_customer_id: Optional[str] = None,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None
    ) -> Subscription:
        """Create a new subscription for a user"""
        try:
            # Check if user already has an active subscription
            existing_subscription = self.get_active_subscription(user_id)
            if existing_subscription:
                logger.warning(f"User {user_id} already has an active subscription")
                raise ValueError("User already has an active subscription")
            
            # Create new subscription
            subscription = Subscription(
                user_id=user_id,
                tier=tier,
                status=SubscriptionStatus.ACTIVE,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=stripe_customer_id,
                current_period_start=current_period_start or datetime.utcnow(),
                current_period_end=current_period_end
            )
            
            self.db.add(subscription)
            
            # Update user's subscription fields
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.subscription_tier = tier
                user.subscription_status = SubscriptionStatus.ACTIVE
                user.stripe_customer_id = stripe_customer_id
                user.current_period_start = current_period_start or datetime.utcnow()
                user.current_period_end = current_period_end
                
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Created subscription for user {user_id} with tier {tier.value}")
            return subscription
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating subscription for user {user_id}: {e}")
            raise
    
    async def update_subscription(
        self,
        subscription_id: str,
        status: Optional[SubscriptionStatus] = None,
        tier: Optional[SubscriptionTier] = None,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        cancel_at_period_end: Optional[bool] = None
    ) -> Optional[Subscription]:
        """Update an existing subscription"""
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            
            if not subscription:
                logger.warning(f"Subscription {subscription_id} not found")
                return None
            
            # Update subscription fields
            if status is not None:
                subscription.status = status
            if tier is not None:
                subscription.tier = tier
            if current_period_start is not None:
                subscription.current_period_start = current_period_start
            if current_period_end is not None:
                subscription.current_period_end = current_period_end
            if cancel_at_period_end is not None:
                subscription.cancel_at_period_end = cancel_at_period_end
                
            # Update user's subscription fields to match
            user = self.db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                if status is not None:
                    user.subscription_status = status
                if tier is not None:
                    user.subscription_tier = tier
                if current_period_start is not None:
                    user.current_period_start = current_period_start
                if current_period_end is not None:
                    user.current_period_end = current_period_end
                if cancel_at_period_end is not None:
                    user.cancel_at_period_end = cancel_at_period_end
            
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Updated subscription {subscription_id}")
            return subscription
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating subscription {subscription_id}: {e}")
            raise
    
    async def cancel_subscription(
        self,
        user_id: str,
        cancel_immediately: bool = False
    ) -> Optional[Subscription]:
        """Cancel a user's subscription"""
        try:
            subscription = self.get_active_subscription(user_id)
            if not subscription:
                logger.warning(f"No active subscription found for user {user_id}")
                return None
            
            if cancel_immediately:
                # Cancel immediately
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.utcnow()
                subscription.current_period_end = datetime.utcnow()
                
                # Downgrade user to Free tier
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    user.subscription_tier = SubscriptionTier.FREE
                    user.subscription_status = SubscriptionStatus.CANCELED
                    user.current_period_end = datetime.utcnow()
            else:
                # Cancel at period end
                subscription.cancel_at_period_end = True
                
                # Update user record
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    user.cancel_at_period_end = True
            
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Canceled subscription for user {user_id} (immediate: {cancel_immediately})")
            return subscription
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error canceling subscription for user {user_id}: {e}")
            raise
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID"""
        return self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
    
    def get_active_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's active subscription"""
        return self.db.query(Subscription).filter(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        ).first()
    
    def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Get all subscriptions for a user"""
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).order_by(Subscription.created_at.desc()).all()
    
    # Usage Limit Checking and Enforcement
    
    async def check_usage_limits(self, user_id: str, usage_type: UsageType) -> UsageLimitResult:
        """Check if user can perform the requested action based on usage limits"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return UsageLimitResult(False, "User not found")
            
            # Pro users have unlimited access
            if user.is_pro_active():
                return UsageLimitResult(True, "Pro user - unlimited access")
            
            # Free users have weekly limits
            if usage_type == UsageType.RESUME_PROCESSING:
                return await self._check_weekly_resume_limit(user)
            elif usage_type == UsageType.BULK_PROCESSING:
                return UsageLimitResult(False, "Bulk processing requires Pro subscription")
            elif usage_type == UsageType.COVER_LETTER:
                return UsageLimitResult(False, "Cover letters require Pro subscription")
            else:
                return UsageLimitResult(True, "No limits for this usage type")
                
        except Exception as e:
            logger.error(f"Error checking usage limits for user {user_id}: {e}")
            return UsageLimitResult(False, f"Error checking limits: {str(e)}")
    
    async def _check_weekly_resume_limit(self, user: User) -> UsageLimitResult:
        """Check weekly resume processing limit for Free users"""
        # Reset weekly usage if needed
        if user.should_reset_weekly_usage():
            await self.reset_weekly_usage(user.id)
            user.reset_weekly_usage()
        
        weekly_limit = 5  # Free users get 5 sessions per week
        current_usage = user.weekly_usage_count
        remaining = max(0, weekly_limit - current_usage)
        
        if current_usage >= weekly_limit:
            return UsageLimitResult(
                False, 
                f"Weekly limit of {weekly_limit} sessions exceeded",
                remaining=0,
                limit=weekly_limit
            )
        
        return UsageLimitResult(
            True,
            f"Within weekly limit ({current_usage}/{weekly_limit})",
            remaining=remaining,
            limit=weekly_limit
        )
    
    async def can_use_feature(self, user_id: str, feature: str) -> bool:
        """Check if user can use a specific feature"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        return user.can_use_feature(feature)
    
    async def get_bulk_processing_limit(self, user_id: str) -> int:
        """Get bulk processing limit for user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0
        
        if user.is_pro_active():
            return 10  # Pro users can process up to 10 jobs at once
        else:
            return 1   # Free users can only process 1 job at a time
    
    # Usage Tracking and Reset Functionality
    
    async def track_usage(
        self,
        user_id: str,
        usage_type: UsageType,
        count: int = 1,
        extra_data: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> UsageTracking:
        """Track user usage"""
        try:
            # Validate count parameter
            if count < 0:
                count = 0  # Don't allow negative usage counts
            elif count > 100:
                count = 100  # Cap extremely large counts
                
            # Create usage tracking record
            usage_record = UsageTracking(
                user_id=user_id,
                usage_type=usage_type,
                count=count,
                extra_data=extra_data,
                session_id=session_id
            )
            
            self.db.add(usage_record)
            
            # Update user's usage counters
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.total_usage_count += count
                
                if usage_type == UsageType.RESUME_PROCESSING:
                    user.weekly_usage_count += count
                    user.resumes_generated += count  # Legacy field
                elif usage_type == UsageType.BULK_PROCESSING:
                    user.jobs_processed += count  # Legacy field
            
            self.db.commit()
            self.db.refresh(usage_record)
            
            logger.info(f"Tracked usage for user {user_id}: {usage_type.value} x{count}")
            return usage_record
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error tracking usage for user {user_id}: {e}")
            raise
    
    async def reset_weekly_usage(self, user_id: str) -> bool:
        """Reset weekly usage counter for a user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.reset_weekly_usage()
            self.db.commit()
            
            logger.info(f"Reset weekly usage for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting weekly usage for user {user_id}: {e}")
            return False
    
    async def reset_all_weekly_usage(self) -> int:
        """Reset weekly usage for all users (scheduled task)"""
        try:
            # Find users whose weekly usage should be reset
            users_to_reset = self.db.query(User).filter(
                or_(
                    User.weekly_usage_reset.is_(None),
                    User.weekly_usage_reset <= datetime.utcnow() - timedelta(days=7)
                )
            ).all()
            
            reset_count = 0
            for user in users_to_reset:
                user.reset_weekly_usage()
                reset_count += 1
            
            self.db.commit()
            
            logger.info(f"Reset weekly usage for {reset_count} users")
            return reset_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting weekly usage for all users: {e}")
            return 0
    
    async def get_usage_statistics(self, user_id: str) -> Dict:
        """Get usage statistics for a user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Get usage by type for current week
            week_start = datetime.utcnow() - timedelta(days=7)
            weekly_usage = self.db.query(
                UsageTracking.usage_type,
                func.sum(UsageTracking.count).label('total')
            ).filter(
                and_(
                    UsageTracking.user_id == user_id,
                    UsageTracking.usage_date >= week_start
                )
            ).group_by(UsageTracking.usage_type).all()
            
            # Get usage by type for current month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_usage = self.db.query(
                UsageTracking.usage_type,
                func.sum(UsageTracking.count).label('total')
            ).filter(
                and_(
                    UsageTracking.user_id == user_id,
                    UsageTracking.usage_date >= month_start
                )
            ).group_by(UsageTracking.usage_type).all()
            
            # Get total usage
            total_usage = self.db.query(
                UsageTracking.usage_type,
                func.sum(UsageTracking.count).label('total')
            ).filter(
                UsageTracking.user_id == user_id
            ).group_by(UsageTracking.usage_type).all()
            
            return {
                "user_id": user_id,
                "subscription_tier": user.subscription_tier.value,
                "is_pro_active": user.is_pro_active(),
                "weekly_usage": {usage.usage_type.value: usage.total for usage in weekly_usage},
                "monthly_usage": {usage.usage_type.value: usage.total for usage in monthly_usage},
                "total_usage": {usage.usage_type.value: usage.total for usage in total_usage},
                "current_limits": user.get_usage_limits_new(),
                "weekly_usage_count": user.weekly_usage_count,
                "weekly_usage_reset": user.weekly_usage_reset.isoformat() if user.weekly_usage_reset else None,
                "total_usage_count": user.total_usage_count
            }
            
        except Exception as e:
            logger.error(f"Error getting usage statistics for user {user_id}: {e}")
            return {}
    
    # Subscription Status Validation
    
    async def validate_subscription_status(self, user_id: str) -> Dict:
        """Validate and return current subscription status"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"valid": False, "reason": "User not found"}
            
            subscription = self.get_active_subscription(user_id)
            
            # Check if subscription is expired
            if user.subscription_tier == SubscriptionTier.PRO:
                if not user.is_pro_active():
                    # Subscription expired, downgrade user
                    await self._downgrade_expired_subscription(user_id)
                    return {
                        "valid": False,
                        "reason": "Subscription expired and user downgraded to Free",
                        "action_taken": "downgraded_to_free"
                    }
            
            return {
                "valid": True,
                "subscription_tier": user.subscription_tier.value,
                "subscription_status": user.subscription_status.value,
                "is_pro_active": user.is_pro_active(),
                "current_period_end": user.current_period_end.isoformat() if user.current_period_end else None,
                "cancel_at_period_end": user.cancel_at_period_end,
                "subscription": subscription.to_dict() if subscription else None
            }
            
        except Exception as e:
            logger.error(f"Error validating subscription status for user {user_id}: {e}")
            return {"valid": False, "reason": f"Validation error: {str(e)}"}
    
    # Automatic Tier Downgrade Logic
    
    async def _downgrade_expired_subscription(self, user_id: str) -> bool:
        """Downgrade user to Free tier when subscription expires"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Update user to Free tier
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_status = SubscriptionStatus.CANCELED
            
            # Update subscription record
            subscription = self.get_active_subscription(user_id)
            if subscription:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Downgraded expired subscription for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error downgrading expired subscription for user {user_id}: {e}")
            return False
    
    async def process_expired_subscriptions(self) -> int:
        """Process all expired subscriptions (scheduled task)"""
        try:
            # Find users with expired Pro subscriptions
            expired_users = self.db.query(User).filter(
                and_(
                    User.subscription_tier == SubscriptionTier.PRO,
                    User.current_period_end < datetime.utcnow(),
                    User.subscription_status == SubscriptionStatus.ACTIVE
                )
            ).all()
            
            downgraded_count = 0
            for user in expired_users:
                if await self._downgrade_expired_subscription(str(user.id)):
                    downgraded_count += 1
            
            logger.info(f"Processed {downgraded_count} expired subscriptions")
            return downgraded_count
            
        except Exception as e:
            logger.error(f"Error processing expired subscriptions: {e}")
            return 0
    
    # Helper Methods for Subscription Date Calculations
    
    def calculate_next_billing_date(self, current_date: datetime, billing_cycle: str = "monthly") -> datetime:
        """Calculate next billing date"""
        if billing_cycle == "monthly":
            # Add one month
            if current_date.month == 12:
                return current_date.replace(year=current_date.year + 1, month=1)
            else:
                return current_date.replace(month=current_date.month + 1)
        elif billing_cycle == "yearly":
            return current_date.replace(year=current_date.year + 1)
        else:
            raise ValueError(f"Unsupported billing cycle: {billing_cycle}")
    
    def calculate_prorated_amount(
        self,
        full_amount: int,
        period_start: datetime,
        period_end: datetime,
        upgrade_date: datetime
    ) -> int:
        """Calculate prorated amount for mid-cycle upgrades"""
        total_days = (period_end - period_start).days
        
        # Handle edge cases
        if total_days <= 0:
            return full_amount
        
        # If upgrade is before period start, charge full amount
        if upgrade_date <= period_start:
            return full_amount
        
        # If upgrade is after period end, no charge
        if upgrade_date >= period_end:
            return 0
        
        remaining_days = (period_end - upgrade_date).days
        prorated_amount = int((remaining_days / total_days) * full_amount)
        return max(0, prorated_amount)
    
    def get_subscription_renewal_date(self, user_id: str) -> Optional[datetime]:
        """Get next renewal date for user's subscription"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.current_period_end:
            return None
        
        return user.current_period_end
    
    def days_until_renewal(self, user_id: str) -> int:
        """Get days until subscription renewal"""
        renewal_date = self.get_subscription_renewal_date(user_id)
        if not renewal_date:
            return 0
        
        delta = renewal_date - datetime.utcnow()
        return max(0, delta.days)
    
    def is_in_grace_period(self, user_id: str, grace_days: int = 3) -> bool:
        """Check if user is in grace period after failed payment"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.subscription_status != SubscriptionStatus.PAST_DUE:
            return False
        
        if not user.current_period_end:
            return False
        
        days_past_due = (datetime.utcnow() - user.current_period_end).days
        return days_past_due <= grace_days
    
    # Subscription Analytics and Reporting
    
    async def get_subscription_metrics(self) -> Dict:
        """Get subscription metrics for admin dashboard"""
        try:
            # Total users by tier
            tier_counts = self.db.query(
                User.subscription_tier,
                func.count(User.id).label('count')
            ).group_by(User.subscription_tier).all()
            
            # Active subscriptions
            active_subscriptions = self.db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).count()
            
            # Canceled subscriptions this month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            canceled_this_month = self.db.query(Subscription).filter(
                and_(
                    Subscription.status == SubscriptionStatus.CANCELED,
                    Subscription.canceled_at >= month_start
                )
            ).count()
            
            # New subscriptions this month
            new_this_month = self.db.query(Subscription).filter(
                Subscription.created_at >= month_start
            ).count()
            
            return {
                "tier_distribution": {tier.subscription_tier.value: tier.count for tier in tier_counts},
                "active_subscriptions": active_subscriptions,
                "canceled_this_month": canceled_this_month,
                "new_subscriptions_this_month": new_this_month,
                "churn_rate": canceled_this_month / max(1, active_subscriptions) * 100,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription metrics: {e}")
            return {}