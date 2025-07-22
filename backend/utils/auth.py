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
from config.security import get_security_settings

def get_secret_key():
    """Get the JWT secret key from settings"""
    settings = get_security_settings()
    return settings.jwt_secret_key

SECRET_KEY = get_secret_key()
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
            
            if user_id is None:
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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify user exists and is active
            user = db.query(User).filter(User.id == user_uuid).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or inactive user",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify session if session_id is provided
            if session_id:
                # Convert string session_id back to UUID for database query
                try:
                    session_uuid = uuid.UUID(session_id)
                except ValueError:
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
                
                if not session:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                if session.is_expired():
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session expired",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Update last activity
                session.last_activity = datetime.utcnow()
                db.commit()
            
            return user
            
        except JWTError as e:
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

def require_admin_access(user: User):
    """Require admin access for admin-only endpoints"""
    # Check if user is admin (you can implement this based on your admin logic)
    # For now, we'll check if the user email is in admin list or has admin role
    admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
    admin_emails = [email.strip() for email in admin_emails if email.strip()]
    
    # Check if user email is in admin list
    if user.email not in admin_emails:
        # Alternative: check for admin role if you have role-based system
        # if not hasattr(user, 'is_admin') or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user

async def require_admin(token: str = Depends(security)) -> User:
    """Dependency to require admin access"""
    user = await get_current_user(token)
    return require_admin_access(user)

# Backward compatibility for existing code
def authenticate_user(email: str, password: str, db: Session):
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user 