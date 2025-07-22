"""
Migration: Add subscription system tables and fields
Date: 2025-01-17
Description: Adds subscription-related tables and extends User model with subscription fields
"""

from sqlalchemy import text
from config.database import engine, SessionLocal
import logging

logger = logging.getLogger(__name__)

def upgrade():
    """Apply the migration"""
    db = SessionLocal()
    
    try:
        # Check if we're using SQLite or PostgreSQL
        is_sqlite = str(engine.url).startswith('sqlite')
        
        logger.info("Starting subscription system migration...")
        
        # 1. Add new columns to users table
        logger.info("Adding new columns to users table...")
        
        if is_sqlite:
            # SQLite doesn't support adding ENUM columns directly, so we use TEXT with CHECK constraints
            user_columns = [
                "ALTER TABLE users ADD COLUMN subscription_tier TEXT DEFAULT 'free'",
                "ALTER TABLE users ADD COLUMN stripe_customer_id TEXT",
                "ALTER TABLE users ADD COLUMN subscription_status TEXT DEFAULT 'active'",
                "ALTER TABLE users ADD COLUMN current_period_start DATETIME",
                "ALTER TABLE users ADD COLUMN current_period_end DATETIME",
                "ALTER TABLE users ADD COLUMN cancel_at_period_end BOOLEAN DEFAULT 0",
                "ALTER TABLE users ADD COLUMN weekly_usage_count INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN weekly_usage_reset DATETIME DEFAULT CURRENT_TIMESTAMP",
                "ALTER TABLE users ADD COLUMN total_usage_count INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN preferred_tailoring_mode TEXT DEFAULT 'light'"
            ]
        else:
            # PostgreSQL with proper ENUM types
            # First create the ENUM types
            enum_queries = [
                """
                DO $$ BEGIN
                    CREATE TYPE subscription_tier_enum AS ENUM ('free', 'pro');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """,
                """
                DO $$ BEGIN
                    CREATE TYPE subscription_status_enum AS ENUM ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'incomplete_expired', 'trialing');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """,
                """
                DO $$ BEGIN
                    CREATE TYPE tailoring_mode_enum AS ENUM ('light', 'heavy');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """,
                """
                DO $$ BEGIN
                    CREATE TYPE usage_type_enum AS ENUM ('resume_processing', 'cover_letter', 'bulk_processing');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """,
                """
                DO $$ BEGIN
                    CREATE TYPE payment_status_enum AS ENUM ('pending', 'succeeded', 'failed', 'canceled', 'refunded');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
                """
            ]
            
            for query in enum_queries:
                db.execute(text(query))
            
            user_columns = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier subscription_tier_enum DEFAULT 'free'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255)",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status subscription_status_enum DEFAULT 'active'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_period_start TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN DEFAULT FALSE",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS weekly_usage_count INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS weekly_usage_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_usage_count INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_tailoring_mode tailoring_mode_enum DEFAULT 'light'"
            ]
        
        for query in user_columns:
            try:
                db.execute(text(query))
                logger.info(f"Executed: {query}")
            except Exception as e:
                logger.warning(f"Column might already exist: {e}")
        
        # 2. Create subscriptions table
        logger.info("Creating subscriptions table...")
        
        if is_sqlite:
            subscriptions_table = """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                stripe_subscription_id TEXT UNIQUE,
                stripe_customer_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                tier TEXT NOT NULL DEFAULT 'free',
                current_period_start DATETIME,
                current_period_end DATETIME,
                cancel_at_period_end BOOLEAN DEFAULT 0,
                canceled_at DATETIME,
                stripe_price_id TEXT,
                stripe_product_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            subscriptions_table = """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                stripe_subscription_id VARCHAR(255) UNIQUE,
                stripe_customer_id VARCHAR(255) NOT NULL,
                status subscription_status_enum NOT NULL DEFAULT 'active',
                tier subscription_tier_enum NOT NULL DEFAULT 'free',
                current_period_start TIMESTAMP WITH TIME ZONE,
                current_period_end TIMESTAMP WITH TIME ZONE,
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                canceled_at TIMESTAMP WITH TIME ZONE,
                stripe_price_id VARCHAR(255),
                stripe_product_id VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        
        db.execute(text(subscriptions_table))
        
        # 3. Create usage_tracking table
        logger.info("Creating usage_tracking table...")
        
        if is_sqlite:
            usage_tracking_table = """
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                usage_type TEXT NOT NULL,
                usage_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                count INTEGER NOT NULL DEFAULT 1,
                metadata TEXT,
                session_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            usage_tracking_table = """
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                usage_type usage_type_enum NOT NULL,
                usage_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                count INTEGER NOT NULL DEFAULT 1,
                metadata TEXT,
                session_id VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        
        db.execute(text(usage_tracking_table))
        
        # 4. Create payment_history table
        logger.info("Creating payment_history table...")
        
        if is_sqlite:
            payment_history_table = """
            CREATE TABLE IF NOT EXISTS payment_history (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                stripe_payment_intent_id TEXT UNIQUE,
                stripe_invoice_id TEXT,
                stripe_charge_id TEXT,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'usd',
                status TEXT NOT NULL,
                description TEXT,
                payment_method_type TEXT,
                failure_reason TEXT,
                payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:
            payment_history_table = """
            CREATE TABLE IF NOT EXISTS payment_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                stripe_payment_intent_id VARCHAR(255) UNIQUE,
                stripe_invoice_id VARCHAR(255),
                stripe_charge_id VARCHAR(255),
                amount INTEGER NOT NULL,
                currency VARCHAR(3) NOT NULL DEFAULT 'usd',
                status payment_status_enum NOT NULL,
                description TEXT,
                payment_method_type VARCHAR(50),
                failure_reason VARCHAR(255),
                payment_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        
        db.execute(text(payment_history_table))
        
        # 5. Create indexes for better performance
        logger.info("Creating indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_usage_tracking_usage_date ON usage_tracking(usage_date)",
            "CREATE INDEX IF NOT EXISTS idx_payment_history_user_id ON payment_history(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_payment_history_stripe_payment_intent_id ON payment_history(stripe_payment_intent_id)"
        ]
        
        for index_query in indexes:
            try:
                db.execute(text(index_query))
                logger.info(f"Created index: {index_query}")
            except Exception as e:
                logger.warning(f"Index might already exist: {e}")
        
        # 6. Migrate existing users to new subscription system
        logger.info("Migrating existing users to new subscription system...")
        
        migration_query = """
        UPDATE users 
        SET 
            subscription_tier = CASE 
                WHEN role = 'pro' THEN 'pro' 
                ELSE 'free' 
            END,
            current_period_start = subscription_start,
            current_period_end = subscription_end
        WHERE subscription_tier IS NULL OR subscription_tier = ''
        """
        
        db.execute(text(migration_query))
        
        db.commit()
        logger.info("✅ Subscription system migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Migration failed: {e}")
        raise e
    finally:
        db.close()

def downgrade():
    """Rollback the migration"""
    db = SessionLocal()
    
    try:
        logger.info("Rolling back subscription system migration...")
        
        # Drop tables in reverse order
        tables_to_drop = [
            "DROP TABLE IF EXISTS payment_history",
            "DROP TABLE IF EXISTS usage_tracking", 
            "DROP TABLE IF EXISTS subscriptions"
        ]
        
        for query in tables_to_drop:
            db.execute(text(query))
            logger.info(f"Dropped table: {query}")
        
        # Note: We don't drop the new columns from users table to avoid data loss
        # In a production environment, you might want to handle this differently
        
        db.commit()
        logger.info("✅ Migration rollback completed!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Migration rollback failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    upgrade()