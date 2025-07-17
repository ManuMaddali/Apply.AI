from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from typing import Optional
from sqlalchemy.orm import Session

from config.database import get_db
from models.user import User, UserSession

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secure-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthManager:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            session_id: str = payload.get("session_id")
            
            print(f"🔍 Token validation - User ID: {user_id}, Session ID: {session_id}")
            
            if user_id is None:
                print("❌ Token validation failed: No user ID in token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Convert string user_id back to UUID for database query
            try:
                import uuid
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                print(f"❌ Invalid UUID format: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify user exists and is active
            user = db.query(User).filter(User.id == user_uuid).first()
            if not user or not user.is_active:
                print(f"❌ User validation failed - User found: {user is not None}, Active: {user.is_active if user else 'N/A'}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or inactive user",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            print(f"✅ User validation passed - Email: {user.email}")
            
            # Verify session if session_id is provided
            if session_id:
                # Convert string session_id back to UUID for database query
                try:
                    session_uuid = uuid.UUID(session_id)
                except ValueError:
                    print(f"❌ Invalid session UUID format: {session_id}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid session format",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                session = db.query(UserSession).filter(
                    UserSession.id == session_uuid,
                    UserSession.user_id == user_uuid,
                    UserSession.is_active == True
                ).first()
                
                print(f"🔍 Session lookup - Found: {session is not None}")
                if session:
                    print(f"🔍 Session details - Active: {session.is_active}, Expires: {session.expires_at}, Now: {datetime.utcnow()}")
                    print(f"🔍 Session expired check: {session.is_expired()}")
                
                if not session:
                    print("❌ Session validation failed: Session not found")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                if session.is_expired():
                    print("❌ Session validation failed: Session expired")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session expired",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                print("✅ Session validation passed")
                
                # Update last activity
                session.last_activity = datetime.utcnow()
                db.commit()
            
            return user
            
        except JWTError as e:
            print(f"❌ JWT Error: {str(e)}")
            print(f"❌ Token received: {credentials.credentials[:50]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Usage in routes
def get_current_user(user: User = Depends(AuthManager.verify_token)):
    """Get current authenticated user"""
    return user

def require_premium_user(user: User = Depends(get_current_user)):
    """Require premium user for certain endpoints"""
    if not user.is_premium():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return user

def require_verified_user(user: User = Depends(get_current_user)):
    """Require verified user for certain endpoints"""
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return user

def check_usage_limits(user: User, action: str = "resume_generation"):
    """Check if user can perform action based on usage limits"""
    if action == "resume_generation":
        if not user.can_generate_resume():
            limits = user.get_usage_limits()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly resume generation limit reached ({limits['resumes_per_month']}). Please upgrade to Pro plan."
            )
    return True

# Backward compatibility for existing code
def authenticate_user(email: str, password: str, db: Session):
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user 