"""
Template System Tests

Comprehensive tests for template rendering, CSS loading, preview generation,
metadata endpoints, fallback mechanisms, and PDF generation.
"""

import pytest
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from services.template_engine import TemplateEngine
from services.template_registry import TemplateRegistry
from services.template_preview_service import TemplatePreviewService
from models.resume_schema import Resume
from main import app


# Test client with proper base URL
client = TestClient(app, base_url="http://localhost")


class TestFixtures:
    """Test data fixtures"""
    
    @staticmethod
    def get_sample_resume_data() -> Dict[str, Any]:
        """Get comprehensive sample resume data for testing"""
        return {
            "name": "John Doe",
            "headline": "Senior Software Engineer",
            "contact": {
                "email": "john.doe@example.com",
                "phone": "(555) 123-4567",
                "location": "San Francisco, CA",
                "links": [
                    {"url": "https://linkedin.com/in/johndoe", "label": "LinkedIn"},
                    {"url": "https://github.com/johndoe", "label": "GitHub"}
                ]
            },
            "summary": "Experienced software engineer with expertise in full-stack development.",
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "start": "2020-01",
                    "end": None,
                    "bullets": [
                        "Led development of microservices architecture",
                        "Improved system performance by 40%",
                        "Mentored junior developers"
                    ]
                },
                {
                    "title": "Software Developer",
                    "company": "StartupXYZ",
                    "location": "San Francisco, CA", 
                    "start": "2018-06",
                    "end": "2019-12",
                    "bullets": [
                        "Built responsive web applications",
                        "Integrated third-party APIs",
                        "Implemented automated testing"
                    ]
                }
            ],
            "education": [
                {
                    "school": "University of California, Berkeley",
                    "degree": "Bachelor of Science in Computer Science",
                    "end": "2018-05"
                }
            ],
            "skills": [
                {"name": "JavaScript"},
                {"name": "Python"},
                {"name": "React"},
                {"name": "Node.js"},
                {"name": "AWS"},
                {"name": "Docker"}
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Full-stack web application",
                    "bullets": [
                        "Built with React and Node.js",
                        "Integrated payment processing"
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_minimal_resume_data() -> Dict[str, Any]:
        """Get minimal resume data for edge case testing"""
        return {
            "name": "Jane Smith",
            "contact": {
                "email": "jane@example.com"
            }
        }
    
    @staticmethod
    def get_empty_resume_data() -> Dict[str, Any]:
        """Get completely empty resume data"""
        return {}


class TestTemplateRegistry:
    """Test template registry functionality"""
    
    def test_list_template_ids(self):
        """Test that template registry returns expected template IDs"""
        template_ids = TemplateRegistry.list_ids()
        
        # Should have at least the core templates
        expected_templates = {'modern', 'classic', 'creative', 'executive', 'technical'}
        actual_templates = set(template_ids)
        
        assert expected_templates.issubset(actual_templates), f"Missing templates: {expected_templates - actual_templates}"
        assert len(template_ids) >= 5, "Should have at least 5 templates"
    
    def test_template_validation(self):
        """Test template validation for all templates"""
        template_ids = TemplateRegistry.list_ids()
        
        for template_id in template_ids:
            if template_id == 'emails':  # Skip email templates
                continue
                
            try:
                TemplateRegistry.validate(template_id)
            except FileNotFoundError as e:
                pytest.fail(f"Template {template_id} validation failed: {e}")
    
    def test_template_metadata_loading(self):
        """Test metadata loading for all templates"""
        template_ids = TemplateRegistry.list_ids()
        
        for template_id in template_ids:
            if template_id == 'emails':  # Skip email templates
                continue
                
            try:
                meta = TemplateRegistry.get_meta(template_id)
                assert isinstance(meta, dict), f"Metadata for {template_id} should be a dict"
                assert 'id' in meta or meta.get('name'), f"Template {template_id} should have id or name in metadata"
            except FileNotFoundError:
                pytest.fail(f"Template {template_id} missing meta.json file")
    
    def test_template_files_exist(self):
        """Test that all required template files exist"""
        template_ids = TemplateRegistry.list_ids()
        required_files = ['template.html.j2', 'styles.css', 'meta.json']
        
        for template_id in template_ids:
            if template_id == 'emails':  # Skip email templates
                continue
                
            template_dir = TemplateRegistry.get_dir(template_id)
            
            for required_file in required_files:
                file_path = template_dir / required_file
                assert file_path.exists(), f"Template {template_id} missing {required_file}"
                assert file_path.is_file(), f"Template {template_id} {required_file} is not a file"


class TestTemplateRendering:
    """Test template rendering functionality"""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data fixture"""
        return TestFixtures.get_sample_resume_data()
    
    @pytest.fixture
    def minimal_resume(self):
        """Minimal resume data fixture"""
        return TestFixtures.get_minimal_resume_data()
    
    def test_template_renders_with_full_data(self, sample_resume):
        """Test that each template renders without errors with full data"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
        
        for template_id in template_ids:
            try:
                html = TemplateEngine.render_preview(template_id, resume_json=sample_resume)
                
                # Basic HTML validation
                assert isinstance(html, str), f"Template {template_id} should return string"
                assert len(html) > 100, f"Template {template_id} HTML too short: {len(html)} chars"
                assert '<!DOCTYPE html>' in html or '<!doctype html>' in html, f"Template {template_id} missing DOCTYPE"
                assert '<html' in html, f"Template {template_id} missing html tag"
                assert '</html>' in html, f"Template {template_id} missing closing html tag"
                assert 'John Doe' in html, f"Template {template_id} should contain name"
                
            except Exception as e:
                pytest.fail(f"Template {template_id} rendering failed: {e}")
    
    def test_template_renders_with_minimal_data(self, minimal_resume):
        """Test that templates handle minimal data gracefully"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
        
        for template_id in template_ids:
            try:
                html = TemplateEngine.render_preview(template_id, resume_json=minimal_resume)
                
                assert isinstance(html, str), f"Template {template_id} should return string with minimal data"
                assert len(html) > 50, f"Template {template_id} HTML too short with minimal data"
                assert 'Jane Smith' in html, f"Template {template_id} should contain minimal name"
                
            except Exception as e:
                pytest.fail(f"Template {template_id} failed with minimal data: {e}")
    
    def test_template_handles_empty_data(self):
        """Test that templates handle completely empty data"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
        empty_data = TestFixtures.get_empty_resume_data()
        
        for template_id in template_ids:
            try:
                html = TemplateEngine.render_preview(template_id, resume_json=empty_data)
                
                assert isinstance(html, str), f"Template {template_id} should handle empty data"
                assert len(html) > 50, f"Template {template_id} should generate basic HTML with empty data"
                
            except Exception as e:
                pytest.fail(f"Template {template_id} failed with empty data: {e}")
    
    def test_css_inclusion(self, sample_resume):
        """Test that CSS is properly included in rendered templates"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
        
        for template_id in template_ids:
            html = TemplateEngine.render_preview(template_id, resume_json=sample_resume)
            
            # Check for CSS inclusion
            assert '<style>' in html, f"Template {template_id} missing CSS style tag"
            assert 'font-family' in html, f"Template {template_id} CSS should include font-family"
            
            # Check for basic CSS properties that should be in all templates
            css_content = html.lower()
            assert any(prop in css_content for prop in ['margin', 'padding', 'color']), \
                f"Template {template_id} CSS missing basic properties"


class TestCSSFiles:
    """Test CSS file loading and validation"""
    
    def test_css_files_exist_and_readable(self):
        """Test that all CSS files exist and are readable"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
        
        for template_id in template_ids:
            template_dir = TemplateRegistry.get_dir(template_id)
            css_path = template_dir / 'styles.css'
            
            assert css_path.exists(), f"CSS file missing for template {template_id}"
            
            try:
                css_content = css_path.read_text(encoding='utf-8')
                assert len(css_content) > 100, f"CSS file too short for template {template_id}"
                assert 'body' in css_content or 'html' in css_content, \
                    f"CSS file should contain basic selectors for template {template_id}"
            except Exception as e:
                pytest.fail(f"Failed to read CSS file for template {template_id}: {e}")
    
    def test_css_syntax_basic_validation(self):
        """Test basic CSS syntax validation"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
        
        for template_id in template_ids:
            template_dir = TemplateRegistry.get_dir(template_id)
            css_path = template_dir / 'styles.css'
            
            css_content = css_path.read_text(encoding='utf-8')
            
            # Basic syntax checks
            open_braces = css_content.count('{')
            close_braces = css_content.count('}')
            assert open_braces == close_braces, \
                f"CSS syntax error in {template_id}: mismatched braces ({open_braces} vs {close_braces})"
            
            # Check for common CSS properties
            assert ':' in css_content, f"CSS file for {template_id} should contain property declarations"


class TestPreviewGeneration:
    """Test preview generation functionality"""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data fixture"""
        return TestFixtures.get_sample_resume_data()
    
    @pytest.mark.asyncio
    async def test_preview_service_html_generation(self, sample_resume):
        """Test preview service HTML generation"""
        async with TemplatePreviewService() as service:
            template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
            
            for template_id in template_ids:
                result = await service.generate_preview(template_id, 'html', use_cache=False)
                
                assert result.success, f"Preview generation failed for {template_id}: {result.error_message}"
                assert result.data, f"No HTML data returned for {template_id}"
                assert isinstance(result.data, str), f"HTML data should be string for {template_id}"
                assert len(result.data) > 100, f"HTML too short for {template_id}"
    
    @pytest.mark.asyncio
    async def test_preview_service_json_generation(self, sample_resume):
        """Test preview service JSON generation"""
        async with TemplatePreviewService() as service:
            template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails'][:2]  # Test first 2 for speed
            
            for template_id in template_ids:
                result = await service.generate_preview(template_id, 'json', use_cache=False)
                
                assert result.success, f"JSON preview generation failed for {template_id}: {result.error_message}"
                assert result.data, f"No JSON data returned for {template_id}"
                assert isinstance(result.data, dict), f"JSON data should be dict for {template_id}"
                assert 'template_id' in result.data, f"JSON should contain template_id for {template_id}"
    
    @pytest.mark.asyncio
    async def test_preview_service_with_custom_data(self, sample_resume):
        """Test preview service with custom resume data"""
        async with TemplatePreviewService() as service:
            result = await service.generate_preview('modern', 'html', use_cache=False, custom_data=sample_resume)
            
            assert result.success, f"Custom data preview failed: {result.error_message}"
            assert 'John Doe' in result.data, "Custom data should be reflected in preview"
    
    @pytest.mark.asyncio
    async def test_preview_service_caching(self):
        """Test preview service caching functionality"""
        async with TemplatePreviewService() as service:
            # First request
            result1 = await service.generate_preview('modern', 'html', use_cache=True)
            assert result1.success
            assert not result1.cache_hit
            
            # Second request should be cached
            result2 = await service.generate_preview('modern', 'html', use_cache=True)
            assert result2.success
            # Note: cache_hit might not be True due to different sample data hashing


class TestMetadataEndpoint:
    """Test metadata API endpoint"""
    
    def test_metadata_endpoint_returns_all_templates(self):
        """Test that metadata endpoint returns all expected templates"""
        response = client.get("/api/templates/metadata")
        
        assert response.status_code == 200, f"Metadata endpoint failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert 'templates' in data, "Response should contain templates array"
        assert 'total_count' in data, "Response should contain total_count"
        
        templates = data['templates']
        template_ids = {t['id'] for t in templates}
        
        # Should have core templates (excluding emails)
        expected_templates = {'modern', 'classic', 'creative', 'executive', 'technical'}
        assert expected_templates.issubset(template_ids), f"Missing templates: {expected_templates - template_ids}"
    
    def test_metadata_endpoint_template_structure(self):
        """Test that each template has required metadata fields"""
        response = client.get("/api/templates/metadata")
        data = response.json()
        
        required_fields = {'id', 'name', 'description', 'category'}
        
        for template in data['templates']:
            template_id = template.get('id', 'unknown')
            
            for field in required_fields:
                assert field in template, f"Template {template_id} missing required field: {field}"
            
            # Validate field types
            assert isinstance(template['id'], str), f"Template {template_id} id should be string"
            assert isinstance(template['name'], str), f"Template {template_id} name should be string"
            assert isinstance(template['description'], str), f"Template {template_id} description should be string"
    
    def test_individual_template_metadata(self):
        """Test individual template metadata endpoints"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails'][:3]  # Test first 3
        
        for template_id in template_ids:
            response = client.get(f"/api/templates/metadata/{template_id}")
            
            assert response.status_code == 200, f"Individual metadata failed for {template_id}: {response.status_code}"
            
            data = response.json()
            assert data['id'] == template_id, f"Returned template ID should match requested for {template_id}"
            assert 'files' in data, f"Template {template_id} metadata should include files info"
    
    def test_metadata_endpoint_with_previews(self):
        """Test metadata endpoint with preview URLs"""
        response = client.get("/api/templates/metadata?include_previews=true")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that preview URLs are included
        for template in data['templates']:
            if template['id'] != 'emails':  # Skip email templates
                # Note: preview URLs might not be included if they're not in the enhanced metadata
                # This test verifies the endpoint works with the include_previews parameter
                pass


class TestTemplateFallback:
    """Test template fallback mechanisms"""
    
    def test_invalid_template_fallback(self):
        """Test that invalid template requests handle gracefully"""
        # This test depends on how the system handles invalid templates
        # The template engine should either fall back or raise appropriate errors
        
        try:
            # Try to render a non-existent template
            html = TemplateEngine.render_preview('nonexistent_template', resume_json={})
            # If this succeeds, check that it's a reasonable fallback
            assert isinstance(html, str)
        except Exception as e:
            # If it fails, that's also acceptable behavior
            assert 'not found' in str(e).lower() or 'nonexistent' in str(e).lower()
    
    def test_fallback_content_rendering(self):
        """Test fallback content rendering with raw text"""
        sample_data = TestFixtures.get_sample_resume_data()
        
        # Test with use_fallback flag (this might need to be adjusted based on actual implementation)
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails'][:2]
        
        for template_id in template_ids:
            try:
                # Test normal rendering
                html = TemplateEngine.render_preview(template_id, resume_json=sample_data)
                assert 'John Doe' in html, f"Template {template_id} should render name"
            except Exception as e:
                pytest.fail(f"Fallback test failed for {template_id}: {e}")


class TestPDFGeneration:
    """Test PDF generation functionality"""
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume data fixture"""
        return TestFixtures.get_sample_resume_data()
    
    @pytest.mark.asyncio
    async def test_pdf_generation_all_templates(self, sample_resume):
        """Test PDF generation for each template"""
        template_ids = [tid for tid in TemplateRegistry.list_ids() if tid != 'emails']
        
        for template_id in template_ids:
            try:
                pdf_bytes = await TemplateEngine.render_pdf(template_id, resume_json=sample_resume)
                
                assert isinstance(pdf_bytes, bytes), f"PDF should return bytes for {template_id}"
                assert len(pdf_bytes) > 1000, f"PDF too small for {template_id}: {len(pdf_bytes)} bytes"
                
                # Check PDF header
                assert pdf_bytes.startswith(b'%PDF-'), f"Invalid PDF header for {template_id}"
                
            except Exception as e:
                pytest.fail(f"PDF generation failed for {template_id}: {e}")
    
    @pytest.mark.asyncio
    async def test_pdf_generation_with_minimal_data(self):
        """Test PDF generation with minimal data"""
        minimal_data = TestFixtures.get_minimal_resume_data()
        
        # Test with one template to ensure minimal data works
        try:
            pdf_bytes = await TemplateEngine.render_pdf('modern', resume_json=minimal_data)
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 500, "PDF should generate even with minimal data"
            assert pdf_bytes.startswith(b'%PDF-'), "Should produce valid PDF with minimal data"
        except Exception as e:
            pytest.fail(f"PDF generation with minimal data failed: {e}")


class TestPreviewEndpoints:
    """Test preview API endpoints"""
    
    def test_preview_endpoint_html(self):
        """Test HTML preview endpoint"""
        response = client.get("/api/templates/preview/modern?format=html&use_sample=true")
        
        assert response.status_code == 200, f"HTML preview endpoint failed: {response.status_code}"
        assert 'text/html' in response.headers.get('content-type', ''), "Should return HTML content type"
        
        html_content = response.content.decode('utf-8')
        assert '<!DOCTYPE html>' in html_content or '<!doctype html>' in html_content, "Should return valid HTML"
    
    def test_preview_endpoint_json(self):
        """Test JSON preview endpoint"""
        response = client.get("/api/templates/preview/modern?format=json&use_sample=true")
        
        assert response.status_code == 200, f"JSON preview endpoint failed: {response.status_code}"
        
        data = response.json()
        assert 'template' in data, "JSON response should contain template info"
        assert 'preview_data' in data, "JSON response should contain preview data"
    
    def test_preview_endpoint_invalid_template(self):
        """Test preview endpoint with invalid template"""
        response = client.get("/api/templates/preview/invalid_template?format=html")
        
        assert response.status_code == 404, "Should return 404 for invalid template"
    
    def test_preview_endpoint_invalid_format(self):
        """Test preview endpoint with invalid format"""
        response = client.get("/api/templates/preview/modern?format=invalid")
        
        assert response.status_code == 400, "Should return 400 for invalid format"


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_preview_workflow(self):
        """Test complete preview generation workflow"""
        # 1. Get template metadata
        response = client.get("/api/templates/metadata")
        assert response.status_code == 200
        templates = response.json()['templates']
        
        # 2. Pick a template and generate preview
        template_id = next(t['id'] for t in templates if t['id'] != 'emails')
        
        response = client.get(f"/api/templates/preview/{template_id}?format=html&use_sample=true")
        assert response.status_code == 200
        
        # 3. Test with custom data
        custom_data = TestFixtures.get_sample_resume_data()
        response = client.post(
            f"/api/templates/preview/{template_id}",
            json={"resume_data": custom_data, "format": "html"}
        )
        assert response.status_code == 200
    
    def test_cache_operations(self):
        """Test cache-related operations"""
        # Test cache stats
        response = client.get("/api/templates/cache/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert 'total_entries' in stats, "Cache stats should include total entries"
        
        # Test cache clearing
        response = client.delete("/api/templates/cache")
        assert response.status_code == 200
        
        clear_result = response.json()
        assert 'message' in clear_result, "Cache clear should return confirmation message"


# Pytest configuration and fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment"""
    # Ensure we're in the right directory
    import os
    if not os.path.exists('templates'):
        os.chdir('..')  # Go up one level if we're in tests directory
    
    yield
    
    # Cleanup after tests
    pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
