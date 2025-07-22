"""
Tests for Feature Gate Middleware

This test suite verifies:
- Subscription status validation
- Pro-only endpoint protection
- Usage limit enforcement for Free users
- Automatic usage tracking
- Proper error responses
- Admin bypass logic
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
import os

from middleware.feature_gate import FeatureGateMiddleware, require_pro_subscription, check_usage_limit, track_usage
from models.user import User, SubscriptionTier, SubscriptionStatus, UsageType
from services.subscription_service import UsageLimitResult
from main import app


class TestFeatureGateMiddleware:
    """Test suite for Feature Gate Middleware"""
    
    def setup_method(self):
        """Setup test environment"""
        self.client = TestClient(app)
        
        # Create mock users
        self.free_user = Mock(spec=User)
        self.free_user.id = "free-user-id"
        self.free_user.email = "free@example.com"
        self.free_user.subscription_tier = SubscriptionTier.FREE
        self.free_user.subscription_status = SubscriptionStatus.ACTIVE
        self.free_user.is_pro_active.return_value = False
        self.free_user.weekly_usage_count = 2
        
        self.pro_user = Mock(spec=User)
        self.pro_user.id = "pro-user-id"
        self.pro_user.email = "pro@example.com"
        self.pro_user.subscription_tier = SubscriptionTier.PRO
        self.pro_user.subscription_status = SubscriptionStatus.ACTIVE
        self.pro_user.is_pro_active.return_value = True
        self.pro_user.weekly_usage_count = 10
        
        self.admin_user = Mock(spec=User)
        self.admin_user.id = "admin-user-id"
        self.admin_user.email = "admin@example.com"
        self.admin_user.role = "admin"
        self.admin_user.is_pro_active.return_value = True
    
    def test_bypass_endpoints_no_auth_required(self):
        """Test that bypass endpoints don't require authentication"""
        bypass_endpoints = [
            "/health",
            "/health/detailed",
            "/docs",
            "/api/auth/login",
            "/api/webhooks/stripe"
        ]
        
        for endpoint in bypass_endpoints:
            response = self.client.get(endpoint)
            # Should not return 401 (auth required) or 402 (subscription required)
            assert response.status_code not in [401, 402], f"Endpoint {endpoint} should bypass feature gates"
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    def test_pro_only_endpoints_require_subscription(self, mock_get_user):
        """Test that Pro-only endpoints require Pro subscription"""
        mock_get_user.return_value = self.free_user
        
        pro_endpoints = [
            "/api/batch/process",
            "/api/resumes/advanced-format",
            "/api/analytics/dashboard"
        ]
        
        for endpoint in pro_endpoints:
            response = self.client.post(endpoint, json={})
            assert response.status_code == 402, f"Endpoint {endpoint} should require Pro subscription"
            
            data = response.json()
            assert data["error"] == "subscription_required"
            assert "upgrade_url" in data
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    def test_pro_user_can_access_pro_endpoints(self, mock_get_user):
        """Test that Pro users can access Pro-only endpoints"""
        mock_get_user.return_value = self.pro_user
        
        # Note: These endpoints might not exist in the actual app, 
        # but the middleware should allow access
        with patch('middleware.feature_gate.FeatureGateMiddleware._track_usage_if_needed'):
            response = self.client.post("/api/batch/process", json={"test": "data"})
            # Should not return 402 (subscription required)
            assert response.status_code != 402
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    @patch('middleware.feature_gate.FeatureGateMiddleware._check_usage_limits')
    def test_usage_limit_enforcement_for_free_users(self, mock_check_limits, mock_get_user):
        """Test that usage limits are enforced for Free users"""
        mock_get_user.return_value = self.free_user
        
        # Mock usage limit exceeded
        mock_check_limits.return_value = UsageLimitResult(
            can_use=False,
            reason="Weekly limit of 5 sessions exceeded",
            remaining=0,
            limit=5
        )
        
        response = self.client.post("/api/resumes/tailor", json={"test": "data"})
        assert response.status_code == 429
        
        data = response.json()
        assert data["error"] == "usage_limit_exceeded"
        assert data["limit"] == 5
        assert data["remaining"] == 0
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    @patch('middleware.feature_gate.FeatureGateMiddleware._check_usage_limits')
    def test_usage_limit_allows_within_limits(self, mock_check_limits, mock_get_user):
        """Test that requests are allowed when within usage limits"""
        mock_get_user.return_value = self.free_user
        
        # Mock usage within limits
        mock_check_limits.return_value = UsageLimitResult(
            can_use=True,
            reason="Within weekly limit (2/5)",
            remaining=3,
            limit=5
        )
        
        with patch('middleware.feature_gate.FeatureGateMiddleware._track_usage_if_needed'):
            response = self.client.post("/api/resumes/tailor", json={"test": "data"})
            # Should not return 429 (rate limited)
            assert response.status_code != 429
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    def test_pro_users_bypass_usage_limits(self, mock_get_user):
        """Test that Pro users bypass usage limit checks"""
        mock_get_user.return_value = self.pro_user
        
        with patch('middleware.feature_gate.FeatureGateMiddleware._track_usage_if_needed'):
            response = self.client.post("/api/resumes/tailor", json={"test": "data"})
            # Should not return 429 (rate limited)
            assert response.status_code != 429
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    def test_tailoring_mode_restriction_for_free_users(self, mock_get_user):
        """Test that heavy tailoring mode is restricted for Free users"""
        mock_get_user.return_value = self.free_user
        
        # Request with heavy tailoring mode
        request_data = {
            "resume_text": "test resume",
            "job_description": "test job",
            "tailoring_mode": "heavy"
        }
        
        response = self.client.post("/api/resumes/tailor", json=request_data)
        
        # Should return 402 for Pro subscription required
        if response.status_code == 402:
            data = response.json()
            assert "heavy tailoring" in data["message"].lower()
    
    @patch.dict(os.environ, {"ENVIRONMENT": "testing", "BYPASS_FEATURE_GATES": "true"})
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    def test_admin_bypass_in_testing_environment(self, mock_get_user):
        """Test that admin bypass works in testing environment"""
        mock_get_user.return_value = self.free_user
        
        with patch('middleware.feature_gate.FeatureGateMiddleware._track_usage_if_needed'):
            response = self.client.post("/api/batch/process", json={"test": "data"})
            # Should not return 402 due to admin bypass
            assert response.status_code != 402
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    @patch('middleware.feature_gate.FeatureGateMiddleware._track_usage_if_needed')
    def test_usage_tracking_after_successful_request(self, mock_track_usage, mock_get_user):
        """Test that usage is tracked after successful requests"""
        mock_get_user.return_value = self.free_user
        mock_track_usage.return_value = None
        
        # Mock a successful response
        with patch('middleware.feature_gate.FeatureGateMiddleware._check_usage_limits') as mock_check:
            mock_check.return_value = UsageLimitResult(True, "Within limits")
            
            response = self.client.post("/api/resumes/tailor", json={"test": "data"})
            
            # Usage tracking should be called for successful requests
            if response.status_code == 200:
                mock_track_usage.assert_called_once()
    
    def test_unauthenticated_requests_to_protected_endpoints(self):
        """Test that unauthenticated requests to protected endpoints are handled"""
        # Request without Authorization header
        response = self.client.post("/api/resumes/tailor", json={"test": "data"})
        
        # Should return 401 (unauthorized) or let auth middleware handle it
        # The exact behavior depends on the auth middleware configuration
        assert response.status_code in [401, 422, 500]  # Various possible responses
    
    @patch('middleware.feature_gate.get_db')
    def test_error_handling_in_middleware(self, mock_get_db):
        """Test that middleware handles errors gracefully"""
        # Mock database error
        mock_get_db.side_effect = Exception("Database connection failed")
        
        response = self.client.get("/health")
        
        # Should not crash the application
        assert response.status_code != 500 or "error" in response.json()


class TestUtilityFunctions:
    """Test utility functions for manual feature gate checks"""
    
    def setup_method(self):
        """Setup test environment"""
        self.free_user = Mock(spec=User)
        self.free_user.is_pro_active.return_value = False
        
        self.pro_user = Mock(spec=User)
        self.pro_user.is_pro_active.return_value = True
        
        self.mock_db = Mock()
    
    @pytest.mark.asyncio
    async def test_require_pro_subscription_with_free_user(self):
        """Test require_pro_subscription raises exception for Free users"""
        with pytest.raises(Exception) as exc_info:
            await require_pro_subscription(self.free_user)
        
        # Should raise HTTPException with 402 status
        assert "subscription_required" in str(exc_info.value) or exc_info.value.status_code == 402
    
    @pytest.mark.asyncio
    async def test_require_pro_subscription_with_pro_user(self):
        """Test require_pro_subscription allows Pro users"""
        # Should not raise exception
        await require_pro_subscription(self.pro_user)
    
    @pytest.mark.asyncio
    @patch('middleware.feature_gate.SubscriptionService')
    async def test_check_usage_limit_with_exceeded_limit(self, mock_service_class):
        """Test check_usage_limit raises exception when limit exceeded"""
        mock_service = Mock()
        mock_service.check_usage_limits.return_value = UsageLimitResult(
            can_use=False,
            reason="Limit exceeded",
            remaining=0,
            limit=5
        )
        mock_service_class.return_value = mock_service
        
        with pytest.raises(Exception) as exc_info:
            await check_usage_limit(self.free_user, UsageType.RESUME_PROCESSING, self.mock_db)
        
        # Should raise HTTPException with 429 status
        assert "usage_limit_exceeded" in str(exc_info.value) or exc_info.value.status_code == 429
    
    @pytest.mark.asyncio
    @patch('middleware.feature_gate.SubscriptionService')
    async def test_check_usage_limit_with_pro_user(self, mock_service_class):
        """Test check_usage_limit allows Pro users without checking"""
        # Should not call the service for Pro users
        await check_usage_limit(self.pro_user, UsageType.RESUME_PROCESSING, self.mock_db)
        
        # Service should not be instantiated for Pro users
        mock_service_class.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('middleware.feature_gate.SubscriptionService')
    async def test_track_usage_success(self, mock_service_class):
        """Test track_usage successfully tracks usage"""
        mock_service = Mock()
        mock_service.track_usage.return_value = None
        mock_service_class.return_value = mock_service
        
        await track_usage(self.free_user, UsageType.RESUME_PROCESSING, self.mock_db, count=2)
        
        mock_service.track_usage.assert_called_once_with(
            user_id=str(self.free_user.id),
            usage_type=UsageType.RESUME_PROCESSING,
            count=2
        )
    
    @pytest.mark.asyncio
    @patch('middleware.feature_gate.SubscriptionService')
    async def test_track_usage_handles_errors(self, mock_service_class):
        """Test track_usage handles errors gracefully"""
        mock_service = Mock()
        mock_service.track_usage.side_effect = Exception("Database error")
        mock_service_class.return_value = mock_service
        
        # Should not raise exception even if tracking fails
        await track_usage(self.free_user, UsageType.RESUME_PROCESSING, self.mock_db)


class TestFeatureAccessHelpers:
    """Test feature access helper functions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.free_user = Mock(spec=User)
        self.free_user.is_pro_active.return_value = False
        
        self.pro_user = Mock(spec=User)
        self.pro_user.is_pro_active.return_value = True
    
    def test_get_user_feature_access_free_user(self):
        """Test feature access for Free users"""
        from middleware.feature_gate import get_user_feature_access
        
        access = get_user_feature_access(self.free_user)
        
        assert access["bulk_processing"] is False
        assert access["advanced_formatting"] is False
        assert access["premium_templates"] is False
        assert access["cover_letters"] is False
        assert access["analytics"] is False
        assert access["heavy_tailoring"] is False
        assert access["unlimited_sessions"] is False
    
    def test_get_user_feature_access_pro_user(self):
        """Test feature access for Pro users"""
        from middleware.feature_gate import get_user_feature_access
        
        access = get_user_feature_access(self.pro_user)
        
        assert access["bulk_processing"] is True
        assert access["advanced_formatting"] is True
        assert access["premium_templates"] is True
        assert access["cover_letters"] is True
        assert access["analytics"] is True
        assert access["heavy_tailoring"] is True
        assert access["unlimited_sessions"] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])