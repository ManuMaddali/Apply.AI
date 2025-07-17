#!/usr/bin/env python3
"""
Database Cleanup Script for Testing
===================================

This script clears all user data from the database for testing purposes.
Run this whenever you want to start fresh during development.

Usage:
    python cleanup_db.py              # Interactive cleanup
    python cleanup_db.py --force      # Force cleanup without prompts
    python cleanup_db.py --help       # Show help
"""

import sys
import os
import argparse
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import SessionLocal
from models.user import User, UserSession, PasswordReset, EmailVerification

def print_banner():
    """Print a nice banner"""
    print("\n" + "="*60)
    print("🧹 ApplyAI Database Cleanup Tool")
    print("="*60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def get_database_stats(db):
    """Get current database statistics"""
    stats = {
        'users': db.query(User).count(),
        'sessions': db.query(UserSession).count(),
        'password_resets': db.query(PasswordReset).count(),
        'email_verifications': db.query(EmailVerification).count()
    }
    return stats

def print_stats(stats, title="Database Statistics"):
    """Print database statistics"""
    print(f"📊 {title}")
    print(f"   👥 Users: {stats['users']}")
    print(f"   🔐 Sessions: {stats['sessions']}")
    print(f"   🔑 Password Resets: {stats['password_resets']}")
    print(f"   📧 Email Verifications: {stats['email_verifications']}")
    print(f"   📈 Total Records: {sum(stats.values())}")
    print()

def list_users(db):
    """List all users in the database"""
    users = db.query(User).all()
    if users:
        print("👥 Current Users:")
        for user in users:
            status = "✅ Active" if user.is_active else "❌ Inactive"
            verified = "✅ Verified" if user.email_verified else "❌ Unverified"
            print(f"   • {user.email} ({user.auth_provider.value}) - {status}, {verified}")
        print()
    else:
        print("👥 No users found")
        print()

def confirm_cleanup(force=False):
    """Confirm cleanup operation"""
    if force:
        return True
    
    print("⚠️  WARNING: This will permanently delete ALL user data!")
    print("   • All user accounts")
    print("   • All user sessions")
    print("   • All password reset tokens")
    print("   • All email verification tokens")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ").lower().strip()
    return response in ['yes', 'y']

def cleanup_database(force=False):
    """Clean up the database"""
    print_banner()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get initial stats
        initial_stats = get_database_stats(db)
        print_stats(initial_stats, "Current Database Status")
        
        # Show current users
        list_users(db)
        
        # Check if database is already empty
        if initial_stats['users'] == 0:
            print("✅ Database is already empty! Nothing to clean.")
            return True
        
        # Confirm cleanup
        if not confirm_cleanup(force):
            print("❌ Cleanup cancelled by user")
            return False
        
        print("🧹 Starting database cleanup...")
        print()
        
        # Delete all related data first (foreign key constraints)
        print("🗑️  Deleting related data...")
        
        # Email verifications
        deleted_verifications = db.query(EmailVerification).count()
        db.query(EmailVerification).delete()
        print(f"   ✅ Deleted {deleted_verifications} email verifications")
        
        # Password resets
        deleted_resets = db.query(PasswordReset).count()
        db.query(PasswordReset).delete()
        print(f"   ✅ Deleted {deleted_resets} password resets")
        
        # User sessions
        deleted_sessions = db.query(UserSession).count()
        db.query(UserSession).delete()
        print(f"   ✅ Deleted {deleted_sessions} user sessions")
        
        # Delete all users
        print("\n🗑️  Deleting users...")
        deleted_users = db.query(User).count()
        db.query(User).delete()
        print(f"   ✅ Deleted {deleted_users} users")
        
        # Commit all changes
        db.commit()
        print()
        
        # Get final stats
        final_stats = get_database_stats(db)
        print_stats(final_stats, "Final Database Status")
        
        print("✅ Database cleanup completed successfully!")
        print("🎉 You can now register with any email address")
        print("🚀 Ready for fresh testing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Clean up ApplyAI database for testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cleanup_db.py              # Interactive cleanup
    python cleanup_db.py --force      # Force cleanup without prompts
    python cleanup_db.py --stats      # Show database stats only
        """
    )
    
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force cleanup without confirmation prompts'
    )
    
    parser.add_argument(
        '--stats', 
        action='store_true',
        help='Show database statistics only (no cleanup)'
    )
    
    args = parser.parse_args()
    
    # Stats only mode
    if args.stats:
        print_banner()
        db = SessionLocal()
        try:
            stats = get_database_stats(db)
            print_stats(stats)
            list_users(db)
        finally:
            db.close()
        return
    
    # Cleanup mode
    success = cleanup_database(args.force)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 