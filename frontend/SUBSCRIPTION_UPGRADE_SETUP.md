# Subscription Upgrade Flow Setup

This document explains how to set up and use the subscription upgrade flow components.

## Components Overview

### 1. UpgradeModal
The main modal component that handles the complete upgrade flow:
- Stripe Elements integration for secure payment processing
- Feature comparison display
- Loading states and error handling
- Success confirmation with immediate feature access
- 3D Secure authentication support

### 2. UpgradeButton
Reusable button components for triggering upgrades:
- `UpgradeButton` - Base component with customizable variants
- `ProUpgradeButton` - Primary upgrade button
- `CompactUpgradeButton` - Small upgrade button
- `FeatureUpgradeButton` - Feature-specific upgrade button

### 3. UpgradePrompt (Enhanced)
Enhanced prompt components that now integrate with the upgrade modal:
- `UpgradePrompt` - Base prompt component
- `UsageLimitPrompt` - For usage limit scenarios
- `FeatureBlockedPrompt` - For blocked features
- `BulkProcessingPrompt` - For bulk processing promotion

## Setup Instructions

### 1. Environment Configuration

Add your Stripe publishable key to `.env.local`:

```bash
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
```

For production, use your live Stripe key:
```bash
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key_here
```

### 2. Backend API Endpoints

Ensure these endpoints are implemented in your backend:

- `POST /api/subscription/upgrade` - Create subscription with payment method
- `GET /api/subscription/status` - Get current subscription status
- `GET /api/subscription/usage` - Get usage statistics
- `POST /api/subscription/cancel` - Cancel subscription

### 3. Stripe Webhook Configuration

Configure Stripe webhooks to handle subscription events:
- `subscription.created`
- `subscription.updated` 
- `subscription.deleted`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`

## Usage Examples

### Basic Upgrade Button
```jsx
import UpgradeButton from '../components/UpgradeButton';

<UpgradeButton feature="bulk_processing">
  Unlock Bulk Processing
</UpgradeButton>
```

### Usage Limit Prompt
```jsx
import { UsageLimitPrompt } from '../components/UpgradePrompt';

<UsageLimitPrompt 
  weeklyUsage={4} 
  weeklyLimit={5} 
/>
```

### Feature Blocked Prompt
```jsx
import { FeatureBlockedPrompt } from '../components/UpgradePrompt';

<FeatureBlockedPrompt 
  feature="advanced_formatting"
  compact={true}
/>
```

### Manual Modal Trigger
```jsx
import { useState } from 'react';
import UpgradeModal from '../components/UpgradeModal';

const [showModal, setShowModal] = useState(false);

<button onClick={() => setShowModal(true)}>
  Upgrade Now
</button>

<UpgradeModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  feature="analytics"
/>
```

## Integration with Subscription Hook

Use the subscription hook to check feature access:

```jsx
import { useSubscription } from '../hooks/useSubscription';

const { isProUser, canUseFeature, hasExceededLimit } = useSubscription();

// Check if user can use a feature
if (!canUseFeature('bulk_processing')) {
  return <FeatureBlockedPrompt feature="bulk_processing" />;
}

// Show usage warnings
if (hasExceededLimit) {
  return <UsageLimitPrompt />;
}
```

## Event Handling

The upgrade flow dispatches custom events for real-time updates:

```jsx
// Listen for subscription updates
useEffect(() => {
  const handleSubscriptionUpdate = (event) => {
    console.log('Subscription updated:', event.detail);
    // Refresh subscription data
  };

  window.addEventListener('subscriptionUpdated', handleSubscriptionUpdate);
  return () => window.removeEventListener('subscriptionUpdated', handleSubscriptionUpdate);
}, []);
```

## Testing

Use the subscription test page to verify all components:

1. Navigate to `/testing` (development only)
2. Switch to "Subscription Testing" tab
3. Test all upgrade flows and components

## Security Considerations

1. **Never expose secret keys** - Only use publishable keys in frontend
2. **Validate on backend** - Always verify payments server-side
3. **Webhook security** - Verify webhook signatures from Stripe
4. **PCI Compliance** - Stripe Elements handles sensitive card data

## Error Handling

The components handle common error scenarios:

- **Payment failures** - Clear error messages with retry options
- **Network errors** - Graceful degradation with retry mechanisms
- **3D Secure** - Automatic handling of authentication challenges
- **Subscription conflicts** - Clear messaging about current status

## Customization

### Styling
All components use Tailwind CSS classes and can be customized:

```jsx
<UpgradeButton 
  className="custom-styles"
  variant="outline"
  size="large"
>
  Custom Button
</UpgradeButton>
```

### Feature Comparison
Modify the feature comparison in `UpgradeModal.jsx`:

```jsx
const features = [
  {
    name: 'Your Feature',
    free: 'Limited',
    pro: 'Unlimited',
    icon: '🚀'
  }
  // Add more features...
];
```

## Troubleshooting

### Common Issues

1. **Stripe not loading**: Check publishable key configuration
2. **Payment failures**: Verify backend endpoint implementation
3. **Modal not opening**: Check component state management
4. **Styling issues**: Ensure Tailwind CSS is properly configured

### Debug Mode

Enable debug logging by setting:
```bash
NEXT_PUBLIC_DEBUG_STRIPE=true
```

This will log Stripe events and payment processing steps to the console.