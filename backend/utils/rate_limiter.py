from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from typing import Optional
from datetime import datetime

# Rate limiting configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEFAULT_LIMITS = ["200 per day", "50 per hour"]

# Initialize limiter with fallback to in-memory storage if Redis is not available
def create_limiter():
    # Always use in-memory storage for development to avoid Redis dependency
    if os.getenv("ENVIRONMENT", "development") == "development":
        print("🔄 Using in-memory rate limiting for development")
        return Limiter(
            key_func=get_remote_address,
            storage_uri="memory://",
            default_limits=DEFAULT_LIMITS
        )
    
    # Try Redis for production
    try:
        import redis
        # Test Redis connection first
        r = redis.Redis.from_url(REDIS_URL)
        r.ping()  # This will raise an exception if Redis is not available
        
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=REDIS_URL,
            default_limits=DEFAULT_LIMITS
        )
        print("✅ Rate limiting with Redis backend enabled")
        return limiter
    except Exception as e:
        # Fallback to in-memory rate limiting
        print(f"⚠️  Redis not available, using in-memory rate limiting: {e}")
        return Limiter(
            key_func=get_remote_address,
            storage_uri="memory://",
            default_limits=DEFAULT_LIMITS
        )

limiter = create_limiter()

# Custom rate limit key functions
def get_user_id_from_request(request: Request) -> str:
    """Extract user ID from JWT token for authenticated rate limiting"""
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from jose import jwt
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
            return payload.get("sub", get_remote_address(request))
    except Exception:
        pass
    return get_remote_address(request)

def get_api_key_from_request(request: Request) -> str:
    """Extract API key for API-based rate limiting"""
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    return get_remote_address(request)

# Rate limit configurations for different endpoints
class RateLimits:
    # File upload limits
    FILE_UPLOAD = "3/minute"
    
    # AI processing limits
    AI_PROCESSING = "10/minute"
    
    # Batch processing limits
    BATCH_PROCESSING = "2/minute"
    
    # Authentication limits
    AUTH_LOGIN = "5/minute"
    
    # General API limits
    API_GENERAL = "100/hour"
    
    # Job scraping limits
    JOB_SCRAPING = "20/minute"

# Security monitoring for rate limiting
class RateLimitMonitor:
    @staticmethod
    def log_rate_limit_hit(request: Request, endpoint: str):
        """Log rate limit violations for security monitoring"""
        import logging
        import json
        
        security_event = {
            "timestamp": str(datetime.utcnow()),
            "event_type": "rate_limit_exceeded",
            "endpoint": endpoint,
            "ip_address": get_remote_address(request),
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "severity": "warning"
        }
        
        logging.getLogger("security").warning(json.dumps(security_event))

# Custom rate limit exception handler
def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors"""
    RateLimitMonitor.log_rate_limit_hit(request, str(request.url))
    
    # Calculate retry_after based on available attributes or use default
    retry_after = getattr(exc, 'retry_after', None)
    if retry_after is None:
        # Default retry time if not available
        retry_after = 60  # 1 minute default
    
    response = {
        "error": "Rate limit exceeded",
        "message": f"You have exceeded the rate limit. Try again in {retry_after} seconds.",
        "retry_after": retry_after
    }
    
    return HTTPException(
        status_code=429,
        detail=response,
        headers={"Retry-After": str(retry_after)}
    )

# Rate limiting decorators for common use cases
def rate_limit_file_upload(limiter_instance: Limiter):
    """Rate limit for file upload endpoints"""
    return limiter_instance.limit(RateLimits.FILE_UPLOAD, key_func=get_user_id_from_request)

def rate_limit_ai_processing(limiter_instance: Limiter):
    """Rate limit for AI processing endpoints"""
    return limiter_instance.limit(RateLimits.AI_PROCESSING, key_func=get_user_id_from_request)

def rate_limit_batch_processing(limiter_instance: Limiter):
    """Rate limit for batch processing endpoints"""
    return limiter_instance.limit(RateLimits.BATCH_PROCESSING, key_func=get_user_id_from_request) 