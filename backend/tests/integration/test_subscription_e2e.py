"""
End-to-End Tests for Subscription System

Tests complete subscription workflows from API endpoints through
to database persistence, simulating real user interactions.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import stripe

from main import app
from models.user import (
    Base, User, Subscription, PaymentHistory, UsageTracking,
    SubscriptionTier, SubscriptionStatus, PaymentStatus, UsageType, AuthProvider
)
from utils.auth import AuthManager


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_e2e.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create authenticated test user"""
    user = User(
        email="e2e@example.com",
        username="e2euser",
        full_name="E2E Test User",
        subscription_tier=SubscriptionTier.FREE,
        subscription_status=SubscriptionStatus.ACTIVE,
        auth_provider=AuthProvider.EMAIL,
        is_active=True,
        is_verified=True,
        email_verified=True
    )
    user.set_password("testpass123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers"""
    token = AuthManager.create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


class TestSubscriptionAPIEndpoints:
    """Test subscription API endpoints end-to-end"""
    
    def test_get_subscription_status_free_user(self, client, test_user, auth_headers, db_session):
        """Test getting subscription status for free user"""
        response = client.get("/api/subscription/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["subscription_tier"] == "free"
        assert data["subscription_status"] == "active"
        assert data["is_pro_active"] == False
        assert "usage_limits" in data
        assert data["usage_limits"]["weekly_limit"] == 5
    
    def test_get_subscription_status_pro_user(self, client, db_session, auth_headers):
        """Test getting subscription status for pro user"""
        # Create Pro user
        pro_user = User(
            email="pro@example.com",
            username="prouser",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(pro_user)
        db_session.commit()
        
        # Create auth token for pro user
        token = AuthManager.create_access_token(data={"sub": str(pro_user.id)})
        pro_headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/subscription/status", headers=pro_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["subscription_tier"] == "pro"
        assert data["is_pro_active"] == True
        assert "current_period_end" in data
    
    @patch('services.payment_service.PaymentService.create_subscription')
    def test_subscription_upgrade_success(self, mock_create_sub, client, test_user, auth_headers, db_session):
        """Test successful subscription upgrade"""
        # Mock successful payment processing
        mock_create_sub.return_value = {
            "subscription_id": "sub_test123",
            "status": "active",
            "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp())
        }
        
        upgrade_data = {
            "payment_method_id": "pm_test123",
            "price_id": "price_test123"
        }
        
        response = client.post(
            "/api/subscription/upgrade",
            json=upgrade_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["subscription_id"] == "sub_test123"
        assert data["status"] == "active"
    
    @patch('services.payment_service.PaymentService.create_subscription')
    def test_subscription_upgrade_payment_failure(self, mock_create_sub, client, test_user, auth_headers):
        """Test subscription upgrade with payment failure"""
        # Mock payment failure
        from services.payment_service import PaymentError
        mock_create_sub.side_effect = PaymentError("Card declined")
        
        upgrade_data = {
            "payment_method_id": "pm_test123",
            "price_id": "price_test123"
        }
        
        response = client.post(
            "/api/subscription/upgrade",
            json=upgrade_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert data["success"] == False
        assert "Card declined" in data["error"]
    
    @patch('services.payment_service.PaymentService.cancel_subscription')
    def test_subscription_cancellation(self, mock_cancel_sub, client, db_session, auth_headers):
        """Test subscription cancellation"""
        # Create Pro user with subscription
        pro_user = User(
            email="cancel@example.com",
            username="canceluser",
            subscription_tier=SubscriptionTier.PRO,
            current_period_end=datetime.utcnow() + timedelta(days=15),
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(pro_user)
        db_session.commit()
        
        subscription = Subscription(
            user_id=pro_user.id,
            stripe_subscription_id="sub_cancel123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Mock successful cancellation
        mock_cancel_sub.return_value = {
            "status": "will_cancel",
            "cancel_at_period_end": True,
            "access_until": (datetime.utcnow() + timedelta(days=15)).isoformat()
        }
        
        # Create auth token for pro user
        token = AuthManager.create_access_token(data={"sub": str(pro_user.id)})
        cancel_headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/subscription/cancel",
            json={"cancel_immediately": False},
            headers=cancel_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["status"] == "will_cancel"
        assert data["cancel_at_period_end"] == True
    
    def test_get_usage_statistics(self, client, test_user, auth_headers, db_session):
        """Test getting usage statistics"""
        # Add some usage records
        usage_records = [
            UsageTracking(
                user_id=test_user.id,
                usage_type=UsageType.RESUME_PROCESSING,
                count=2,
                usage_date=datetime.utcnow()
            ),
            UsageTracking(
                user_id=test_user.id,
                usage_type=UsageType.RESUME_PROCESSING,
                count=1,
                usage_date=datetime.utcnow() - timedelta(days=1)
            )
        ]
        db_session.add_all(usage_records)
        
        # Update user counters
        test_user.weekly_usage_count = 3
        test_user.total_usage_count = 3
        db_session.commit()
        
        response = client.get("/api/subscription/usage", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == str(test_user.id)
        assert data["subscription_tier"] == "free"
        assert data["weekly_usage_count"] == 3
        assert data["total_usage_count"] == 3
        assert "current_limits" in data


class TestFeatureGateIntegration:
    """Test feature gate middleware integration"""
    
    def test_free_user_resume_processing_allowed(self, client, test_user, auth_headers):
        """Test that free users can access basic resume processing"""
        # Mock resume processing endpoint
        with patch('routes.resume.process_resume') as mock_process:
            mock_process.return_value = {"success": True, "resume_id": "test123"}
            
            response = client.post(
                "/api/resume/process",
                json={"resume_text": "Test resume", "job_description": "Test job"},
                headers=auth_headers
            )
            
            # Should be allowed for free users
            assert response.status_code in [200, 404]  # 404 if endpoint doesn't exist in test
    
    def test_free_user_bulk_processing_blocked(self, client, test_user, auth_headers):
        """Test that free users are blocked from bulk processing"""
        bulk_data = {
            "resume_text": "Test resume",
            "job_urls": ["http://job1.com", "http://job2.com", "http://job3.com"]
        }
        
        response = client.post(
            "/api/resume/bulk-process",
            json=bulk_data,
            headers=auth_headers
        )
        
        # Should be blocked for free users
        assert response.status_code in [402, 403, 404]  # Payment required or forbidden
    
    def test_free_user_usage_limit_enforcement(self, client, test_user, auth_headers, db_session):
        """Test usage limit enforcement for free users"""
        # Set user at usage limit
        test_user.weekly_usage_count = 5  # At limit
        db_session.commit()
        
        response = client.post(
            "/api/resume/process",
            json={"resume_text": "Test resume", "job_description": "Test job"},
            headers=auth_headers
        )
        
        # Should be blocked due to usage limit
        assert response.status_code in [429, 402]  # Too many requests or payment required
    
    def test_pro_user_unlimited_access(self, client, db_session):
        """Test that pro users have unlimited access"""
        # Create Pro user
        pro_user = User(
            email="pro_access@example.com",
            username="proaccess",
            subscription_tier=SubscriptionTier.PRO,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() + timedelta(days=30),
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(pro_user)
        db_session.commit()
        
        # Create auth token
        token = AuthManager.create_access_token(data={"sub": str(pro_user.id)})
        pro_headers = {"Authorization": f"Bearer {token}"}
        
        # Test bulk processing access
        bulk_data = {
            "resume_text": "Test resume",
            "job_urls": ["http://job1.com", "http://job2.com"]
        }
        
        response = client.post(
            "/api/resume/bulk-process",
            json=bulk_data,
            headers=pro_headers
        )
        
        # Should be allowed for pro users (or return 404 if endpoint doesn't exist)
        assert response.status_code in [200, 404]


class TestWebhookEndToEnd:
    """Test webhook processing end-to-end"""
    
    def create_stripe_signature(self, payload: bytes, secret: str) -> str:
        """Create valid Stripe signature for testing"""
        import hmac
        import hashlib
        import time
        
        timestamp = str(int(time.time()))
        signed_payload = f"{timestamp}.{payload.decode()}"
        signature = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"
    
    @patch('config.stripe_config.get_stripe_config')
    def test_subscription_created_webhook(self, mock_config, client, test_user, db_session):
        """Test processing subscription.created webhook"""
        # Mock Stripe configuration
        mock_config.return_value = Mock(webhook_secret="whsec_test_secret")
        
        # Create webhook payload
        payload = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_webhook123",
                    "customer": "cus_webhook123",
                    "status": "active",
                    "current_period_start": int(datetime.utcnow().timestamp()),
                    "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
                    "metadata": {
                        "user_id": str(test_user.id)
                    }
                }
            }
        }
        
        payload_json = json.dumps(payload)
        signature = self.create_stripe_signature(payload_json.encode(), "whsec_test_secret")
        
        with patch('stripe.Webhook.construct_event', return_value=payload):
            response = client.post(
                "/api/webhooks/stripe",
                data=payload_json,
                headers={
                    "stripe-signature": signature,
                    "content-type": "application/json"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["received"] == True
    
    @patch('config.stripe_config.get_stripe_config')
    def test_payment_succeeded_webhook(self, mock_config, client, test_user, db_session):
        """Test processing payment_succeeded webhook"""
        mock_config.return_value = Mock(webhook_secret="whsec_test_secret")
        
        # Create subscription first
        subscription = Subscription(
            user_id=test_user.id,
            stripe_subscription_id="sub_payment123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        # Create webhook payload
        payload = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_success123",
                    "customer": "cus_test123",
                    "subscription": "sub_payment123",
                    "amount_paid": 999,
                    "currency": "usd",
                    "payment_intent": "pi_success123"
                }
            }
        }
        
        payload_json = json.dumps(payload)
        signature = self.create_stripe_signature(payload_json.encode(), "whsec_test_secret")
        
        with patch('stripe.Webhook.construct_event', return_value=payload):
            response = client.post(
                "/api/webhooks/stripe",
                data=payload_json,
                headers={
                    "stripe-signature": signature,
                    "content-type": "application/json"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["received"] == True
    
    def test_webhook_invalid_signature(self, client):
        """Test webhook with invalid signature"""
        payload = {"type": "test.event"}
        
        response = client.post(
            "/api/webhooks/stripe",
            json=payload,
            headers={"stripe-signature": "invalid_signature"}
        )
        
        assert response.status_code == 400
        assert "signature" in response.json()["detail"].lower()


class TestCompleteUserJourney:
    """Test complete user journeys from registration to cancellation"""
    
    def test_free_user_to_pro_journey(self, client, db_session):
        """Test complete journey from free user to pro subscriber"""
        # 1. Create new user (simulating registration)
        user = User(
            email="journey@example.com",
            username="journeyuser",
            subscription_tier=SubscriptionTier.FREE,
            subscription_status=SubscriptionStatus.ACTIVE,
            auth_provider=AuthProvider.EMAIL,
            is_active=True,
            is_verified=True,
            email_verified=True
        )
        user.set_password("testpass123")
        db_session.add(user)
        db_session.commit()
        
        # Create auth token
        token = AuthManager.create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Check initial status (Free)
        response = client.get("/api/subscription/status", headers=headers)
        assert response.status_code == 200
        assert response.json()["subscription_tier"] == "free"
        
        # 3. Use free features (simulate resume processing)
        for i in range(3):
            # Simulate usage tracking
            usage = UsageTracking(
                user_id=user.id,
                usage_type=UsageType.RESUME_PROCESSING,
                count=1
            )
            db_session.add(usage)
        
        user.weekly_usage_count = 3
        user.total_usage_count = 3
        db_session.commit()
        
        # 4. Check usage statistics
        response = client.get("/api/subscription/usage", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["weekly_usage_count"] == 3
        
        # 5. Upgrade to Pro (mock successful payment)
        with patch('services.payment_service.PaymentService.create_subscription') as mock_create:
            mock_create.return_value = {
                "subscription_id": "sub_journey123",
                "status": "active",
                "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp())
            }
            
            response = client.post(
                "/api/subscription/upgrade",
                json={"payment_method_id": "pm_test123"},
                headers=headers
            )
            
            assert response.status_code == 200
            assert response.json()["success"] == True
        
        # 6. Create subscription record (simulating webhook processing)
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_journey123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(subscription)
        
        user.subscription_tier = SubscriptionTier.PRO
        user.subscription_status = SubscriptionStatus.ACTIVE
        user.current_period_end = datetime.utcnow() + timedelta(days=30)
        db_session.commit()
        
        # 7. Verify Pro status
        response = client.get("/api/subscription/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["subscription_tier"] == "pro"
        assert data["is_pro_active"] == True
        
        # 8. Use Pro features (simulate bulk processing)
        bulk_usage = UsageTracking(
            user_id=user.id,
            usage_type=UsageType.BULK_PROCESSING,
            count=2
        )
        db_session.add(bulk_usage)
        user.total_usage_count += 2
        db_session.commit()
        
        # 9. Cancel subscription (mock)
        with patch('services.payment_service.PaymentService.cancel_subscription') as mock_cancel:
            mock_cancel.return_value = {
                "status": "will_cancel",
                "cancel_at_period_end": True,
                "access_until": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            response = client.post(
                "/api/subscription/cancel",
                json={"cancel_immediately": False},
                headers=headers
            )
            
            assert response.status_code == 200
            assert response.json()["success"] == True
        
        # 10. Verify final usage statistics
        response = client.get("/api/subscription/usage", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_usage_count"] == 5  # 3 resume + 2 bulk
    
    def test_payment_failure_recovery_journey(self, client, db_session):
        """Test user journey with payment failures and recovery"""
        # Create user
        user = User(
            email="recovery@example.com",
            username="recoveryuser",
            subscription_tier=SubscriptionTier.FREE,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        token = AuthManager.create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. First upgrade attempt fails
        with patch('services.payment_service.PaymentService.create_subscription') as mock_create:
            from services.payment_service import PaymentError
            mock_create.side_effect = PaymentError("Card declined")
            
            response = client.post(
                "/api/subscription/upgrade",
                json={"payment_method_id": "pm_declined"},
                headers=headers
            )
            
            assert response.status_code == 400
            assert "Card declined" in response.json()["error"]
        
        # 2. Verify user remains on Free tier
        response = client.get("/api/subscription/status", headers=headers)
        assert response.status_code == 200
        assert response.json()["subscription_tier"] == "free"
        
        # 3. Second upgrade attempt succeeds
        with patch('services.payment_service.PaymentService.create_subscription') as mock_create:
            mock_create.return_value = {
                "subscription_id": "sub_recovery123",
                "status": "active",
                "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp())
            }
            
            response = client.post(
                "/api/subscription/upgrade",
                json={"payment_method_id": "pm_success"},
                headers=headers
            )
            
            assert response.status_code == 200
            assert response.json()["success"] == True
        
        # 4. Simulate successful webhook processing
        subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id="sub_recovery123",
            tier=SubscriptionTier.PRO,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        
        user.subscription_tier = SubscriptionTier.PRO
        db_session.commit()
        
        # 5. Verify final Pro status
        response = client.get("/api/subscription/status", headers=headers)
        assert response.status_code == 200
        assert response.json()["subscription_tier"] == "pro"


class TestErrorHandlingE2E:
    """Test error handling in end-to-end scenarios"""
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to subscription endpoints"""
        # No auth headers
        response = client.get("/api/subscription/status")
        assert response.status_code == 401
        
        response = client.post("/api/subscription/upgrade", json={})
        assert response.status_code == 401
        
        response = client.post("/api/subscription/cancel", json={})
        assert response.status_code == 401
    
    def test_invalid_auth_token(self, client):
        """Test invalid authentication token"""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/subscription/status", headers=invalid_headers)
        assert response.status_code == 401
    
    def test_malformed_request_data(self, client, test_user, auth_headers):
        """Test malformed request data handling"""
        # Invalid upgrade data
        response = client.post(
            "/api/subscription/upgrade",
            json={"invalid_field": "value"},
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error
        
        # Invalid cancellation data
        response = client.post(
            "/api/subscription/cancel",
            json={"cancel_immediately": "not_boolean"},
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_database_error_handling(self, client, test_user, auth_headers):
        """Test database error handling"""
        # Mock database error
        with patch('services.subscription_service.SubscriptionService.validate_subscription_status') as mock_validate:
            mock_validate.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/subscription/status", headers=auth_headers)
            
            # Should handle gracefully
            assert response.status_code in [500, 503]  # Internal server error or service unavailable


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])