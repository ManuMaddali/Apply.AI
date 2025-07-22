"""
Test suite for Advanced Formatting API endpoints

This test suite covers:
- Advanced formatting API endpoints
- Template and color scheme retrieval
- Formatting validation endpoints
- PDF generation with advanced formatting
- Pro vs Free user access control
- Integration with existing endpoints
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app
from models.user import User, SubscriptionTier
from services.advanced_formatting_service import FormattingTemplate, ColorScheme, FontFamily


class TestAdvancedFormattingAPI:
    """Test cases for the Advanced Formatting API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.sample_resume_text = """
John Doe
john.doe@email.com | (555) 123-4567

PROFESSIONAL EXPERIENCE
Software Engineer | Tech Company | 2020-2023
• Developed web applications using Python and JavaScript
• Collaborated with cross-functional teams

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2016-2020

SKILLS
Programming Languages: Python, JavaScript, Java
"""
    
    def create_mock_user(self, is_pro: bool = False):
        """Create a mock user for testing"""
        user = Mock(spec=User)
        user.id = "test-user-id"
        user.email = "test@example.com"
        user.subscription_tier = SubscriptionTier.PRO if is_pro else SubscriptionTier.FREE
        user.is_pro_active.return_value = is_pro
        return user
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_get_available_templates_free_user(self, mock_get_user):
        """Test getting available templates for free user"""
        mock_get_user.return_value = self.create_mock_user(is_pro=False)
        
        response = self.client.get("/api/resumes/advanced-format/templates")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        assert "color_schemes" in data
        assert "font_families" in data
        
        # Free user should only get standard template
        templates = data["templates"]
        assert len(templates) == 1
        assert templates[0]["id"] == FormattingTemplate.STANDARD.value
        assert templates[0]["pro_only"] is False
        
        # Should still get all color schemes and fonts
        assert len(data["color_schemes"]) == 6
        assert len(data["font_families"]) == 5
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_get_available_templates_pro_user(self, mock_get_user):
        """Test getting available templates for Pro user"""
        mock_get_user.return_value = self.create_mock_user(is_pro=True)
        
        response = self.client.get("/api/resumes/advanced-format/templates")
        
        assert response.status_code == 200
        data = response.json()
        
        # Pro user should get all templates
        templates = data["templates"]
        assert len(templates) == 7  # All templates
        
        # Check that Pro templates are included
        template_ids = [t["id"] for t in templates]
        assert FormattingTemplate.STANDARD.value in template_ids
        assert FormattingTemplate.MODERN.value in template_ids
        assert FormattingTemplate.EXECUTIVE.value in template_ids
        assert FormattingTemplate.CREATIVE.value in template_ids
        
        # Check Pro-only flag
        pro_templates = [t for t in templates if t["pro_only"] is True]
        assert len(pro_templates) == 6  # All except standard
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_validate_formatting_options_valid_free_user(self, mock_get_user):
        """Test validating formatting options for free user with valid request"""
        mock_get_user.return_value = self.create_mock_user(is_pro=False)
        
        request_data = {
            "resume_text": self.sample_resume_text,
            "job_title": "Software Engineer",
            "template": FormattingTemplate.STANDARD.value,
            "color_scheme": ColorScheme.CLASSIC_BLUE.value,
            "font_family": FontFamily.HELVETICA.value,
            "font_size": 10
        }
        
        response = self.client.post("/api/resumes/advanced-format/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True
        assert data["ats_compatible"] is True
        assert "Valid formatting request" in data["message"]
        assert len(data["warnings"]) == 0
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_validate_formatting_options_invalid_free_user(self, mock_get_user):
        """Test validating formatting options for free user with Pro template"""
        mock_get_user.return_value = self.create_mock_user(is_pro=False)
        
        request_data = {
            "resume_text": self.sample_resume_text,
            "job_title": "Software Engineer",
            "template": FormattingTemplate.MODERN.value,  # Pro template
            "color_scheme": ColorScheme.CLASSIC_BLUE.value,
            "font_family": FontFamily.HELVETICA.value,
            "font_size": 10
        }
        
        response = self.client.post("/api/resumes/advanced-format/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is False
        assert "requires Pro subscription" in data["message"]
        assert len(data["warnings"]) > 0
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_validate_formatting_options_ats_warnings(self, mock_get_user):
        """Test validating formatting options with ATS compatibility warnings"""
        mock_get_user.return_value = self.create_mock_user(is_pro=True)
        
        request_data = {
            "resume_text": self.sample_resume_text,
            "job_title": "Software Engineer",
            "template": FormattingTemplate.CREATIVE.value,  # May not be ATS compatible
            "color_scheme": ColorScheme.CREATIVE_TEAL.value,
            "font_family": FontFamily.HELVETICA.value,
            "font_size": 8,  # Too small for ATS
            "use_two_columns": True  # Problematic for ATS
        }
        
        response = self.client.post("/api/resumes/advanced-format/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True
        assert data["ats_compatible"] is False
        assert len(data["warnings"]) > 0
        
        # Check specific warnings
        warnings_text = " ".join(data["warnings"])
        assert "ATS compatible" in warnings_text
        assert "font size" in warnings_text or "Two-column" in warnings_text
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_generate_standard_formatted_resume(self, mock_get_user):
        """Test generating a standard formatted resume"""
        mock_get_user.return_value = self.create_mock_user(is_pro=False)
        
        request_data = {
            "resume_text": self.sample_resume_text,
            "job_title": "Software Engineer",
            "template": FormattingTemplate.STANDARD.value,
            "color_scheme": ColorScheme.CLASSIC_BLUE.value,
            "font_family": FontFamily.HELVETICA.value,
            "filename": "test_resume.pdf"
        }
        
        response = self.client.post("/api/resumes/advanced-format/generate-standard", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert "test_resume.pdf" in response.headers["content-disposition"]
        assert response.headers["x-template-used"] == "standard"
        assert response.headers["x-ats-compatible"] == "true"
        
        # Check that PDF content is not empty
        assert len(response.content) > 0
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_generate_advanced_formatted_resume_pro_user(self, mock_get_user):
        """Test generating an advanced formatted resume for Pro user"""
        mock_get_user.return_value = self.create_mock_user(is_pro=True)
        
        request_data = {
            "resume_text": self.sample_resume_text,
            "job_title": "Senior Software Engineer",
            "template": FormattingTemplate.MODERN.value,
            "color_scheme": ColorScheme.MODERN_GRAY.value,
            "font_family": FontFamily.HELVETICA.value,
            "font_size": 11,
            "filename": "advanced_resume.pdf"
        }
        
        response = self.client.post("/api/resumes/advanced-format/generate", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert "advanced_resume.pdf" in response.headers["content-disposition"]
        assert response.headers["x-template-used"] == FormattingTemplate.MODERN.value
        
        # Check that PDF content is not empty
        assert len(response.content) > 0
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_generate_advanced_formatted_resume_free_user_pro_template(self, mock_get_user):
        """Test generating advanced formatted resume for free user with Pro template (should fail)"""
        mock_get_user.return_value = self.create_mock_user(is_pro=False)
        
        request_data = {
            "resume_text": self.sample_resume_text,
            "job_title": "Software Engineer",
            "template": FormattingTemplate.EXECUTIVE.value,  # Pro template
            "color_scheme": ColorScheme.EXECUTIVE_BLACK.value,
            "font_family": FontFamily.TIMES.value
        }
        
        response = self.client.post("/api/resumes/advanced-format/generate", json=request_data)
        
        assert response.status_code == 402  # Payment required
        data = response.json()
        
        assert data["detail"]["error"] == "subscription_required"
        assert "Pro subscription" in data["detail"]["message"]
        assert data["detail"]["feature"] == "advanced_formatting"
        assert "/upgrade" in data["detail"]["upgrade_url"]
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_generate_advanced_formatted_resume_invalid_template(self, mock_get_user):
        """Test generating advanced formatted resume with invalid template"""
        mock_get_user.return_value = self.create_mock_user(is_pro=True)
        
        request_data = {
            "resume_text": self.sample_resume_text,
            "job_title": "Software Engineer",
            "template": "invalid_template",
            "color_scheme": ColorScheme.CLASSIC_BLUE.value,
            "font_family": FontFamily.HELVETICA.value
        }
        
        response = self.client.post("/api/resumes/advanced-format/generate", json=request_data)
        
        assert response.status_code == 400
        assert "Invalid template" in response.json()["detail"]
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_get_template_preview_free_user(self, mock_get_user):
        """Test getting template preview for free user"""
        mock_get_user.return_value = self.create_mock_user(is_pro=False)
        
        # Free user can access standard template preview
        response = self.client.get(f"/api/resumes/advanced-format/preview/{FormattingTemplate.STANDARD.value}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["template"] == FormattingTemplate.STANDARD.value
        assert data["available"] is True
        assert data["pro_only"] is False
        assert "preview_url" in data
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_get_template_preview_free_user_pro_template(self, mock_get_user):
        """Test getting Pro template preview for free user (should fail)"""
        mock_get_user.return_value = self.create_mock_user(is_pro=False)
        
        response = self.client.get(f"/api/resumes/advanced-format/preview/{FormattingTemplate.MODERN.value}")
        
        assert response.status_code == 402  # Payment required
        data = response.json()
        
        assert data["detail"]["error"] == "subscription_required"
        assert "Pro subscription" in data["detail"]["message"]
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_get_template_preview_pro_user(self, mock_get_user):
        """Test getting template preview for Pro user"""
        mock_get_user.return_value = self.create_mock_user(is_pro=True)
        
        response = self.client.get(f"/api/resumes/advanced-format/preview/{FormattingTemplate.EXECUTIVE.value}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["template"] == FormattingTemplate.EXECUTIVE.value
        assert data["available"] is True
        assert data["pro_only"] is True
        assert "preview_url" in data
    
    @patch('routes.advanced_formatting.get_current_user')
    def test_get_template_preview_invalid_template(self, mock_get_user):
        """Test getting preview for invalid template"""
        mock_get_user.return_value = self.create_mock_user(is_pro=True)
        
        response = self.client.get("/api/resumes/advanced-format/preview/invalid_template")
        
        assert response.status_code == 400
        assert "Invalid template" in response.json()["detail"]
    
    def test_api_endpoints_without_auth(self):
        """Test that API endpoints require authentication"""
        # This test assumes authentication is required
        # The actual behavior depends on your authentication setup
        
        response = self.client.get("/api/resumes/advanced-format/templates")
        # Should return 401 or redirect to login, depending on auth setup
        # Adjust assertion based on your authentication implementation
        assert response.status_code in [401, 403, 422]  # Common auth failure codes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])