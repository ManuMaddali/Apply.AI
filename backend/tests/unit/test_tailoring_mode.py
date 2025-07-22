#!/usr/bin/env python3
"""
Test script for tailoring mode functionality
Tests Light vs Heavy tailoring modes and Pro user access control
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.user import User, TailoringMode, SubscriptionTier, SubscriptionStatus
from utils.gpt_prompt import GPTProcessor
from utils.langchain_processor import LangChainResumeProcessor

# Test data
SAMPLE_RESUME = """
JOHN SMITH
Software Engineer
john.smith@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johnsmith

PROFESSIONAL EXPERIENCE

TechCorp Inc. | San Francisco, CA
Software Developer | Jan 2020 - Present
• Developed web applications using React and Node.js for internal tools
• Worked with databases to store and retrieve user information
• Collaborated with team members on various projects
• Fixed bugs and improved application performance
• Participated in code reviews and team meetings

StartupXYZ | San Francisco, CA  
Junior Developer | Jun 2018 - Dec 2019
• Built features for mobile application using React Native
• Helped with testing and debugging of software applications
• Worked on API integrations with third-party services
• Assisted senior developers with complex programming tasks

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2018

SKILLS
Programming Languages: JavaScript, Python, Java
Frameworks: React, Node.js, Express
Databases: MySQL, MongoDB
Tools: Git, Docker, AWS
"""

SAMPLE_JOB_DESCRIPTION = """
Senior Product Manager - Data Platform

We are seeking an experienced Senior Product Manager to lead our data platform initiatives. The ideal candidate will have 5+ years of product management experience with a strong background in data analytics, machine learning, and enterprise software.

Key Responsibilities:
- Define and execute product strategy for our data analytics platform
- Collaborate with engineering, design, and data science teams to deliver high-impact features
- Conduct user research and analyze customer feedback to inform product decisions
- Manage product roadmap and prioritize features based on business impact
- Work with stakeholders across the organization to align on product vision
- Drive adoption of data-driven decision making across the company
- Lead cross-functional teams in an agile development environment

Requirements:
- 5+ years of product management experience, preferably in B2B SaaS
- Strong analytical skills and experience with data visualization tools
- Experience with machine learning and AI product development
- Excellent communication and stakeholder management skills
- Bachelor's degree in Engineering, Computer Science, or related field
- Experience with agile methodologies and product development lifecycle
- Track record of launching successful products and driving user adoption

Preferred Qualifications:
- MBA or advanced degree
- Experience with enterprise software and platform products
- Knowledge of SQL, Python, or other data analysis tools
- Experience working with large datasets and analytics platforms
"""

def create_test_users():
    """Create test users with different subscription tiers"""
    
    # Free user
    free_user = User(
        id="free-user-123",
        email="free@test.com",
        subscription_tier=SubscriptionTier.FREE,
        subscription_status=SubscriptionStatus.ACTIVE
    )
    
    # Pro user with active subscription
    pro_user = User(
        id="pro-user-123", 
        email="pro@test.com",
        subscription_tier=SubscriptionTier.PRO,
        subscription_status=SubscriptionStatus.ACTIVE,
        current_period_end=datetime.utcnow() + timedelta(days=30)
    )
    
    # Expired Pro user
    expired_pro_user = User(
        id="expired-pro-user-123",
        email="expired@test.com", 
        subscription_tier=SubscriptionTier.PRO,
        subscription_status=SubscriptionStatus.ACTIVE,
        current_period_end=datetime.utcnow() - timedelta(days=1)
    )
    
    return free_user, pro_user, expired_pro_user

def test_tailoring_mode_access_control():
    """Test that tailoring mode access is properly controlled"""
    print("🧪 Testing Tailoring Mode Access Control")
    print("=" * 50)
    
    free_user, pro_user, expired_pro_user = create_test_users()
    
    # Test Free user access
    print(f"Free user can use Heavy tailoring: {free_user.can_use_feature('heavy_tailoring')}")
    print(f"Free user is Pro active: {free_user.is_pro_active()}")
    
    # Test Pro user access  
    print(f"Pro user can use Heavy tailoring: {pro_user.can_use_feature('heavy_tailoring')}")
    print(f"Pro user is Pro active: {pro_user.is_pro_active()}")
    
    # Test expired Pro user access
    print(f"Expired Pro user can use Heavy tailoring: {expired_pro_user.can_use_feature('heavy_tailoring')}")
    print(f"Expired Pro user is Pro active: {expired_pro_user.is_pro_active()}")
    
    print()

def test_gpt_processor_tailoring_modes():
    """Test GPT processor with different tailoring modes"""
    print("🧪 Testing GPT Processor Tailoring Modes")
    print("=" * 50)
    
    try:
        processor = GPTProcessor()
        
        # Test Light tailoring mode
        print("Testing Light Tailoring Mode...")
        light_result = processor.tailor_resume(
            SAMPLE_RESUME,
            SAMPLE_JOB_DESCRIPTION,
            "Senior Product Manager",
            {},
            TailoringMode.LIGHT
        )
        
        if light_result:
            print("✅ Light tailoring mode completed successfully")
            print(f"Light result length: {len(light_result)} characters")
            print("Light result preview:")
            print(light_result[:300] + "..." if len(light_result) > 300 else light_result)
        else:
            print("❌ Light tailoring mode failed")
        
        print("\n" + "-" * 30 + "\n")
        
        # Test Heavy tailoring mode
        print("Testing Heavy Tailoring Mode...")
        heavy_result = processor.tailor_resume(
            SAMPLE_RESUME,
            SAMPLE_JOB_DESCRIPTION,
            "Senior Product Manager", 
            {},
            TailoringMode.HEAVY
        )
        
        if heavy_result:
            print("✅ Heavy tailoring mode completed successfully")
            print(f"Heavy result length: {len(heavy_result)} characters")
            print("Heavy result preview:")
            print(heavy_result[:300] + "..." if len(heavy_result) > 300 else heavy_result)
        else:
            print("❌ Heavy tailoring mode failed")
            
        # Compare results
        if light_result and heavy_result:
            print(f"\n📊 Comparison:")
            print(f"Light mode length: {len(light_result)}")
            print(f"Heavy mode length: {len(heavy_result)}")
            print(f"Length difference: {abs(len(heavy_result) - len(light_result))} characters")
            
            # Check for different content
            if light_result != heavy_result:
                print("✅ Light and Heavy modes produce different results")
            else:
                print("⚠️ Light and Heavy modes produce identical results")
        
    except Exception as e:
        print(f"❌ GPT Processor test failed: {str(e)}")
    
    print()

def test_langchain_processor_tailoring_modes():
    """Test LangChain processor with different tailoring modes"""
    print("🧪 Testing LangChain Processor Tailoring Modes")
    print("=" * 50)
    
    try:
        processor = LangChainResumeProcessor()
        
        if not processor.langchain_available:
            print("⚠️ LangChain not available, skipping LangChain tests")
            return
        
        # Test Light tailoring mode
        print("Testing Light Tailoring Mode with RAG...")
        light_result = processor.tailor_resume_with_rag(
            SAMPLE_RESUME,
            SAMPLE_JOB_DESCRIPTION,
            "Senior Product Manager",
            {},
            TailoringMode.LIGHT
        )
        
        if light_result:
            print("✅ Light tailoring mode with RAG completed successfully")
            print(f"Light result keys: {list(light_result.keys())}")
            if 'tailored_resume' in light_result:
                resume_length = len(light_result['tailored_resume'])
                print(f"Light resume length: {resume_length} characters")
        else:
            print("❌ Light tailoring mode with RAG failed")
        
        print("\n" + "-" * 30 + "\n")
        
        # Test Heavy tailoring mode
        print("Testing Heavy Tailoring Mode with RAG...")
        heavy_result = processor.tailor_resume_with_rag(
            SAMPLE_RESUME,
            SAMPLE_JOB_DESCRIPTION,
            "Senior Product Manager",
            {},
            TailoringMode.HEAVY
        )
        
        if heavy_result:
            print("✅ Heavy tailoring mode with RAG completed successfully")
            print(f"Heavy result keys: {list(heavy_result.keys())}")
            if 'tailored_resume' in heavy_result:
                resume_length = len(heavy_result['tailored_resume'])
                print(f"Heavy resume length: {resume_length} characters")
        else:
            print("❌ Heavy tailoring mode with RAG failed")
            
        # Compare results
        if (light_result and heavy_result and 
            'tailored_resume' in light_result and 'tailored_resume' in heavy_result):
            light_resume = light_result['tailored_resume']
            heavy_resume = heavy_result['tailored_resume']
            
            print(f"\n📊 RAG Comparison:")
            print(f"Light mode length: {len(light_resume)}")
            print(f"Heavy mode length: {len(heavy_resume)}")
            print(f"Length difference: {abs(len(heavy_resume) - len(light_resume))} characters")
            
            # Check for different content
            if light_resume != heavy_resume:
                print("✅ Light and Heavy RAG modes produce different results")
            else:
                print("⚠️ Light and Heavy RAG modes produce identical results")
        
    except Exception as e:
        print(f"❌ LangChain Processor test failed: {str(e)}")
    
    print()

def test_fallback_behavior():
    """Test that Free users fall back to Light mode when requesting Heavy"""
    print("🧪 Testing Fallback Behavior")
    print("=" * 50)
    
    free_user, pro_user, expired_pro_user = create_test_users()
    
    # Simulate the logic from the route handler
    def simulate_tailoring_mode_validation(user, requested_mode):
        effective_mode = requested_mode or TailoringMode.LIGHT
        fallback = False
        fallback_reason = None
        
        if effective_mode == TailoringMode.HEAVY and not user.is_pro_active():
            effective_mode = TailoringMode.LIGHT
            fallback = True
            fallback_reason = "Heavy tailoring requires Pro subscription"
        
        return effective_mode, fallback, fallback_reason
    
    # Test Free user requesting Heavy mode
    effective, fallback, reason = simulate_tailoring_mode_validation(free_user, TailoringMode.HEAVY)
    print(f"Free user requests Heavy → Effective: {effective.value}, Fallback: {fallback}, Reason: {reason}")
    
    # Test Pro user requesting Heavy mode
    effective, fallback, reason = simulate_tailoring_mode_validation(pro_user, TailoringMode.HEAVY)
    print(f"Pro user requests Heavy → Effective: {effective.value}, Fallback: {fallback}, Reason: {reason}")
    
    # Test Free user requesting Light mode
    effective, fallback, reason = simulate_tailoring_mode_validation(free_user, TailoringMode.LIGHT)
    print(f"Free user requests Light → Effective: {effective.value}, Fallback: {fallback}, Reason: {reason}")
    
    print()

def test_prompt_differences():
    """Test that Light and Heavy modes generate different prompts"""
    print("🧪 Testing Prompt Differences")
    print("=" * 50)
    
    try:
        processor = GPTProcessor()
        
        # Generate prompts for both modes
        light_prompt = processor._create_tailoring_prompt(
            SAMPLE_RESUME,
            SAMPLE_JOB_DESCRIPTION,
            "Senior Product Manager",
            {},
            TailoringMode.LIGHT
        )
        
        heavy_prompt = processor._create_tailoring_prompt(
            SAMPLE_RESUME,
            SAMPLE_JOB_DESCRIPTION,
            "Senior Product Manager",
            {},
            TailoringMode.HEAVY
        )
        
        print(f"Light prompt length: {len(light_prompt)} characters")
        print(f"Heavy prompt length: {len(heavy_prompt)} characters")
        
        # Check for mode-specific keywords
        light_keywords = ["LIGHT TAILORING MODE", "minimal changes", "preserve", "25% content change"]
        heavy_keywords = ["HEAVY TAILORING MODE", "comprehensive transformation", "70% content transformation", "aggressive"]
        
        light_found = sum(1 for keyword in light_keywords if keyword.lower() in light_prompt.lower())
        heavy_found = sum(1 for keyword in heavy_keywords if keyword.lower() in heavy_prompt.lower())
        
        print(f"Light mode keywords found in light prompt: {light_found}/{len(light_keywords)}")
        print(f"Heavy mode keywords found in heavy prompt: {heavy_found}/{len(heavy_keywords)}")
        
        if light_prompt != heavy_prompt:
            print("✅ Light and Heavy modes generate different prompts")
        else:
            print("❌ Light and Heavy modes generate identical prompts")
            
    except Exception as e:
        print(f"❌ Prompt difference test failed: {str(e)}")
    
    print()

def main():
    """Run all tailoring mode tests"""
    print("🚀 Starting Tailoring Mode Tests")
    print("=" * 60)
    print()
    
    # Run all tests
    test_tailoring_mode_access_control()
    test_fallback_behavior()
    test_prompt_differences()
    
    # Only run AI tests if we have an API key
    if os.getenv("OPENAI_API_KEY"):
        print("🤖 Running AI-powered tests (this may take a while)...")
        print()
        test_gpt_processor_tailoring_modes()
        test_langchain_processor_tailoring_modes()
    else:
        print("⚠️ OPENAI_API_KEY not found, skipping AI-powered tests")
        print()
    
    print("✅ All tailoring mode tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()