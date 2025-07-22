"""
Performance Tests for Subscription System

Tests performance characteristics of subscription services under load.
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import concurrent.futures
import threading
from typing import List, Dict

from models.user import (
    Base, User, Subscription, UsageTracking, PaymentHistory,
    SubscriptionTier, SubscriptionStatus, UsageType, AuthProvider
)
from services.subscription_service import SubscriptionService
from services.payment_service import PaymentService


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_performance.db"
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
def subscription_service(db_session):
    """Create SubscriptionService instance"""
    return SubscriptionService(db_session)


@pytest.fixture
def payment_service(db_session):
    """Create PaymentService instance with mocked config"""
    with patch('services.payment_service.get_stripe_config') as mock_config:
        mock_config.return_value = Mock(
            secret_key="sk_test_123",
            publishable_key="pk_test_123",
            webhook_secret="whsec_test_123",
            pro_monthly_price_id="price_test_123",
            environment="test"
        )
        
        with patch('stripe.api_key'):
            return PaymentService(db_session)


class TestSubscriptionServicePerformance:
    """Test performance of SubscriptionService operations"""
    
    @pytest.mark.asyncio
    async def test_usage_limit_check_performance(self, subscription_service, db_session):
        """Test performance of usage limit checks"""
        # Create test users
        users = []
        for i in range(100):
            user = User(
                email=f"perf{i}@example.com",
                username=f"perf{i}",
                subscription_tier=SubscriptionTier.FREE if i % 2 == 0 else SubscriptionTier.PRO,
                weekly_usage_count=i % 6,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Measure performance of usage limit checks
        start_time = time.time()
        
        tasks = []
        for user in users:
            task = subscription_service.check_usage_limits(
                str(user.id), 
                UsageType.RESUME_PROCESSING
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 2.0, f"Usage limit checks took too long: {duration}s"
        assert len(results) == 100
        assert all(hasattr(r, 'can_use') for r in results)
        
        # Calculate average time per check
        avg_time_per_check = duration / 100
        assert avg_time_per_check < 0.02, f"Average time per check too high: {avg_time_per_check}s"
    
    @pytest.mark.asyncio
    async def test_bulk_usage_tracking_performance(self, subscription_service, db_session):
        """Test performance of bulk usage tracking"""
        # Create test user
        user = User(
            email="bulk@example.com",
            username="bulkuser",
            subscription_tier=SubscriptionTier.PRO,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Measure bulk usage tracking performance
        start_time = time.time()
        
        # Track 500 usage records
        tasks = []
        for i in range(500):
            task = subscription_service.track_usage(
                user_id=str(user.id),
                usage_type=UsageType.RESUME_PROCESSING,
                count=1,
                session_id=f"session_{i}"
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 10.0, f"Bulk usage tracking took too long: {duration}s"
        
        # Verify all records were created
        updated_user = db_session.query(User).filter(User.id == user.id).first()
        assert updated_user.total_usage_count == 500
        
        # Calculate throughput
        throughput = 500 / duration
        assert throughput > 50, f"Usage tracking throughput too low: {throughput} ops/sec"
    
    @pytest.mark.asyncio
    async def test_subscription_metrics_performance(self, subscription_service, db_session):
        """Test performance of subscription metrics calculation"""
        # Create large dataset
        users = []
        subscriptions = []
        
        for i in range(200):
            user = User(
                email=f"metrics{i}@example.com",
                username=f"metrics{i}",
                subscription_tier=SubscriptionTier.PRO if i % 3 == 0 else SubscriptionTier.FREE,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
            
            if i % 3 == 0:  # Pro users
                subscription = Subscription(
                    user_id=user.id,
                    tier=SubscriptionTier.PRO,
                    status=SubscriptionStatus.ACTIVE if i % 10 != 0 else SubscriptionStatus.CANCELED,
                    stripe_customer_id=f"cus_{i}"
                )
                subscriptions.append(subscription)
        
        db_session.add_all(users)
        db_session.flush()  # Get user IDs
        
        # Update subscription user_ids
        for i, subscription in enumerate(subscriptions):
            subscription.user_id = users[i * 3].id
        
        db_session.add_all(subscriptions)
        db_session.commit()
        
        # Measure metrics calculation performance
        start_time = time.time()
        metrics = await subscription_service.get_subscription_metrics()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 3.0, f"Metrics calculation took too long: {duration}s"
        assert "tier_distribution" in metrics
        assert "active_subscriptions" in metrics
        
        # Verify correctness
        assert metrics["tier_distribution"]["free"] > 0
        assert metrics["tier_distribution"]["pro"] > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_subscription_operations(self, subscription_service, db_session):
        """Test performance under concurrent operations"""
        # Create test users
        users = []
        for i in range(50):
            user = User(
                email=f"concurrent{i}@example.com",
                username=f"concurrent{i}",
                subscription_tier=SubscriptionTier.FREE,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Define concurrent operations
        async def mixed_operations(user):
            operations = []
            
            # Check usage limits
            operations.append(
                subscription_service.check_usage_limits(str(user.id), UsageType.RESUME_PROCESSING)
            )
            
            # Track usage
            operations.append(
                subscription_service.track_usage(str(user.id), UsageType.RESUME_PROCESSING, count=1)
            )
            
            # Get usage statistics
            operations.append(
                subscription_service.get_usage_statistics(str(user.id))
            )
            
            # Validate subscription status
            operations.append(
                subscription_service.validate_subscription_status(str(user.id))
            )
            
            return await asyncio.gather(*operations)
        
        # Execute concurrent operations
        start_time = time.time()
        
        tasks = [mixed_operations(user) for user in users]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 5.0, f"Concurrent operations took too long: {duration}s"
        assert len(results) == 50
        
        # Calculate operations per second
        total_operations = 50 * 4  # 4 operations per user
        ops_per_second = total_operations / duration
        assert ops_per_second > 40, f"Operations per second too low: {ops_per_second}"
    
    def test_database_query_performance(self, subscription_service, db_session):
        """Test database query performance with large datasets"""
        # Create large dataset
        users = []
        usage_records = []
        
        for i in range(1000):
            user = User(
                email=f"query{i}@example.com",
                username=f"query{i}",
                subscription_tier=SubscriptionTier.FREE if i % 2 == 0 else SubscriptionTier.PRO,
                weekly_usage_count=i % 10,
                total_usage_count=i % 50,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.flush()
        
        # Create usage records
        for i, user in enumerate(users):
            for j in range(5):  # 5 records per user
                record = UsageTracking(
                    user_id=user.id,
                    usage_type=UsageType.RESUME_PROCESSING,
                    count=1,
                    usage_date=datetime.utcnow() - timedelta(days=j)
                )
                usage_records.append(record)
        
        db_session.add_all(usage_records)
        db_session.commit()
        
        # Test query performance
        start_time = time.time()
        
        # Query all Pro users
        pro_users = db_session.query(User).filter(
            User.subscription_tier == SubscriptionTier.PRO
        ).all()
        
        # Query usage statistics
        recent_usage = db_session.query(UsageTracking).filter(
            UsageTracking.usage_date >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Query users with high usage
        high_usage_users = db_session.query(User).filter(
            User.total_usage_count > 25
        ).all()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 1.0, f"Database queries took too long: {duration}s"
        assert len(pro_users) == 500  # Half the users
        assert recent_usage > 0
        assert len(high_usage_users) > 0


class TestPaymentServicePerformance:
    """Test performance of PaymentService operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_customer_creation(self, payment_service, db_session):
        """Test performance of concurrent customer creation"""
        # Create test users
        users = []
        for i in range(20):
            user = User(
                email=f"customer{i}@example.com",
                username=f"customer{i}",
                full_name=f"Customer {i}",
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Mock Stripe customer creation
        with patch('stripe.Customer.create') as mock_create:
            mock_create.side_effect = lambda **kwargs: Mock(id=f"cus_{kwargs['email'].split('@')[0]}")
            
            # Measure concurrent customer creation
            start_time = time.time()
            
            tasks = [payment_service.create_customer(user) for user in users]
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Performance assertions
            assert duration < 3.0, f"Concurrent customer creation took too long: {duration}s"
            assert len(results) == 20
            assert all(result.startswith("cus_") for result in results)
            
            # Calculate throughput
            throughput = 20 / duration
            assert throughput > 7, f"Customer creation throughput too low: {throughput} ops/sec"
    
    @pytest.mark.asyncio
    async def test_webhook_processing_performance(self, payment_service):
        """Test webhook processing performance with multiple events"""
        webhook_events = []
        
        # Create multiple webhook events
        for i in range(50):
            event = {
                'type': 'customer.subscription.created',
                'data': {
                    'object': {
                        'id': f'sub_perf_{i}',
                        'customer': f'cus_perf_{i}',
                        'status': 'active',
                        'metadata': {'user_id': f'user_{i}'}
                    }
                }
            }
            webhook_events.append(event)
        
        # Mock webhook processing
        with patch('stripe.Webhook.construct_event') as mock_construct:
            with patch.object(payment_service, '_handle_subscription_created') as mock_handler:
                mock_handler.return_value = {'status': 'processed'}
                
                # Process webhooks concurrently
                start_time = time.time()
                
                async def process_webhook(event):
                    mock_construct.return_value = event
                    return await payment_service.handle_webhook(b'payload', 'signature')
                
                tasks = [process_webhook(event) for event in webhook_events]
                results = await asyncio.gather(*tasks)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Performance assertions
                assert duration < 2.0, f"Webhook processing took too long: {duration}s"
                assert len(results) == 50
                assert all(r['status'] == 'processed' for r in results)
                
                # Calculate throughput
                throughput = 50 / duration
                assert throughput > 25, f"Webhook processing throughput too low: {throughput} ops/sec"
    
    @pytest.mark.asyncio
    async def test_payment_retry_performance(self, payment_service):
        """Test payment retry mechanism performance"""
        # Test multiple payment retries
        payment_intents = [f"pi_retry_{i}" for i in range(10)]
        
        # Mock payment confirmation with failures then success
        call_counts = {}
        
        def mock_confirm_payment_intent(payment_intent_id):
            call_counts[payment_intent_id] = call_counts.get(payment_intent_id, 0) + 1
            
            # Fail first 2 attempts, succeed on 3rd
            if call_counts[payment_intent_id] < 3:
                from services.payment_service import PaymentError
                raise PaymentError("Payment failed")
            
            return {'status': 'succeeded', 'id': payment_intent_id}
        
        with patch.object(payment_service, 'confirm_payment_intent', side_effect=mock_confirm_payment_intent):
            start_time = time.time()
            
            # Retry payments concurrently
            tasks = [
                payment_service.retry_failed_payment(pi_id, max_retries=3) 
                for pi_id in payment_intents
            ]
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Performance assertions
            # Should complete with exponential backoff but not take too long
            assert 5 < duration < 15, f"Payment retries took unexpected time: {duration}s"
            assert len(results) == 10
            assert all(r['status'] == 'succeeded' for r in results)
            
            # Verify all payments were retried correctly
            assert all(call_counts[pi_id] == 3 for pi_id in payment_intents)


class TestMemoryAndResourceUsage:
    """Test memory usage and resource consumption"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_large_datasets(self, subscription_service, db_session):
        """Test memory usage with large datasets"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        users = []
        for i in range(500):
            user = User(
                email=f"memory{i}@example.com",
                username=f"memory{i}",
                subscription_tier=SubscriptionTier.PRO if i % 2 == 0 else SubscriptionTier.FREE,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Create usage records
        usage_records = []
        for user in users:
            for j in range(10):  # 10 records per user = 5000 total
                record = UsageTracking(
                    user_id=user.id,
                    usage_type=UsageType.RESUME_PROCESSING,
                    count=1,
                    usage_date=datetime.utcnow() - timedelta(days=j % 30)
                )
                usage_records.append(record)
        
        db_session.add_all(usage_records)
        db_session.commit()
        
        # Perform operations that load data
        start_time = time.time()
        
        # Get statistics for all users
        tasks = [
            subscription_service.get_usage_statistics(str(user.id)) 
            for user in users[:100]  # Test subset to avoid timeout
        ]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Performance and memory assertions
        assert end_time - start_time < 10.0, "Operations took too long"
        assert len(results) == 100
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase}MB"
    
    def test_database_connection_efficiency(self, subscription_service, db_session):
        """Test database connection usage efficiency"""
        # Create test data
        users = []
        for i in range(100):
            user = User(
                email=f"conn{i}@example.com",
                username=f"conn{i}",
                subscription_tier=SubscriptionTier.FREE,
                weekly_usage_count=i % 6,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        # Test that operations don't create excessive database connections
        start_time = time.time()
        
        # Perform many operations that should reuse connections
        for user in users:
            # These operations should use the same session efficiently
            subscription_service.get_active_subscription(str(user.id))
            
            # Simulate usage limit check (should be fast with proper indexing)
            limits = asyncio.run(
                subscription_service.check_usage_limits(str(user.id), UsageType.RESUME_PROCESSING)
            )
            assert hasattr(limits, 'can_use')
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete efficiently
        assert duration < 2.0, f"Database operations took too long: {duration}s"


class TestScalabilityLimits:
    """Test system behavior at scale limits"""
    
    @pytest.mark.asyncio
    async def test_maximum_concurrent_operations(self, subscription_service, db_session):
        """Test system behavior with maximum concurrent operations"""
        # Create test user
        user = User(
            email="scale@example.com",
            username="scaleuser",
            subscription_tier=SubscriptionTier.PRO,
            auth_provider=AuthProvider.EMAIL
        )
        db_session.add(user)
        db_session.commit()
        
        # Test with high concurrency
        concurrent_operations = 100
        
        async def single_operation():
            return await subscription_service.check_usage_limits(
                str(user.id), 
                UsageType.RESUME_PROCESSING
            )
        
        start_time = time.time()
        
        # Create many concurrent tasks
        tasks = [single_operation() for _ in range(concurrent_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        # Performance assertions
        assert duration < 5.0, f"High concurrency test took too long: {duration}s"
        assert len(successful_results) >= concurrent_operations * 0.9, "Too many operations failed"
        assert len(failed_results) < concurrent_operations * 0.1, "Too many operations failed"
        
        # Calculate success rate
        success_rate = len(successful_results) / concurrent_operations
        assert success_rate >= 0.9, f"Success rate too low: {success_rate}"
    
    @pytest.mark.asyncio
    async def test_large_batch_processing(self, subscription_service, db_session):
        """Test processing large batches of operations"""
        # Create many users
        batch_size = 200
        users = []
        
        for i in range(batch_size):
            user = User(
                email=f"batch{i}@example.com",
                username=f"batch{i}",
                subscription_tier=SubscriptionTier.PRO if i % 10 == 0 else SubscriptionTier.FREE,
                weekly_usage_count=i % 6,
                auth_provider=AuthProvider.EMAIL
            )
            users.append(user)
        
        # Batch insert for efficiency
        db_session.add_all(users)
        db_session.commit()
        
        # Test batch operations
        start_time = time.time()
        
        # Process all users in batches
        batch_results = []
        batch_size_limit = 50  # Process in smaller batches
        
        for i in range(0, len(users), batch_size_limit):
            batch = users[i:i + batch_size_limit]
            
            # Process batch concurrently
            tasks = [
                subscription_service.validate_subscription_status(str(user.id))
                for user in batch
            ]
            
            batch_result = await asyncio.gather(*tasks)
            batch_results.extend(batch_result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 10.0, f"Batch processing took too long: {duration}s"
        assert len(batch_results) == batch_size
        
        # Verify all results are valid
        valid_results = [r for r in batch_results if isinstance(r, dict) and 'valid' in r]
        assert len(valid_results) == batch_size, "Not all batch operations returned valid results"
        
        # Calculate throughput
        throughput = batch_size / duration
        assert throughput > 20, f"Batch processing throughput too low: {throughput} ops/sec"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])