#!/usr/bin/env python3
"""
Debug script to test OAuth callback functionality
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from config.database import get_db, SessionLocal
from models.user import User, AuthProvider
from utils.social_auth import get_social_auth_service
from datetime import datetime

async def test_oauth_flow():
    """Test the OAuth flow with a mock user"""
    
    # Test data - this would normally come from OAuth provider
    test_user_data = {
        'provider': 'google',
        'provider_id': '123456789',
        'email': 'manumaddali7@gmail.com',  # Use existing user
        'full_name': 'Test OAuth User',
        'profile_image': 'https://example.com/avatar.jpg',
        'email_verified': True
    }
    
    print("🔍 Testing OAuth callback flow...")
    print(f"📧 Test email: {test_user_data['email']}")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == test_user_data['email']).first()
        print(f"👤 Existing user found: {existing_user is not None}")
        
        if existing_user:
            print(f"   User ID: {existing_user.id}")
            print(f"   Auth provider: {existing_user.auth_provider}")
            print(f"   Is active: {existing_user.is_active}")
            
            # Test update scenario
            print("\n🔄 Testing user update...")
            try:
                existing_user.last_login = datetime.utcnow()
                if existing_user.auth_provider != AuthProvider.GOOGLE:
                    existing_user.auth_provider = AuthProvider.GOOGLE
                    existing_user.provider_id = test_user_data['provider_id']
                
                db.flush()
                print("✅ User update successful")
                
            except Exception as e:
                print(f"❌ User update failed: {e}")
                db.rollback()
        else:
            # Test create scenario
            print("\n➕ Testing user creation...")
            try:
                new_user = User(
                    email=test_user_data['email'],
                    full_name=test_user_data['full_name'],
                    profile_image=test_user_data['profile_image'],
                    auth_provider=AuthProvider.GOOGLE,
                    provider_id=test_user_data['provider_id'],
                    email_verified=test_user_data['email_verified'],
                    is_verified=True,
                    is_active=True,
                    last_login=datetime.utcnow()
                )
                
                db.add(new_user)
                db.flush()
                print("✅ User creation successful")
                print(f"   New user ID: {new_user.id}")
                
            except Exception as e:
                print(f"❌ User creation failed: {e}")
                db.rollback()
        
        # Test commit
        print("\n💾 Testing database commit...")
        try:
            db.commit()
            print("✅ Database commit successful")
        except Exception as e:
            print(f"❌ Database commit failed: {e}")
            db.rollback()
            
    except Exception as e:
        print(f"❌ General error: {e}")
        db.rollback()
    finally:
        db.close()

async def test_social_auth_service():
    """Test the social auth service"""
    print("\n🔧 Testing social auth service...")
    
    try:
        social_auth = get_social_auth_service()
        print("✅ Social auth service created")
        
        # Test OAuth URLs
        urls = social_auth.get_oauth_urls()
        print(f"🔗 OAuth URLs generated: {len(urls)} providers")
        for provider, url in urls.items():
            print(f"   {provider}: {url[:100]}...")
            
    except Exception as e:
        print(f"❌ Social auth service error: {e}")

def test_database_connection():
    """Test basic database connection"""
    print("\n🗄️  Testing database connection...")
    
    try:
        db = SessionLocal()
        
        # Test basic query
        user_count = db.query(User).count()
        print(f"✅ Database connection successful")
        print(f"   Total users: {user_count}")
        
        # Test specific user lookup
        test_email = "manumaddali7@gmail.com"
        user = db.query(User).filter(User.email == test_email).first()
        if user:
            print(f"   Found user: {user.email} ({user.auth_provider.value})")
        else:
            print(f"   User not found: {test_email}")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")

if __name__ == "__main__":
    print("🚀 Starting OAuth debug tests...\n")
    
    # Test database connection first
    test_database_connection()
    
    # Test social auth service
    asyncio.run(test_social_auth_service())
    
    # Test OAuth flow
    asyncio.run(test_oauth_flow())
    
    print("\n✅ Debug tests completed!")