from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os
from typing import List

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "media-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Remove server header for security (if present)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response

class RequestSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize incoming requests for security"""
    
    async def dispatch(self, request: Request, call_next):
        # Log suspicious requests
        await self._log_suspicious_activity(request)
        
        # Continue processing
        response = await call_next(request)
        return response
    
    async def _log_suspicious_activity(self, request: Request):
        """Log potentially suspicious request patterns"""
        import logging
        import json
        from datetime import datetime
        
        suspicious_patterns = [
            "script>", "javascript:", "vbscript:", "onload=", "onerror=",
            "../", "..\\", "passwd", "shadow", "etc/passwd",
            "cmd.exe", "powershell", "bash", "/bin/",
            "union select", "drop table", "insert into",
            "base64", "eval(", "exec(", "system("
        ]
        
        # Check URL path
        url_path = str(request.url).lower()
        
        # Check headers
        user_agent = request.headers.get("User-Agent", "").lower()
        
        # Check for suspicious patterns
        for pattern in suspicious_patterns:
            if pattern in url_path or pattern in user_agent:
                security_event = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": "suspicious_request",
                    "ip_address": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("User-Agent", "Unknown"),
                    "url": str(request.url),
                    "method": request.method,
                    "pattern_matched": pattern,
                    "severity": "high"
                }
                
                logging.getLogger("security").warning(json.dumps(security_event))
                break

def get_allowed_origins() -> List[str]:
    """Get allowed origins from environment"""
    origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in origins_str.split(",")]
    
    # Add development origins if in development
    if os.getenv("ENVIRONMENT", "development") == "development":
        dev_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001"
        ]
        origins.extend(dev_origins)
    
    return list(set(origins))  # Remove duplicates

def get_trusted_hosts() -> List[str]:
    """Get trusted hosts from environment"""
    hosts_str = os.getenv("TRUSTED_HOSTS", "localhost")
    hosts = [host.strip() for host in hosts_str.split(",")]
    
    # Add development hosts if in development
    if os.getenv("ENVIRONMENT", "development") == "development":
        dev_hosts = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0"
        ]
        hosts.extend(dev_hosts)
    
    return list(set(hosts))  # Remove duplicates

def setup_security_middleware(app: FastAPI):
    """Configure all security middleware for the application"""
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"],
        max_age=86400,  # 24 hours
    )
    
    # Trusted hosts middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=get_trusted_hosts()
    )
    
    # Request sanitization middleware
    app.add_middleware(RequestSanitizationMiddleware)
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

# Health check endpoint security
def setup_health_check_security(app: FastAPI):
    """Setup security for health check endpoints"""
    
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint"""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/health/detailed")
    async def detailed_health_check():
        """Detailed health check - should be protected in production"""
        import psutil
        import sys
        
        # Only show detailed info in development
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                    "python_version": sys.version
                }
            }
        else:
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Security configuration validation
def validate_security_config():
    """Validate security configuration on startup"""
    import sys
    
    required_env_vars = [
        "JWT_SECRET_KEY",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Validate JWT secret key length
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if len(jwt_secret) < 32:
        print("❌ JWT_SECRET_KEY must be at least 32 characters long")
        sys.exit(1)
    
    # Validate OpenAI API key format
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key.startswith("sk-"):
        print("❌ OPENAI_API_KEY must start with 'sk-'")
        sys.exit(1)
    
    print("✅ Security configuration validated successfully") 