import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import sys

class SecuritySettings(BaseSettings):
    """Security configuration settings with validation"""
    
    # API Keys
    openai_api_key: str
    jwt_secret_key: str
    
    # Database & Cache
    database_url: Optional[str] = None
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Security Configuration
    allowed_origins: str = "http://localhost:3000"
    trusted_hosts: str = "localhost"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_per_minute: int = 10
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    
    # File Upload Security
    upload_dir: str = "uploads"
    max_file_age_hours: int = 24
    
    # Authentication
    access_token_expire_minutes: int = 30
    
    # Template Configuration
    template_preview_cache: Optional[str] = "true"
    template_preview_format: Optional[str] = "png"
    max_preview_size: Optional[str] = "1024"
    
    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    email_from: Optional[str] = None
    email_from_name: str = "ApplyAI"
    
    # Social Authentication
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    
    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v):
        if not v:
            raise ValueError('JWT_SECRET_KEY is required')
        if len(v) < 32:
            raise ValueError('JWT secret must be at least 32 characters')
        return v
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v):
        if not v:
            raise ValueError('OPENAI_API_KEY is required')
        if not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format')
        return v
    
    @field_validator('smtp_port')
    @classmethod
    def validate_smtp_port(cls, v):
        if v < 1 or v > 65535:
            raise ValueError('SMTP port must be between 1 and 65535')
        return v
    
    @field_validator('email_from')
    @classmethod
    def validate_email_from(cls, v):
        if v is None:
            return v  # Allow None for development
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format for email_from')
        return v
    

    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        allowed_envs = ['development', 'staging', 'production']
        if v not in allowed_envs:
            raise ValueError(f'Environment must be one of: {", ".join(allowed_envs)}')
        return v
    
    @field_validator('max_file_size')
    @classmethod
    def validate_file_size(cls, v):
        if v > 50 * 1024 * 1024:  # 50MB max
            raise ValueError('Max file size cannot exceed 50MB')
        return v
    
    @field_validator('rate_limit_per_minute')
    @classmethod
    def validate_rate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Rate limit must be between 1 and 1000 requests per minute')
        return v
    
    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v):
        if v is None:
            return v  # Allow None for development
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('Redis URL must start with redis:// or rediss://')
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_prefix": "",
    }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins with environment-specific handling"""
        # Parse allowed origins from string
        origins = [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        
        if self.is_development:
            # Add development origins
            dev_origins = [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ]
            return list(set(origins + dev_origins))
        return origins
    
    def get_trusted_hosts(self) -> List[str]:
        """Get trusted hosts with environment-specific handling"""
        # Parse trusted hosts from string
        hosts = [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]
        
        if self.is_development:
            # Add development hosts
            dev_hosts = [
                "localhost",
                "127.0.0.1",
                "0.0.0.0"
            ]
            return list(set(hosts + dev_hosts))
        return hosts

@lru_cache()
def get_security_settings() -> SecuritySettings:
    """Get cached security settings"""
    return SecuritySettings()

def validate_security_environment():
    """Validate security environment on startup"""
    try:
        settings = get_security_settings()
        
        # Production-specific validations
        if settings.is_production:
            if settings.debug:
                print("❌ WARNING: Debug mode should be disabled in production")
            
            if "localhost" in settings.allowed_origins:
                print("❌ WARNING: Localhost should not be in allowed origins for production")
            
            if not settings.sentry_dsn:
                print("⚠️  WARNING: Sentry DSN not configured for production monitoring")
        
        # Log configuration status
        print(f"✅ Security configuration validated for {settings.environment} environment")
        print(f"📁 Upload directory: {settings.upload_dir}")
        print(f"🔒 Max file size: {settings.max_file_size / (1024*1024):.1f}MB")
        print(f"⏱️  Rate limit: {settings.rate_limit_per_minute} requests/minute")
        print(f"🌐 CORS origins: {len(settings.get_cors_origins())} configured")
        
        return settings
        
    except Exception as e:
        print(f"❌ Security configuration validation failed: {e}")
        sys.exit(1)

# Security configuration presets
class SecurityPresets:
    """Predefined security configurations for different environments"""
    
    @staticmethod
    def development():
        """Development environment preset"""
        return {
            "debug": True,
            "log_level": "DEBUG",
            "rate_limit_per_minute": 100,
            "max_file_age_hours": 1,
            "allowed_origins": ["http://localhost:3000", "http://localhost:3001"],
            "trusted_hosts": ["localhost", "127.0.0.1"]
        }
    
    @staticmethod
    def staging():
        """Staging environment preset"""
        return {
            "debug": False,
            "log_level": "INFO",
            "rate_limit_per_minute": 50,
            "max_file_age_hours": 12,
            "allowed_origins": ["https://staging.yourdomain.com"],
            "trusted_hosts": ["staging.yourdomain.com"]
        }
    
    @staticmethod
    def production():
        """Production environment preset"""
        return {
            "debug": False,
            "log_level": "WARNING",
            "rate_limit_per_minute": 10,
            "max_file_age_hours": 24,
            "allowed_origins": ["https://yourdomain.com", "https://www.yourdomain.com"],
            "trusted_hosts": ["yourdomain.com", "www.yourdomain.com"]
        }

# Security monitoring configuration
class SecurityMonitoring:
    """Security monitoring and alerting configuration"""
    
    @staticmethod
    def setup_logging():
        """Setup security logging configuration"""
        import logging
        import json
        from datetime import datetime
        
        # Create security logger
        security_logger = logging.getLogger("security")
        security_logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler("security.log")
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        security_logger.addHandler(handler)
        
        return security_logger
    
    @staticmethod
    def log_security_event(event_type: str, details: dict, severity: str = "info"):
        """Log security events with structured format"""
        import logging
        import json
        from datetime import datetime
        
        security_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        logger = logging.getLogger("security")
        getattr(logger, severity.lower())(json.dumps(security_event))

# Environment validation helper
def check_required_env_vars():
    """Check if all required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required variables")
        sys.exit(1)
    
    return True 