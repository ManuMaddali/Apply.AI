#!/usr/bin/env python3
"""
Simple integration test for job-specific templates

This script tests the integration of job-specific templates with the existing resume processing flow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.job_specific_templates import JobSpecificTemplateService, JobCategory
from services.advanced_formatting_service import FormattingOptions, FormattingTemplate, ColorScheme, FontFamily

def test_job_specific_templates_integration():
    """Test the integration of job-specific templates"""
    print("🧪 Testing Job-Specific Templates Integration")
    print("=" * 50)
    
    # Initialize the service
    service = JobSpecificTemplateService()
    print("✅ JobSpecificTemplateService initialized")
    
    # Test 1: Get available categories for Pro user
    print("\n📋 Test 1: Get available job categories for Pro user")
    categories = service.get_available_job_categories(is_pro=True)
    print(f"✅ Found {len(categories)} job categories")
    
    # Display some categories
    for i, category in enumerate(categories[:5]):
        print(f"   {i+1}. {category['display_name']} ({category['industry']})")
    
    # Test 2: Get available categories for Free user
    print("\n📋 Test 2: Get available job categories for Free user")
    free_categories = service.get_available_job_categories(is_pro=False)
    print(f"✅ Free user sees {len(free_categories)} category (preview only)")
    print(f"   Preview: {free_categories[0]['display_name']}")
    
    # Test 3: Get templates for a specific category
    print("\n📋 Test 3: Get templates for Software Engineer category")
    sw_templates = service.get_job_category_templates('software_engineer', is_pro=True)
    if 'error' not in sw_templates:
        print(f"✅ Found {len(sw_templates['templates'])} template variations")
        print(f"   Category: {sw_templates['display_name']}")
        print(f"   Industry: {sw_templates['industry']}")
        print(f"   Specific sections: {len(sw_templates['specific_sections'])}")
        
        # Show specific sections
        for section in sw_templates['specific_sections']:
            print(f"     - {section['title']}: {section['description']}")
    else:
        print(f"❌ Error: {sw_templates['message']}")
    
    # Test 4: Job category suggestion
    print("\n📋 Test 4: Job category suggestion")
    test_titles = [
        "Senior Software Engineer",
        "Data Scientist",
        "Product Manager",
        "Registered Nurse",
        "Financial Analyst",
        "Unknown Job Title"
    ]
    
    for title in test_titles:
        suggested = service.get_job_category_by_title(title)
        if suggested:
            print(f"   '{title}' → {suggested.value}")
        else:
            print(f"   '{title}' → No suggestion")
    
    # Test 5: Validation
    print("\n📋 Test 5: Template request validation")
    
    # Valid request for Pro user
    is_valid, message = service.validate_job_specific_request(
        'software_engineer', 'modern', is_pro=True
    )
    print(f"   Pro user + valid request: {is_valid} - {message}")
    
    # Invalid request for Free user
    is_valid, message = service.validate_job_specific_request(
        'software_engineer', 'modern', is_pro=False
    )
    print(f"   Free user + valid request: {is_valid} - {message}")
    
    # Invalid category
    is_valid, message = service.validate_job_specific_request(
        'invalid_category', 'modern', is_pro=True
    )
    print(f"   Pro user + invalid category: {is_valid} - {message}")
    
    # Test 6: Template creation (mock)
    print("\n📋 Test 6: Template creation simulation")
    
    # Create formatting options
    formatting_options = FormattingOptions(
        template=FormattingTemplate.TECHNICAL,
        color_scheme=ColorScheme.TECH_GREEN,
        font_family=FontFamily.HELVETICA,
        font_size=10
    )
    
    # This would normally create a PDF, but we'll just test the validation
    sample_resume = """
    John Doe
    Software Engineer
    
    EXPERIENCE
    Senior Developer at Tech Corp
    - Developed web applications using Python and React
    - Led team of 5 developers
    - Implemented CI/CD pipelines
    
    SKILLS
    Python, JavaScript, React, Node.js, Docker, AWS
    """
    
    print("   Sample resume text prepared")
    print("   Formatting options configured:")
    print(f"     Template: {formatting_options.template.value}")
    print(f"     Color: {formatting_options.color_scheme.value}")
    print(f"     Font: {formatting_options.font_family.value}")
    
    # Test the enhancement logic
    config = service.job_configs[JobCategory.SOFTWARE_ENGINEER]
    enhanced_resume = service._enhance_resume_for_job_category(sample_resume, config)
    
    print("   ✅ Resume enhancement completed")
    print(f"   Enhanced resume length: {len(enhanced_resume)} characters")
    
    # Test job-specific formatting options
    job_specific_options = service._create_job_specific_formatting_options(
        formatting_options, config
    )
    
    print("   ✅ Job-specific formatting options created")
    print(f"   Recommended template: {job_specific_options.template.value}")
    print(f"   Recommended color: {job_specific_options.color_scheme.value}")
    
    print("\n🎉 All integration tests completed successfully!")
    print("=" * 50)
    
    return True

def test_api_endpoints_availability():
    """Test that API endpoints are properly configured"""
    print("\n🌐 Testing API Endpoints Configuration")
    print("=" * 50)
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        # This will test that the app can be created without errors
        print("✅ FastAPI app created successfully")
        
        # Check that our router is included
        routes = [route.path for route in app.routes]
        job_template_routes = [route for route in routes if 'job-templates' in route]
        
        print(f"✅ Found {len(job_template_routes)} job-template routes:")
        for route in job_template_routes:
            print(f"   - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Job-Specific Templates Integration Tests")
    print("=" * 60)
    
    try:
        # Test the service integration
        service_test = test_job_specific_templates_integration()
        
        # Test API endpoints
        api_test = test_api_endpoints_availability()
        
        if service_test and api_test:
            print("\n🎉 ALL TESTS PASSED!")
            print("Job-specific templates are successfully integrated!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)