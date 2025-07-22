"""
Comprehensive tests for Job-Specific Templates functionality

This test suite covers:
- Job category discovery and validation
- Template generation with job-specific optimizations
- Pro vs Free user access control
- API endpoint functionality
- Integration with existing resume processing
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Import the main app and services
from main import app
from services.job_specific_templates import (
    JobSpecificTemplateService,
    JobCategory,
    JobTemplateConfig,
    JobSpecificSection
)
from services.advanced_formatting_service import FormattingOptions, FormattingTemplate, ColorScheme, FontFamily
from models.user import User, SubscriptionTier, SubscriptionStatus, TailoringMode

# Test client - will be initialized in test methods to avoid startup issues


class TestJobSpecificTemplateService:
    """Test the core JobSpecificTemplateService functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = JobSpecificTemplateService()
        
        # Mock users
        self.free_user = Mock(spec=User)
        self.free_user.is_pro_active.return_value = False
        self.free_user.subscription_tier = SubscriptionTier.FREE
        self.free_user.email = "free@test.com"
        
        self.pro_user = Mock(spec=User)
        self.pro_user.is_pro_active.return_value = True
        self.pro_user.subscription_tier = SubscriptionTier.PRO
        self.pro_user.subscription_status = SubscriptionStatus.ACTIVE
        self.pro_user.current_period_end = datetime.utcnow() + timedelta(days=30)
        self.pro_user.email = "pro@test.com"
    
    def test_get_available_job_categories_free_user(self):
        """Test that free users get limited preview information"""
        categories = self.service.get_available_job_categories(is_pro=False)
        
        assert len(categories) == 1
        assert categories[0]['category'] == 'preview'
        assert categories[0]['pro_only'] is True
        assert categories[0]['available'] is False
        assert 'upgrade_url' in categories[0]
    
    def test_get_available_job_categories_pro_user(self):
        """Test that Pro users get full category list"""
        categories = self.service.get_available_job_categories(is_pro=True)
        
        assert len(categories) > 1
        assert all(cat['available'] is True for cat in categories)
        assert all(cat['pro_only'] is True for cat in categories)
        
        # Check that we have expected categories
        category_names = [cat['category'] for cat in categories]
        assert 'software_engineer' in category_names
        assert 'data_scientist' in category_names
        assert 'product_manager' in category_names
    
    def test_get_job_category_templates_free_user(self):
        """Test that free users get error for template requests"""
        result = self.service.get_job_category_templates('software_engineer', is_pro=False)
        
        assert 'error' in result
        assert 'Pro subscription required' in result['message']
        assert 'upgrade_url' in result
    
    def test_get_job_category_templates_pro_user(self):
        """Test that Pro users get full template details"""
        result = self.service.get_job_category_templates('software_engineer', is_pro=True)
        
        assert 'error' not in result
        assert result['category'] == 'software_engineer'
        assert 'templates' in result
        assert len(result['templates']) == len(FormattingTemplate)
        assert 'specific_sections' in result
        assert 'ats_keywords' in result
    
    def test_get_job_category_templates_invalid_category(self):
        """Test handling of invalid job category"""
        result = self.service.get_job_category_templates('invalid_category', is_pro=True)
        
        assert 'error' in result
        assert 'not found' in result['message']
        assert 'available_categories' in result
    
    def test_validate_job_specific_request_free_user(self):
        """Test validation fails for free users"""
        is_valid, message = self.service.validate_job_specific_request(
            'software_engineer', 'modern', is_pro=False
        )
        
        assert is_valid is False
        assert 'Pro subscription required' in message
    
    def test_validate_job_specific_request_pro_user_valid(self):
        """Test validation succeeds for valid Pro user request"""
        is_valid, message = self.service.validate_job_specific_request(
            'software_engineer', 'modern', is_pro=True
        )
        
        assert is_valid is True
        assert 'Valid' in message
    
    def test_validate_job_specific_request_invalid_category(self):
        """Test validation fails for invalid category"""
        is_valid, message = self.service.validate_job_specific_request(
            'invalid_category', 'modern', is_pro=True
        )
        
        assert is_valid is False
        assert 'Invalid job category' in message
    
    def test_validate_job_specific_request_invalid_template(self):
        """Test validation fails for invalid template"""
        is_valid, message = self.service.validate_job_specific_request(
            'software_engineer', 'invalid_template', is_pro=True
        )
        
        assert is_valid is False
        assert 'Invalid template' in message
    
    def test_get_job_category_by_title_software_engineer(self):
        """Test job category suggestion for software engineer titles"""
        test_titles = [
            "Senior Software Engineer",
            "Frontend Developer",
            "Backend Engineer",
            "Full Stack Developer",
            "Software Developer"
        ]
        
        for title in test_titles:
            category = self.service.get_job_category_by_title(title)
            assert category == JobCategory.SOFTWARE_ENGINEER
    
    def test_get_job_category_by_title_data_scientist(self):
        """Test job category suggestion for data science titles"""
        test_titles = [
            "Data Scientist",
            "Senior Data Analyst",
            "Machine Learning Engineer",
            "Data Analytics Manager"
        ]
        
        for title in test_titles:
            category = self.service.get_job_category_by_title(title)
            assert category == JobCategory.DATA_SCIENTIST
    
    def test_get_job_category_by_title_no_match(self):
        """Test job category suggestion returns None for unmatched titles"""
        category = self.service.get_job_category_by_title("Underwater Basket Weaver")
        assert category is None
    
    @patch('services.job_specific_templates.JobSpecificTemplateService._enhance_resume_for_job_category')
    @patch('services.advanced_formatting_service.AdvancedFormattingService.create_advanced_formatted_resume')
    def test_create_job_specific_resume_success(self, mock_create_resume, mock_enhance):
        """Test successful job-specific resume creation"""
        mock_enhance.return_value = "Enhanced resume text"
        mock_create_resume.return_value = True
        
        formatting_options = FormattingOptions(
            template=FormattingTemplate.MODERN,
            color_scheme=ColorScheme.TECH_GREEN,
            font_family=FontFamily.HELVETICA,
            font_size=10
        )
        
        result = self.service.create_job_specific_resume(
            "Original resume text",
            "software_engineer",
            "modern",
            formatting_options,
            "/tmp/test_resume.pdf",
            "Software Engineer"
        )
        
        assert result is True
        mock_enhance.assert_called_once()
        mock_create_resume.assert_called_once()
    
    @patch('services.advanced_formatting_service.AdvancedFormattingService.create_advanced_formatted_resume')
    def test_create_job_specific_resume_invalid_category(self, mock_create_resume):
        """Test job-specific resume creation with invalid category"""
        formatting_options = FormattingOptions(
            template=FormattingTemplate.MODERN,
            color_scheme=ColorScheme.TECH_GREEN,
            font_family=FontFamily.HELVETICA,
            font_size=10
        )
        
        result = self.service.create_job_specific_resume(
            "Original resume text",
            "invalid_category",
            "modern",
            formatting_options,
            "/tmp/test_resume.pdf",
            "Test Job"
        )
        
        assert result is False
        mock_create_resume.assert_not_called()


class TestJobSpecificTemplatesAPI:
    """Test the job-specific templates API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_auth_patcher = patch('routes.job_specific_templates.AuthManager.verify_token')
        self.mock_auth = self.mock_auth_patcher.start()
        
        # Mock Pro user by default
        self.pro_user = Mock(spec=User)
        self.pro_user.is_pro_active.return_value = True
        self.pro_user.subscription_tier = SubscriptionTier.PRO
        self.pro_user.email = "pro@test.com"
        self.mock_auth.return_value = self.pro_user
    
    def teardown_method(self):
        """Clean up patches"""
        self.mock_auth_patcher.stop()
    
    def test_get_job_categories_pro_user(self):
        """Test GET /api/job-templates/categories for Pro user"""
        with TestClient(app) as client:
            response = client.get("/api/job-templates/categories")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['user_tier'] == 'pro'
            assert data['pro_required'] is False
            assert len(data['categories']) > 1
    
    def test_get_job_categories_free_user(self):
        """Test GET /api/job-templates/categories for Free user"""
        # Mock free user
        free_user = Mock(spec=User)
        free_user.is_pro_active.return_value = False
        free_user.subscription_tier = SubscriptionTier.FREE
        self.mock_auth.return_value = free_user
        
        with TestClient(app) as client:
            response = client.get("/api/job-templates/categories")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['user_tier'] == 'free'
            assert data['pro_required'] is True
            assert len(data['categories']) == 1
            assert data['categories'][0]['category'] == 'preview'
    
    def test_get_job_category_details_valid(self):
        """Test GET /api/job-templates/categories/{category} for valid category"""
        with TestClient(app) as client:
            response = client.get("/api/job-templates/categories/software_engineer")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['user_tier'] == 'pro'
            assert 'category_details' in data
            assert data['category_details']['category'] == 'software_engineer'
    
    def test_get_job_category_details_invalid(self):
        """Test GET /api/job-templates/categories/{category} for invalid category"""
        with TestClient(app) as client:
            response = client.get("/api/job-templates/categories/invalid_category")
            
            assert response.status_code == 404
            assert "not found" in response.json()['detail']
    
    def test_get_job_category_details_free_user(self):
        """Test GET /api/job-templates/categories/{category} for Free user"""
        # Mock free user
        free_user = Mock(spec=User)
        free_user.is_pro_active.return_value = False
        self.mock_auth.return_value = free_user
        
        with TestClient(app) as client:
            response = client.get("/api/job-templates/categories/software_engineer")
            
            assert response.status_code == 402
            assert "Pro subscription required" in response.json()['detail']
    
    def test_suggest_job_category_valid_title(self):
        """Test POST /api/job-templates/suggest-category with valid job title"""
        request_data = {"job_title": "Senior Software Engineer"}
        with TestClient(app) as client:
            response = client.post("/api/job-templates/suggest-category", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['suggested_category'] == 'software_engineer'
            assert data['confidence'] == 'high'
            assert 'category_details' in data
    
    def test_suggest_job_category_no_match(self):
        """Test POST /api/job-templates/suggest-category with unmatched title"""
        request_data = {"job_title": "Underwater Basket Weaver"}
        with TestClient(app) as client:
            response = client.post("/api/job-templates/suggest-category", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['suggested_category'] is None
            assert data['confidence'] == 'none'
            assert 'alternatives' in data
    
    def test_suggest_job_category_empty_title(self):
        """Test POST /api/job-templates/suggest-category with empty title"""
        request_data = {"job_title": ""}
        with TestClient(app) as client:
            response = client.post("/api/job-templates/suggest-category", json=request_data)
            
            assert response.status_code == 400
            assert "cannot be empty" in response.json()['detail']
    
    def test_validate_template_request_valid(self):
        """Test POST /api/job-templates/validate with valid request"""
        request_data = {
            "job_category": "software_engineer",
            "formatting_template": "modern"
        }
        with TestClient(app) as client:
            response = client.post("/api/job-templates/validate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['valid'] is True
            assert data['user_tier'] == 'pro'
    
    def test_validate_template_request_free_user(self):
        """Test POST /api/job-templates/validate for Free user"""
        # Mock free user
        free_user = Mock(spec=User)
        free_user.is_pro_active.return_value = False
        self.mock_auth.return_value = free_user
        
        request_data = {
            "job_category": "software_engineer",
            "formatting_template": "modern"
        }
        with TestClient(app) as client:
            response = client.post("/api/job-templates/validate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['valid'] is False
            assert data['upgrade_required'] is True
            assert 'upgrade_url' in data
    
    def test_validate_template_request_invalid_category(self):
        """Test POST /api/job-templates/validate with invalid category"""
        request_data = {
            "job_category": "invalid_category",
            "formatting_template": "modern"
        }
        with TestClient(app) as client:
            response = client.post("/api/job-templates/validate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['valid'] is False
            assert 'available_categories' in data
    
    def test_get_template_preview_valid(self):
        """Test GET /api/job-templates/preview/{category}/{template}"""
        with TestClient(app) as client:
            response = client.get("/api/job-templates/preview/software_engineer/modern")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['category'] == 'software_engineer'
            assert data['template'] == 'modern'
            assert data['preview_available'] is True
            assert 'template_info' in data
            assert 'category_details' in data
    
    def test_get_template_preview_free_user(self):
        """Test GET /api/job-templates/preview/{category}/{template} for Free user"""
        # Mock free user
        free_user = Mock(spec=User)
        free_user.is_pro_active.return_value = False
        self.mock_auth.return_value = free_user
        
        with TestClient(app) as client:
            response = client.get("/api/job-templates/preview/software_engineer/modern")
            
            assert response.status_code == 402
            assert "Pro subscription required" in response.json()['detail']
    
    def test_get_template_stats_pro_user(self):
        """Test GET /api/job-templates/stats for Pro user"""
        with TestClient(app) as client:
            response = client.get("/api/job-templates/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['user_tier'] == 'pro'
            assert 'popular_categories' in data
            assert 'popular_templates' in data
            assert 'total_categories' in data
    
    def test_get_template_stats_free_user(self):
        """Test GET /api/job-templates/stats for Free user"""
        # Mock free user
        free_user = Mock(spec=User)
        free_user.is_pro_active.return_value = False
        self.mock_auth.return_value = free_user
        
        with TestClient(app) as client:
            response = client.get("/api/job-templates/stats")
            
            assert response.status_code == 402
            assert "Pro subscription required" in response.json()['detail']


class TestJobSpecificTemplatesIntegration:
    """Test integration of job-specific templates with existing resume processing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_auth_patcher = patch('routes.generate_resumes.AuthManager.verify_token')
        self.mock_auth = self.mock_auth_patcher.start()
        
        # Mock Pro user
        self.pro_user = Mock(spec=User)
        self.pro_user.is_pro_active.return_value = True
        self.pro_user.subscription_tier = SubscriptionTier.PRO
        self.pro_user.email = "pro@test.com"
        self.mock_auth.return_value = self.pro_user
        
        # Create test resume file
        self.test_file_content = """
        John Doe
        Software Engineer
        
        EXPERIENCE
        Senior Developer at Tech Corp
        - Developed web applications
        - Led team of 5 developers
        
        SKILLS
        Python, JavaScript, React, Node.js
        """
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write(self.test_file_content)
        self.temp_file.close()
        
        # Move to uploads directory
        self.file_id = os.path.basename(self.temp_file.name)
        os.makedirs("uploads", exist_ok=True)
        os.rename(self.temp_file.name, f"uploads/{self.file_id}")
    
    def teardown_method(self):
        """Clean up test files and patches"""
        self.mock_auth_patcher.stop()
        
        # Clean up test files
        try:
            os.remove(f"uploads/{self.file_id}")
        except FileNotFoundError:
            pass
        
        # Clean up any generated output files
        if os.path.exists("outputs"):
            for file in os.listdir("outputs"):
                if file.startswith("test_"):
                    try:
                        os.remove(f"outputs/{file}")
                    except FileNotFoundError:
                        pass
    
    @patch('services.job_specific_templates.JobSpecificTemplateService.create_job_specific_resume')
    @patch('utils.gpt_prompt.GPTProcessor.tailor_resume')
    def test_tailor_endpoint_with_job_specific_template(self, mock_tailor, mock_create_resume):
        """Test /api/resumes/tailor endpoint with job-specific template"""
        mock_tailor.return_value = "Tailored resume content"
        mock_create_resume.return_value = True
        
        request_data = {
            "resume_text": self.test_file_content,
            "job_description": "We are looking for a Senior Software Engineer...",
            "job_title": "Senior Software Engineer",
            "use_job_specific_template": True,
            "job_category": "software_engineer",
            "formatting_template": "technical",
            "generate_pdf": True
        }
        
        with TestClient(app) as client:
            response = client.post("/api/resumes/tailor", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'tailored_resume' in data
            assert 'pdf' in data
            
            # Verify job-specific template was called
            mock_create_resume.assert_called_once()
    
    @patch('services.job_specific_templates.JobSpecificTemplateService.create_job_specific_resume')
    @patch('utils.gpt_prompt.GPTProcessor.tailor_resume')
    def test_bulk_generation_with_job_specific_template(self, mock_tailor, mock_create_resume):
        """Test /api/resumes/generate-resumes endpoint with job-specific template"""
        mock_tailor.return_value = "Tailored resume content"
        mock_create_resume.return_value = True
        
        request_data = {
            "file_id": self.file_id,
            "jobs": [
                {
                    "id": 1,
                    "url": "https://example.com/job1",
                    "status": "success",
                    "job_description": "We are looking for a Senior Software Engineer..."
                }
            ],
            "output_format": "pdf",
            "use_job_specific_template": True,
            "job_category": "software_engineer",
            "formatting_template": "technical"
        }
        
        with TestClient(app) as client:
            response = client.post("/api/resumes/generate-resumes", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['successful_generations'] == 1
            assert len(data['resumes']) == 1
            assert data['resumes'][0]['status'] == 'success'
            
            # Verify job-specific template was called
            mock_create_resume.assert_called_once()
    
    @patch('utils.gpt_prompt.GPTProcessor.tailor_resume')
    def test_job_specific_template_fallback_free_user(self, mock_tailor):
        """Test that Free users fall back to standard processing"""
        # Mock free user
        free_user = Mock(spec=User)
        free_user.is_pro_active.return_value = False
        free_user.subscription_tier = SubscriptionTier.FREE
        self.mock_auth.return_value = free_user
        
        mock_tailor.return_value = "Tailored resume content"
        
        request_data = {
            "resume_text": self.test_file_content,
            "job_description": "We are looking for a Senior Software Engineer...",
            "job_title": "Senior Software Engineer",
            "use_job_specific_template": True,  # This should be ignored for free users
            "job_category": "software_engineer",
            "generate_pdf": True
        }
        
        with patch('utils.resume_editor.ResumeEditor.create_tailored_resume_pdf') as mock_create_pdf:
            mock_create_pdf.return_value = True
            
            with TestClient(app) as client:
                response = client.post("/api/resumes/tailor", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data['success'] is True
                
                # Verify standard PDF creation was used, not job-specific
                mock_create_pdf.assert_called_once()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])