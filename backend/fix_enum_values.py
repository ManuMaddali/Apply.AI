#!/usr/bin/env python3
"""
Fix TailoringMode enum values in database
This script updates lowercase enum values to uppercase to match the enum definition
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_db
from sqlalchemy import text

def fix_tailoring_mode_enum():
    """Fix tailoring mode enum values in database"""
    db = next(get_db())
    
    try:
        print("🔍 Checking current tailoring mode values...")
        
        # Check current values
        result = db.execute(text("SELECT DISTINCT preferred_tailoring_mode FROM users WHERE preferred_tailoring_mode IS NOT NULL"))
        current_values = [row[0] for row in result.fetchall()]
        print(f"Current values: {current_values}")
        
        # Update lowercase to uppercase
        if 'light' in current_values:
            print("📝 Updating 'light' to 'LIGHT'...")
            db.execute(text("UPDATE users SET preferred_tailoring_mode = 'LIGHT' WHERE preferred_tailoring_mode = 'light'"))
            
        if 'heavy' in current_values:
            print("📝 Updating 'heavy' to 'HEAVY'...")
            db.execute(text("UPDATE users SET preferred_tailoring_mode = 'HEAVY' WHERE preferred_tailoring_mode = 'heavy'"))
        
        # Commit changes
        db.commit()
        
        # Verify changes
        result = db.execute(text("SELECT DISTINCT preferred_tailoring_mode FROM users WHERE preferred_tailoring_mode IS NOT NULL"))
        updated_values = [row[0] for row in result.fetchall()]
        print(f"✅ Updated values: {updated_values}")
        
        print("✅ TailoringMode enum values fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing enum values: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_tailoring_mode_enum()
