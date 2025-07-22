"""
Payment Service - Stripe integration for subscription management

This service handles all payment-related operations including:
- Stripe customer creation and management
- Subscription creation and cancellation
- Payment method handling and validation
- Secure payment intent creation for subscription upgrades
- Error handling for payment failures and retries
"""

import stripe
import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.user import (
    User, Subscription, PaymentHistory,
    SubscriptionTier, SubscriptionStatus, PaymentStatus
)
from config.stripe_config import get_stripe_config, StripeConfig
from utils.subscription_logger import subscription_logger, log_payment_success, log_payment_failure, EventCategory

logger = logging.getLogger(__name__)


class PaymentError(Exception):
    """Custom exception for payment-related errors"""
    def __init__(self, message: str, stripe_error: Optional[stripe.error.StripeError] = None):
        self.message = message
        self.stripe_error = stripe_error
        super().__init__(self.message)


class PaymentService:
    """Service for handling Stripe payment processing and subscription management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Load Stripe configuration
        self.config = get_stripe_config()
        
        # Initialize Stripe with API keys
        self.stripe_secret_key = self.config.secret_key
        self.stripe_publishable_key = self.config.publishable_key
        self.webhook_secret = self.config.webhook_secret
        self.pro_monthly_price_id = self.config.pro_monthly_price_id
        
        stripe.api_key = self.stripe_secret_key
        
        logger.info(f"PaymentService initialized with Stripe configuration for {self.config.environment} environment")
    
    # Customer Management
    
    async def create_customer(self, user: User) -> str:
        """Create a Stripe customer for the user"""
        try:
            # Check if customer already exists
            if user.stripe_customer_id:
                try:
                    # Verify customer exists in Stripe
                    customer = stripe.Customer.retrieve(user.stripe_customer_id)
                    if customer and not customer.get('deleted'):
                        logger.info(f"Customer already exists for user {user.id}: {user.stripe_customer_id}")
                        return user.stripe_customer_id
                except stripe.error.InvalidRequestError:
                    # Customer doesn't exist in Stripe, create new one
                    logger.warning(f"Stripe customer {user.stripe_customer_id} not found, creating new one")
                    user.stripe_customer_id = None
            
            # Create new Stripe customer
            customer_data = {
                'email': user.email,
                'name': user.full_name or user.username or user.email.split('@')[0],
                'metadata': {
                    'user_id': str(user.id),
                    'created_via': 'payment_service'
                }
            }
            
            if user.phone:
                customer_data['phone'] = user.phone
            
            customer = stripe.Customer.create(**customer_data)
            
            # Update user with customer ID
            user.stripe_customer_id = customer.id
            self.db.commit()
            
            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            
            # Log customer creation event
            subscription_logger.log_subscription_event(
                event_type="customer_created",
                category=EventCategory.PAYMENT,
                user_id=str(user.id),
                details={
                    "stripe_customer_id": customer.id,
                    "customer_email": user.email
                }
            )
            
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer for user {user.id}: {e}")
            raise PaymentError(f"Failed to create customer: {str(e)}", e)
        except Exception as e:
            logger.error(f"Error creating customer for user {user.id}: {e}")
            raise PaymentError(f"Failed to create customer: {str(e)}")
    
    async def update_customer(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Update Stripe customer information"""
        try:
            customer = stripe.Customer.modify(customer_id, **kwargs)
            logger.info(f"Updated Stripe customer {customer_id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating customer {customer_id}: {e}")
            raise PaymentError(f"Failed to update customer: {str(e)}", e)
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve Stripe customer information"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            if customer.get('deleted'):
                return None
            return customer
            
        except stripe.error.InvalidRequestError:
            logger.warning(f"Stripe customer {customer_id} not found")
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving customer {customer_id}: {e}")
            raise PaymentError(f"Failed to retrieve customer: {str(e)}", e)
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve Stripe subscription information"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            if subscription.get('status') == 'canceled' and subscription.get('canceled_at'):
                # Return canceled subscriptions for status sync
                return subscription
            return subscription
            
        except stripe.error.InvalidRequestError:
            logger.warning(f"Stripe subscription {subscription_id} not found")
            return None
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription {subscription_id}: {e}")
            raise PaymentError(f"Failed to retrieve subscription: {str(e)}", e)
    
    # Subscription Management
    
    async def create_subscription(
        self,
        user_id: str,
        payment_method_id: str,
        price_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new subscription for the user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise PaymentError("User not found")
            
            # Ensure customer exists
            customer_id = await self.create_customer(user)
            
            # Use default Pro monthly price if not specified
            if not price_id:
                price_id = self.pro_monthly_price_id
                if not price_id:
                    raise PaymentError("No price ID configured for Pro subscription")
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            
            # Create subscription
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': 'default_incomplete',
                'payment_settings': {'save_default_payment_method': 'on_subscription'},
                'expand': ['latest_invoice.payment_intent'],
                'metadata': {
                    'user_id': str(user_id),
                    'tier': 'pro'
                }
            }
            
            subscription = stripe.Subscription.create(**subscription_data)
            
            # Handle subscription status
            if subscription.status == 'incomplete':
                # Payment requires confirmation
                payment_intent = subscription.latest_invoice.payment_intent
                return {
                    'subscription_id': subscription.id,
                    'client_secret': payment_intent.client_secret,
                    'status': 'requires_payment_confirmation',
                    'payment_intent_id': payment_intent.id
                }
            elif subscription.status == 'active':
                # Subscription is immediately active
                await self._handle_successful_subscription(user, subscription)
                
                # Log successful subscription creation
                log_payment_success(
                    user_id=str(user_id),
                    payment_intent_id=subscription.latest_invoice.payment_intent.id if subscription.latest_invoice else "immediate",
                    amount=9.99  # Default Pro price
                )
                
                return {
                    'subscription_id': subscription.id,
                    'status': 'active',
                    'current_period_end': subscription.current_period_end
                }
            else:
                # Handle other statuses
                return {
                    'subscription_id': subscription.id,
                    'status': subscription.status,
                    'error': f'Subscription created with status: {subscription.status}'
                }
                
        except stripe.error.CardError as e:
            logger.error(f"Card error creating subscription for user {user_id}: {e}")
            await self._record_payment_failure(user_id, str(e), payment_method_id)
            
            # Log payment failure with detailed information
            log_payment_failure(
                user_id=str(user_id),
                error_code=e.code or "card_error",
                error_message=e.user_message or str(e),
                payment_method_id=payment_method_id,
                amount=9.99  # Default Pro price
            )
            
            raise PaymentError(f"Payment failed: {e.user_message}", e)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription for user {user_id}: {e}")
            raise PaymentError(f"Payment processing failed: {str(e)}", e)
        except Exception as e:
            logger.error(f"Error creating subscription for user {user_id}: {e}")
            raise PaymentError(f"Failed to create subscription: {str(e)}")
    
    async def cancel_subscription(
        self,
        user_id: str,
        cancel_immediately: bool = False
    ) -> Dict[str, Any]:
        """Cancel user's subscription"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise PaymentError("User not found")
            
            # Find active subscription
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).first()
            
            if not subscription or not subscription.stripe_subscription_id:
                raise PaymentError("No active subscription found")
            
            # Cancel in Stripe
            if cancel_immediately:
                # Cancel immediately
                stripe_subscription = stripe.Subscription.delete(
                    subscription.stripe_subscription_id
                )
                
                # Update local records immediately
                await self._handle_subscription_cancellation(user, stripe_subscription, immediate=True)
                
                return {
                    'status': 'canceled',
                    'canceled_at': datetime.utcnow().isoformat(),
                    'access_until': datetime.utcnow().isoformat()
                }
            else:
                # Cancel at period end
                stripe_subscription = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                
                # Update local records
                subscription.cancel_at_period_end = True
                user.cancel_at_period_end = True
                self.db.commit()
                
                return {
                    'status': 'will_cancel',
                    'cancel_at_period_end': True,
                    'access_until': datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat()
                }
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription for user {user_id}: {e}")
            raise PaymentError(f"Failed to cancel subscription: {str(e)}", e)
        except Exception as e:
            logger.error(f"Error canceling subscription for user {user_id}: {e}")
            raise PaymentError(f"Failed to cancel subscription: {str(e)}")
    
    async def update_subscription_status(
        self,
        stripe_subscription_id: str,
        status: Optional[str] = None
    ) -> Optional[Subscription]:
        """Update subscription status from Stripe webhook or manual sync"""
        try:
            # Get subscription from Stripe
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            
            # Find local subscription
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_subscription_id
            ).first()
            
            if not subscription:
                logger.warning(f"Local subscription not found for Stripe subscription {stripe_subscription_id}")
                return None
            
            # Update status based on Stripe data
            new_status = self._map_stripe_status(stripe_subscription.status)
            subscription.status = new_status
            subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
            subscription.cancel_at_period_end = stripe_subscription.cancel_at_period_end or False
            
            # Update user record
            user = self.db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                user.subscription_status = new_status
                user.current_period_start = subscription.current_period_start
                user.current_period_end = subscription.current_period_end
                user.cancel_at_period_end = subscription.cancel_at_period_end
                
                # Update tier based on status
                if new_status == SubscriptionStatus.ACTIVE:
                    user.subscription_tier = SubscriptionTier.PRO
                elif new_status in [SubscriptionStatus.CANCELED, SubscriptionStatus.UNPAID]:
                    user.subscription_tier = SubscriptionTier.FREE
            
            self.db.commit()
            
            logger.info(f"Updated subscription {stripe_subscription_id} status to {new_status.value}")
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating subscription {stripe_subscription_id}: {e}")
            raise PaymentError(f"Failed to update subscription: {str(e)}", e)
        except Exception as e:
            logger.error(f"Error updating subscription {stripe_subscription_id}: {e}")
            raise PaymentError(f"Failed to update subscription: {str(e)}")
    
    # Payment Method Management
    
    async def get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer's payment methods"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            
            return [
                {
                    'id': pm.id,
                    'type': pm.type,
                    'card': {
                        'brand': pm.card.brand,
                        'last4': pm.card.last4,
                        'exp_month': pm.card.exp_month,
                        'exp_year': pm.card.exp_year
                    } if pm.card else None,
                    'created': pm.created
                }
                for pm in payment_methods.data
            ]
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting payment methods for customer {customer_id}: {e}")
            raise PaymentError(f"Failed to get payment methods: {str(e)}", e)
    
    async def add_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
        set_as_default: bool = False
    ) -> Dict[str, Any]:
        """Add payment method to customer"""
        try:
            # Attach payment method
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Set as default if requested
            if set_as_default:
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={'default_payment_method': payment_method_id}
                )
            
            logger.info(f"Added payment method {payment_method_id} to customer {customer_id}")
            return payment_method
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error adding payment method {payment_method_id} to customer {customer_id}: {e}")
            raise PaymentError(f"Failed to add payment method: {str(e)}", e)
    
    async def remove_payment_method(self, payment_method_id: str) -> bool:
        """Remove payment method"""
        try:
            stripe.PaymentMethod.detach(payment_method_id)
            logger.info(f"Removed payment method {payment_method_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error removing payment method {payment_method_id}: {e}")
            raise PaymentError(f"Failed to remove payment method: {str(e)}", e)
    
    # Payment Intent Creation
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = 'usd',
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a payment intent for one-time payments or subscription upgrades"""
        try:
            intent_data = {
                'amount': amount,
                'currency': currency,
                'automatic_payment_methods': {'enabled': True},
                'metadata': metadata or {}
            }
            
            if customer_id:
                intent_data['customer'] = customer_id
            
            if payment_method_id:
                intent_data['payment_method'] = payment_method_id
                intent_data['confirmation_method'] = 'manual'
                intent_data['confirm'] = True
            
            payment_intent = stripe.PaymentIntent.create(**intent_data)
            
            return {
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            raise PaymentError(f"Failed to create payment intent: {str(e)}", e)
    
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Confirm a payment intent"""
        try:
            confirm_data = {}
            if payment_method_id:
                confirm_data['payment_method'] = payment_method_id
            
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                **confirm_data
            )
            
            return {
                'id': payment_intent.id,
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment intent {payment_intent_id}: {e}")
            raise PaymentError(f"Failed to confirm payment: {str(e)}", e)
    
    # Webhook Handling
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            if not self.webhook_secret:
                raise PaymentError("Webhook secret not configured")
            
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            event_type = event['type']
            event_data = event['data']['object']
            
            logger.info(f"Processing webhook event: {event_type}")
            
            # Handle different event types
            if event_type == 'customer.subscription.created':
                return await self._handle_subscription_created(event_data)
            elif event_type == 'customer.subscription.updated':
                return await self._handle_subscription_updated(event_data)
            elif event_type == 'customer.subscription.deleted':
                return await self._handle_subscription_deleted(event_data)
            elif event_type == 'invoice.payment_succeeded':
                return await self._handle_payment_succeeded(event_data)
            elif event_type == 'invoice.payment_failed':
                return await self._handle_payment_failed(event_data)
            elif event_type == 'customer.subscription.trial_will_end':
                return await self._handle_trial_will_end(event_data)
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {'status': 'ignored', 'event_type': event_type}
                
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise PaymentError("Invalid webhook signature", e)
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise PaymentError(f"Webhook processing failed: {str(e)}")
    
    # Error Handling and Retry Logic
    
    async def retry_failed_payment(
        self,
        payment_intent_id: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Retry a failed payment with exponential backoff"""
        for attempt in range(max_retries):
            try:
                # Wait before retry (exponential backoff)
                if attempt > 0:
                    import asyncio
                    wait_time = 2 ** attempt  # 2, 4, 8 seconds
                    await asyncio.sleep(wait_time)
                
                # Attempt to confirm payment intent
                result = await self.confirm_payment_intent(payment_intent_id)
                
                if result['status'] == 'succeeded':
                    logger.info(f"Payment retry succeeded on attempt {attempt + 1}")
                    return result
                
            except PaymentError as e:
                logger.warning(f"Payment retry attempt {attempt + 1} failed: {e.message}")
                if attempt == max_retries - 1:
                    raise
        
        raise PaymentError(f"Payment failed after {max_retries} attempts")
    
    async def _record_payment_failure(
        self,
        user_id: str,
        error_message: str,
        payment_method_id: Optional[str] = None
    ) -> PaymentHistory:
        """Record payment failure in database"""
        try:
            payment_record = PaymentHistory(
                user_id=user_id,
                amount=0,  # Unknown amount for failed payment
                currency='usd',
                status=PaymentStatus.FAILED,
                description=f"Payment failed: {error_message}",
                metadata={
                    'payment_method_id': payment_method_id,
                    'error_message': error_message,
                    'failure_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.db.add(payment_record)
            self.db.commit()
            
            return payment_record
            
        except Exception as e:
            logger.error(f"Error recording payment failure: {e}")
            self.db.rollback()
            raise
    
    # Helper Methods
    
    async def _handle_successful_subscription(
        self,
        user: User,
        stripe_subscription: Dict[str, Any]
    ) -> None:
        """Handle successful subscription creation"""
        try:
            # Handle both dict and Stripe object formats
            def get_attr(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                else:
                    return getattr(obj, key, default)
            
            # Create local subscription record
            subscription = Subscription(
                user_id=user.id,
                stripe_subscription_id=get_attr(stripe_subscription, 'id'),
                stripe_customer_id=get_attr(stripe_subscription, 'customer'),
                tier=SubscriptionTier.PRO,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.fromtimestamp(get_attr(stripe_subscription, 'current_period_start')),
                current_period_end=datetime.fromtimestamp(get_attr(stripe_subscription, 'current_period_end')),
                cancel_at_period_end=get_attr(stripe_subscription, 'cancel_at_period_end', False)
            )
            
            self.db.add(subscription)
            
            # Update user
            user.subscription_tier = SubscriptionTier.PRO
            user.subscription_status = SubscriptionStatus.ACTIVE
            user.current_period_start = subscription.current_period_start
            user.current_period_end = subscription.current_period_end
            user.cancel_at_period_end = subscription.cancel_at_period_end
            
            # Record successful payment
            if stripe_subscription.get('latest_invoice'):
                invoice = stripe.Invoice.retrieve(stripe_subscription.latest_invoice)
                if invoice.amount_paid > 0:
                    payment_record = PaymentHistory(
                        user_id=user.id,
                        stripe_payment_intent_id=invoice.payment_intent,
                        amount=invoice.amount_paid,
                        currency=invoice.currency,
                        status=PaymentStatus.SUCCEEDED,
                        description=f"Pro subscription payment - {subscription.current_period_start.strftime('%B %Y')}"
                    )
                    self.db.add(payment_record)
            
            self.db.commit()
            
            logger.info(f"Successfully activated Pro subscription for user {user.id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error handling successful subscription for user {user.id}: {e}")
            raise
    
    async def _handle_subscription_cancellation(
        self,
        user: User,
        stripe_subscription: Dict[str, Any],
        immediate: bool = False
    ) -> None:
        """Handle subscription cancellation"""
        try:
            # Handle both dict and Stripe object formats
            def get_attr(obj, key, default=None):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                else:
                    return getattr(obj, key, default)
            
            # Update subscription record
            subscription_id = get_attr(stripe_subscription, 'id')
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.utcnow()
                
                if immediate:
                    subscription.current_period_end = datetime.utcnow()
            
            # Update user
            if immediate:
                user.subscription_tier = SubscriptionTier.FREE
                user.subscription_status = SubscriptionStatus.CANCELED
                user.current_period_end = datetime.utcnow()
            else:
                user.cancel_at_period_end = True
            
            self.db.commit()
            
            logger.info(f"Handled subscription cancellation for user {user.id} (immediate: {immediate})")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error handling subscription cancellation for user {user.id}: {e}")
            raise
    
    def _map_stripe_status(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe subscription status to local enum"""
        status_mapping = {
            'active': SubscriptionStatus.ACTIVE,
            'canceled': SubscriptionStatus.CANCELED,
            'past_due': SubscriptionStatus.PAST_DUE,
            'unpaid': SubscriptionStatus.UNPAID,
            'incomplete': SubscriptionStatus.INCOMPLETE,
            'incomplete_expired': SubscriptionStatus.INCOMPLETE_EXPIRED,
            'trialing': SubscriptionStatus.TRIALING
        }
        
        return status_mapping.get(stripe_status, SubscriptionStatus.ACTIVE)
    
    # Webhook Event Handlers
    
    async def _handle_subscription_created(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.created webhook"""
        try:
            user_id = subscription_data.get('metadata', {}).get('user_id')
            if not user_id:
                logger.warning("No user_id in subscription metadata")
                return {'status': 'ignored', 'reason': 'no_user_id'}
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for subscription creation")
                return {'status': 'ignored', 'reason': 'user_not_found'}
            
            await self._handle_successful_subscription(user, subscription_data)
            
            return {'status': 'processed', 'action': 'subscription_created'}
            
        except Exception as e:
            logger.error(f"Error handling subscription.created webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.updated webhook"""
        try:
            await self.update_subscription_status(subscription_data['id'])
            return {'status': 'processed', 'action': 'subscription_updated'}
            
        except Exception as e:
            logger.error(f"Error handling subscription.updated webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.deleted webhook"""
        try:
            user_id = subscription_data.get('metadata', {}).get('user_id')
            if not user_id:
                logger.warning("No user_id in subscription metadata")
                return {'status': 'ignored', 'reason': 'no_user_id'}
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found for subscription deletion")
                return {'status': 'ignored', 'reason': 'user_not_found'}
            
            await self._handle_subscription_cancellation(user, subscription_data, immediate=True)
            
            return {'status': 'processed', 'action': 'subscription_deleted'}
            
        except Exception as e:
            logger.error(f"Error handling subscription.deleted webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _handle_payment_succeeded(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_succeeded webhook"""
        try:
            customer_id = invoice_data.get('customer')
            if not customer_id:
                return {'status': 'ignored', 'reason': 'no_customer'}
            
            # Find user by customer ID
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.warning(f"User not found for customer {customer_id}")
                return {'status': 'ignored', 'reason': 'user_not_found'}
            
            # Record successful payment
            payment_record = PaymentHistory(
                user_id=user.id,
                stripe_payment_intent_id=invoice_data.get('payment_intent'),
                amount=invoice_data.get('amount_paid', 0),
                currency=invoice_data.get('currency', 'usd'),
                status=PaymentStatus.SUCCEEDED,
                description=f"Subscription payment - {datetime.utcnow().strftime('%B %Y')}"
            )
            
            self.db.add(payment_record)
            self.db.commit()
            
            logger.info(f"Recorded successful payment for user {user.id}")
            
            return {'status': 'processed', 'action': 'payment_recorded'}
            
        except Exception as e:
            logger.error(f"Error handling payment.succeeded webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _handle_payment_failed(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_failed webhook"""
        try:
            customer_id = invoice_data.get('customer')
            if not customer_id:
                return {'status': 'ignored', 'reason': 'no_customer'}
            
            # Find user by customer ID
            user = self.db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if not user:
                logger.warning(f"User not found for customer {customer_id}")
                return {'status': 'ignored', 'reason': 'user_not_found'}
            
            # Record failed payment
            await self._record_payment_failure(
                str(user.id),
                f"Invoice payment failed: {invoice_data.get('id')}",
                None
            )
            
            # Update subscription status to past_due
            if user.subscription_tier == SubscriptionTier.PRO:
                user.subscription_status = SubscriptionStatus.PAST_DUE
                self.db.commit()
            
            logger.info(f"Handled payment failure for user {user.id}")
            
            return {'status': 'processed', 'action': 'payment_failure_recorded'}
            
        except Exception as e:
            logger.error(f"Error handling payment.failed webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _handle_trial_will_end(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer.subscription.trial_will_end webhook"""
        try:
            user_id = subscription_data.get('metadata', {}).get('user_id')
            if not user_id:
                return {'status': 'ignored', 'reason': 'no_user_id'}
            
            # This could trigger email notifications or other actions
            logger.info(f"Trial ending soon for user {user_id}")
            
            return {'status': 'processed', 'action': 'trial_ending_noted'}
            
        except Exception as e:
            logger.error(f"Error handling trial_will_end webhook: {e}")
            return {'status': 'error', 'error': str(e)}    

    # Additional Payment Management Methods
    
    async def get_receipt_url(self, invoice_id: str) -> Optional[str]:
        """Get receipt URL for a Stripe invoice"""
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            if invoice and invoice.hosted_invoice_url:
                return invoice.hosted_invoice_url
            return None
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting receipt URL for invoice {invoice_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting receipt URL for invoice {invoice_id}: {e}")
            return None
    
    async def set_default_payment_method(self, customer_id: str, payment_method_id: str) -> bool:
        """Set default payment method for customer"""
        try:
            # Update customer's default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={'default_payment_method': payment_method_id}
            )
            
            # Also update any active subscriptions
            subscriptions = stripe.Subscription.list(customer=customer_id, status='active')
            for subscription in subscriptions.data:
                stripe.Subscription.modify(
                    subscription.id,
                    default_payment_method=payment_method_id
                )
            
            logger.info(f"Set default payment method {payment_method_id} for customer {customer_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error setting default payment method: {e}")
            raise PaymentError(f"Failed to set default payment method: {str(e)}", e)
        except Exception as e:
            logger.error(f"Error setting default payment method: {e}")
            raise PaymentError(f"Failed to set default payment method: {str(e)}")