# Subscription Lifecycle Management Implementation

This document describes the automated subscription lifecycle management system that handles subscription status synchronization, usage resets, grace periods, downgrades, renewal reminders, and data cleanup.

## Overview

The subscription lifecycle management system consists of several components:

1. **SubscriptionLifecycleService** - Core service handling lifecycle operations
2. **TaskScheduler** - Background task scheduler for automated execution
3. **Email notifications** - Automated email notifications for various lifecycle events
4. **API endpoints** - Admin endpoints for monitoring and manual task execution

## Features Implemented

### ✅ Scheduled Tasks for Subscription Status Synchronization
- Hourly synchronization with Stripe subscription status
- Automatic detection and correction of status discrepancies
- Handles subscription updates, cancellations, and renewals

### ✅ Automatic Weekly Usage Reset for Free Users
- Weekly reset of usage counters for Free tier users
- Runs every Sunday at 3 AM UTC
- Maintains usage tracking history

### ✅ Grace Period Handling for Failed Payments
- 3-day grace period for failed payments
- Automated email reminders on day 1 and final warning on day 3
- Automatic downgrade after grace period expires

### ✅ Automated Downgrade Process for Expired Subscriptions
- Daily check for expired Pro subscriptions
- Automatic downgrade to Free tier while preserving user data
- Email notifications for subscription expiry

### ✅ Subscription Renewal Reminders and Notifications
- Renewal reminders at 7 days, 3 days, and 1 day before renewal
- Only sent to users who haven't canceled their subscription
- Customizable email templates

### ✅ Cleanup Tasks for Expired Sessions and Old Usage Data
- Weekly cleanup of expired user sessions
- Removal of old usage tracking data (90-day retention)
- Cleanup of old failed payment records (2-year retention)
- Database optimization with VACUUM

## Architecture

### Core Services

#### SubscriptionLifecycleService
```python
# Main service class handling all lifecycle operations
class SubscriptionLifecycleService:
    async def sync_subscription_status() -> LifecycleTaskResult
    async def reset_weekly_usage() -> LifecycleTaskResult
    async def handle_grace_periods() -> LifecycleTaskResult
    async def process_expired_subscriptions() -> LifecycleTaskResult
    async def send_renewal_reminders() -> LifecycleTaskResult
    async def cleanup_old_data() -> LifecycleTaskResult
```

#### TaskScheduler
```python
# Background task scheduler with configurable intervals
class TaskScheduler:
    async def start()  # Start the scheduler
    async def stop()   # Stop the scheduler
    async def run_task_now(task_name: str)  # Run task immediately
    async def run_all_tasks_now()  # Run all tasks
```

### Database Schema

The system uses the following database tables:

- **users** - Extended with subscription fields
- **subscriptions** - Stripe subscription records
- **usage_tracking** - User activity tracking
- **payment_history** - Payment transaction records
- **user_sessions** - User session management

### Email Templates

The system includes email templates for:

- Payment failure reminders
- Final grace period warnings
- Downgrade notifications
- Subscription expiry notifications
- Renewal reminders

## Configuration

### Environment Variables

```bash
# Stripe Configuration (required for production)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Admin Configuration
ADMIN_EMAILS=admin@example.com,admin2@example.com
```

### Task Schedule

Default task schedule:
- **Subscription Sync**: Every hour
- **Usage Reset**: Weekly (Sunday 3 AM UTC)
- **Grace Period Check**: Daily (2 AM UTC)
- **Expired Processing**: Daily (2 AM UTC)
- **Renewal Reminders**: Daily (2 AM UTC)
- **Data Cleanup**: Weekly (Sunday 3 AM UTC)

## API Endpoints

### Admin Endpoints

```bash
# Get scheduler status
GET /api/lifecycle/status

# Get specific task status
GET /api/lifecycle/tasks/{task_name}/status

# Run task immediately
POST /api/lifecycle/tasks/{task_name}/run

# Run all tasks
POST /api/lifecycle/tasks/run-all

# Enable/disable tasks
POST /api/lifecycle/tasks/{task_name}/enable
POST /api/lifecycle/tasks/{task_name}/disable

# Add custom task
POST /api/lifecycle/tasks/custom

# Remove task
DELETE /api/lifecycle/tasks/{task_name}
```

### Health Check

```bash
# Basic health check (all users)
GET /api/lifecycle/health
```

## Usage Examples

### Starting the Scheduler

The scheduler starts automatically when the FastAPI application starts:

```python
# In main.py startup event
from services.task_scheduler import start_scheduler
await start_scheduler()
```

### Manual Task Execution

```python
# Run a specific task
from services.task_scheduler import get_scheduler
scheduler = get_scheduler()
result = await scheduler.run_task_now("subscription_sync")
```

### Adding Custom Tasks

```python
# Add a custom task via API
POST /api/lifecycle/tasks/custom
{
    "name": "custom_sync",
    "task_type": "subscription_sync",
    "interval_minutes": 30
}
```

## Monitoring and Logging

### Task Results

Each task returns a `LifecycleTaskResult` with:
- Success status
- Number of items processed
- Error messages
- Detailed information

### Logging

The system provides comprehensive logging:
- Task execution status
- Error details
- Performance metrics
- User actions (downgrades, notifications)

### Health Monitoring

Monitor system health via:
- Scheduler status endpoint
- Task execution history
- Error counts and patterns

## Testing

Run the test suite to verify functionality:

```bash
cd backend
python test_lifecycle_management.py
```

The test suite covers:
- All lifecycle service methods
- Task scheduler operations
- Database operations
- Error handling

## Deployment Considerations

### Production Setup

1. **Environment Variables**: Set all required environment variables
2. **Database Migration**: Run the migration to add required tables/columns
3. **Stripe Configuration**: Configure Stripe webhooks and API keys
4. **Email Configuration**: Set up SMTP for email notifications
5. **Monitoring**: Set up logging and monitoring for task execution

### Performance

- Tasks are designed to be non-blocking
- Database operations use proper indexing
- Cleanup tasks prevent database bloat
- Error handling prevents task failures from affecting other tasks

### Security

- Admin-only endpoints require authentication
- Stripe webhook signature verification
- Secure email template rendering
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **Stripe Configuration Missing**
   - Set STRIPE_SECRET_KEY environment variable
   - Verify Stripe webhook configuration

2. **Email Notifications Not Sending**
   - Check SMTP configuration
   - Verify email credentials
   - Check email service logs

3. **Tasks Not Running**
   - Check scheduler status via API
   - Verify task is enabled
   - Check application logs for errors

4. **Database Errors**
   - Run database migration
   - Check database permissions
   - Verify table schema

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check task status:
```bash
curl -H "Authorization: Bearer <admin-token>" \
     http://localhost:8000/api/lifecycle/status
```

## Future Enhancements

Potential improvements:
- Webhook-based real-time synchronization
- Advanced analytics and reporting
- Customizable grace periods per user
- A/B testing for email templates
- Integration with external monitoring systems

## Requirements Satisfied

This implementation satisfies all requirements from task 16:

- ✅ **6.4**: Grace period handling for failed payments
- ✅ **6.5**: Subscription renewal reminders and notifications  
- ✅ **8.3**: Automatic weekly usage reset for Free users
- ✅ **8.4**: Automated downgrade process for expired subscriptions
- ✅ **8.5**: Cleanup tasks for expired sessions and old usage data

The system provides a robust, scalable solution for automated subscription lifecycle management with comprehensive monitoring, error handling, and administrative controls.