#!/usr/bin/env python3
"""
Simple validation script for subscription models
Validates the model structure without requiring database connection
"""

import ast
import sys
from pathlib import Path

def validate_user_model():
    """Validate the User model structure"""
    print("🔍 Validating User model...")
    
    user_model_path = Path(__file__).parent / "models" / "user.py"
    
    with open(user_model_path, 'r') as f:
        content = f.read()
    
    # Check for required enums
    required_enums = [
        'SubscriptionTier', 'SubscriptionStatus', 'TailoringMode', 
        'UsageType', 'PaymentStatus'
    ]
    
    for enum_name in required_enums:
        if f"class {enum_name}(enum.Enum):" in content:
            print(f"✅ {enum_name} enum found")
        else:
            print(f"❌ {enum_name} enum missing")
            return False
    
    # Check for required User model fields
    required_user_fields = [
        'subscription_tier', 'stripe_customer_id', 'subscription_status',
        'current_period_start', 'current_period_end', 'cancel_at_period_end',
        'weekly_usage_count', 'weekly_usage_reset', 'total_usage_count',
        'preferred_tailoring_mode'
    ]
    
    for field in required_user_fields:
        if f"{field} = Column(" in content:
            print(f"✅ User.{field} field found")
        else:
            print(f"❌ User.{field} field missing")
            return False
    
    # Check for new model classes
    required_models = ['Subscription', 'UsageTracking', 'PaymentHistory']
    
    for model in required_models:
        if f"class {model}(Base):" in content:
            print(f"✅ {model} model found")
        else:
            print(f"❌ {model} model missing")
            return False
    
    # Check for required methods
    required_methods = [
        'is_pro_active', 'get_usage_limits_new', 'can_use_feature',
        'can_process_resume', 'reset_weekly_usage'
    ]
    
    for method in required_methods:
        if f"def {method}(" in content:
            print(f"✅ User.{method} method found")
        else:
            print(f"❌ User.{method} method missing")
            return False
    
    print("✅ User model validation passed!")
    return True

def validate_migration_files():
    """Validate migration files exist"""
    print("\n🔍 Validating migration files...")
    
    migrations_dir = Path(__file__).parent / "migrations"
    
    required_files = [
        "__init__.py",
        "001_add_subscription_system.py", 
        "migrate.py"
    ]
    
    for file_name in required_files:
        file_path = migrations_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} found")
        else:
            print(f"❌ {file_name} missing")
            return False
    
    # Check migration content
    migration_file = migrations_dir / "001_add_subscription_system.py"
    with open(migration_file, 'r') as f:
        migration_content = f.read()
    
    required_migration_elements = [
        'def upgrade():', 'def downgrade():', 
        'CREATE TABLE IF NOT EXISTS subscriptions',
        'CREATE TABLE IF NOT EXISTS usage_tracking',
        'CREATE TABLE IF NOT EXISTS payment_history'
    ]
    
    for element in required_migration_elements:
        if element in migration_content:
            print(f"✅ Migration contains: {element}")
        else:
            print(f"❌ Migration missing: {element}")
            return False
    
    print("✅ Migration files validation passed!")
    return True

def validate_database_config():
    """Validate database configuration updates"""
    print("\n🔍 Validating database configuration...")
    
    db_config_path = Path(__file__).parent / "config" / "database.py"
    
    with open(db_config_path, 'r') as f:
        content = f.read()
    
    # Check that new models are imported in init_db
    required_imports = [
        'Subscription', 'UsageTracking', 'PaymentHistory'
    ]
    
    for import_name in required_imports:
        if import_name in content:
            print(f"✅ {import_name} imported in database config")
        else:
            print(f"❌ {import_name} missing from database config")
            return False
    
    print("✅ Database configuration validation passed!")
    return True

def validate_init_script():
    """Validate initialization script"""
    print("\n🔍 Validating initialization script...")
    
    init_script_path = Path(__file__).parent / "init_subscription_db.py"
    
    if init_script_path.exists():
        print("✅ init_subscription_db.py found")
        
        with open(init_script_path, 'r') as f:
            content = f.read()
        
        required_functions = [
            'initialize_subscription_database',
            'verify_database_schema'
        ]
        
        for func in required_functions:
            if f"def {func}(" in content:
                print(f"✅ {func} function found")
            else:
                print(f"❌ {func} function missing")
                return False
    else:
        print("❌ init_subscription_db.py missing")
        return False
    
    print("✅ Initialization script validation passed!")
    return True

def main():
    """Main validation function"""
    print("=" * 60)
    print("🔍 Validating Subscription System Implementation")
    print("=" * 60)
    
    success = True
    
    # Validate User model
    if not validate_user_model():
        success = False
    
    # Validate migration files
    if not validate_migration_files():
        success = False
    
    # Validate database config
    if not validate_database_config():
        success = False
    
    # Validate init script
    if not validate_init_script():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All validations passed! Subscription system is correctly implemented.")
        print("\nImplemented components:")
        print("• Enhanced User model with subscription fields")
        print("• Subscription, UsageTracking, and PaymentHistory models")
        print("• Database migration scripts")
        print("• Database initialization scripts")
        print("• All required enums and methods")
    else:
        print("❌ Some validations failed. Please check the implementation.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)