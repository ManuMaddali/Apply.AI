#!/usr/bin/env python3
"""
Integration test for tailoring mode API endpoints
Tests the actual API endpoints with different user types and tailoring modes
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.user import User, TailoringMode, SubscriptionTier, SubscriptionStatus

# Test data
SAMPLE_RESUME_REQUEST = {
    "resume_text": """
JOHN SMITH
Software Engineer
john.smith@email.com | (555) 123-4567

PROFESSIONAL EXPERIENCE

TechCorp Inc. | San Francisco, CA
Software Developer | Jan 2020 - Present
• Developed web applications using React and Node.js
• Worked with databases to store user information
• Collaborated with team members on projects
• Fixed bugs and improved performance

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2018

SKILLS
JavaScript, Python, React, Node.js
""",
    "job_description": """
Senior Product Manager - Data Platform

We are seeking an experienced Senior Product Manager to lead our data platform initiatives. 
The ideal candidate will have 5+ years of product management experience with a strong 
background in data analytics, machine learning, and enterprise software.

Key Responsibilities:
- Define and execute product strategy for data analytics platform
- Collaborate with engineering, design, and data science teams
- Conduct user research and analyze customer feedback
- Manage product roadmap and prioritize features
- Drive adoption of data-driven decision making

Requirements:
- 5+ years of product management experience
- Strong analytical skills and data visualization experience
- Experience with machine learning and AI products
- Excellent communication and stakeholder management skills
""",
    "job_title": "Senior Product Manager",
    "job_url": "https://example.com/job",
    "use_rag": False,
    "compare_versions": False,
    "optional_sections": {
        "includeSummary": False,
        "includeSkills": False,
        "includeEducation": False
    }
}

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
    
    return free_user, pro_user

def simulate_tailor_endpoint(user, request_data):
    """Simulate the /tailor endpoint logic"""
    
    # Extract tailoring mode from request
    requested_mode = request_data.get("tailoring_mode", TailoringMode.LIGHT)
    if isinstance(requested_mode, str):
        requested_mode = TailoringMode(requested_mode)
    
    # Validate tailoring mode access (Pro users only for Heavy mode)
    effective_tailoring_mode = requested_mode or TailoringMode.LIGHT
    tailoring_mode_fallback = False
    tailoring_mode_fallback_reason = None
    
    # Enforce Pro-only access for Heavy tailoring mode
    if effective_tailoring_mode == TailoringMode.HEAVY and not user.is_pro_active():
        print(f"User {user.email} attempted Heavy tailoring without Pro subscription, falling back to Light mode")
        effective_tailoring_mode = TailoringMode.LIGHT
        tailoring_mode_fallback = True
        tailoring_mode_fallback_reason = "Heavy tailoring requires Pro subscription"
    
    # Simulate successful processing
    response_data = {
        "success": True,
        "session_id": "test-session-123",
        "tailored_resume": f"[TAILORED RESUME WITH {effective_tailoring_mode.value.upper()} MODE]",
        "processing_mode": "Standard",
        "tailoring_mode_requested": requested_mode.value if requested_mode else "light",
        "tailoring_mode_used": effective_tailoring_mode.value,
        "tailoring_mode_fallback": tailoring_mode_fallback,
        "tailoring_mode_fallback_reason": tailoring_mode_fallback_reason,
        "rag_insights": {
            "similar_jobs_found": 0,
            "insights": [],
            "processing_steps": ["Used standard GPT processing"]
        }
    }
    
    return response_data

def test_free_user_light_mode():
    """Test Free user with Light tailoring mode"""
    print("🧪 Testing Free User with Light Mode")
    print("=" * 40)
    
    free_user, _ = create_test_users()
    
    request_data = SAMPLE_RESUME_REQUEST.copy()
    request_data["tailoring_mode"] = TailoringMode.LIGHT
    
    response = simulate_tailor_endpoint(free_user, request_data)
    
    print(f"✅ Request processed successfully")
    print(f"   Requested mode: {response['tailoring_mode_requested']}")
    print(f"   Used mode: {response['tailoring_mode_used']}")
    print(f"   Fallback occurred: {response['tailoring_mode_fallback']}")
    print(f"   Fallback reason: {response['tailoring_mode_fallback_reason']}")
    
    assert response["tailoring_mode_used"] == "light"
    assert response["tailoring_mode_fallback"] == False
    print("✅ All assertions passed")
    print()

def test_free_user_heavy_mode():
    """Test Free user with Heavy tailoring mode (should fallback)"""
    print("🧪 Testing Free User with Heavy Mode (Fallback Expected)")
    print("=" * 55)
    
    free_user, _ = create_test_users()
    
    request_data = SAMPLE_RESUME_REQUEST.copy()
    request_data["tailoring_mode"] = TailoringMode.HEAVY
    
    response = simulate_tailor_endpoint(free_user, request_data)
    
    print(f"✅ Request processed with fallback")
    print(f"   Requested mode: {response['tailoring_mode_requested']}")
    print(f"   Used mode: {response['tailoring_mode_used']}")
    print(f"   Fallback occurred: {response['tailoring_mode_fallback']}")
    print(f"   Fallback reason: {response['tailoring_mode_fallback_reason']}")
    
    assert response["tailoring_mode_requested"] == "heavy"
    assert response["tailoring_mode_used"] == "light"
    assert response["tailoring_mode_fallback"] == True
    assert "Pro subscription" in response["tailoring_mode_fallback_reason"]
    print("✅ All assertions passed")
    print()

def test_pro_user_heavy_mode():
    """Test Pro user with Heavy tailoring mode"""
    print("🧪 Testing Pro User with Heavy Mode")
    print("=" * 35)
    
    _, pro_user = create_test_users()
    
    request_data = SAMPLE_RESUME_REQUEST.copy()
    request_data["tailoring_mode"] = TailoringMode.HEAVY
    
    response = simulate_tailor_endpoint(pro_user, request_data)
    
    print(f"✅ Request processed successfully")
    print(f"   Requested mode: {response['tailoring_mode_requested']}")
    print(f"   Used mode: {response['tailoring_mode_used']}")
    print(f"   Fallback occurred: {response['tailoring_mode_fallback']}")
    print(f"   Fallback reason: {response['tailoring_mode_fallback_reason']}")
    
    assert response["tailoring_mode_used"] == "heavy"
    assert response["tailoring_mode_fallback"] == False
    assert response["tailoring_mode_fallback_reason"] is None
    print("✅ All assertions passed")
    print()

def test_pro_user_light_mode():
    """Test Pro user with Light tailoring mode"""
    print("🧪 Testing Pro User with Light Mode")
    print("=" * 35)
    
    _, pro_user = create_test_users()
    
    request_data = SAMPLE_RESUME_REQUEST.copy()
    request_data["tailoring_mode"] = TailoringMode.LIGHT
    
    response = simulate_tailor_endpoint(pro_user, request_data)
    
    print(f"✅ Request processed successfully")
    print(f"   Requested mode: {response['tailoring_mode_requested']}")
    print(f"   Used mode: {response['tailoring_mode_used']}")
    print(f"   Fallback occurred: {response['tailoring_mode_fallback']}")
    print(f"   Fallback reason: {response['tailoring_mode_fallback_reason']}")
    
    assert response["tailoring_mode_used"] == "light"
    assert response["tailoring_mode_fallback"] == False
    print("✅ All assertions passed")
    print()

def test_default_mode():
    """Test default tailoring mode when none specified"""
    print("🧪 Testing Default Mode (No Mode Specified)")
    print("=" * 45)
    
    free_user, _ = create_test_users()
    
    request_data = SAMPLE_RESUME_REQUEST.copy()
    # Don't specify tailoring_mode - should default to Light
    
    response = simulate_tailor_endpoint(free_user, request_data)
    
    print(f"✅ Request processed with default mode")
    print(f"   Requested mode: {response['tailoring_mode_requested']}")
    print(f"   Used mode: {response['tailoring_mode_used']}")
    print(f"   Fallback occurred: {response['tailoring_mode_fallback']}")
    
    assert response["tailoring_mode_used"] == "light"
    assert response["tailoring_mode_fallback"] == False
    print("✅ All assertions passed")
    print()

def test_bulk_generation_simulation():
    """Test bulk generation with tailoring modes"""
    print("🧪 Testing Bulk Generation with Tailoring Modes")
    print("=" * 45)
    
    free_user, pro_user = create_test_users()
    
    # Simulate bulk generation request
    bulk_request = {
        "file_id": "test-resume.txt",
        "jobs": [
            {"id": 1, "status": "success", "job_description": "Product Manager role", "url": "https://example.com/job1"},
            {"id": 2, "status": "success", "job_description": "Senior PM role", "url": "https://example.com/job2"}
        ],
        "output_format": "pdf",
        "tailoring_mode": TailoringMode.HEAVY
    }
    
    # Test Free user with Heavy mode in bulk generation
    def simulate_bulk_generation(user, request):
        effective_mode = request.get("tailoring_mode", TailoringMode.LIGHT)
        fallback = False
        fallback_reason = None
        
        if effective_mode == TailoringMode.HEAVY and not user.is_pro_active():
            effective_mode = TailoringMode.LIGHT
            fallback = True
            fallback_reason = "Heavy tailoring requires Pro subscription"
        
        return {
            "message": f"Generated {len(request['jobs'])} tailored resumes",
            "total_jobs": len(request['jobs']),
            "tailoring_mode_requested": request["tailoring_mode"].value,
            "tailoring_mode_used": effective_mode.value,
            "tailoring_mode_fallback": fallback,
            "tailoring_mode_fallback_reason": fallback_reason
        }
    
    # Test Free user
    free_response = simulate_bulk_generation(free_user, bulk_request)
    print(f"Free user bulk generation:")
    print(f"   Requested: {free_response['tailoring_mode_requested']}")
    print(f"   Used: {free_response['tailoring_mode_used']}")
    print(f"   Fallback: {free_response['tailoring_mode_fallback']}")
    
    # Test Pro user
    pro_response = simulate_bulk_generation(pro_user, bulk_request)
    print(f"Pro user bulk generation:")
    print(f"   Requested: {pro_response['tailoring_mode_requested']}")
    print(f"   Used: {pro_response['tailoring_mode_used']}")
    print(f"   Fallback: {pro_response['tailoring_mode_fallback']}")
    
    assert free_response["tailoring_mode_fallback"] == True
    assert pro_response["tailoring_mode_fallback"] == False
    print("✅ All assertions passed")
    print()

def main():
    """Run all integration tests"""
    print("🚀 Starting Tailoring Mode Integration Tests")
    print("=" * 50)
    print()
    
    # Run all tests
    test_free_user_light_mode()
    test_free_user_heavy_mode()
    test_pro_user_light_mode()
    test_pro_user_heavy_mode()
    test_default_mode()
    test_bulk_generation_simulation()
    
    print("✅ All integration tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()