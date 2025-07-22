"""
Stripe Configuration - Centralized Stripe settings and validation

This module handles:
- Stripe API key configuration and validation
- Environment-specific settings
- Price ID management
- Webhook configuration
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StripeConfig:
    """Stripe configuration settings"""
    secret_key: str
    publishable_key: str
    webhook_secret: Optional[str] = None
    pro_monthly_price_id: Optional[str] = None
    environment: str = "development"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """Validate Stripe configuration"""
        if not self.secret_key:
            raise ValueError("STRIPE_SECRET_KEY is required")
        
        if not self.publishable_key:
            raise ValueError("STRIPE_PUBLISHABLE_KEY is required")
        
        # Validate key formats
        if self.environment == "production":
            if not self.secret_key.startswith("sk_live_"):
                raise ValueError("Production environment requires live secret key (sk_live_)")
            if not self.publishable_key.startswith("pk_live_"):
                raise ValueError("Production environment requires live publishable key (pk_live_)")
        else:
            if not self.secret_key.startswith("sk_test_"):
                logger.warning("Development environment should use test secret key (sk_test_)")
            if not self.publishable_key.startswith("pk_test_"):
                logger.warning("Development environment should use test publishable key (pk_test_)")
        
        # Validate webhook secret format if provided
        if self.webhook_secret and not self.webhook_secret.startswith("whsec_"):
            logger.warning("Webhook secret should start with 'whsec_'")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"
    
    @property
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(self.secret_key and self.publishable_key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding sensitive data)"""
        return {
            "environment": self.environment,
            "is_production": self.is_production,
            "is_configured": self.is_configured,
            "has_webhook_secret": bool(self.webhook_secret),
            "has_pro_price_id": bool(self.pro_monthly_price_id),
            "publishable_key": self.publishable_key  # Safe to expose
        }


def load_stripe_config() -> StripeConfig:
    """Load Stripe configuration from environment variables"""
    try:
        # Determine environment
        environment = os.getenv("NODE_ENV", "development")
        
        # Load configuration
        config = StripeConfig(
            secret_key=os.getenv("STRIPE_SECRET_KEY", ""),
            publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
            webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
            pro_monthly_price_id=os.getenv("STRIPE_PRICE_ID_PRO_MONTHLY"),
            environment=environment
        )
        
        logger.info(f"Loaded Stripe configuration for {environment} environment")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load Stripe configuration: {e}")
        raise


def get_stripe_prices() -> Dict[str, str]:
    """Get configured Stripe price IDs"""
    return {
        "pro_monthly": os.getenv("STRIPE_PRICE_ID_PRO_MONTHLY", ""),
        # Add more price IDs as needed
        # "pro_yearly": os.getenv("STRIPE_PRICE_ID_PRO_YEARLY", ""),
    }


def validate_stripe_environment() -> bool:
    """Validate that Stripe is properly configured for the current environment"""
    try:
        config = load_stripe_config()
        
        # Check required configuration
        if not config.is_configured:
            logger.error("Stripe is not properly configured")
            return False
        
        # Check price IDs
        prices = get_stripe_prices()
        if not prices.get("pro_monthly"):
            logger.warning("Pro monthly price ID not configured")
        
        # Environment-specific checks
        if config.is_production:
            if not config.webhook_secret:
                logger.error("Webhook secret is required in production")
                return False
        
        logger.info("Stripe environment validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Stripe environment validation failed: {e}")
        return False


# Global configuration instance
_stripe_config: Optional[StripeConfig] = None


def get_stripe_config() -> StripeConfig:
    """Get global Stripe configuration instance"""
    global _stripe_config
    
    if _stripe_config is None:
        _stripe_config = load_stripe_config()
    
    return _stripe_config


def refresh_stripe_config() -> StripeConfig:
    """Refresh global Stripe configuration from environment"""
    global _stripe_config
    _stripe_config = load_stripe_config()
    return _stripe_config


# Stripe webhook event types we handle
SUPPORTED_WEBHOOK_EVENTS = [
    "customer.subscription.created",
    "customer.subscription.updated", 
    "customer.subscription.deleted",
    "invoice.payment_succeeded",
    "invoice.payment_failed",
    "customer.subscription.trial_will_end",
    "payment_intent.succeeded",
    "payment_intent.payment_failed"
]


def is_supported_webhook_event(event_type: str) -> bool:
    """Check if webhook event type is supported"""
    return event_type in SUPPORTED_WEBHOOK_EVENTS