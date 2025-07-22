"""
Migration: Add subscription lifecycle management columns

This migration adds the necessary columns for subscription lifecycle management
to the existing users table and creates new tables for subscriptions, usage tracking,
and payment history.
"""

import sqlite3
import os
from datetime import datetime


def run_migration():
    """Run the migration to add subscription lifecycle columns"""
    db_path = "applyai.db"
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Running subscription lifecycle migration...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add subscription columns to users table if they don't exist
        subscription_columns = [
            ("subscription_tier", "TEXT DEFAULT 'free'"),
            ("stripe_customer_id", "TEXT"),
            ("subscription_status", "TEXT DEFAULT 'active'"),
            ("current_period_start", "TIMESTAMP"),
            ("current_period_end", "TIMESTAMP"),
            ("cancel_at_period_end", "BOOLEAN DEFAULT 0"),
            ("weekly_usage_count", "INTEGER DEFAULT 0"),
            ("weekly_usage_reset", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("total_usage_count", "INTEGER DEFAULT 0"),
            ("preferred_tailoring_mode", "TEXT DEFAULT 'light'"),
        ]
        
        for column_name, column_def in subscription_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ Error adding column {column_name}: {e}")
        
        # Create subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                stripe_subscription_id TEXT UNIQUE,
                stripe_customer_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                tier TEXT NOT NULL DEFAULT 'free',
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                cancel_at_period_end BOOLEAN DEFAULT 0,
                canceled_at TIMESTAMP,
                stripe_price_id TEXT,
                stripe_product_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created subscriptions table")
        
        # Create usage_tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                usage_type TEXT NOT NULL,
                usage_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                count INTEGER NOT NULL DEFAULT 1,
                extra_data TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created usage_tracking table")
        
        # Create payment_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                stripe_payment_intent_id TEXT UNIQUE,
                stripe_invoice_id TEXT,
                stripe_charge_id TEXT,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'usd',
                status TEXT NOT NULL,
                description TEXT,
                payment_method_type TEXT,
                failure_reason TEXT,
                payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created payment_history table")
        
        # Create user_sessions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                refresh_token TEXT UNIQUE,
                user_agent TEXT,
                ip_address TEXT,
                device_type TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created user_sessions table")
        
        # Create email_verifications table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                verification_token TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                is_verified BOOLEAN DEFAULT 0,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created email_verifications table")
        
        # Create password_resets table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                reset_token TEXT UNIQUE NOT NULL,
                is_used BOOLEAN DEFAULT 0,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        print("✅ Created password_resets table")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier)",
            "CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status)",
            "CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_users_current_period_end ON users(current_period_end)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)",
            "CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_usage_tracking_date ON usage_tracking(usage_date)",
            "CREATE INDEX IF NOT EXISTS idx_payment_history_user_id ON payment_history(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                if "already exists" not in str(e).lower():
                    print(f"⚠️ Error creating index: {e}")
        
        print("✅ Created database indexes")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()