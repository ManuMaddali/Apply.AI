from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import secrets
import re

from config.database import get_db, DatabaseManager
from models.user import User, UserSession, PasswordReset, EmailVerification, UserRole, AuthProvider
from utils.auth import AuthManager
from utils.rate_limiter import limiter, RateLimits

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Pydantic models for request/response
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not v or len(v) < 5:
            raise ValueError('Valid email address required')
        return v.lower()

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class SocialAuthRequest(BaseModel):
    provider: str
    access_token: str
    provider_id: str
    email: EmailStr
    full_name: Optional[str] = None
    profile_image: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None

# Helper functions
def get_client_info(request: Request) -> Dict[str, str]:
    """Extract client information from request"""
    return {
        "user_agent": request.headers.get("user-agent", "Unknown"),
        "ip_address": request.client.host if request.client else "Unknown",
        "device_type": "web"  # Could be enhanced to detect mobile/desktop
    }

def create_user_session(user: User, request: Request, remember_me: bool = False) -> UserSession:
    """Create a new user session"""
    client_info = get_client_info(request)
    
    # Generate session tokens
    session_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32) if remember_me else None
    
    # Set expiration time
    expires_in = timedelta(days=30) if remember_me else timedelta(hours=24)
    expires_at = datetime.utcnow() + expires_in
    
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        refresh_token=refresh_token,
        user_agent=client_info["user_agent"],
        ip_address=client_info["ip_address"],
        device_type=client_info["device_type"],
        expires_at=expires_at
    )
    
    return session

def send_verification_email(user: User, verification_token: str):
    """Send email verification email"""
    from utils.email_service import get_email_service
    
    email_service = get_email_service()
    success = email_service.send_verification_email(
        user_email=user.email,
        user_name=user.full_name,
        verification_token=verification_token
    )
    
    if not success:
        print(f"❌ Failed to send verification email to {user.email}")
    else:
        print(f"✅ Verification email sent to {user.email}")
    
def send_password_reset_email(user: User, reset_token: str):
    """Send password reset email"""
    from utils.email_service import get_email_service
    
    email_service = get_email_service()
    success = email_service.send_password_reset_email(
        user_email=user.email,
        user_name=user.full_name,
        reset_token=reset_token
    )
    
    if not success:
        print(f"❌ Failed to send password reset email to {user.email}")
    else:
        print(f"✅ Password reset email sent to {user.email}")

# Authentication endpoints
@router.post("/register", response_model=AuthResponse)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def register(request: Request, user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Check username availability if provided
        if user_data.username:
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            role=UserRole.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        user.set_password(user_data.password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create email verification token
        verification_token = secrets.token_urlsafe(32)
        verification = EmailVerification(
            user_id=user.id,
            verification_token=verification_token,
            email=user.email,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(verification)
        db.commit()
        
        # Send verification email
        send_verification_email(user, verification_token)
        
        return AuthResponse(
            success=True,
            message="Account created successfully. Please check your email to verify your account.",
            user=user.to_dict()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login(request: Request, login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    try:
        # Find user by email (case-insensitive)
        # Convert email to lowercase for case-insensitive comparison
        normalized_email = login_data.email.lower()
        user = db.query(User).filter(User.email.ilike(normalized_email)).first()
        if not user or not user.verify_password(login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Check if email is verified (only for email auth users)
        if user.auth_provider == AuthProvider.EMAIL and not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email address before logging in"
            )
        
        # Create session
        session = create_user_session(user, request, login_data.remember_me)
        db.add(session)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "session_id": str(session.id)
        }
        access_token = AuthManager.create_access_token(token_data)
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user=user.to_dict(),
            access_token=access_token,
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/social-login", response_model=AuthResponse)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def social_login(request: Request, social_data: SocialAuthRequest, db: Session = Depends(get_db)):
    """Login or register with social provider"""
    try:
        # Map provider names to enum values
        provider_map = {
            "google": AuthProvider.GOOGLE,
            "github": AuthProvider.GITHUB,
            "microsoft": AuthProvider.MICROSOFT
        }
        
        provider = provider_map.get(social_data.provider.lower())
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported social provider"
            )
        
        # Verify the access token with the provider
        from utils.social_auth import get_social_auth_service
        social_auth_service = get_social_auth_service()
        
        verified_user_data = await social_auth_service.verify_social_token(
            provider=social_data.provider,
            access_token=social_data.access_token
        )
        
        if not verified_user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid social authentication token"
            )
        
        # Use verified data instead of client-provided data
        email = verified_user_data.get('email')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required for social authentication"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Update existing user's social info if needed
            if user.auth_provider != provider:
                user.auth_provider = provider
                user.provider_id = verified_user_data.get('provider_id')
            
            # Update profile image if not set
            if verified_user_data.get('profile_image') and not user.profile_image:
                user.profile_image = verified_user_data.get('profile_image')
            
            # Update name if not set
            if verified_user_data.get('full_name') and not user.full_name:
                user.full_name = verified_user_data.get('full_name')
                
        else:
            # Create new user
            user = User(
                email=email,
                full_name=verified_user_data.get('full_name'),
                profile_image=verified_user_data.get('profile_image'),
                auth_provider=provider,
                provider_id=verified_user_data.get('provider_id'),
                role=UserRole.FREE,
                email_verified=verified_user_data.get('email_verified', True),
                is_verified=True
            )
            db.add(user)
        
        # Create session
        session = create_user_session(user, request, True)  # Social logins are "remember me" by default
        db.add(session)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "session_id": str(session.id)
        }
        access_token = AuthManager.create_access_token(token_data)
        
        return AuthResponse(
            success=True,
            message="Social login successful",
            user=user.to_dict(),
            access_token=access_token,
            expires_in=1800  # 30 minutes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Social login failed: {str(e)}"
        )

@router.post("/logout")
async def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Logout user and invalidate session"""
    try:
        # Decode token to get session info
        from jose import jwt
        from utils.auth import SECRET_KEY, ALGORITHM
        
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        session_id = payload.get("session_id")
        
        if session_id:
            # Invalidate session
            session = db.query(UserSession).filter(UserSession.id == session_id).first()
            if session:
                session.is_active = False
                db.commit()
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        return {"success": True, "message": "Logged out successfully"}  # Always return success for logout

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, reset_data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    try:
        user = db.query(User).filter(User.email == reset_data.email).first()
        if not user:
            # Don't reveal if email exists
            return {"success": True, "message": "If the email exists, you will receive reset instructions"}
        
        # Create reset token
        reset_token = secrets.token_urlsafe(32)
        password_reset = PasswordReset(
            user_id=user.id,
            reset_token=reset_token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(password_reset)
        db.commit()
        
        # Send reset email
        send_password_reset_email(user, reset_token)
        
        return {"success": True, "message": "If the email exists, you will receive reset instructions"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(request: Request, reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    try:
        # Find valid reset token
        password_reset = db.query(PasswordReset).filter(
            PasswordReset.reset_token == reset_data.token,
            PasswordReset.is_used == False
        ).first()
        
        if not password_reset or password_reset.is_expired():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update user password
        user = db.query(User).filter(User.id == password_reset.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.set_password(reset_data.new_password)
        
        # Mark reset token as used
        password_reset.is_used = True
        password_reset.used_at = datetime.utcnow()
        
        # Invalidate all existing sessions
        db.query(UserSession).filter(UserSession.user_id == user.id).update({
            "is_active": False
        })
        
        db.commit()
        
        return {"success": True, "message": "Password reset successful"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.post("/verify-email")
@limiter.limit("5/minute")
async def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    """Verify email address"""
    try:
        # Find verification token
        verification = db.query(EmailVerification).filter(
            EmailVerification.verification_token == token,
            EmailVerification.is_verified == False
        ).first()
        
        if not verification or verification.is_expired():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Update user verification status
        user = db.query(User).filter(User.id == verification.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.email_verified = True
        user.is_verified = True
        
        # Mark verification as complete
        verification.is_verified = True
        verification.verified_at = datetime.utcnow()
        
        db.commit()
        
        return {"success": True, "message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )

@router.post("/resend-verification")
@limiter.limit("3/minute")
async def resend_verification(request: Request, email_data: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Resend email verification"""
    try:
        user = db.query(User).filter(User.email == email_data.email).first()
        if not user:
            return {"success": True, "message": "If the email exists, verification email will be sent"}
        
        if user.email_verified:
            return {"success": True, "message": "Email is already verified"}
        
        # Create new verification token
        verification_token = secrets.token_urlsafe(32)
        verification = EmailVerification(
            user_id=user.id,
            verification_token=verification_token,
            email=user.email,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(verification)
        db.commit()
        
        # Send verification email
        send_verification_email(user, verification_token)
        
        return {"success": True, "message": "Verification email sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

@router.get("/me")
async def get_current_user(request: Request, user: User = Depends(AuthManager.verify_token)):
    """Get current user information"""
    return {"success": True, "user": user.to_dict()}

@router.get("/sessions")
async def get_user_sessions(request: Request, user: User = Depends(AuthManager.verify_token), db: Session = Depends(get_db)):
    """Get user's active sessions"""
    # Get active sessions
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True
    ).all()
    
    session_data = []
    for session in sessions:
        session_data.append({
            "id": str(session.id),
            "user_agent": session.user_agent,
            "ip_address": session.ip_address,
            "device_type": session.device_type,
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "created_at": session.created_at.isoformat()
        })
    
    return {"success": True, "sessions": session_data}

@router.delete("/sessions/{session_id}")
async def revoke_session(request: Request, session_id: str, user: User = Depends(AuthManager.verify_token), db: Session = Depends(get_db)):
    """Revoke a specific session"""
    # Find and revoke session
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.is_active = False
    db.commit()
    
    return {"success": True, "message": "Session revoked successfully"}

@router.get("/oauth/urls")
async def get_oauth_urls(request: Request):
    """Get OAuth URLs for social authentication"""
    try:
        from utils.social_auth import get_social_auth_service
        social_auth_service = get_social_auth_service()
        
        urls = social_auth_service.get_oauth_urls()
        
        return {
            "success": True,
            "urls": urls,
            "message": "OAuth URLs retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth URLs: {str(e)}"
        )

class OAuthCallbackRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None

@router.post("/oauth/callback/{provider}")
async def oauth_callback(request: Request, provider: str, callback_data: OAuthCallbackRequest, db: Session = Depends(get_db)):
    """Handle OAuth callback from social providers"""
    try:
        from utils.social_auth import get_social_auth_service
        
        # Validate provider
        supported_providers = ['google', 'github']
        if provider.lower() not in supported_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider"
            )
        
        social_auth_service = get_social_auth_service()
        
        # Use the redirect URI provided by the frontend if available
        # Otherwise, fall back to constructing it from CORS origins
        redirect_uri = callback_data.redirect_uri
        if not redirect_uri:
            frontend_url = social_auth_service.settings.get_cors_origins()[0] if social_auth_service.settings.get_cors_origins() else "http://localhost:3000"
            redirect_uri = f"{frontend_url}/auth/callback/{provider}"
        
        print(f"Using redirect URI: {redirect_uri}")
        print(f"Provider: {provider}")
        print(f"Code: {callback_data.code[:10]}...")  # Print first 10 chars of code for debugging
        
        # Debug OAuth settings
        if provider.lower() == 'google':
            print(f"Google Client ID: {social_auth_service.settings.google_client_id[:10]}...")
            print(f"Google Client Secret: {social_auth_service.settings.google_client_secret[:5]}...")
        elif provider.lower() == 'github':
            print(f"GitHub Client ID: {social_auth_service.settings.github_client_id}")
            print(f"GitHub Client Secret: {social_auth_service.settings.github_client_secret[:5]}...")
        
        access_token = await social_auth_service.exchange_code_for_token(
            provider=provider,
            code=callback_data.code,
            redirect_uri=redirect_uri
        )
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for access token"
            )
        
        # Verify token and get user data
        print(f"Verifying {provider} token...")
        verified_user_data = await social_auth_service.verify_social_token(
            provider=provider,
            access_token=access_token
        )
        
        if not verified_user_data:
            print(f"Failed to verify {provider} token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid {provider} access token"
            )
            
        print(f"Successfully verified {provider} token")
        print(f"User data: {verified_user_data}")
        
        # Check if user exists
        email = verified_user_data.get('email')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required for social authentication"
            )
        
        # Map provider to enum
        provider_map = {
            "google": AuthProvider.GOOGLE,
            "github": AuthProvider.GITHUB
        }
        
        auth_provider = provider_map.get(provider.lower())
        user = db.query(User).filter(User.email == email).first()
        

        
        if user:
            # Update existing user
            user.last_login = datetime.utcnow()
            
            if user.auth_provider != auth_provider:
                user.auth_provider = auth_provider
                user.provider_id = verified_user_data.get('provider_id')
            
            if verified_user_data.get('profile_image') and not user.profile_image:
                user.profile_image = verified_user_data.get('profile_image')
            
            if verified_user_data.get('full_name') and not user.full_name:
                user.full_name = verified_user_data.get('full_name')
        else:
            # Create new user with last_login already set
            user = User(
                email=email,
                full_name=verified_user_data.get('full_name'),
                profile_image=verified_user_data.get('profile_image'),
                auth_provider=auth_provider,
                provider_id=verified_user_data.get('provider_id'),
                role=UserRole.FREE,
                email_verified=verified_user_data.get('email_verified', True),
                is_verified=True,
                is_active=True,
                last_login=datetime.utcnow()  # Set last_login on creation
            )
            db.add(user)
        
        # Create session
        session = create_user_session(user, request, True)
        db.add(session)
        
        # Commit everything
        db.commit()
        db.refresh(user)
        db.refresh(session)
        
        # Create JWT token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "session_id": str(session.id)
        }
        access_token = AuthManager.create_access_token(token_data)
        
        return AuthResponse(
            success=True,
            message="OAuth authentication successful",
            user=user.to_dict(),
            access_token=access_token,
            expires_in=1800
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        ) 