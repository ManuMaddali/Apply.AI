"""
Integration test for Advanced Formatting with existing PDF generation

This test verifies that advanced formatting is properly integrated
with the existing resume generation endpoints.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from services.advanced_formatting_service import (
    AdvancedFormattingService,
    FormattingOptions,
    FormattingTemplate,
    ColorScheme,
    FontFamily
)
from routes.batch_processing import generate_pdf_from_text
from models.user import User, SubscriptionTier


class TestAdvancedFormattingIntegration:
    """Test advanced formatting integration with existing systems"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = AdvancedFormattingService()
        self.sample_resume_text = """
John Doe
john.doe@email.com | (555) 123-4567

PROFESSIONAL EXPERIENCE
Software Engineer | Tech Company | 2020-2023
• Developed web applications using Python and JavaScript
• Collaborated with cross-functional teams to deliver features
• Improved system performance by 30%

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2016-2020

SKILLS
Programming Languages: Python, JavaScript, Java
Frameworks: React, Django, Flask
Databases: PostgreSQL, MongoDB
"""
    
    def test_generate_pdf_from_text_standard_formatting(self):
        """Test PDF generation with standard formatting (Free users)"""
        pdf_buffer = generate_pdf_from_text(
            resume_text=self.sample_resume_text,
            job_title="Software Engineer",
            formatting_options=None,
            use_advanced_formatting=False,
            is_pro_user=False
        )
        
        assert pdf_buffer is not None
        assert len(pdf_buffer.getvalue()) > 0
        
        # Verify it's a valid PDF by checking header
        pdf_content = pdf_buffer.getvalue()
        assert pdf_content.startswith(b'%PDF-')
    
    def test_generate_pdf_from_text_advanced_formatting_pro_user(self):
        """Test PDF generation with advanced formatting (Pro users)"""
        formatting_options = FormattingOptions(
            template=FormattingTemplate.MODERN,
            color_scheme=ColorScheme.MODERN_GRAY,
            font_family=FontFamily.HELVETICA,
            font_size=11
        )
        
        pdf_buffer = generate_pdf_from_text(
            resume_text=self.sample_resume_text,
            job_title="Senior Software Engineer",
            formatting_options=formatting_options,
            use_advanced_formatting=True,
            is_pro_user=True
        )
        
        assert pdf_buffer is not None
        assert len(pdf_buffer.getvalue()) > 0
        
        # Verify it's a valid PDF
        pdf_content = pdf_buffer.getvalue()
        assert pdf_content.startswith(b'%PDF-')
    
    def test_generate_pdf_from_text_advanced_formatting_free_user_fallback(self):
        """Test that free users fall back to standard formatting"""
        formatting_options = FormattingOptions(
            template=FormattingTemplate.EXECUTIVE,  # Pro template
            color_scheme=ColorScheme.EXECUTIVE_BLACK,
            font_family=FontFamily.TIMES,
            font_size=12
        )
        
        # Free user requesting advanced formatting should fall back
        pdf_buffer = generate_pdf_from_text(
            resume_text=self.sample_resume_text,
            job_title="Software Engineer",
            formatting_options=formatting_options,
            use_advanced_formatting=True,
            is_pro_user=False  # Free user
        )
        
        assert pdf_buffer is not None
        assert len(pdf_buffer.getvalue()) > 0
        
        # Should still generate a valid PDF (fallback)
        pdf_content = pdf_buffer.getvalue()
        assert pdf_content.startswith(b'%PDF-')
    
    def test_generate_pdf_from_text_with_empty_resume(self):
        """Test PDF generation with empty resume text"""
        pdf_buffer = generate_pdf_from_text(
            resume_text="",
            job_title="Software Engineer",
            formatting_options=None,
            use_advanced_formatting=False,
            is_pro_user=False
        )
        
        assert pdf_buffer is not None
        assert len(pdf_buffer.getvalue()) > 0
        
        # Should generate fallback PDF
        pdf_content = pdf_buffer.getvalue()
        assert pdf_content.startswith(b'%PDF-')
    
    def test_advanced_formatting_service_with_all_templates(self):
        """Test advanced formatting service with all available templates"""
        templates_to_test = [
            FormattingTemplate.STANDARD,
            FormattingTemplate.MODERN,
            FormattingTemplate.EXECUTIVE,
            FormattingTemplate.MINIMAL,
            FormattingTemplate.ACADEMIC,
            FormattingTemplate.TECHNICAL
        ]
        
        for template in templates_to_test:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                formatting_options = FormattingOptions(
                    template=template,
                    color_scheme=ColorScheme.CLASSIC_BLUE,
                    font_family=FontFamily.HELVETICA,
                    font_size=10
                )
                
                success = self.service.create_advanced_formatted_resume(
                    self.sample_resume_text,
                    formatting_options,
                    temp_path,
                    f"Test Job - {template.value}"
                )
                
                assert success is True, f"Failed to create PDF with template {template.value}"
                assert os.path.exists(temp_path), f"PDF file not created for template {template.value}"
                assert os.path.getsize(temp_path) > 0, f"Empty PDF created for template {template.value}"
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_advanced_formatting_service_with_all_color_schemes(self):
        """Test advanced formatting service with all available color schemes"""
        color_schemes_to_test = [
            ColorScheme.CLASSIC_BLUE,
            ColorScheme.MODERN_GRAY,
            ColorScheme.EXECUTIVE_BLACK,
            ColorScheme.CREATIVE_TEAL,
            ColorScheme.WARM_BROWN,
            ColorScheme.TECH_GREEN
        ]
        
        for color_scheme in color_schemes_to_test:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                formatting_options = FormattingOptions(
                    template=FormattingTemplate.MODERN,
                    color_scheme=color_scheme,
                    font_family=FontFamily.HELVETICA,
                    font_size=10
                )
                
                success = self.service.create_advanced_formatted_resume(
                    self.sample_resume_text,
                    formatting_options,
                    temp_path,
                    f"Test Job - {color_scheme.value}"
                )
                
                assert success is True, f"Failed to create PDF with color scheme {color_scheme.value}"
                assert os.path.exists(temp_path), f"PDF file not created for color scheme {color_scheme.value}"
                assert os.path.getsize(temp_path) > 0, f"Empty PDF created for color scheme {color_scheme.value}"
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_advanced_formatting_service_with_all_font_families(self):
        """Test advanced formatting service with all available font families"""
        font_families_to_test = [
            FontFamily.HELVETICA,
            FontFamily.TIMES,
            FontFamily.CALIBRI,
            FontFamily.ARIAL,
            FontFamily.GARAMOND
        ]
        
        for font_family in font_families_to_test:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                formatting_options = FormattingOptions(
                    template=FormattingTemplate.STANDARD,
                    color_scheme=ColorScheme.CLASSIC_BLUE,
                    font_family=font_family,
                    font_size=10
                )
                
                success = self.service.create_advanced_formatted_resume(
                    self.sample_resume_text,
                    formatting_options,
                    temp_path,
                    f"Test Job - {font_family.value}"
                )
                
                assert success is True, f"Failed to create PDF with font family {font_family.value}"
                assert os.path.exists(temp_path), f"PDF file not created for font family {font_family.value}"
                assert os.path.getsize(temp_path) > 0, f"Empty PDF created for font family {font_family.value}"
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    def test_ats_compatibility_across_templates(self):
        """Test ATS compatibility validation across different templates"""
        ats_results = {}
        
        for template in FormattingTemplate:
            formatting_options = FormattingOptions(
                template=template,
                color_scheme=ColorScheme.CLASSIC_BLUE,
                font_family=FontFamily.HELVETICA,
                font_size=10,
                use_two_columns=False,
                include_border=False
            )
            
            is_compatible = self.service._validate_ats_compatibility(formatting_options)
            ats_results[template.value] = is_compatible
        
        # Standard template should always be ATS compatible
        assert ats_results[FormattingTemplate.STANDARD.value] is True
        
        # Creative template should be flagged as potentially incompatible
        assert ats_results[FormattingTemplate.CREATIVE.value] is False
        
        # Most other templates should be compatible with good settings
        compatible_templates = [
            FormattingTemplate.STANDARD.value,
            FormattingTemplate.MODERN.value,
            FormattingTemplate.EXECUTIVE.value,
            FormattingTemplate.MINIMAL.value,
            FormattingTemplate.ACADEMIC.value,
            FormattingTemplate.TECHNICAL.value
        ]
        
        for template in compatible_templates:
            if template != FormattingTemplate.CREATIVE.value:
                assert ats_results[template] is True, f"Template {template} should be ATS compatible"
    
    def test_fallback_behavior(self):
        """Test fallback behavior when advanced formatting fails"""
        # Test with invalid output path to trigger fallback
        invalid_path = "/invalid/nonexistent/path/resume.pdf"
        
        formatting_options = FormattingOptions(
            template=FormattingTemplate.MODERN,
            color_scheme=ColorScheme.MODERN_GRAY,
            font_family=FontFamily.HELVETICA
        )
        
        success = self.service.create_advanced_formatted_resume(
            self.sample_resume_text,
            formatting_options,
            invalid_path,
            "Software Engineer"
        )
        
        # Should fail gracefully
        assert success is False
        
        # Test standard formatting fallback
        success = self.service.create_standard_formatted_resume(
            self.sample_resume_text,
            invalid_path,
            "Software Engineer"
        )
        
        # Should also fail with invalid path
        assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])