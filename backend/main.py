from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Security imports
from middleware.security import setup_security_middleware
from middleware.feature_gate import setup_feature_gate_middleware
from config.security import validate_security_environment, SecurityMonitoring, check_required_env_vars
from utils.rate_limiter import limiter, custom_rate_limit_handler
from utils.file_security import cleanup_temp_files
from slowapi.errors import RateLimitExceeded

# Import routes
from routes.upload_resume import router as upload_router
from routes.scrape_jobs import router as scrape_router
from routes.generate_resumes import router as generate_router
from routes.batch_processing import router as batch_router
from routes.auth import router as auth_router
from routes.webhooks import router as webhooks_router
from routes.advanced_formatting import router as advanced_formatting_router
from routes.job_specific_templates import router as job_templates_router
from routes.analytics import router as analytics_router
from routes.premium_cover_letters import router as premium_cover_letters_router
from routes.analytics_privacy import router as analytics_privacy_router
from routes.subscription import router as subscription_router
from routes.admin_analytics import router as admin_analytics_router
from routes.lifecycle_management import router as lifecycle_router

# Database initialization
from config.database import init_db, check_database_health

# Validate security configuration on startup
settings = validate_security_environment()

# Initialize security logging
SecurityMonitoring.setup_logging()

# Initialize FastAPI app with security-focused configuration
app = FastAPI(
    title="Apply.AI - Secure Resume Tailoring API",
    description="Production-ready AI Resume Tailoring with comprehensive security features",
    version="2.0.0",
    docs_url="/docs" if settings.is_development else None,  # Hide docs in production
    redoc_url="/redoc" if settings.is_development else None,  # Hide redoc in production
    openapi_url="/openapi.json" if settings.is_development else None,  # Hide OpenAPI in production
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Setup comprehensive security middleware
setup_security_middleware(app)

# Setup feature gate middleware for subscription control
setup_feature_gate_middleware(app)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Include routers with rate limiting
app.include_router(auth_router, prefix="/api", tags=["authentication"])
app.include_router(upload_router, prefix="/api/resumes", tags=["resumes"])
app.include_router(scrape_router, prefix="/api/jobs", tags=["jobs"])
app.include_router(generate_router, prefix="/api/resumes", tags=["resumes"])
app.include_router(batch_router, prefix="/api/batch", tags=["batch"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(advanced_formatting_router, tags=["advanced-formatting"])
app.include_router(job_templates_router, prefix="/api/job-templates", tags=["job-specific-templates"])
app.include_router(analytics_router, tags=["analytics"])
app.include_router(premium_cover_letters_router, tags=["premium-cover-letters"])
app.include_router(analytics_privacy_router, tags=["analytics-privacy"])
app.include_router(subscription_router, tags=["subscription"])
app.include_router(admin_analytics_router, tags=["admin-analytics"])
app.include_router(lifecycle_router, tags=["lifecycle-management"])

# Mount static files
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    print(f"🚀 Apply.AI API starting up in {settings.environment} mode")
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    # Check database health
    if not check_database_health():
        print("❌ Database health check failed")
        raise Exception("Database connection failed")
    
    # Validate security configuration
    check_required_env_vars()
    
    # Initialize security monitoring
    SecurityMonitoring.log_security_event(
        "application_startup",
        {
            "version": "2.0.0",
            "environment": settings.environment,
            "security_features": [
                "rate_limiting",
                "file_validation",
                "cors_configured",
                "security_headers",
                "input_sanitization"
            ]
        },
        "info"
    )
    
    # Start subscription lifecycle task scheduler - TEMPORARILY DISABLED
    # TODO: Fix scheduler startup issue
    try:
        # from services.task_scheduler import start_scheduler
        # await start_scheduler()
        print("⚠️ Subscription lifecycle scheduler temporarily disabled")
    except Exception as e:
        print(f"⚠️ Failed to start lifecycle scheduler: {e}")
        # Don't fail startup if scheduler fails
    
    print("✅ Security configuration validated")
    print("✅ Application ready for requests")

@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Basic health check endpoint"""
    db_healthy = check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": settings.environment,
        "database": "connected" if db_healthy else "disconnected"
    }

@app.get("/health/detailed")
@limiter.limit("10/minute")
async def detailed_health_check(request: Request):
    """Detailed health check - limited in production"""
    if settings.is_production:
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    try:
        import psutil
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "environment": settings.environment,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "security": {
                "rate_limiting": "enabled",
                "file_validation": "enabled",
                "cors_configured": "enabled",
                "security_headers": "enabled"
            }
        }
    except Exception as e:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "environment": settings.environment,
            "note": "Basic health check only"
        }

@app.get("/docs-fixed")
async def docs_fixed():
    """Fixed documentation endpoint"""
    return HTMLResponse(content="""
    <html>
        <head>
            <title>API Documentation</title>
        </head>
        <body>
            <h1>Apply.AI Resume Tailoring API</h1>
            <p>Documentation available at <a href="/docs">/docs</a></p>
        </body>
    </html>
    """)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with security logging"""
    import traceback
    
    # Log security-relevant errors
    if isinstance(exc, (ValueError, TypeError, AttributeError)):
        SecurityMonitoring.log_security_event(
            "application_error",
            {
                "error": str(exc),
                "endpoint": str(request.url),
                "method": request.method,
                "ip": request.client.host if request.client else "unknown"
            },
            "error"
        )
    
    # Don't expose internal errors in production
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc),
                "type": type(exc).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    print("🔄 Apply.AI API shutting down...")
    
    # Stop subscription lifecycle scheduler
    try:
        from services.task_scheduler import stop_scheduler
        await stop_scheduler()
        print("✅ Subscription lifecycle scheduler stopped")
    except Exception as e:
        print(f"⚠️ Error stopping lifecycle scheduler: {e}")
    
    # Cleanup temporary files
    try:
        cleanup_temp_files()
        print("✅ Temporary files cleaned up")
    except Exception as e:
        print(f"⚠️  Error during cleanup: {e}")
    
    # Log shutdown event
    SecurityMonitoring.log_security_event(
        "application_shutdown",
        {"timestamp": datetime.utcnow().isoformat()},
        "info"
    )
    
    print("✅ Application shutdown complete")

@app.get("/")
@limiter.limit("60/minute")
async def root(request: Request):
    """Root endpoint with API information"""
    return {
        "message": "🔒 Apply.AI - Secure Resume Tailoring API",
        "version": "2.0.0",
        "environment": settings.environment,
        "security": "enabled",
        "docs": "/docs" if settings.is_development else "Contact admin for API documentation",
        "health": "/health",
        "features": [
            "Secure Authentication",
            "Rate Limiting", 
            "File Validation",
            "Batch Processing",
            "Real-time Processing",
            "Comprehensive Security"
        ]
    }

# SSL/TLS Configuration (if certificates exist)
if __name__ == "__main__":
    import uvicorn
    
    # Check for SSL certificates
    cert_file = "backend/certs/server.crt"
    key_file = "backend/certs/server.key"
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("🔒 SSL certificates found - starting with HTTPS")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            ssl_keyfile=key_file,
            ssl_certfile=cert_file,
            reload=True
        )
    else:
        print("🌐 Starting with HTTP (no SSL certificates found)")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        ) 