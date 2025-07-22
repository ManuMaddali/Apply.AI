"""
Simple tests for Feature Gate Middleware functionality
"""

import pytest
from unittest.mock import Mock, patch
from middleware.feature_gate import FeatureGateMiddleware, get_user_feature_access
from models.user import User, SubscriptionTier, SubscriptionStatus


def test_feature_gate_middleware_import():
    """Test that the middleware can be imported"""
    assert FeatureGateMiddleware is not None


def test_get_user_feature_access_free_user():
    """Test feature access for Free users"""
    # Create mock free user
    free_user = Mock(spec=User)
    free_user.is_pro_active.return_value = False
    
    access = get_user_feature_access(free_user)
    
    # Free users should have limited access
    assert access["bulk_processing"] is False
    assert access["advanced_formatting"] is False
    assert access["premium_templates"] is False
    assert access["cover_letters"] is False
    assert access["analytics"] is False
    assert access["heavy_tailoring"] is False
    assert access["unlimited_sessions"] is False


def test_get_user_feature_access_pro_user():
    """Test feature access for Pro users"""
    # Create mock pro user
    pro_user = Mock(spec=User)
    pro_user.is_pro_active.return_value = True
    
    access = get_user_feature_access(pro_user)
    
    # Pro users should have full access
    assert access["bulk_processing"] is True
    assert access["advanced_formatting"] is True
    assert access["premium_templates"] is True
    assert access["cover_letters"] is True
    assert access["analytics"] is True
    assert access["heavy_tailoring"] is True
    assert access["unlimited_sessions"] is True


def test_middleware_pattern_compilation():
    """Test that regex patterns compile correctly"""
    from fastapi import FastAPI
    
    app = FastAPI()
    middleware = FeatureGateMiddleware(app)
    
    # Check that patterns are compiled
    assert hasattr(middleware, 'pro_only_compiled')
    assert hasattr(middleware, 'usage_tracked_compiled')
    assert hasattr(middleware, 'bypass_compiled')
    assert hasattr(middleware, 'admin_bypass_compiled')
    
    # Check that patterns are not empty
    assert len(middleware.pro_only_compiled) > 0
    assert len(middleware.usage_tracked_compiled) > 0
    assert len(middleware.bypass_compiled) > 0


def test_bypass_endpoint_detection():
    """Test bypass endpoint detection"""
    from fastapi import FastAPI, Request
    from unittest.mock import Mock
    
    app = FastAPI()
    middleware = FeatureGateMiddleware(app)
    
    # Create mock requests for bypass endpoints
    bypass_endpoints = [
        "/health",
        "/api/auth/login",
        "/api/webhooks/stripe",
        "/docs",
        "/static/test.css"
    ]
    
    for endpoint in bypass_endpoints:
        mock_request = Mock(spec=Request)
        mock_request.url.path = endpoint
        
        should_bypass = middleware._should_bypass_feature_gate(mock_request)
        assert should_bypass, f"Endpoint {endpoint} should bypass feature gates"


def test_pro_only_endpoint_detection():
    """Test Pro-only endpoint detection"""
    from fastapi import FastAPI, Request
    from unittest.mock import Mock
    
    app = FastAPI()
    middleware = FeatureGateMiddleware(app)
    
    # Create mock requests for Pro-only endpoints
    pro_endpoints = [
        "/api/batch/process",
        "/api/resumes/advanced-format",
        "/api/analytics/dashboard"
    ]
    
    for endpoint in pro_endpoints:
        mock_request = Mock(spec=Request)
        mock_request.url.path = endpoint
        
        is_pro_only = middleware._is_pro_only_endpoint(mock_request)
        assert is_pro_only, f"Endpoint {endpoint} should require Pro subscription"


def test_usage_type_detection():
    """Test usage type detection for endpoints"""
    from fastapi import FastAPI, Request
    from unittest.mock import Mock
    from models.user import UsageType
    
    app = FastAPI()
    middleware = FeatureGateMiddleware(app)
    
    # Test usage-tracked endpoints
    usage_endpoints = [
        ("/api/resumes/tailor", UsageType.RESUME_PROCESSING),
        ("/api/batch/process", UsageType.BULK_PROCESSING),
        ("/api/resumes/cover-letter", UsageType.COVER_LETTER)
    ]
    
    for endpoint, expected_type in usage_endpoints:
        mock_request = Mock(spec=Request)
        mock_request.url.path = endpoint
        
        usage_type = middleware._get_usage_type_for_endpoint(mock_request)
        assert usage_type == expected_type, f"Endpoint {endpoint} should have usage type {expected_type}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])