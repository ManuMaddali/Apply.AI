#!/usr/bin/env python3
"""
Database Initialization Script for Subscription System
Creates all tables and runs necessary migrations
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from config.database import init_db, create_default_users, engine, SessionLocal
from migrations.migrate import MigrationRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_subscription_database():
    """Initialize the database with subscription system"""
    try:
        logger.info("🚀 Initializing subscription database...")
        
        # 1. Create base tables using existing init_db
        logger.info("Creating base database tables...")
        init_db()
        
        # 2. Run subscription system migrations
        logger.info("Running subscription system migrations...")
        runner = MigrationRunner()
        success = runner.run_all_migrations()
        runner.close()
        
        if not success:
            logger.error("❌ Migration failed, database initialization incomplete")
            return False
        
        # 3. Create default users (if in development)
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.info("Creating default users...")
            create_default_users()
        
        logger.info("✅ Subscription database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def verify_database_schema():
    """Verify that all required tables exist"""
    db = SessionLocal()
    
    try:
        logger.info("🔍 Verifying database schema...")
        
        # Check if we're using SQLite or PostgreSQL
        is_sqlite = str(engine.url).startswith('sqlite')
        
        if is_sqlite:
            # SQLite table check
            tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        else:
            # PostgreSQL table check
            tables_query = "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        
        from sqlalchemy import text
        result = db.execute(text(tables_query))
        existing_tables = {row[0] for row in result.fetchall()}
        
        required_tables = {
            'users', 'user_sessions', 'password_resets', 'email_verifications',
            'subscriptions', 'usage_tracking', 'payment_history', 'migration_history'
        }
        
        missing_tables = required_tables - existing_tables
        
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False
        
        logger.info("✅ All required tables exist")
        
        # Check for required columns in users table
        if is_sqlite:
            columns_query = "PRAGMA table_info(users)"
        else:
            columns_query = """
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND table_schema = 'public'
            """
        
        result = db.execute(text(columns_query))
        if is_sqlite:
            existing_columns = {row[1] for row in result.fetchall()}  # SQLite PRAGMA returns (cid, name, type, ...)
        else:
            existing_columns = {row[0] for row in result.fetchall()}
        
        required_columns = {
            'subscription_tier', 'stripe_customer_id', 'subscription_status',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'weekly_usage_count', 'weekly_usage_reset', 'total_usage_count',
            'preferred_tailoring_mode'
        }
        
        missing_columns = required_columns - existing_columns
        
        if missing_columns:
            logger.error(f"❌ Missing columns in users table: {missing_columns}")
            return False
        
        logger.info("✅ All required columns exist in users table")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema verification failed: {e}")
        return False
    finally:
        db.close()

def main():
    """Main initialization function"""
    logger.info("=" * 60)
    logger.info("🎯 ApplyAI Subscription Database Initialization")
    logger.info("=" * 60)
    
    # Initialize database
    if not initialize_subscription_database():
        logger.error("❌ Database initialization failed")
        sys.exit(1)
    
    # Verify schema
    if not verify_database_schema():
        logger.error("❌ Schema verification failed")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🎉 Database initialization completed successfully!")
    logger.info("=" * 60)
    
    # Show migration status
    runner = MigrationRunner()
    runner.get_migration_status()
    runner.close()

if __name__ == "__main__":
    main()