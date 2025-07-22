"""
Feature Gate Middleware - Access control based on subscription status

This middleware handles:
- Subscription status validation before request processing
- Pro-only endpoint protection
- Usage limit enforcement for Free users
- Automatic usage tracking after successful requests
- Proper error responses for subscription violations
- Bypass logic for admin users and testing
"""

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, List, Set
import logging
import json
import os
import re

from config.database import get_db
from models.user import User, SubscriptionTier, SubscriptionStatus, UsageType
from services.subscription_service import SubscriptionService, UsageLimitResult
from utils.auth import AuthManager
# Import SecurityMonitoring with fallback
try:
    from config.security import SecurityMonitoring
except ImportError:
    # Fallback for testing environment
    class SecurityMonitoring:
        @staticmethod
        def log_security_event(event_type: str, details: dict, severity: str = "info"):
            import logging
            logger = logging.getLogger("security")
            getattr(logger, severity.lower())(f"{event_type}: {details}")

logger = logging.getLogger(__name__)


class FeatureGateMiddleware(BaseHTTPMiddleware):
    """Middleware to control access to features based on subscription status"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Define Pro-only endpoints (patterns)
        self.pro_only_endpoints = {
            # Bulk processing endpoints
            r"/api/batch/.*",
            
            # Advanced formatting endpoints
            r"/api/resumes/advanced-format.*",
            r"/api/resumes/premium-templates.*",
            
            # Premium cover letter endpoints
            r"/api/resumes/premium-cover-letter.*",
            r"/api/cover-letters/premium.*",
            
            # Analytics endpoints
            r"/api/analytics/.*",
            r"/api/dashboard/analytics.*",
            
            # Heavy tailoring mode (handled in request body)
            # This will be checked in the request processing
        }
        
        # Define endpoints that count towards usage limits
        self.usage_tracked_endpoints = {
            r"/api/resumes/tailor": UsageType.RESUME_PROCESSING,
            r"/api/resumes/generate-resumes": UsageType.RESUME_PROCESSING,
            r"/api/batch/process": UsageType.BULK_PROCESSING,
            r"/api/resumes/cover-letter": UsageType.COVER_LETTER,
            r"/api/cover-letters/generate": UsageType.COVER_LETTER,
        }
        
        # Define endpoints that bypass feature gates (health checks, auth, etc.)
        self.bypass_endpoints = {
            r"/health.*",
            r"/api/auth/.*",
            r"/api/webhooks/.*",
            r"/docs.*",
            r"/redoc.*",
            r"/openapi\.json",
            r"/static/.*",
            r"/outputs/.*",
        }
        
        # Admin bypass patterns (for testing and admin access)
        self.admin_bypass_patterns = {
            r"/api/admin/.*",
        }
        
        # Compile regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        self.pro_only_compiled = [re.compile(pattern) for pattern in self.pro_only_endpoints]
        self.usage_tracked_compiled = [(re.compile(pattern), usage_type) 
                                     for pattern, usage_type in self.usage_tracked_endpoints.items()]
        self.bypass_compiled = [re.compile(pattern) for pattern in self.bypass_endpoints]
        self.admin_bypass_compiled = [re.compile(pattern) for pattern in self.admin_bypass_patterns]
    
    async def dispatch(self, request: Request, call_next):
        """Main middleware dispatch method"""
        try:
            # Check if endpoint should bypass feature gates
            if self._should_bypass_feature_gate(request):
                return await call_next(request)
            
            # Get current user (if authenticated)
            user = await self._get_current_user(request)
            
            # If no user and endpoint requires authentication, let auth middleware handle it
            if not user and self._requires_authentication(request):
                return await call_next(request)
            
            # Check admin bypass
            if user and self._is_admin_bypass(request, user):
                response = await call_next(request)
                # Still track usage for admin users for analytics
                if response.status_code == 200:
                    await self._track_usage_if_needed(request, user)
                return response
            
            # Check Pro-only endpoint access
            if self._is_pro_only_endpoint(request):
                if not user:
                    return self._create_auth_required_response()
                
                if not user.is_pro_active():
                    return self._create_pro_required_response(request.url.path)
            
            # Check usage limits for Free users
            if user and not user.is_pro_active():
                usage_check = await self._check_usage_limits(request, user)
                if not usage_check.can_use:
                    return self._create_usage_limit_response(usage_check, request.url.path)
            
            # Check tailoring mode restrictions in request body
            if user and not user.is_pro_active():
                tailoring_check = await self._check_tailoring_mode_restriction(request)
                if tailoring_check:
                    return tailoring_check
            
            # Process the request
            response = await call_next(request)
            
            # Track usage after successful request
            if response.status_code == 200 and user:
                await self._track_usage_if_needed(request, user)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in FeatureGateMiddleware: {e}")
            # Log security event for middleware errors
            SecurityMonitoring.log_security_event(
                "feature_gate_error",
                {
                    "error": str(e),
                    "endpoint": str(request.url),
                    "method": request.method,
                    "ip": request.client.host if request.client else "unknown"
                },
                "error"
            )
            # Continue processing - don't block requests due to middleware errors
            return await call_next(request)
    
    def _should_bypass_feature_gate(self, request: Request) -> bool:
        """Check if request should bypass feature gate checks"""
        path = request.url.path
        return any(pattern.match(path) for pattern in self.bypass_compiled)
    
    def _requires_authentication(self, request: Request) -> bool:
        """Check if endpoint requires authentication"""
        # Most API endpoints require authentication except public ones
        path = request.url.path
        public_paths = ["/health", "/", "/docs", "/redoc", "/openapi.json"]
        return path.startswith("/api/") and path not in public_paths
    
    def _is_admin_bypass(self, request: Request, user: User) -> bool:
        """Check if request should bypass checks for admin users"""
        path = request.url.path
        
        # Check admin endpoint patterns
        if any(pattern.match(path) for pattern in self.admin_bypass_compiled):
            return True
        
        # Check if user is admin (you can customize this logic)
        # For now, check if user has admin role or is in testing mode
        if hasattr(user, 'role') and str(user.role).lower() == 'admin':
            return True
        
        # Check testing environment bypass
        if os.getenv("ENVIRONMENT") == "testing" and os.getenv("BYPASS_FEATURE_GATES") == "true":
            return True
        
        return False
    
    def _is_pro_only_endpoint(self, request: Request) -> bool:
        """Check if endpoint requires Pro subscription"""
        path = request.url.path
        return any(pattern.match(path) for pattern in self.pro_only_compiled)
    
    async def _get_current_user(self, request: Request) -> Optional[User]:
        """Extract current user from request"""
        try:
            # Check for Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            # Get database session
            db = next(get_db())
            
            try:
                # Use AuthManager to verify token and get user
                from fastapi.security import HTTPAuthorizationCredentials
                credentials = HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=auth_header.split(" ")[1]
                )
                
                user = AuthManager.verify_token(credentials, db)
                return user
                
            except Exception as e:
                logger.debug(f"Token verification failed: {e}")
                return None
            finally:
                db.close()
                
        except Exception as e:
            logger.debug(f"Error getting current user: {e}")
            return None
    
    async def _check_usage_limits(self, request: Request, user: User) -> UsageLimitResult:
        """Check usage limits for the current request"""
        try:
            # Get database session
            db = next(get_db())
            
            try:
                subscription_service = SubscriptionService(db)
                
                # Determine usage type for this endpoint
                usage_type = self._get_usage_type_for_endpoint(request)
                if not usage_type:
                    return UsageLimitResult(True, "No usage limits for this endpoint")
                
                # Check usage limits
                return await subscription_service.check_usage_limits(str(user.id), usage_type)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error checking usage limits: {e}")
            # Default to allowing access if check fails
            return UsageLimitResult(True, "Usage check failed - allowing access")
    
    def _get_usage_type_for_endpoint(self, request: Request) -> Optional[UsageType]:
        """Get usage type for the current endpoint"""
        path = request.url.path
        
        for pattern, usage_type in self.usage_tracked_compiled:
            if pattern.match(path):
                return usage_type
        
        return None
    
    async def _check_tailoring_mode_restriction(self, request: Request) -> Optional[Response]:
        """Check if request contains restricted tailoring mode for Free users"""
        try:
            # Only check for resume processing endpoints
            if not any(pattern.match(request.url.path) for pattern, _ in self.usage_tracked_compiled):
                return None
            
            # Check if request has body
            if request.method not in ["POST", "PUT", "PATCH"]:
                return None
            
            # Try to read request body to check for tailoring mode
            # Note: This is a simplified check - in production you might want to
            # parse the body more carefully or check specific endpoints
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')
                    if 'tailoring_mode' in body_str.lower() and 'heavy' in body_str.lower():
                        return self._create_pro_required_response(
                            request.url.path,
                            "Heavy tailoring mode requires Pro subscription"
                        )
            except Exception:
                # If we can't read the body, don't block the request
                pass
            
            return None
            
        except Exception as e:
            logger.debug(f"Error checking tailoring mode restriction: {e}")
            return None
    
    async def _track_usage_if_needed(self, request: Request, user: User):
        """Track usage for successful requests"""
        try:
            usage_type = self._get_usage_type_for_endpoint(request)
            if not usage_type:
                return
            
            # Get database session
            db = next(get_db())
            
            try:
                subscription_service = SubscriptionService(db)
                
                # Track the usage
                await subscription_service.track_usage(
                    user_id=str(user.id),
                    usage_type=usage_type,
                    count=1,
                    extra_data=json.dumps({
                        "endpoint": request.url.path,
                        "method": request.method,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                )
                
                logger.info(f"Tracked usage for user {user.id}: {usage_type.value}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            # Don't fail the request if usage tracking fails
    
    def _create_auth_required_response(self) -> JSONResponse:
        """Create response for authentication required"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "authentication_required",
                "message": "Authentication required to access this feature",
                "code": 401
            }
        )
    
    def _create_pro_required_response(self, endpoint: str, custom_message: str = None) -> JSONResponse:
        """Create response for Pro subscription required"""
        message = custom_message or "This feature requires a Pro subscription"
        
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={
                "error": "subscription_required",
                "message": message,
                "code": 402,
                "upgrade_url": "/upgrade",
                "current_tier": "free",
                "endpoint": endpoint,
                "features": {
                    "bulk_processing": "Process up to 10 jobs simultaneously",
                    "advanced_formatting": "Custom fonts, colors, and layouts",
                    "premium_templates": "Access to premium resume templates",
                    "cover_letters": "AI-generated cover letters",
                    "analytics": "Resume performance analytics",
                    "heavy_tailoring": "Comprehensive resume restructuring"
                }
            }
        )
    
    def _create_usage_limit_response(self, usage_check: UsageLimitResult, endpoint: str) -> JSONResponse:
        """Create response for usage limit exceeded"""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "usage_limit_exceeded",
                "message": usage_check.reason,
                "code": 429,
                "limit": usage_check.limit,
                "remaining": usage_check.remaining,
                "endpoint": endpoint,
                "upgrade_url": "/upgrade",
                "reset_info": "Usage limits reset weekly for Free users",
                "pro_benefits": {
                    "unlimited_sessions": "No weekly limits",
                    "bulk_processing": "Process multiple jobs at once",
                    "priority_support": "Faster processing and support"
                }
            }
        )


# Utility functions for manual feature gate checks in route handlers

async def require_pro_subscription(user: User) -> None:
    """Utility function to require Pro subscription in route handlers"""
    if not user.is_pro_active():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "subscription_required",
                "message": "This feature requires a Pro subscription",
                "upgrade_url": "/upgrade"
            }
        )


async def check_usage_limit(user: User, usage_type: UsageType, db: Session) -> None:
    """Utility function to check usage limits in route handlers"""
    if user.is_pro_active():
        return  # Pro users have unlimited access
    
    subscription_service = SubscriptionService(db)
    usage_check = await subscription_service.check_usage_limits(str(user.id), usage_type)
    
    if not usage_check.can_use:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "usage_limit_exceeded",
                "message": usage_check.reason,
                "limit": usage_check.limit,
                "remaining": usage_check.remaining,
                "upgrade_url": "/upgrade"
            }
        )


async def track_usage(user: User, usage_type: UsageType, db: Session, count: int = 1) -> None:
    """Utility function to track usage in route handlers"""
    try:
        subscription_service = SubscriptionService(db)
        await subscription_service.track_usage(
            user_id=str(user.id),
            usage_type=usage_type,
            count=count
        )
    except Exception as e:
        logger.error(f"Error tracking usage: {e}")
        # Don't fail the request if usage tracking fails


def get_user_feature_access(user: User) -> Dict[str, bool]:
    """Get user's feature access permissions"""
    if user.is_pro_active():
        return {
            "bulk_processing": True,
            "advanced_formatting": True,
            "premium_templates": True,
            "cover_letters": True,
            "analytics": True,
            "heavy_tailoring": True,
            "unlimited_sessions": True
        }
    else:
        return {
            "bulk_processing": False,
            "advanced_formatting": False,
            "premium_templates": False,
            "cover_letters": False,
            "analytics": False,
            "heavy_tailoring": False,
            "unlimited_sessions": False
        }


def setup_feature_gate_middleware(app):
    """Setup feature gate middleware for the application"""
    app.add_middleware(FeatureGateMiddleware)
    logger.info("Feature gate middleware configured successfully")