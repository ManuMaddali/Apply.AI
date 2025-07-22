# Payment Service Integration Guide

This document provides comprehensive guidance for integrating the PaymentService with Stripe for subscription management.

## Overview

The PaymentService provides a complete Stripe integration for handling:
- Customer creation and management
- Subscription creation and cancellation
- Payment method handling and validation
- Secure payment intent creation for subscription upgrades
- Error handling for payment failures and retries
- Webhook processing for real-time subscription updates

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PRICE_ID_PRO_MONTHLY=price_your_pro_monthly_price_id_here
```

### Production vs Development

The service automatically detects the environment and validates key formats:
- **Development**: Uses `sk_test_` and `pk_test_` keys
- **Production**: Requires `sk_live_` and `pk_live_` keys

## Basic Usage

### Initialize the Service

```python
from services.payment_service import PaymentService
from sqlalchemy.orm import Session

# Initialize with database session
payment_service = PaymentService(db_session)
```

### Customer Management

```python
# Create a new Stripe customer
customer_id = await payment_service.create_customer(user)

# Update customer information
await payment_service.update_customer(
    customer_id, 
    name="New Name",
    email="new@email.com"
)

# Retrieve customer information
customer = await payment_service.get_customer(customer_id)
```

### Subscription Management

```python
# Create a Pro subscription
result = await payment_service.create_subscription(
    user_id=str(user.id),
    payment_method_id="pm_1234567890"
)

if result['status'] == 'active':
    print("Subscription activated immediately")
elif result['status'] == 'requires_payment_confirmation':
    # Handle 3D Secure or other authentication
    client_secret = result['client_secret']
    # Send client_secret to frontend for confirmation

# Cancel subscription immediately
await payment_service.cancel_subscription(
    user_id=str(user.id),
    cancel_immediately=True
)

# Cancel at period end
await payment_service.cancel_subscription(
    user_id=str(user.id),
    cancel_immediately=False
)
```

### Payment Methods

```python
# Get customer's payment methods
payment_methods = await payment_service.get_payment_methods(customer_id)

# Add new payment method
await payment_service.add_payment_method(
    customer_id=customer_id,
    payment_method_id="pm_new_method",
    set_as_default=True
)

# Remove payment method
await payment_service.remove_payment_method("pm_old_method")
```

### Payment Intents

```python
# Create payment intent for one-time payment
intent = await payment_service.create_payment_intent(
    amount=999,  # $9.99 in cents
    currency='usd',
    customer_id=customer_id
)

# Confirm payment intent
result = await payment_service.confirm_payment_intent(
    payment_intent_id=intent['id'],
    payment_method_id="pm_1234567890"
)
```

## Error Handling

The service provides comprehensive error handling with custom `PaymentError` exceptions:

```python
from services.payment_service import PaymentError

try:
    await payment_service.create_subscription(user_id, payment_method_id)
except PaymentError as e:
    if e.stripe_error:
        # Handle specific Stripe errors
        if isinstance(e.stripe_error, stripe.error.CardError):
            print(f"Card declined: {e.stripe_error.user_message}")
        elif isinstance(e.stripe_error, stripe.error.RateLimitError):
            print("Rate limit exceeded, retry later")
    else:
        print(f"Payment error: {e.message}")
```

### Retry Logic

The service includes automatic retry logic for failed payments:

```python
# Retry failed payment with exponential backoff
try:
    result = await payment_service.retry_failed_payment(
        payment_intent_id="pi_failed_payment",
        max_retries=3
    )
except PaymentError as e:
    print(f"Payment failed after retries: {e.message}")
```

## Webhook Integration

### Setting Up Webhooks

1. In your Stripe Dashboard, create a webhook endpoint pointing to your server
2. Add the webhook secret to your environment variables
3. Configure the webhook to send these events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### Webhook Handler

```python
from fastapi import Request, HTTPException

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    try:
        result = await payment_service.handle_webhook(payload, signature)
        return {"status": "success", "result": result}
    except PaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Database Integration

The PaymentService automatically manages database records:

### Subscription Records
- Creates `Subscription` records for new subscriptions
- Updates subscription status from webhooks
- Maintains sync between Stripe and local database

### Payment History
- Records successful payments
- Tracks failed payment attempts
- Stores payment metadata for auditing

### User Updates
- Updates user subscription tier and status
- Manages subscription period dates
- Tracks usage limits and preferences

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
python -m pytest test_payment_service.py -v
```

### Validation Script

Validate the implementation without API keys:

```bash
python validate_payment_service.py
```

### Stripe Test Mode

Use Stripe's test mode for development:

```bash
# Test card numbers
4242424242424242  # Visa - succeeds
4000000000000002  # Visa - declined
4000000000009995  # Visa - insufficient funds
```

## Security Considerations

### API Key Management
- Never commit API keys to version control
- Use environment variables for all sensitive data
- Rotate keys regularly in production

### Webhook Security
- Always verify webhook signatures
- Use HTTPS endpoints for webhooks
- Implement idempotency for webhook handlers

### Payment Data
- Never store raw payment method details
- Use Stripe's secure tokenization
- Implement proper access controls

## Monitoring and Logging

The service includes comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment_service")

# Logs include:
# - Customer creation/updates
# - Subscription lifecycle events
# - Payment successes/failures
# - Webhook processing
# - Error conditions
```

## Common Integration Patterns

### Subscription Upgrade Flow

```python
async def upgrade_user_to_pro(user_id: str, payment_method_id: str):
    try:
        # Create subscription
        result = await payment_service.create_subscription(
            user_id=user_id,
            payment_method_id=payment_method_id
        )
        
        if result['status'] == 'active':
            # Subscription is active immediately
            return {"success": True, "message": "Upgraded to Pro!"}
        elif result['status'] == 'requires_payment_confirmation':
            # Need 3D Secure confirmation
            return {
                "success": False,
                "requires_confirmation": True,
                "client_secret": result['client_secret']
            }
        else:
            return {"success": False, "message": "Subscription creation failed"}
            
    except PaymentError as e:
        return {"success": False, "message": str(e)}
```

### Subscription Status Check

```python
async def check_subscription_status(user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user.subscription_tier == SubscriptionTier.PRO:
        if user.is_pro_active():
            return {"status": "active", "tier": "pro"}
        else:
            # Subscription expired, sync with Stripe
            subscription = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).first()
            
            if subscription:
                await payment_service.update_subscription_status(
                    subscription.stripe_subscription_id
                )
    
    return {"status": "free", "tier": "free"}
```

## Troubleshooting

### Common Issues

1. **Invalid API Keys**
   - Verify keys are correct for your environment
   - Check key permissions in Stripe Dashboard

2. **Webhook Signature Verification Failed**
   - Ensure webhook secret matches Stripe Dashboard
   - Verify endpoint URL is accessible

3. **Payment Method Declined**
   - Use test card numbers in development
   - Check card details and billing address

4. **Subscription Not Created**
   - Verify price ID exists in Stripe
   - Check customer has valid payment method

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.getLogger("payment_service").setLevel(logging.DEBUG)
```

## Next Steps

1. **Set up Stripe Account**
   - Create Stripe account
   - Get API keys
   - Create product and price for Pro subscription

2. **Configure Environment**
   - Add API keys to environment variables
   - Set up webhook endpoint

3. **Test Integration**
   - Run validation script
   - Test with Stripe test mode
   - Verify webhook processing

4. **Deploy to Production**
   - Use live API keys
   - Configure production webhook endpoint
   - Monitor payment processing

## Support

For issues with the PaymentService implementation:
1. Check the validation script output
2. Review error logs
3. Verify Stripe Dashboard for payment details
4. Test with Stripe's test mode first

For Stripe-specific issues:
- Consult Stripe Documentation: https://stripe.com/docs
- Use Stripe's test mode for development
- Contact Stripe Support for API issues