"""
Test webhook integration - Basic tests for webhook functionality

This test file verifies that the webhook endpoint is properly configured
and can handle basic webhook events.
"""

import pytest
import json
import hmac
import hashlib
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from services.payment_service import PaymentService
from config.stripe_config import get_stripe_config

client = TestClient(app)


def create_stripe_signature(payload: bytes, secret: str) -> str:
    """Create a valid Stripe signature for testing"""
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode()}"
    signature = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


class TestWebhookEndpoint:
    """Test webhook endpoint functionality"""
    
    def test_webhook_endpoint_exists(self):
        """Test that webhook endpoint is accessible"""
        # Test with invalid signature to verify endpoint exists
        response = client.post(
            "/api/webhooks/stripe",
            json={"type": "test"},
            headers={"stripe-signature": "invalid"}
        )
        
        # Should return 400 for missing/invalid signature, not 404
        assert response.status_code in [400, 500]  # Not 404
    
    def test_webhook_missing_signature(self):
        """Test webhook with missing signature header"""
        response = client.post(
            "/api/webhooks/stripe",
            json={"type": "test"}
        )
        
        assert response.status_code == 400
        assert "Missing Stripe signature header" in response.json()["detail"]
    
    @patch('services.payment_service.PaymentService.handle_webhook')
    def test_webhook_processing_success(self, mock_handle_webhook):
        """Test successful webhook processing"""
        # Mock successful webhook processing
        mock_handle_webhook.return_value = {
            "status": "processed",
            "action": "subscription_created"
        }
        
        # Create test payload
        payload = json.dumps({
            "type": "customer.subscription.created",
            "data": {"object": {"id": "sub_test"}}
        })
        
        # Create valid signature (using test secret)
        test_secret = "whsec_test_secret"
        signature = create_stripe_signature(payload.encode(), test_secret)
        
        with patch('config.stripe_config.get_stripe_config') as mock_config:
            mock_config.return_value.webhook_secret = test_secret
            
            response = client.post(
                "/api/webhooks/stripe",
                data=payload,
                headers={
                    "stripe-signature": signature,
                    "content-type": "application/json"
                }
            )
        
        assert response.status_code == 200
        assert response.json()["received"] == True
    
    def test_webhook_test_endpoint(self):
        """Test webhook test endpoint"""
        with patch('config.stripe_config.get_stripe_config') as mock_config:
            mock_config.return_value.is_production = False
            mock_config.return_value.environment = "development"
            mock_config.return_value.webhook_secret = "whsec_test"
            
            response = client.get("/api/webhooks/stripe/test")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "supported_events" in data
            assert data["webhook_configured"] == True
    
    def test_webhook_health_check(self):
        """Test webhook health check endpoint"""
        with patch('config.stripe_config.get_stripe_config') as mock_config:
            mock_config.return_value.webhook_secret = "whsec_test"
            mock_config.return_value.is_configured = True
            mock_config.return_value.environment = "test"
            
            response = client.get("/api/webhooks/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["webhook_configured"] == True
            assert data["stripe_configured"] == True


class TestWebhookEventHandling:
    """Test specific webhook event handling"""
    
    @pytest.fixture
    def mock_payment_service(self):
        """Create mock payment service"""
        with patch('services.payment_service.PaymentService') as mock:
            service = MagicMock()
            mock.return_value = service
            yield service
    
    def test_subscription_created_event(self, mock_payment_service):
        """Test subscription.created webhook event"""
        # Mock the webhook handler
        mock_payment_service.handle_webhook.return_value = {
            "status": "processed",
            "action": "subscription_created"
        }
        
        payload = json.dumps({
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test123",
                    "customer": "cus_test123",
                    "status": "active",
                    "metadata": {"user_id": "user_123"}
                }
            }
        })
        
        test_secret = "whsec_test_secret"
        signature = create_stripe_signature(payload.encode(), test_secret)
        
        with patch('config.stripe_config.get_stripe_config') as mock_config:
            mock_config.return_value.webhook_secret = test_secret
            
            response = client.post(
                "/api/webhooks/stripe",
                data=payload,
                headers={
                    "stripe-signature": signature,
                    "content-type": "application/json"
                }
            )
        
        assert response.status_code == 200
        assert response.json()["received"] == True
    
    def test_payment_succeeded_event(self, mock_payment_service):
        """Test invoice.payment_succeeded webhook event"""
        mock_payment_service.handle_webhook.return_value = {
            "status": "processed",
            "action": "payment_recorded"
        }
        
        payload = json.dumps({
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "amount_paid": 999,
                    "currency": "usd"
                }
            }
        })
        
        test_secret = "whsec_test_secret"
        signature = create_stripe_signature(payload.encode(), test_secret)
        
        with patch('config.stripe_config.get_stripe_config') as mock_config:
            mock_config.return_value.webhook_secret = test_secret
            
            response = client.post(
                "/api/webhooks/stripe",
                data=payload,
                headers={
                    "stripe-signature": signature,
                    "content-type": "application/json"
                }
            )
        
        assert response.status_code == 200
        assert response.json()["received"] == True
    
    def test_payment_failed_event(self, mock_payment_service):
        """Test invoice.payment_failed webhook event"""
        mock_payment_service.handle_webhook.return_value = {
            "status": "processed",
            "action": "payment_failure_recorded"
        }
        
        payload = json.dumps({
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test123",
                    "customer": "cus_test123",
                    "amount_due": 999,
                    "currency": "usd"
                }
            }
        })
        
        test_secret = "whsec_test_secret"
        signature = create_stripe_signature(payload.encode(), test_secret)
        
        with patch('config.stripe_config.get_stripe_config') as mock_config:
            mock_config.return_value.webhook_secret = test_secret
            
            response = client.post(
                "/api/webhooks/stripe",
                data=payload,
                headers={
                    "stripe-signature": signature,
                    "content-type": "application/json"
                }
            )
        
        assert response.status_code == 200
        assert response.json()["received"] == True


if __name__ == "__main__":
    # Run basic tests
    print("Testing webhook endpoint...")
    
    # Test endpoint exists
    response = client.get("/api/webhooks/health")
    print(f"Health check: {response.status_code}")
    
    # Test webhook test endpoint
    try:
        response = client.get("/api/webhooks/stripe/test")
        print(f"Test endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ Webhook endpoints are accessible")
        else:
            print("❌ Webhook test endpoint failed")
    except Exception as e:
        print(f"❌ Error testing webhook endpoints: {e}")
    
    print("Basic webhook tests completed.")