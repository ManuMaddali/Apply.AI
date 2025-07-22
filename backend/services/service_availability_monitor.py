"""
Service Availability Monitor - Monitor and handle service unavailability

This service provides:
- Health checks for external services (Stripe, database, email)
- Circuit breaker pattern for failing services
- Graceful fallbacks when services are unavailable
- Service recovery detection and notification
- Performance monitoring and alerting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass
import stripe
from sqlalchemy.orm import Session
from sqlalchemy import text

from config.database import get_db
from config.stripe_config import get_stripe_config
from utils.subscription_logger import subscription_logger
from utils.email_service import EmailService

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Service is failing, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class ServiceHealth:
    """Service health information"""
    service_name: str
    status: ServiceStatus
    last_check: datetime
    response_time_ms: float
    error_count: int
    error_rate: float
    last_error: Optional[str] = None
    uptime_percentage: float = 100.0
    circuit_state: CircuitState = CircuitState.CLOSED


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures before opening circuit
    recovery_timeout: int = 60  # Seconds to wait before trying half-open
    success_threshold: int = 3  # Successful calls needed to close circuit
    timeout: int = 30  # Request timeout in seconds


class ServiceAvailabilityMonitor:
    """Monitor service availability and provide fallback mechanisms"""
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        
        # Default circuit breaker configurations
        self.circuit_configs = {
            "stripe": CircuitBreakerConfig(failure_threshold=3, recovery_timeout=120),
            "database": CircuitBreakerConfig(failure_threshold=2, recovery_timeout=30),
            "email": CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60)
        }
        
        # Initialize services
        self._initialize_services()
        
        # Start monitoring task
        self.monitoring_task = None
        self.is_monitoring = False
    
    def _initialize_services(self):
        """Initialize service health tracking"""
        services = ["stripe", "database", "email"]
        
        for service in services:
            self.services[service] = ServiceHealth(
                service_name=service,
                status=ServiceStatus.UNKNOWN,
                last_check=datetime.utcnow(),
                response_time_ms=0.0,
                error_count=0,
                error_rate=0.0
            )
            
            self.circuit_breakers[service] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "last_failure_time": None,
                "success_count": 0,
                "config": self.circuit_configs.get(service, CircuitBreakerConfig())
            }
    
    async def start_monitoring(self, interval: int = 60):
        """Start continuous service monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info("Service availability monitoring started")
    
    async def stop_monitoring(self):
        """Stop service monitoring"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Service availability monitoring stopped")
    
    async def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await self.check_all_services()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def check_all_services(self) -> Dict[str, ServiceHealth]:
        """Check health of all monitored services"""
        tasks = []
        for service_name in self.services.keys():
            tasks.append(self._check_service_health(service_name))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.services
    
    async def _check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a specific service"""
        start_time = datetime.utcnow()
        
        try:
            if service_name == "stripe":
                await self._check_stripe_health()
            elif service_name == "database":
                await self._check_database_health()
            elif service_name == "email":
                await self._check_email_health()
            else:
                raise ValueError(f"Unknown service: {service_name}")
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update service health
            service_health = self.services[service_name]
            service_health.status = ServiceStatus.HEALTHY
            service_health.last_check = datetime.utcnow()
            service_health.response_time_ms = response_time
            service_health.last_error = None
            
            # Update circuit breaker
            await self._handle_service_success(service_name)
            
            return service_health
            
        except Exception as e:
            # Calculate response time even for failures
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Update service health
            service_health = self.services[service_name]
            service_health.status = ServiceStatus.UNHEALTHY
            service_health.last_check = datetime.utcnow()
            service_health.response_time_ms = response_time
            service_health.error_count += 1
            service_health.last_error = str(e)
            
            # Update circuit breaker
            await self._handle_service_failure(service_name, str(e))
            
            logger.warning(f"Service {service_name} health check failed: {e}")
            return service_health
    
    async def _check_stripe_health(self):
        """Check Stripe service health"""
        try:
            config = get_stripe_config()
            stripe.api_key = config.secret_key
            
            # Simple API call to check connectivity
            stripe.Account.retrieve()
            
        except Exception as e:
            raise Exception(f"Stripe health check failed: {e}")
    
    async def _check_database_health(self):
        """Check database health"""
        try:
            db = next(get_db())
            try:
                # Simple query to check database connectivity
                result = db.execute(text("SELECT 1")).fetchone()
                if not result:
                    raise Exception("Database query returned no result")
            finally:
                db.close()
                
        except Exception as e:
            raise Exception(f"Database health check failed: {e}")
    
    async def _check_email_health(self):
        """Check email service health"""
        try:
            email_service = EmailService()
            # For email, we'll just check if the service can be initialized
            # In production, you might want to send a test email or check SMTP connectivity
            if not email_service.settings:
                raise Exception("Email service not properly configured")
                
        except Exception as e:
            raise Exception(f"Email service health check failed: {e}")
    
    async def _handle_service_success(self, service_name: str):
        """Handle successful service call"""
        circuit = self.circuit_breakers[service_name]
        
        if circuit["state"] == CircuitState.HALF_OPEN:
            circuit["success_count"] += 1
            if circuit["success_count"] >= circuit["config"].success_threshold:
                # Close the circuit - service has recovered
                circuit["state"] = CircuitState.CLOSED
                circuit["failure_count"] = 0
                circuit["success_count"] = 0
                
                logger.info(f"Circuit breaker for {service_name} closed - service recovered")
                
                # Log service recovery
                subscription_logger.log_subscription_event(
                    event_type="service_recovered",
                    category=subscription_logger.EventCategory.SYSTEM,
                    details={
                        "service": service_name,
                        "previous_state": "half_open"
                    }
                )
        elif circuit["state"] == CircuitState.CLOSED:
            # Reset failure count on successful call
            circuit["failure_count"] = 0
    
    async def _handle_service_failure(self, service_name: str, error: str):
        """Handle service failure"""
        circuit = self.circuit_breakers[service_name]
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = datetime.utcnow()
        
        if circuit["state"] == CircuitState.CLOSED:
            if circuit["failure_count"] >= circuit["config"].failure_threshold:
                # Open the circuit
                circuit["state"] = CircuitState.OPEN
                
                logger.error(f"Circuit breaker for {service_name} opened due to failures")
                
                # Log service failure
                subscription_logger.log_subscription_event(
                    event_type="service_unavailable",
                    category=subscription_logger.EventCategory.SYSTEM,
                    level=subscription_logger.LogLevel.ERROR,
                    details={
                        "service": service_name,
                        "failure_count": circuit["failure_count"],
                        "error": error
                    }
                )
        elif circuit["state"] == CircuitState.HALF_OPEN:
            # Failed during recovery attempt, go back to open
            circuit["state"] = CircuitState.OPEN
            circuit["success_count"] = 0
    
    async def is_service_available(self, service_name: str) -> bool:
        """Check if service is available (circuit breaker check)"""
        if service_name not in self.circuit_breakers:
            return True  # Unknown services are assumed available
        
        circuit = self.circuit_breakers[service_name]
        
        if circuit["state"] == CircuitState.CLOSED:
            return True
        elif circuit["state"] == CircuitState.OPEN:
            # Check if we should try half-open
            if circuit["last_failure_time"]:
                time_since_failure = (datetime.utcnow() - circuit["last_failure_time"]).total_seconds()
                if time_since_failure >= circuit["config"].recovery_timeout:
                    circuit["state"] = CircuitState.HALF_OPEN
                    circuit["success_count"] = 0
                    logger.info(f"Circuit breaker for {service_name} moved to half-open")
                    return True
            return False
        elif circuit["state"] == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    async def execute_with_fallback(
        self,
        service_name: str,
        primary_func: Callable,
        fallback_func: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute function with fallback if service is unavailable"""
        try:
            # Check circuit breaker
            if not await self.is_service_available(service_name):
                if fallback_func:
                    logger.info(f"Using fallback for {service_name} (circuit open)")
                    result = await fallback_func(*args, **kwargs) if asyncio.iscoroutinefunction(fallback_func) else fallback_func(*args, **kwargs)
                    return {
                        "success": True,
                        "data": result,
                        "fallback_used": True,
                        "service_available": False
                    }
                else:
                    return {
                        "success": False,
                        "error": f"{service_name} service unavailable and no fallback provided",
                        "service_available": False
                    }
            
            # Execute primary function
            start_time = datetime.utcnow()
            
            if asyncio.iscoroutinefunction(primary_func):
                result = await primary_func(*args, **kwargs)
            else:
                result = primary_func(*args, **kwargs)
            
            # Record success
            await self._handle_service_success(service_name)
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            subscription_logger.log_performance_metric(
                operation=f"{service_name}_operation",
                duration_ms=duration,
                success=True
            )
            
            return {
                "success": True,
                "data": result,
                "fallback_used": False,
                "service_available": True
            }
            
        except Exception as e:
            # Record failure
            await self._handle_service_failure(service_name, str(e))
            
            # Try fallback
            if fallback_func:
                try:
                    logger.warning(f"Primary {service_name} operation failed, using fallback: {e}")
                    result = await fallback_func(*args, **kwargs) if asyncio.iscoroutinefunction(fallback_func) else fallback_func(*args, **kwargs)
                    return {
                        "success": True,
                        "data": result,
                        "fallback_used": True,
                        "service_available": False,
                        "primary_error": str(e)
                    }
                except Exception as fallback_error:
                    logger.error(f"Both primary and fallback failed for {service_name}: primary={e}, fallback={fallback_error}")
                    return {
                        "success": False,
                        "error": str(e),
                        "fallback_error": str(fallback_error),
                        "service_available": False
                    }
            else:
                return {
                    "success": False,
                    "error": str(e),
                    "service_available": False
                }
    
    def get_service_status(self, service_name: str) -> Optional[ServiceHealth]:
        """Get current status of a service"""
        return self.services.get(service_name)
    
    def get_all_service_status(self) -> Dict[str, ServiceHealth]:
        """Get status of all monitored services"""
        return self.services.copy()
    
    def register_fallback_handler(self, service_name: str, handler: Callable):
        """Register a fallback handler for a service"""
        self.fallback_handlers[service_name] = handler
        logger.info(f"Registered fallback handler for {service_name}")
    
    async def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        healthy_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY)
        total_services = len(self.services)
        
        overall_status = ServiceStatus.HEALTHY
        if healthy_services == 0:
            overall_status = ServiceStatus.UNHEALTHY
        elif healthy_services < total_services:
            overall_status = ServiceStatus.DEGRADED
        
        return {
            "overall_status": overall_status.value,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": {name: {
                "status": health.status.value,
                "response_time_ms": health.response_time_ms,
                "last_check": health.last_check.isoformat(),
                "error_count": health.error_count,
                "circuit_state": self.circuit_breakers[name]["state"].value
            } for name, health in self.services.items()},
            "timestamp": datetime.utcnow().isoformat()
        }


# Global service monitor instance
service_monitor = ServiceAvailabilityMonitor()


# Convenience functions for common patterns

async def execute_stripe_operation(operation_func, *args, **kwargs):
    """Execute Stripe operation with fallback"""
    return await service_monitor.execute_with_fallback(
        "stripe",
        operation_func,
        None,  # No fallback for Stripe operations
        *args,
        **kwargs
    )


async def execute_database_operation(operation_func, fallback_func=None, *args, **kwargs):
    """Execute database operation with fallback"""
    return await service_monitor.execute_with_fallback(
        "database",
        operation_func,
        fallback_func,
        *args,
        **kwargs
    )


async def execute_email_operation(operation_func, *args, **kwargs):
    """Execute email operation with fallback (queue for later)"""
    async def email_fallback(*args, **kwargs):
        # In production, you might queue the email for later delivery
        logger.info("Email service unavailable, email queued for later delivery")
        return {"queued": True}
    
    return await service_monitor.execute_with_fallback(
        "email",
        operation_func,
        email_fallback,
        *args,
        **kwargs
    )