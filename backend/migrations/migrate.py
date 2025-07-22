#!/usr/bin/env python3
"""
Database Migration Runner
Handles running database migrations for the subscription system
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.database import engine, SessionLocal
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationRunner:
    """Handles database migrations"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.migrations_dir = Path(__file__).parent
        self.ensure_migration_table()
    
    def ensure_migration_table(self):
        """Create migrations tracking table if it doesn't exist"""
        try:
            # Check if we're using SQLite or PostgreSQL
            is_sqlite = str(engine.url).startswith('sqlite')
            
            if is_sqlite:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS migration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name TEXT NOT NULL UNIQUE,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT 1
                )
                """
            else:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS migration_history (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    success BOOLEAN DEFAULT TRUE
                )
                """
            
            self.db.execute(text(create_table_query))
            self.db.commit()
            logger.info("Migration tracking table ready")
            
        except Exception as e:
            logger.error(f"Failed to create migration tracking table: {e}")
            self.db.rollback()
            raise
    
    def is_migration_applied(self, migration_name: str) -> bool:
        """Check if a migration has already been applied"""
        try:
            result = self.db.execute(
                text("SELECT COUNT(*) FROM migration_history WHERE migration_name = :name AND success = 1"),
                {"name": migration_name}
            ).scalar()
            return result > 0
        except Exception as e:
            logger.error(f"Failed to check migration status: {e}")
            return False
    
    def record_migration(self, migration_name: str, success: bool = True):
        """Record a migration in the history table"""
        try:
            self.db.execute(
                text("INSERT INTO migration_history (migration_name, success) VALUES (:name, :success)"),
                {"name": migration_name, "success": success}
            )
            self.db.commit()
            logger.info(f"Recorded migration: {migration_name} (success: {success})")
        except Exception as e:
            logger.error(f"Failed to record migration: {e}")
            self.db.rollback()
    
    def run_migration(self, migration_name: str):
        """Run a specific migration"""
        if self.is_migration_applied(migration_name):
            logger.info(f"Migration {migration_name} already applied, skipping")
            return True
        
        try:
            logger.info(f"Running migration: {migration_name}")
            
            # Import and run the migration
            migration_module = __import__(f"migrations.{migration_name}", fromlist=['upgrade'])
            migration_module.upgrade()
            
            # Record successful migration
            self.record_migration(migration_name, True)
            logger.info(f"✅ Migration {migration_name} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration {migration_name} failed: {e}")
            self.record_migration(migration_name, False)
            return False
    
    def run_all_migrations(self):
        """Run all pending migrations"""
        migrations = [
            "001_add_subscription_system"
        ]
        
        logger.info("Starting database migrations...")
        
        success_count = 0
        for migration in migrations:
            if self.run_migration(migration):
                success_count += 1
            else:
                logger.error(f"Migration {migration} failed, stopping")
                break
        
        logger.info(f"Completed {success_count}/{len(migrations)} migrations")
        return success_count == len(migrations)
    
    def rollback_migration(self, migration_name: str):
        """Rollback a specific migration"""
        try:
            logger.info(f"Rolling back migration: {migration_name}")
            
            # Import and run the rollback
            migration_module = __import__(f"migrations.{migration_name}", fromlist=['downgrade'])
            migration_module.downgrade()
            
            # Remove from migration history
            self.db.execute(
                text("DELETE FROM migration_history WHERE migration_name = :name"),
                {"name": migration_name}
            )
            self.db.commit()
            
            logger.info(f"✅ Migration {migration_name} rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration rollback {migration_name} failed: {e}")
            self.db.rollback()
            return False
    
    def get_migration_status(self):
        """Get status of all migrations"""
        try:
            result = self.db.execute(
                text("SELECT migration_name, applied_at, success FROM migration_history ORDER BY applied_at")
            ).fetchall()
            
            logger.info("Migration Status:")
            logger.info("-" * 50)
            for row in result:
                status = "✅ SUCCESS" if row[2] else "❌ FAILED"
                logger.info(f"{row[0]}: {status} at {row[1]}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main migration runner"""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [command]")
        print("Commands:")
        print("  migrate    - Run all pending migrations")
        print("  status     - Show migration status")
        print("  rollback [migration_name] - Rollback specific migration")
        sys.exit(1)
    
    command = sys.argv[1]
    runner = MigrationRunner()
    
    try:
        if command == "migrate":
            success = runner.run_all_migrations()
            sys.exit(0 if success else 1)
            
        elif command == "status":
            runner.get_migration_status()
            
        elif command == "rollback":
            if len(sys.argv) < 3:
                print("Please specify migration name to rollback")
                sys.exit(1)
            migration_name = sys.argv[2]
            success = runner.rollback_migration(migration_name)
            sys.exit(0 if success else 1)
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    finally:
        runner.close()

if __name__ == "__main__":
    main()