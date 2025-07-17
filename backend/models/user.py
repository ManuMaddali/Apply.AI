from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
import enum

Base = declarative_base()

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

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    
    # Role and subscription
    role = Column(Enum(UserRole), default=UserRole.FREE)
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    
    # Authentication provider
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.EMAIL)
    provider_id = Column(String(255), nullable=True)  # External provider user ID
    
    # Usage tracking
    resumes_generated = Column(Integer, default=0)
    jobs_processed = Column(Integer, default=0)
    last_login = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, self.hashed_password)
    
    def is_premium(self) -> bool:
        """Check if user has premium access"""
        return self.role == UserRole.PRO
    
    def is_subscription_active(self) -> bool:
        """Check if subscription is active"""
        if not self.subscription_end:
            return False
        return datetime.utcnow() <= self.subscription_end
    
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
            "subscription_start": self.subscription_start.isoformat() if self.subscription_start else None,
            "subscription_end": self.subscription_end.isoformat() if self.subscription_end else None,
            "resumes_generated": self.resumes_generated,
            "jobs_processed": self.jobs_processed,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "usage_limits": self.get_usage_limits(),
            "can_generate_resume": self.can_generate_resume(),
            "is_premium": self.is_premium(),
            "is_subscription_active": self.is_subscription_active()
        }

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
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