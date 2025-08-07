from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from passlib.context import CryptContext
from typing import Optional, Dict, Any, List

# Type: ignore SQLAlchemy type annotation issues
# mypy: ignore-errors
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
import enum

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

class Base(DeclarativeBase):
    pass

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(enum.Enum):
    FREE = "free"
    PRO = "pro"

class AuthProvider(enum.Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"

# Subscription-related enums
class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"

class TailoringMode(enum.Enum):
    LIGHT = "light"
    HEAVY = "heavy"

class UsageType(enum.Enum):
    RESUME_PROCESSING = "resume_processing"
    COVER_LETTER = "cover_letter"
    BULK_PROCESSING = "bulk_processing"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"

class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for social auth users
    
    # Profile information
    profile_image = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Role and subscription (legacy fields - keeping for backward compatibility)
    role = Column(Enum(UserRole), default=UserRole.FREE)
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    
    # Enhanced subscription fields
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    subscription_status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Usage tracking - enhanced
    weekly_usage_count = Column(Integer, default=0)
    weekly_usage_reset = Column(DateTime, default=func.now())
    total_usage_count = Column(Integer, default=0)
    resumes_generated = Column(Integer, default=0)  # Legacy field
    jobs_processed = Column(Integer, default=0)     # Legacy field
    last_login = Column(DateTime, nullable=True)
    
    # Feature preferences (Pro only)
    preferred_tailoring_mode = Column(Enum(TailoringMode), default=TailoringMode.LIGHT)
    
    # Authentication provider
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.EMAIL)
    provider_id = Column(String(255), nullable=True)  # External provider user ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    usage_tracking = relationship("UsageTracking", back_populates="user", cascade="all, delete-orphan")
    payment_history = relationship("PaymentHistory", back_populates="user", cascade="all, delete-orphan")
    uploaded_files = relationship("FileMetadata", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, str(self.hashed_password))
    
    def is_premium(self) -> bool:
        """Check if user has premium access (legacy method)"""
        return self.role == UserRole.PRO or self.is_pro_active()
    
    def is_subscription_active(self) -> bool:
        """Check if subscription is active (legacy method)"""
        if not self.subscription_end:
            return self.is_pro_active()
        return datetime.utcnow() <= self.subscription_end
    
    def is_pro_active(self) -> bool:
        """Check if user has active Pro subscription"""
        if self.subscription_tier == SubscriptionTier.PRO:
            if self.subscription_status == SubscriptionStatus.ACTIVE:
                if self.current_period_end:
                    return datetime.utcnow() <= self.current_period_end
                return True
        return False
    
    def get_active_subscription(self):
        """Get the user's active subscription"""
        for subscription in self.subscriptions:
            if subscription.is_active():
                return subscription
        return None
    
    def reset_weekly_usage(self):
        """Reset weekly usage counter"""
        self.weekly_usage_count = 0
        self.weekly_usage_reset = datetime.utcnow()
    
    def should_reset_weekly_usage(self) -> bool:
        """Check if weekly usage should be reset"""
        if not self.weekly_usage_reset:
            return True
        days_since_reset = (datetime.utcnow() - self.weekly_usage_reset).days
        return days_since_reset >= 7
    
    def can_use_feature(self, feature: str) -> bool:
        """Check if user can use a specific feature"""
        if self.is_pro_active():
            return True
        
        # Free tier limitations
        free_features = {
            "resume_processing": True,
            "cover_letter": False,
            "bulk_processing": False,
            "advanced_formatting": False,
            "analytics": False,
            "heavy_tailoring": False
        }
        
        return free_features.get(feature, False)
    
    def get_usage_limits_new(self) -> dict:
        """Get usage limits based on subscription tier - matches README specifications"""
        if self.is_pro_active():
            return {
                "weekly_sessions": -1,  # Unlimited resume processing
                "bulk_jobs": 25,        # Up to 25 jobs in batch mode
                "cover_letters": True,
                "advanced_formatting": True,
                "analytics": True,
                "heavy_tailoring": True
            }
        else:
            return {
                "weekly_sessions": 3,   # 3 tailored resumes per week
                "bulk_jobs": 10,        # Up to 10 jobs in batch mode
                "cover_letters": False,
                "advanced_formatting": False,
                "analytics": False,
                "heavy_tailoring": False
            }
    
    def can_process_resume(self) -> bool:
        """Check if user can process more resumes"""
        if self.is_pro_active():
            return True
        
        # Check weekly usage for Free users
        if self.should_reset_weekly_usage():
            self.reset_weekly_usage()
        
        limits = self.get_usage_limits_new()
        return self.weekly_usage_count < limits["weekly_sessions"]
    
    def get_usage_limits(self) -> dict:
        """Get usage limits based on user role"""
        limits = {
            UserRole.FREE: {
                "resumes_per_month": 3,
                "jobs_per_batch": 3,
                "cover_letters": False,
                "advanced_ai": False,
                "priority_support": False
            },
            UserRole.PRO: {
                "resumes_per_month": -1,  # Unlimited
                "jobs_per_batch": 25,
                "cover_letters": True,
                "advanced_ai": True,
                "priority_support": True
            }
        }
        return limits.get(self.role, limits[UserRole.FREE])
    
    def can_generate_resume(self) -> bool:
        """Check if user can generate more resumes"""
        limits = self.get_usage_limits()
        if limits["resumes_per_month"] == -1:
            return True
        
        # Check monthly usage (simplified - you might want to implement proper monthly tracking)
        return self.resumes_generated < limits["resumes_per_month"]
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "profile_image": self.profile_image,
            "phone": self.phone,
            "location": self.location,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "email_verified": self.email_verified,
            "role": self.role.value,
            "auth_provider": self.auth_provider.value,
            
            # Legacy subscription fields
            "subscription_start": self.subscription_start.isoformat() if self.subscription_start else None,
            "subscription_end": self.subscription_end.isoformat() if self.subscription_end else None,
            
            # Enhanced subscription fields
            "subscription_tier": self.subscription_tier.value,
            "subscription_status": self.subscription_status.value,
            "stripe_customer_id": self.stripe_customer_id,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "cancel_at_period_end": self.cancel_at_period_end,
            
            # Usage tracking
            "weekly_usage_count": self.weekly_usage_count,
            "weekly_usage_reset": self.weekly_usage_reset.isoformat() if self.weekly_usage_reset else None,
            "total_usage_count": self.total_usage_count,
            "resumes_generated": self.resumes_generated,
            "jobs_processed": self.jobs_processed,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            
            # Feature preferences
            "preferred_tailoring_mode": self.preferred_tailoring_mode.value,
            
            # Timestamps
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            
            # Computed fields
            "usage_limits": self.get_usage_limits_new(),
            "legacy_usage_limits": self.get_usage_limits(),  # Keep for backward compatibility
            "can_generate_resume": self.can_generate_resume(),
            "can_process_resume": self.can_process_resume(),
            "is_premium": self.is_premium(),
            "is_subscription_active": self.is_subscription_active(),
            "is_pro_active": self.is_pro_active(),
            "active_subscription": self.get_active_subscription().to_dict() if self.get_active_subscription() else None
        }

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True, index=True)
    
    # Session metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_type = Column(String(50), nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, minutes: int = 30):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(minutes=minutes)
        self.last_activity = func.now()

class PasswordReset(Base):
    __tablename__ = "password_resets"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    reset_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Reset status
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="password_resets")
    
    def is_expired(self) -> bool:
        """Check if reset token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if reset token is valid"""
        return not self.is_used and not self.is_expired()

# Email verification tokens
class EmailVerification(Base):
    __tablename__ = "email_verifications"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    verification_token = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)  # Email being verified
    
    # Verification status
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime, nullable=True)
    
    def is_expired(self) -> bool:
        """Check if verification token is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if verification token is valid"""
        return not self.is_verified and not self.is_expired() 

# Subscription model
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_customer_id = Column(String(255), nullable=False, index=True)
    
    # Subscription details
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    tier = Column(Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    
    # Billing period
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    
    # Stripe metadata
    stripe_price_id = Column(String(255), nullable=True)
    stripe_product_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.current_period_end and datetime.utcnow() > self.current_period_end:
            return False
        return True
    
    def is_pro(self) -> bool:
        """Check if this is a Pro subscription"""
        return self.tier == SubscriptionTier.PRO and self.is_active()
    
    def days_until_renewal(self) -> int:
        """Get days until next renewal"""
        if not self.current_period_end:
            return 0
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    def to_dict(self) -> dict:
        """Convert subscription to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "stripe_subscription_id": self.stripe_subscription_id,
            "status": self.status.value,
            "tier": self.tier.value,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "cancel_at_period_end": self.cancel_at_period_end,
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "is_active": self.is_active(),
            "is_pro": self.is_pro(),
            "days_until_renewal": self.days_until_renewal(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Usage tracking model
class UsageTracking(Base):
    __tablename__ = "usage_tracking"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Usage details
    usage_type = Column(Enum(UsageType), nullable=False)
    usage_date = Column(DateTime, nullable=False, default=func.now(), index=True)
    count = Column(Integer, nullable=False, default=1)
    
    # Additional metadata
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    session_id = Column(String(255), nullable=True)  # Optional session tracking
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="usage_tracking")
    
    def to_dict(self) -> dict:
        """Convert usage tracking to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "usage_type": self.usage_type.value,
            "usage_date": self.usage_date.isoformat(),
            "count": self.count,
            "extra_data": self.extra_data,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat()
        }

# Payment history model
class PaymentHistory(Base):
    __tablename__ = "payment_history"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Stripe payment details
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_invoice_id = Column(String(255), nullable=True, index=True)
    stripe_charge_id = Column(String(255), nullable=True, index=True)
    
    # Payment details
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), nullable=False, default="usd")
    status = Column(Enum(PaymentStatus), nullable=False)
    
    # Payment metadata
    description = Column(Text, nullable=True)
    payment_method_type = Column(String(50), nullable=True)  # card, bank_transfer, etc.
    failure_reason = Column(String(255), nullable=True)
    
    # Timestamps
    payment_date = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payment_history")
    
    def amount_in_dollars(self) -> float:
        """Get amount in dollars (from cents)"""
        return self.amount / 100.0
    
    def is_successful(self) -> bool:
        """Check if payment was successful"""
        return self.status == PaymentStatus.SUCCEEDED
    
    def to_dict(self) -> dict:
        """Convert payment history to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "stripe_payment_intent_id": self.stripe_payment_intent_id,
            "stripe_invoice_id": self.stripe_invoice_id,
            "amount": self.amount,
            "amount_dollars": self.amount_in_dollars(),
            "currency": self.currency,
            "status": self.status.value,
            "description": self.description,
            "payment_method_type": self.payment_method_type,
            "failure_reason": self.failure_reason,
            "payment_date": self.payment_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }