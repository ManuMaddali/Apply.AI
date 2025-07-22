"""
Analytics Privacy and User Consent Service

This service handles user consent for analytics data collection,
data anonymization, and privacy compliance for ApplyAI Pro users.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from models.user import User
from services.subscription_service import SubscriptionService


class ConsentType(Enum):
    """Types of analytics consent"""
    BASIC_ANALYTICS = "basic_analytics"
    PERFORMANCE_TRACKING = "performance_tracking"
    USAGE_ANALYTICS = "usage_analytics"
    IMPROVEMENT_ANALYTICS = "improvement_analytics"
    MARKETING_ANALYTICS = "marketing_analytics"


class DataRetentionPeriod(Enum):
    """Data retention periods"""
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_180 = 180
    DAYS_365 = 365


class AnalyticsPrivacyService:
    """Service for managing analytics privacy and user consent"""
    
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
        self.logger = logging.getLogger(__name__)
        
        # Default consent settings for different user types
        self.default_consent = {
            "free": {
                ConsentType.BASIC_ANALYTICS: False,
                ConsentType.PERFORMANCE_TRACKING: False,
                ConsentType.USAGE_ANALYTICS: False,
                ConsentType.IMPROVEMENT_ANALYTICS: False,
                ConsentType.MARKETING_ANALYTICS: False
            },
            "pro": {
                ConsentType.BASIC_ANALYTICS: True,  # Required for Pro features
                ConsentType.PERFORMANCE_TRACKING: True,  # Required for analytics dashboard
                ConsentType.USAGE_ANALYTICS: True,  # Required for recommendations
                ConsentType.IMPROVEMENT_ANALYTICS: False,  # Optional
                ConsentType.MARKETING_ANALYTICS: False  # Optional
            }
        }
    
    async def get_user_consent(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current consent settings for analytics
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing consent settings and metadata
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Get stored consent or use defaults
            stored_consent = getattr(user, 'analytics_consent', None)
            if stored_consent and isinstance(stored_consent, dict):
                consent_settings = stored_consent
            else:
                # Use default consent based on subscription tier
                tier = str(user.subscription_tier) if user.subscription_tier is not None else "free"
                consent_settings = {
                    consent_type.value: granted 
                    for consent_type, granted in self.default_consent.get(tier, self.default_consent["free"]).items()
                }
            
            return {
                "user_id": user_id,
                "consent_settings": consent_settings,
                "consent_date": getattr(user, 'analytics_consent_date', None),
                "subscription_tier": str(user.subscription_tier) if user.subscription_tier is not None else "free",
                "can_collect_analytics": self._can_collect_analytics(consent_settings),
                "required_consents": self._get_required_consents(str(user.subscription_tier) if user.subscription_tier is not None else "free"),
                "optional_consents": self._get_optional_consents(str(user.subscription_tier) if user.subscription_tier is not None else "free")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user consent for {user_id}: {str(e)}")
            return {"error": "Failed to retrieve consent settings"}
    
    async def update_user_consent(
        self,
        user_id: str,
        consent_updates: Dict[str, bool],
        consent_source: str = "user_settings"
    ) -> Dict[str, Any]:
        """
        Update user's consent settings for analytics
        
        Args:
            user_id: User ID
            consent_updates: Dictionary of consent type -> boolean
            consent_source: Source of consent update (user_settings, onboarding, etc.)
            
        Returns:
            Dict containing updated consent settings
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Get current consent settings
            current_consent = await self.get_user_consent(user_id)
            if "error" in current_consent:
                return current_consent
            
            # Update consent settings
            updated_consent = current_consent["consent_settings"].copy()
            for consent_type, granted in consent_updates.items():
                if consent_type in [ct.value for ct in ConsentType]:
                    updated_consent[consent_type] = granted
            
            # Validate required consents for Pro users
            if user.subscription_tier == "pro":
                required_consents = self._get_required_consents("pro")
                for required_consent in required_consents:
                    if not updated_consent.get(required_consent.value, False):
                        return {
                            "error": f"Consent for {required_consent.value} is required for Pro subscription",
                            "required_consent": required_consent.value
                        }
            
            # Store updated consent (in a real implementation, this would be stored in the database)
            # For now, we'll log the consent update
            consent_record = {
                "user_id": user_id,
                "consent_settings": updated_consent,
                "consent_date": datetime.utcnow().isoformat(),
                "consent_source": consent_source,
                "previous_consent": current_consent["consent_settings"]
            }
            
            self.logger.info(f"Analytics consent updated: {json.dumps(consent_record)}")
            
            return {
                "user_id": user_id,
                "consent_settings": updated_consent,
                "consent_date": datetime.utcnow().isoformat(),
                "consent_source": consent_source,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update user consent for {user_id}: {str(e)}")
            return {"error": "Failed to update consent settings"}
    
    async def anonymize_analytics_data(
        self,
        analytics_data: Dict[str, Any],
        anonymization_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Anonymize analytics data for privacy compliance
        
        Args:
            analytics_data: Raw analytics data
            anonymization_level: Level of anonymization (minimal, standard, strict)
            
        Returns:
            Anonymized analytics data
        """
        try:
            anonymized_data = analytics_data.copy()
            
            # Remove or hash personally identifiable information
            if "user_id" in anonymized_data:
                if anonymization_level == "strict":
                    # Remove user_id completely
                    del anonymized_data["user_id"]
                else:
                    # Hash user_id for pseudonymization
                    anonymized_data["user_id"] = self._hash_identifier(anonymized_data["user_id"])
            
            # Remove sensitive metadata
            sensitive_fields = ["email", "name", "ip_address", "device_id", "session_id"]
            for field in sensitive_fields:
                if field in anonymized_data:
                    if anonymization_level == "minimal":
                        anonymized_data[field] = self._hash_identifier(str(anonymized_data[field]))
                    else:
                        del anonymized_data[field]
            
            # Anonymize nested data
            if "event_data" in anonymized_data and isinstance(anonymized_data["event_data"], dict):
                anonymized_data["event_data"] = await self._anonymize_event_data(
                    anonymized_data["event_data"], 
                    anonymization_level
                )
            
            # Add anonymization metadata
            anonymized_data["_anonymization"] = {
                "level": anonymization_level,
                "anonymized_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            return anonymized_data
            
        except Exception as e:
            self.logger.error(f"Failed to anonymize analytics data: {str(e)}")
            return {"error": "Failed to anonymize data"}
    
    async def get_data_retention_policy(self, user_id: str) -> Dict[str, Any]:
        """
        Get data retention policy for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing retention policy details
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Determine retention period based on subscription and consent
            consent_data = await self.get_user_consent(user_id)
            if "error" in consent_data:
                return consent_data
            
            # Default retention periods
            retention_policy = {
                "basic_analytics": DataRetentionPeriod.DAYS_90.value,
                "performance_tracking": DataRetentionPeriod.DAYS_180.value,
                "usage_analytics": DataRetentionPeriod.DAYS_365.value,
                "improvement_analytics": DataRetentionPeriod.DAYS_180.value,
                "marketing_analytics": DataRetentionPeriod.DAYS_90.value
            }
            
            # Adjust based on subscription tier
            if user.subscription_tier == "pro":
                retention_policy.update({
                    "performance_tracking": DataRetentionPeriod.DAYS_365.value,
                    "usage_analytics": DataRetentionPeriod.DAYS_365.value
                })
            
            return {
                "user_id": user_id,
                "subscription_tier": user.subscription_tier,
                "retention_policy": retention_policy,
                "policy_version": "1.0",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get retention policy for {user_id}: {str(e)}")
            return {"error": "Failed to retrieve retention policy"}
    
    async def request_data_deletion(
        self,
        user_id: str,
        deletion_type: str = "all_analytics"
    ) -> Dict[str, Any]:
        """
        Process user request for analytics data deletion
        
        Args:
            user_id: User ID
            deletion_type: Type of deletion (all_analytics, specific_period, etc.)
            
        Returns:
            Dict containing deletion request details
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Create deletion request record
            deletion_request = {
                "request_id": str(uuid.uuid4()),
                "user_id": user_id,
                "deletion_type": deletion_type,
                "requested_at": datetime.utcnow().isoformat(),
                "status": "pending",
                "estimated_completion": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            # Log deletion request for processing
            self.logger.info(f"Analytics data deletion requested: {json.dumps(deletion_request)}")
            
            return {
                "success": True,
                "request_id": deletion_request["request_id"],
                "message": "Data deletion request submitted successfully",
                "estimated_completion_date": deletion_request["estimated_completion"],
                "what_will_be_deleted": self._get_deletion_scope(deletion_type),
                "contact_info": "For questions about data deletion, contact privacy@applyai.com"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process deletion request for {user_id}: {str(e)}")
            return {"error": "Failed to process data deletion request"}
    
    async def export_user_analytics_data(
        self,
        user_id: str,
        include_anonymized: bool = False
    ) -> Dict[str, Any]:
        """
        Export user's analytics data for transparency/portability
        
        Args:
            user_id: User ID
            include_anonymized: Whether to include anonymized data
            
        Returns:
            Dict containing exported analytics data
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Get user consent to ensure we can export their data
            consent_data = await self.get_user_consent(user_id)
            if "error" in consent_data:
                return consent_data
            
            # Collect analytics data (in a real implementation, this would query the analytics database)
            export_data = {
                "user_id": user_id,
                "export_date": datetime.utcnow().isoformat(),
                "consent_settings": consent_data["consent_settings"],
                "data_categories": {
                    "basic_analytics": "Usage patterns and feature adoption",
                    "performance_tracking": "Success rates and optimization scores",
                    "usage_analytics": "Detailed usage statistics and trends",
                    "improvement_analytics": "Feedback and improvement suggestions",
                    "marketing_analytics": "Marketing campaign effectiveness"
                },
                "retention_policy": await self.get_data_retention_policy(user_id),
                "note": "This export contains all analytics data we have collected about you based on your consent settings."
            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to export analytics data for {user_id}: {str(e)}")
            return {"error": "Failed to export analytics data"}
    
    def _can_collect_analytics(self, consent_settings: Dict[str, bool]) -> bool:
        """Check if we can collect any analytics based on consent"""
        return any(consent_settings.values())
    
    def _get_required_consents(self, subscription_tier: str) -> List[ConsentType]:
        """Get required consents for subscription tier"""
        if subscription_tier == "pro":
            return [
                ConsentType.BASIC_ANALYTICS,
                ConsentType.PERFORMANCE_TRACKING,
                ConsentType.USAGE_ANALYTICS
            ]
        return []
    
    def _get_optional_consents(self, subscription_tier: str) -> List[ConsentType]:
        """Get optional consents for subscription tier"""
        required = self._get_required_consents(subscription_tier)
        all_consents = list(ConsentType)
        return [consent for consent in all_consents if consent not in required]
    
    def _hash_identifier(self, identifier: str) -> str:
        """Hash an identifier for pseudonymization"""
        return hashlib.sha256(f"{identifier}_salt_2024".encode()).hexdigest()[:16]
    
    async def _anonymize_event_data(
        self,
        event_data: Dict[str, Any],
        anonymization_level: str
    ) -> Dict[str, Any]:
        """Anonymize event-specific data"""
        anonymized = event_data.copy()
        
        # Remove or anonymize sensitive event data
        sensitive_event_fields = ["company_name", "job_title", "job_url", "resume_content"]
        
        for field in sensitive_event_fields:
            if field in anonymized:
                if anonymization_level == "strict":
                    del anonymized[field]
                elif anonymization_level == "standard":
                    anonymized[field] = f"[ANONYMIZED_{field.upper()}]"
                else:  # minimal
                    anonymized[field] = self._hash_identifier(str(anonymized[field]))
        
        return anonymized
    
    def _get_deletion_scope(self, deletion_type: str) -> List[str]:
        """Get scope of data that will be deleted"""
        scopes = {
            "all_analytics": [
                "All usage analytics and performance data",
                "Success rate tracking",
                "Feature adoption metrics",
                "Keyword optimization history",
                "Template usage statistics"
            ],
            "performance_only": [
                "Success rate data",
                "Keyword optimization scores",
                "Template performance metrics"
            ],
            "usage_only": [
                "Feature usage statistics",
                "Usage patterns and trends",
                "Activity logs"
            ]
        }
        return scopes.get(deletion_type, scopes["all_analytics"])
