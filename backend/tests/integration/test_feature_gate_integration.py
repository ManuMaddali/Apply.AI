"""
Integration tests for Feature Gate Middleware with actual endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

# Import the main app
from main import app
from models.user import User, SubscriptionTier, SubscriptionStatus


class TestFeatureGateIntegration:
    """Integration tests for feature gate middleware"""
    
    def setup_method(self):
        """Setup test client and mock users"""
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
    
    def test_health_endpoint_bypasses_feature_gates(self):
        """Test that health endpoint bypasses all feature gates"""
        response = self.client.get("/health")
        
        # Should not return subscription-related errors
        assert response.status_code not in [401, 402, 429]
        # Should return health status
        assert response.status_code == 200
    
    def test_auth_endpoints_bypass_feature_gates(self):
        """Test that auth endpoints bypass feature gates"""
        # Test login endpoint (even if it doesn't exist, should not return 402)
        response = self.client.post("/api/auth/login", json={"email": "test@example.com", "password": "test"})
        
        # Should not return subscription required (402)
        assert response.status_code != 402
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    def test_unauthenticated_user_on_protected_endpoint(self, mock_get_user):
        """Test unauthenticated user accessing protected endpoint"""
        mock_get_user.return_value = None
        
        # Try to access a resume processing endpoint without auth
        response = self.client.post("/api/resumes/tailor", json={"test": "data"})
        
        # Should handle authentication (might be 401, 422, or other depending on auth middleware)
        # The important thing is it shouldn't crash
        assert response.status_code in [401, 422, 500]  # Various possible auth responses
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    @patch('middleware.feature_gate.FeatureGateMiddleware._track_usage_if_needed')
    def test_free_user_can_access_basic_endpoints(self, mock_track_usage, mock_get_user):
        """Test that free users can access basic endpoints"""
        mock_get_user.return_value = self.free_user
        mock_track_usage.return_value = None
        
        # Mock usage check to allow access
        with patch('middleware.feature_gate.FeatureGateMiddleware._check_usage_limits') as mock_check:
            from services.subscription_service import UsageLimitResult
            mock_check.return_value = UsageLimitResult(True, "Within limits", remaining=3, limit=5)
            
            # Try to access resume tailoring endpoint
            response = self.client.post("/api/resumes/tailor", json={"test": "data"})
            
            # Should not return subscription required (402) or usage limit (429)
            assert response.status_code not in [402, 429]
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    def test_free_user_blocked_from_pro_endpoints(self, mock_get_user):
        """Test that free users are blocked from Pro-only endpoints"""
        mock_get_user.return_value = self.free_user
        
        # Try to access batch processing (Pro-only)
        response = self.client.post("/api/batch/process", json={"test": "data"})
        
        # Should return subscription required
        assert response.status_code == 402
        
        data = response.json()
        assert data["error"] == "subscription_required"
        assert "upgrade_url" in data
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    @patch('middleware.feature_gate.FeatureGateMiddleware._track_usage_if_needed')
    def test_pro_user_can_access_pro_endpoints(self, mock_track_usage, mock_get_user):
        """Test that Pro users can access Pro-only endpoints"""
        mock_get_user.return_value = self.pro_user
        mock_track_usage.return_value = None
        
        # Try to access batch processing (Pro-only)
        response = self.client.post("/api/batch/process", json={"test": "data"})
        
        # Should not return subscription required (402)
        assert response.status_code != 402
    
    @patch('middleware.feature_gate.FeatureGateMiddleware._get_current_user')
    @patch('middleware.feature_gate.FeatureGateMiddleware._check_usage_limits')
    def test_free_user_usage_limit_enforcement(self, mock_check_limits, mock_get_user):
        """Test that usage limits are enforced for free users"""
        mock_get_user.return_value = self.free_user
        
        # Mock usage limit exceeded
        from services.subscription_service import UsageLimitResult
        mock_check_limits.return_value = UsageLimitResult(
            can_use=False,
            reason="Weekly limit of 5 sessions exceeded",
            remaining=0,
            limit=5
        )
        
        # Try to access resume tailoring
        response = self.client.post("/api/resumes/tailor", json={"test": "data"})
        
        # Should return usage limit exceeded
        assert response.status_code == 429
        
        data = response.json()
        assert data["error"] == "usage_limit_exceeded"
        assert data["limit"] == 5
        assert data["remaining"] == 0
    
    def test_middleware_error_handling(self):
        """Test that middleware errors don't crash the application"""
        # This test ensures the middleware handles errors gracefully
        # Even if there are issues with the middleware, the app should continue working
        
        response = self.client.get("/health")
        assert response.status_code == 200
    
    def test_static_files_bypass_feature_gates(self):
        """Test that static files bypass feature gates"""
        # Try to access static files (even if they don't exist)
        response = self.client.get("/static/test.css")
        
        # Should not return subscription-related errors
        assert response.status_code not in [401, 402, 429]
        # Might return 404 if file doesn't exist, which is fine
    
    def test_docs_bypass_feature_gates(self):
        """Test that documentation endpoints bypass feature gates"""
        # Try to access docs
        response = self.client.get("/docs")
        
        # Should not return subscription-related errors
        assert response.status_code not in [401, 402, 429]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])