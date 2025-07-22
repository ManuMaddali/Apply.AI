"""
Test script for subscription lifecycle management

This script tests the lifecycle management functionality including:
- Task scheduler operations
- Lifecycle service methods
- Email notifications
- Database operations
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import SessionLocal, init_db
from models.user import User, Subscription, SubscriptionTier, SubscriptionStatus
from services.subscription_lifecycle_service import SubscriptionLifecycleService, LifecycleTaskType
from services.task_scheduler import TaskScheduler
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_lifecycle_service():
    """Test the lifecycle service methods"""
    print("🧪 Testing Subscription Lifecycle Service")
    
    # Initialize database
    init_db()
    
    lifecycle_service = SubscriptionLifecycleService()
    
    # Test 1: Subscription Status Sync
    print("\n1. Testing subscription status synchronization...")
    try:
        result = await lifecycle_service.sync_subscription_status()
        print(f"✅ Sync result: {result.success}, processed: {result.processed_count}")
        if result.details:
            print(f"   Details: {result.details}")
    except Exception as e:
        print(f"❌ Sync test failed: {e}")
    
    # Test 2: Weekly Usage Reset
    print("\n2. Testing weekly usage reset...")
    try:
        result = await lifecycle_service.reset_weekly_usage()
        print(f"✅ Reset result: {result.success}, processed: {result.processed_count}")
        if result.details:
            print(f"   Details: {result.details}")
    except Exception as e:
        print(f"❌ Reset test failed: {e}")
    
    # Test 3: Grace Period Handling
    print("\n3. Testing grace period handling...")
    try:
        result = await lifecycle_service.handle_grace_periods()
        print(f"✅ Grace period result: {result.success}, processed: {result.processed_count}")
        if result.details:
            print(f"   Details: {result.details}")
    except Exception as e:
        print(f"❌ Grace period test failed: {e}")
    
    # Test 4: Expired Subscription Processing
    print("\n4. Testing expired subscription processing...")
    try:
        result = await lifecycle_service.process_expired_subscriptions()
        print(f"✅ Expired processing result: {result.success}, processed: {result.processed_count}")
        if result.details:
            print(f"   Details: {result.details}")
    except Exception as e:
        print(f"❌ Expired processing test failed: {e}")
    
    # Test 5: Renewal Reminders
    print("\n5. Testing renewal reminders...")
    try:
        result = await lifecycle_service.send_renewal_reminders()
        print(f"✅ Renewal reminders result: {result.success}, processed: {result.processed_count}")
        if result.details:
            print(f"   Details: {result.details}")
    except Exception as e:
        print(f"❌ Renewal reminders test failed: {e}")
    
    # Test 6: Data Cleanup
    print("\n6. Testing data cleanup...")
    try:
        result = await lifecycle_service.cleanup_old_data(retention_days=30)
        print(f"✅ Cleanup result: {result.success}, processed: {result.processed_count}")
        if result.details:
            print(f"   Details: {result.details}")
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")
    
    # Test 7: Run All Tasks
    print("\n7. Testing run all tasks...")
    try:
        results = await lifecycle_service.run_all_lifecycle_tasks()
        successful = sum(1 for r in results if r.success)
        print(f"✅ All tasks result: {successful}/{len(results)} successful")
        for result in results:
            print(f"   - {result.task_type.value}: {'✅' if result.success else '❌'} "
                  f"({result.processed_count} processed)")
    except Exception as e:
        print(f"❌ All tasks test failed: {e}")


async def test_task_scheduler():
    """Test the task scheduler"""
    print("\n🧪 Testing Task Scheduler")
    
    scheduler = TaskScheduler()
    
    # Test 1: Get scheduler status
    print("\n1. Testing scheduler status...")
    try:
        status = scheduler.get_scheduler_status()
        print(f"✅ Scheduler status: {status}")
    except Exception as e:
        print(f"❌ Status test failed: {e}")
    
    # Test 2: Get all task status
    print("\n2. Testing all task status...")
    try:
        all_status = scheduler.get_all_task_status()
        print(f"✅ Found {len(all_status)} tasks:")
        for task_name, task_status in all_status.items():
            print(f"   - {task_name}: enabled={task_status['enabled']}, "
                  f"runs={task_status['run_count']}, errors={task_status['error_count']}")
    except Exception as e:
        print(f"❌ All status test failed: {e}")
    
    # Test 3: Run single task
    print("\n3. Testing single task execution...")
    try:
        result = await scheduler.run_task_now("subscription_sync")
        print(f"✅ Single task result: {result.success}, processed: {result.processed_count}")
    except Exception as e:
        print(f"❌ Single task test failed: {e}")
    
    # Test 4: Enable/Disable task
    print("\n4. Testing task enable/disable...")
    try:
        # Disable a task
        success = scheduler.disable_task("data_cleanup")
        print(f"✅ Disable task: {success}")
        
        # Enable it back
        success = scheduler.enable_task("data_cleanup")
        print(f"✅ Enable task: {success}")
    except Exception as e:
        print(f"❌ Enable/disable test failed: {e}")
    
    # Test 5: Add custom task
    print("\n5. Testing custom task addition...")
    try:
        success = scheduler.add_custom_task(
            "test_custom_sync",
            LifecycleTaskType.SUBSCRIPTION_SYNC,
            15  # Every 15 minutes
        )
        print(f"✅ Add custom task: {success}")
        
        # Remove it
        success = scheduler.remove_task("test_custom_sync")
        print(f"✅ Remove custom task: {success}")
    except Exception as e:
        print(f"❌ Custom task test failed: {e}")


def create_test_data():
    """Create some test data for lifecycle testing"""
    print("\n🧪 Creating Test Data")
    
    db = SessionLocal()
    try:
        # Create a test user with expired subscription
        test_user = db.query(User).filter(User.email == "test_expired@example.com").first()
        if not test_user:
            test_user = User(
                email="test_expired@example.com",
                username="test_expired",
                full_name="Test Expired User",
                subscription_tier=SubscriptionTier.PRO,
                subscription_status=SubscriptionStatus.ACTIVE,
                current_period_end=datetime.utcnow() - timedelta(days=1),  # Expired yesterday
                weekly_usage_count=3,
                weekly_usage_reset=datetime.utcnow() - timedelta(days=8)  # Needs reset
            )
            test_user.set_password("test123")
            db.add(test_user)
        
        # Create a test user with past due subscription
        test_user_past_due = db.query(User).filter(User.email == "test_pastdue@example.com").first()
        if not test_user_past_due:
            test_user_past_due = User(
                email="test_pastdue@example.com",
                username="test_pastdue",
                full_name="Test Past Due User",
                subscription_tier=SubscriptionTier.PRO,
                subscription_status=SubscriptionStatus.PAST_DUE,
                current_period_end=datetime.utcnow() - timedelta(days=2),  # 2 days past due
                weekly_usage_count=5,
                weekly_usage_reset=datetime.utcnow() - timedelta(days=10)
            )
            test_user_past_due.set_password("test123")
            db.add(test_user_past_due)
        
        # Create a test user with upcoming renewal
        test_user_renewal = db.query(User).filter(User.email == "test_renewal@example.com").first()
        if not test_user_renewal:
            test_user_renewal = User(
                email="test_renewal@example.com",
                username="test_renewal",
                full_name="Test Renewal User",
                subscription_tier=SubscriptionTier.PRO,
                subscription_status=SubscriptionStatus.ACTIVE,
                current_period_end=datetime.utcnow() + timedelta(days=3),  # Renews in 3 days
                weekly_usage_count=2,
                weekly_usage_reset=datetime.utcnow() - timedelta(days=2)
            )
            test_user_renewal.set_password("test123")
            db.add(test_user_renewal)
        
        db.commit()
        print("✅ Test data created successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create test data: {e}")
    finally:
        db.close()


async def main():
    """Main test function"""
    print("🚀 Starting Subscription Lifecycle Management Tests")
    print("=" * 60)
    
    # Create test data
    create_test_data()
    
    # Test lifecycle service
    await test_lifecycle_service()
    
    # Test task scheduler
    await test_task_scheduler()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())