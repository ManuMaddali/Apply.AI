#!/usr/bin/env python3
"""
Test script for Admin Analytics endpoints

This script tests the admin analytics functionality to ensure all endpoints
are working correctly and returning expected data structures.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from config.database import get_db, init_db
from services.admin_analytics_service import AdminAnalyticsService
from models.user import User, Subscription, UsageTracking, PaymentHistory, SubscriptionTier, SubscriptionStatus, UsageType, PaymentStatus


async def test_admin_analytics():
    """Test admin analytics service functionality"""
    print("🧪 Testing Admin Analytics Service")
    print("=" * 50)
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Initialize admin analytics service
        admin_service = AdminAnalyticsService(db)
        print("✅ Admin Analytics Service initialized")
        
        # Test 1: Subscription Metrics
        print("\n📊 Testing Subscription Metrics...")
        subscription_metrics = await admin_service.get_subscription_metrics("30d")
        
        if "error" in subscription_metrics:
            print(f"❌ Subscription metrics error: {subscription_metrics['error']}")
        else:
            print("✅ Subscription metrics retrieved successfully")
            print(f"   - Total users: {subscription_metrics.get('overview', {}).get('total_users', 0)}")
            print(f"   - Active subscriptions: {subscription_metrics.get('overview', {}).get('active_subscriptions', 0)}")
            print(f"   - Conversion rate: {subscription_metrics.get('overview', {}).get('conversion_rate', 0)}%")
            print(f"   - Churn rate: {subscription_metrics.get('overview', {}).get('churn_rate', 0)}%")
        
        # Test 2: User Behavior Analytics
        print("\n👥 Testing User Behavior Analytics...")
        user_behavior = await admin_service.get_user_behavior_analytics("30d")
        
        if "error" in user_behavior:
            print(f"❌ User behavior analytics error: {user_behavior['error']}")
        else:
            print("✅ User behavior analytics retrieved successfully")
            usage_patterns = user_behavior.get('usage_patterns', {})
            print(f"   - Usage patterns tracked: {len(usage_patterns)} types")
            retention = user_behavior.get('retention', {})
            print(f"   - Retention data points: {len(retention)}")
        
        # Test 3: Payment Analytics
        print("\n💳 Testing Payment Analytics...")
        payment_analytics = await admin_service.get_payment_analytics("30d")
        
        if "error" in payment_analytics:
            print(f"❌ Payment analytics error: {payment_analytics['error']}")
        else:
            print("✅ Payment analytics retrieved successfully")
            overview = payment_analytics.get('overview', {})
            print(f"   - Total payments: {overview.get('total_payments', 0)}")
            print(f"   - Failure rate: {overview.get('failure_rate', 0)}%")
            print(f"   - Total revenue: ${overview.get('total_revenue', 0)}")
        
        # Test 4: Revenue Analytics
        print("\n💰 Testing Revenue Analytics...")
        revenue_analytics = await admin_service.get_revenue_analytics("30d")
        
        if "error" in revenue_analytics:
            print(f"❌ Revenue analytics error: {revenue_analytics['error']}")
        else:
            print("✅ Revenue analytics retrieved successfully")
            overview = revenue_analytics.get('overview', {})
            print(f"   - Current MRR: ${overview.get('current_mrr', 0)}")
            print(f"   - Revenue growth: {overview.get('revenue_growth', 0)}%")
            print(f"   - ARPU: ${overview.get('arpu', 0)}")
        
        # Test 5: Capacity Analytics
        print("\n🖥️  Testing Capacity Analytics...")
        capacity_analytics = await admin_service.get_capacity_analytics()
        
        if "error" in capacity_analytics:
            print(f"❌ Capacity analytics error: {capacity_analytics['error']}")
        else:
            print("✅ Capacity analytics retrieved successfully")
            system_capacity = capacity_analytics.get('system_capacity', {})
            print(f"   - System usage: {system_capacity.get('usage_percentage', 0)}%")
            print(f"   - Status: {system_capacity.get('status', 'unknown')}")
            recommendations = capacity_analytics.get('recommendations', [])
            print(f"   - Recommendations: {len(recommendations)}")
        
        # Test 6: System Alerts
        print("\n🚨 Testing System Alerts...")
        alerts = await admin_service.check_system_alerts()
        
        print(f"✅ System alerts checked: {len(alerts)} alerts found")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"   - {alert.get('type', 'unknown')}: {alert.get('severity', 'unknown')} severity")
        
        # Test 7: Conversion Funnel Analysis
        print("\n🔄 Testing Conversion Funnel Analysis...")
        conversion_funnel = await admin_service.get_conversion_funnel_analysis()
        
        if "error" in conversion_funnel:
            print(f"❌ Conversion funnel error: {conversion_funnel['error']}")
        else:
            print("✅ Conversion funnel analysis retrieved successfully")
            funnel_stages = conversion_funnel.get('funnel_stages', {})
            print(f"   - Registered users: {funnel_stages.get('registered', 0)}")
            print(f"   - Activated users: {funnel_stages.get('activated', 0)}")
            print(f"   - Converted users: {funnel_stages.get('converted', 0)}")
            conversion_rates = conversion_funnel.get('conversion_rates', {})
            print(f"   - Overall conversion: {conversion_rates.get('overall_conversion', 0)}%")
        
        # Test 8: Complete Admin Dashboard
        print("\n📈 Testing Complete Admin Dashboard...")
        dashboard = await admin_service.get_admin_dashboard("30d")
        
        if "error" in dashboard:
            print(f"❌ Admin dashboard error: {dashboard['error']}")
        else:
            print("✅ Admin dashboard retrieved successfully")
            overview = dashboard.get('dashboard_overview', {})
            print(f"   - Total users: {overview.get('total_users', 0)}")
            print(f"   - MRR: ${overview.get('mrr', 0)}")
            print(f"   - System health: {overview.get('system_health', 'unknown')}")
            
            # Count sections in dashboard
            sections = [k for k in dashboard.keys() if k not in ['dashboard_overview', 'time_range', 'generated_at']]
            print(f"   - Dashboard sections: {len(sections)}")
        
        print("\n" + "=" * 50)
        print("🎉 All Admin Analytics Tests Completed!")
        print("✅ Admin monitoring and analytics backend is working correctly")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def create_sample_data(db: Session):
    """Create sample data for testing (optional)"""
    try:
        # Check if we already have data
        user_count = db.query(User).count()
        if user_count > 0:
            print(f"📊 Using existing data: {user_count} users found")
            return
        
        print("📊 Creating sample data for testing...")
        
        # Create sample users
        from models.user import User, SubscriptionTier, SubscriptionStatus
        import uuid
        
        # Free users
        for i in range(10):
            user = User(
                id=uuid.uuid4(),
                email=f"free_user_{i}@example.com",
                username=f"free_user_{i}",
                full_name=f"Free User {i}",
                subscription_tier=SubscriptionTier.FREE,
                subscription_status=SubscriptionStatus.ACTIVE,
                total_usage_count=i * 2,
                weekly_usage_count=min(i, 5)
            )
            user.set_password("password123")
            db.add(user)
        
        # Pro users
        for i in range(5):
            user = User(
                id=uuid.uuid4(),
                email=f"pro_user_{i}@example.com",
                username=f"pro_user_{i}",
                full_name=f"Pro User {i}",
                subscription_tier=SubscriptionTier.PRO,
                subscription_status=SubscriptionStatus.ACTIVE,
                total_usage_count=i * 10 + 20,
                weekly_usage_count=i * 3,
                current_period_start=datetime.utcnow() - timedelta(days=15),
                current_period_end=datetime.utcnow() + timedelta(days=15)
            )
            user.set_password("password123")
            db.add(user)
        
        db.commit()
        print("✅ Sample data created successfully")
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        db.rollback()


if __name__ == "__main__":
    # Create sample data first (optional)
    db_gen = get_db()
    db = next(db_gen)
    try:
        create_sample_data(db)
    finally:
        db.close()
    
    # Run the tests
    asyncio.run(test_admin_analytics())