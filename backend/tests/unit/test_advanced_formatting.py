"""
Test suite for Advanced Formatting Service - Pro-only PDF formatting functionality

This test suite covers:
- Advanced formatting service functionality
- Template validation and selection
- Color scheme and font family options
- ATS compatibility validation
- Pro vs Free user access control
- Fallback to standard formatting
- Integration with existing PDF generation endpoints
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
from models.user import User, SubscriptionTier


class TestAdvancedFormattingService:
    """Test cases for the AdvancedFormattingService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = AdvancedFormattingService()
        self.sample_resume_text = """
John Doe
john.doe@email.com | (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

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
    
    def test_service_initialization(self):
        """Test that the service initializes correctly with all required components"""
        assert self.service is not None
        assert hasattr(self.service, 'color_schemes')
        assert hasattr(self.service, 'font_mappings')
        assert hasattr(self.service, 'template_configs')
        
        # Check that all color schemes are initialized
        assert len(self.service.color_schemes) == 6
        assert ColorScheme.CLASSIC_BLUE in self.service.color_schemes
        assert ColorScheme.MODERN_GRAY in self.service.color_schemes
        
        # Check that all font mappings are initialized
        assert len(self.service.font_mappings) == 5
        assert FontFamily.HELVETICA in self.service.font_mappings
        assert FontFamily.TIMES in self.service.font_mappings
        
        # Check that all template configs are initialized
        assert len(self.service.template_configs) == 7
        assert FormattingTemplate.STANDARD in self.service.template_configs
        assert FormattingTemplate.MODERN in self.service.template_configs
    
    def test_get_available_templates_free_user(self):
        """Test that free users only get the standard template"""
        templates = self.service.get_available_templates(is_pro=False)
        
        assert len(templates) == 1
        assert templates[0]['id'] == FormattingTemplate.STANDARD.value
        assert templates[0]['pro_only'] is False
        assert 'Standard Professional' in templates[0]['name']
    
    def test_get_available_templates_pro_user(self):
        """Test that Pro users get all templates"""
        templates = self.service.get_available_templates(is_pro=True)
        
        assert len(templates) == 7  # All templates
        
        # Check that standard template is included
        standard_templates = [t for t in templates if t['id'] == FormattingTemplate.STANDARD.value]
        assert len(standard_templates) == 1
        assert standard_templates[0]['pro_only'] is False
        
        # Check that Pro templates are included
        pro_templates = [t for t in templates if t['pro_only'] is True]
        assert len(pro_templates) == 6  # All except standard
        
        # Verify specific Pro templates
        template_ids = [t['id'] for t in templates]
        assert FormattingTemplate.MODERN.value in template_ids
        assert FormattingTemplate.EXECUTIVE.value in template_ids
        assert FormattingTemplate.CREATIVE.value in template_ids
    
    def test_get_available_color_schemes(self):
        """Test that all color schemes are returned"""
        color_schemes = self.service.get_available_color_schemes()
        
        assert len(color_schemes) == 6
        
        # Check specific color schemes
        scheme_ids = [cs['id'] for cs in color_schemes]
        assert ColorScheme.CLASSIC_BLUE.value in scheme_ids
        assert ColorScheme.MODERN_GRAY.value in scheme_ids
        assert ColorScheme.CREATIVE_TEAL.value in scheme_ids
        
        # Check that each scheme has required fields
        for scheme in color_schemes:
            assert 'id' in scheme
            assert 'name' in scheme
            assert 'description' in scheme
            assert 'primary_color' in scheme
            assert scheme['primary_color'].startswith('#')
    
    def test_validate_formatting_request_valid_free_user(self):
        """Test validation for valid free user request (standard template only)"""
        is_valid, message = self.service.validate_formatting_request(
            template=FormattingTemplate.STANDARD.value,
            color_scheme=ColorScheme.CLASSIC_BLUE.value,
            font_family=FontFamily.HELVETICA.value,
            is_pro=False
        )
        
        assert is_valid is True
        assert "Valid formatting request" in message
    
    def test_validate_formatting_request_invalid_free_user(self):
        """Test validation for invalid free user request (Pro template)"""
        is_valid, message = self.service.validate_formatting_request(
            template=FormattingTemplate.MODERN.value,
            color_scheme=ColorScheme.CLASSIC_BLUE.value,
            font_family=FontFamily.HELVETICA.value,
            is_pro=False
        )
        
        assert is_valid is False
        assert "requires Pro subscription" in message
    
    def test_validate_formatting_request_valid_pro_user(self):
        """Test validation for valid Pro user request"""
        is_valid, message = self.service.validate_formatting_request(
            template=FormattingTemplate.EXECUTIVE.value,
            color_scheme=ColorScheme.EXECUTIVE_BLACK.value,
            font_family=FontFamily.TIMES.value,
            is_pro=True
        )
        
        assert is_valid is True
        assert "Valid formatting request" in message
    
    def test_validate_formatting_request_invalid_template(self):
        """Test validation with invalid template"""
        is_valid, message = self.service.validate_formatting_request(
            template="invalid_template",
            color_scheme=ColorScheme.CLASSIC_BLUE.value,
            font_family=FontFamily.HELVETICA.value,
            is_pro=True
        )
        
        assert is_valid is False
        assert "Invalid template" in message
    
    def test_validate_formatting_request_invalid_color_scheme(self):
        """Test validation with invalid color scheme"""
        is_valid, message = self.service.validate_formatting_request(
            template=FormattingTemplate.STANDARD.value,
            color_scheme="invalid_color",
            font_family=FontFamily.HELVETICA.value,
            is_pro=False
        )
        
        assert is_valid is False
        assert "Invalid color scheme" in message
    
    def test_validate_formatting_request_invalid_font_family(self):
        """Test validation with invalid font family"""
        is_valid, message = self.service.validate_formatting_request(
            template=FormattingTemplate.STANDARD.value,
            color_scheme=ColorScheme.CLASSIC_BLUE.value,
            font_family="invalid_font",
            is_pro=False
        )
        
        assert is_valid is False
        assert "Invalid font family" in message
    
    def test_ats_compatibility_validation_good_options(self):
        """Test ATS compatibility validation with good options"""
        options = FormattingOptions(
            template=FormattingTemplate.STANDARD,
            font_size=10,
            use_two_columns=False,
            include_border=False
        )
        
        is_compatible = self.service._validate_ats_compatibility(options)
        assert is_compatible is True
    
    def test_ats_compatibility_validation_bad_font_size(self):
        """Test ATS compatibility validation with bad font size"""
        options = FormattingOptions(
            template=FormattingTemplate.STANDARD,
            font_size=7,  # Too small
            use_two_columns=False,
            include_border=False
        )
        
        is_compatible = self.service._validate_ats_compatibility(options)
        assert is_compatible is False
    
    def test_ats_compatibility_validation_two_columns(self):
        """Test ATS compatibility validation with two columns"""
        options = FormattingOptions(
            template=FormattingTemplate.STANDARD,
            font_size=10,
            use_two_columns=True,  # Problematic for ATS
            include_border=False
        )
        
        is_compatible = self.service._validate_ats_compatibility(options)
        assert is_compatible is False
    
    def test_ats_compatibility_validation_creative_template(self):
        """Test ATS compatibility validation with creative template"""
        options = FormattingOptions(
            template=FormattingTemplate.CREATIVE,  # May not be ATS compatible
            font_size=10,
            use_two_columns=False,
            include_border=False
        )
        
        is_compatible = self.service._validate_ats_compatibility(options)
        assert is_compatible is False
    
    def test_adjust_for_ats_compatibility(self):
        """Test ATS compatibility adjustments"""
        options = FormattingOptions(
            template=FormattingTemplate.CREATIVE,
            font_size=7,  # Too small
            use_two_columns=True,  # Problematic
            include_border=True
        )
        
        adjusted = self.service._adjust_for_ats_compatibility(options)
        
        # Check adjustments
        assert adjusted.font_size >= 9  # Should be clamped
        assert adjusted.use_two_columns is False  # Should be disabled
        assert adjusted.template == FormattingTemplate.MODERN  # Should be changed from CREATIVE
    
    def test_parse_resume_content_basic(self):
        """Test basic resume content parsing"""
        resume_data = self.service._parse_resume_content(self.sample_resume_text)
        
        assert 'name' in resume_data
        assert 'contact' in resume_data
        assert 'sections' in resume_data
        
        # Check name detection
        assert resume_data['name'] == 'John Doe'
        
        # Check contact info detection
        assert len(resume_data['contact']) > 0
        contact_text = ' '.join(resume_data['contact'])
        assert 'john.doe@email.com' in contact_text
        assert '(555) 123-4567' in contact_text
        
        # Check sections
        assert len(resume_data['sections']) > 0
        section_titles = [section['title'] for section in resume_data['sections']]
        assert any('EXPERIENCE' in title.upper() for title in section_titles)
        assert any('EDUCATION' in title.upper() for title in section_titles)
        assert any('SKILLS' in title.upper() for title in section_titles)
    
    def test_create_standard_formatted_resume(self):
        """Test creating a standard formatted resume"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = self.service.create_standard_formatted_resume(
                self.sample_resume_text,
                temp_path,
                "Software Engineer"
            )
            
            assert success is True
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_create_advanced_formatted_resume_standard_template(self):
        """Test creating an advanced formatted resume with standard template"""
        options = FormattingOptions(
            template=FormattingTemplate.STANDARD,
            color_scheme=ColorScheme.CLASSIC_BLUE,
            font_family=FontFamily.HELVETICA,
            font_size=10
        )
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = self.service.create_advanced_formatted_resume(
                self.sample_resume_text,
                options,
                temp_path,
                "Software Engineer"
            )
            
            assert success is True
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_create_advanced_formatted_resume_modern_template(self):
        """Test creating an advanced formatted resume with modern template"""
        options = FormattingOptions(
            template=FormattingTemplate.MODERN,
            color_scheme=ColorScheme.MODERN_GRAY,
            font_family=FontFamily.HELVETICA,
            font_size=11
        )
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = self.service.create_advanced_formatted_resume(
                self.sample_resume_text,
                options,
                temp_path,
                "Senior Software Engineer"
            )
            
            assert success is True
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_create_advanced_formatted_resume_executive_template(self):
        """Test creating an advanced formatted resume with executive template"""
        options = FormattingOptions(
            template=FormattingTemplate.EXECUTIVE,
            color_scheme=ColorScheme.EXECUTIVE_BLACK,
            font_family=FontFamily.TIMES,
            font_size=11
        )
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = self.service.create_advanced_formatted_resume(
                self.sample_resume_text,
                options,
                temp_path,
                "Chief Technology Officer"
            )
            
            assert success is True
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_create_advanced_formatted_resume_with_invalid_path(self):
        """Test creating resume with invalid output path"""
        options = FormattingOptions(
            template=FormattingTemplate.STANDARD,
            color_scheme=ColorScheme.CLASSIC_BLUE,
            font_family=FontFamily.HELVETICA
        )
        
        # Use invalid path
        invalid_path = "/invalid/path/resume.pdf"
        
        success = self.service.create_advanced_formatted_resume(
            self.sample_resume_text,
            options,
            invalid_path,
            "Software Engineer"
        )
        
        assert success is False
    
    def test_create_advanced_formatted_resume_empty_text(self):
        """Test creating resume with empty text"""
        options = FormattingOptions(
            template=FormattingTemplate.STANDARD,
            color_scheme=ColorScheme.CLASSIC_BLUE,
            font_family=FontFamily.HELVETICA
        )
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            success = self.service.create_advanced_formatted_resume(
                "",  # Empty text
                options,
                temp_path,
                "Software Engineer"
            )
            
            # Should still succeed but create a minimal PDF
            assert success is True
            assert os.path.exists(temp_path)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestAdvancedFormattingIntegration:
    """Integration tests for advanced formatting with other components"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = AdvancedFormattingService()
    
    def test_formatting_options_dataclass(self):
        """Test FormattingOptions dataclass functionality"""
        options = FormattingOptions(
            template=FormattingTemplate.MODERN,
            color_scheme=ColorScheme.CREATIVE_TEAL,
            font_family=FontFamily.CALIBRI,
            font_size=12,
            line_spacing=1.5,
            margin_size=0.75,
            use_two_columns=True,
            include_border=True
        )
        
        assert options.template == FormattingTemplate.MODERN
        assert options.color_scheme == ColorScheme.CREATIVE_TEAL
        assert options.font_family == FontFamily.CALIBRI
        assert options.font_size == 12
        assert options.line_spacing == 1.5
        assert options.margin_size == 0.75
        assert options.use_two_columns is True
        assert options.include_border is True
    
    def test_formatting_options_defaults(self):
        """Test FormattingOptions default values"""
        options = FormattingOptions()
        
        assert options.template == FormattingTemplate.STANDARD
        assert options.color_scheme == ColorScheme.CLASSIC_BLUE
        assert options.font_family == FontFamily.HELVETICA
        assert options.font_size == 10
        assert options.line_spacing == 1.2
        assert options.margin_size == 0.5
        assert options.use_two_columns is False
        assert options.include_border is False
    
    def test_enum_values(self):
        """Test that all enum values are properly defined"""
        # Test FormattingTemplate enum
        templates = list(FormattingTemplate)
        assert len(templates) == 7
        assert FormattingTemplate.STANDARD in templates
        assert FormattingTemplate.MODERN in templates
        assert FormattingTemplate.EXECUTIVE in templates
        assert FormattingTemplate.CREATIVE in templates
        assert FormattingTemplate.MINIMAL in templates
        assert FormattingTemplate.ACADEMIC in templates
        assert FormattingTemplate.TECHNICAL in templates
        
        # Test ColorScheme enum
        colors = list(ColorScheme)
        assert len(colors) == 6
        assert ColorScheme.CLASSIC_BLUE in colors
        assert ColorScheme.MODERN_GRAY in colors
        assert ColorScheme.EXECUTIVE_BLACK in colors
        assert ColorScheme.CREATIVE_TEAL in colors
        assert ColorScheme.WARM_BROWN in colors
        assert ColorScheme.TECH_GREEN in colors
        
        # Test FontFamily enum
        fonts = list(FontFamily)
        assert len(fonts) == 5
        assert FontFamily.HELVETICA in fonts
        assert FontFamily.TIMES in fonts
        assert FontFamily.CALIBRI in fonts
        assert FontFamily.ARIAL in fonts
        assert FontFamily.GARAMOND in fonts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])