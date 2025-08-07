import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
import logging

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./applyai.db"  # Default to SQLite for development
)

# Handle PostgreSQL URL format for production
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite settings for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )
else:
    # PostgreSQL settings for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
    )

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models - using the one from models.user
# Base = declarative_base()  # Removed - using DeclarativeBase from models.user instead

# Database dependency for FastAPI
def get_db() -> Generator:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    """Initialize database tables"""
    from models.user import Base
    
    # Import all models to ensure they're registered
    from models.user import (
        User, UserSession, PasswordReset, EmailVerification,
        Subscription, UsageTracking, PaymentHistory
    )
    from models.file_metadata import FileMetadata
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user for development
    if os.getenv("ENVIRONMENT", "development") == "development":
        create_default_users()

def create_default_users():
    """Create default users for development"""
    from models.user import User, UserRole, AuthProvider
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@applyai.com").first()
        if not admin_user:
            # Create admin user
            admin_user = User(
                email="admin@applyai.com",
                username="admin",
                full_name="ApplyAI Admin",
                role=UserRole.PRO,
                auth_provider=AuthProvider.EMAIL,
                is_active=True,
                is_verified=True,
                email_verified=True
            )
            admin_user.set_password("admin123")
            db.add(admin_user)
            
            # Create demo user
            demo_user = db.query(User).filter(User.email == "demo@applyai.com").first()
            if not demo_user:
                demo_user = User(
                    email="demo@applyai.com",
                    username="demo",
                    full_name="Demo User",
                    role=UserRole.FREE,
                    auth_provider=AuthProvider.EMAIL,
                    is_active=True,
                    is_verified=True,
                    email_verified=True
                )
                demo_user.set_password("demo123")
                db.add(demo_user)
            
            db.commit()
            print("✅ Default users created successfully")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating default users: {e}")
    finally:
        db.close()

# Health check for database
def check_database_health():
    """Check database connection health"""
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        return False

# Database utilities
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def get_user_by_email(email: str):
        """Get user by email"""
        from models.user import User
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: str):
        """Get user by ID"""
        from models.user import User
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    @staticmethod
    def create_user(user_data: dict):
        """Create new user"""
        from models.user import User
        db = SessionLocal()
        try:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def update_user(user_id: str, user_data: dict):
        """Update user"""
        from models.user import User
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in user_data.items():
                    setattr(user, key, value)
                db.commit()
                db.refresh(user)
                return user
            return None
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def delete_user(user_id: str):
        """Delete user"""
        from models.user import User
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_active_sessions(user_id: str):
        """Get active sessions for user"""
        from models.user import UserSession
        db = SessionLocal()
        try:
            return db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).all()
        finally:
            db.close()
    
    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions"""
        from models.user import UserSession
        from datetime import datetime
        
        db = SessionLocal()
        try:
            expired_sessions = db.query(UserSession).filter(
                UserSession.expires_at < datetime.utcnow()
            ).all()
            
            for session in expired_sessions:
                session.is_active = False
            
            db.commit()
            return len(expired_sessions)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close() 