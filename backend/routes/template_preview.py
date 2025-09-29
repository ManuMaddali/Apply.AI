"""
Template Preview API Router

Provides endpoints for template previews and metadata.
Includes caching, sample data generation, and screenshot capabilities.
"""

from __future__ import annotations

import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from io import BytesIO
import base64

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from services.template_engine import TemplateEngine
from services.template_registry import TemplateRegistry
from models.resume_schema import Resume

# Optional dependencies for screenshot generation
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

router = APIRouter()

# In-memory cache for previews (in production, use Redis or similar)
_preview_cache: Dict[str, Dict[str, Any]] = {}
_metadata_cache: Optional[Dict[str, Any]] = None
_cache_ttl = timedelta(hours=1)  # Cache for 1 hour


class TemplateMetadata(BaseModel):
    """Template metadata model"""
    id: str
    name: str
    description: str
    category: str
    supports: List[str]
    features: List[str]
    preview_url: Optional[str] = None
    screenshot_url: Optional[str] = None


class PreviewRequest(BaseModel):
    """Request model for custom preview data"""
    resume_data: Optional[Dict[str, Any]] = None
    format: str = "html"  # html, png, json


def generate_sample_resume_data() -> Dict[str, Any]:
    """
    Generate comprehensive sample resume data for template previews
    """
    return {
        "name": "Alexandra Johnson",
        "headline": "Senior Software Engineer & Technical Lead",
        "contact": {
            "email": "alexandra.johnson@email.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA",
            "links": [
                {"url": "https://linkedin.com/in/alexandra-johnson", "label": "LinkedIn"},
                {"url": "https://github.com/alexandra-johnson", "label": "GitHub"},
                {"url": "https://alexandra-johnson.dev", "label": "Portfolio"}
            ]
        },
        "summary": "Innovative Senior Software Engineer with 8+ years of experience building scalable web applications and leading high-performing development teams. Expertise in full-stack development, cloud architecture, and agile methodologies. Proven track record of delivering complex projects that drive business growth and improve user experience.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp Solutions",
                "location": "San Francisco, CA",
                "start": "2021-03",
                "end": None,
                "bullets": [
                    "Led development of microservices architecture serving 2M+ daily active users",
                    "Reduced system latency by 40% through database optimization and caching strategies",
                    "Mentored 5 junior developers and established code review best practices",
                    "Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes"
                ]
            },
            {
                "title": "Full Stack Developer",
                "company": "StartupXYZ",
                "location": "San Francisco, CA",
                "start": "2019-01",
                "end": "2021-02",
                "bullets": [
                    "Built responsive web application using React, Node.js, and PostgreSQL",
                    "Integrated third-party APIs including Stripe, SendGrid, and AWS services",
                    "Collaborated with design team to implement pixel-perfect UI components",
                    "Achieved 99.9% uptime through robust error handling and monitoring"
                ]
            },
            {
                "title": "Software Developer",
                "company": "Digital Agency Inc",
                "location": "San Francisco, CA",
                "start": "2017-06",
                "end": "2018-12",
                "bullets": [
                    "Developed custom WordPress plugins for enterprise clients",
                    "Optimized website performance resulting in 60% faster load times",
                    "Managed multiple client projects simultaneously with strict deadlines",
                    "Created automated testing suite improving code quality and reliability"
                ]
            }
        ],
        "education": [
            {
                "school": "University of California, Berkeley",
                "degree": "Bachelor of Science in Computer Science",
                "end": "2017-05"
            }
        ],
        "skills": [
            {"name": "JavaScript"},
            {"name": "TypeScript"},
            {"name": "Python"},
            {"name": "Java"},
            {"name": "Go"},
            {"name": "SQL"},
            {"name": "React"},
            {"name": "Node.js"},
            {"name": "Express"},
            {"name": "Django"},
            {"name": "Spring Boot"},
            {"name": "GraphQL"},
            {"name": "AWS"},
            {"name": "Docker"},
            {"name": "Kubernetes"},
            {"name": "Jenkins"},
            {"name": "Terraform"},
            {"name": "MongoDB"},
            {"name": "Git"},
            {"name": "Jira"},
            {"name": "Figma"},
            {"name": "Postman"},
            {"name": "Redis"},
            {"name": "Elasticsearch"}
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Full-stack e-commerce solution with real-time inventory management",
                "bullets": [
                    "Built with React, Node.js, PostgreSQL, Redis, and Stripe",
                    "Implemented real-time inventory tracking and management",
                    "Integrated secure payment processing with Stripe API",
                    "Deployed on AWS with auto-scaling capabilities"
                ]
            },
            {
                "name": "Task Management API",
                "description": "RESTful API for team collaboration and project management",
                "bullets": [
                    "Developed using Python, FastAPI, MongoDB, and Docker",
                    "Implemented JWT authentication and role-based access control",
                    "Created comprehensive API documentation with OpenAPI",
                    "Achieved 99.9% uptime with automated testing and monitoring"
                ]
            }
        ]
    }


def _get_cache_key(template_id: str, format_type: str = "html", custom_data: bool = False) -> str:
    """Generate cache key for preview"""
    base_key = f"{template_id}:{format_type}"
    if custom_data:
        base_key += ":custom"
    return hashlib.md5(base_key.encode()).hexdigest()


def _is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """Check if cache entry is still valid"""
    if "timestamp" not in cache_entry:
        return False
    
    cache_time = datetime.fromisoformat(cache_entry["timestamp"])
    return datetime.now() - cache_time < _cache_ttl


async def _generate_screenshot(html_content: str) -> Optional[bytes]:
    """
    Generate PNG screenshot from HTML content using Playwright
    """
    if not PLAYWRIGHT_AVAILABLE:
        return None
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set viewport for consistent screenshots
            await page.set_viewport_size({"width": 1200, "height": 1600})
            
            # Load HTML content
            await page.set_content(html_content, wait_until="networkidle")
            
            # Take screenshot
            screenshot_bytes = await page.screenshot(
                type="png",
                full_page=True,
                clip={"x": 0, "y": 0, "width": 1200, "height": 1600}
            )
            
            await browser.close()
            return screenshot_bytes
            
    except Exception as e:
        print(f"Screenshot generation failed: {e}")
        return None


def _generate_simple_preview_image(template_id: str) -> Optional[bytes]:
    """
    Generate a simple preview image using PIL when Playwright is not available
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Template color schemes
        colors = {
            "modern": {"bg": "#ffffff", "accent": "#2f6fed", "text": "#1a202c"},
            "classic": {"bg": "#ffffff", "accent": "#000000", "text": "#000000"},
            "creative": {"bg": "#f7fafc", "accent": "#667eea", "text": "#2d3748"},
            "technical": {"bg": "#f7fafc", "accent": "#0066cc", "text": "#1a202c"},
            "executive": {"bg": "#ffffff", "accent": "#8B0000", "text": "#000000"}
        }
        
        template_colors = colors.get(template_id, colors["modern"])
        
        # Create image
        width, height = 300, 400
        img = Image.new('RGB', (width, height), template_colors["bg"])
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a better font
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw template preview
        y_pos = 30
        
        # Template name
        draw.text((width//2, y_pos), template_id.title() + " Template", 
                 fill=template_colors["accent"], font=title_font, anchor="mt")
        y_pos += 50
        
        # Sample name
        draw.text((width//2, y_pos), "JOHN SMITH", 
                 fill=template_colors["text"], font=text_font, anchor="mt")
        y_pos += 30
        
        # Contact info
        draw.text((width//2, y_pos), "john.smith@email.com | (555) 123-4567", 
                 fill=template_colors["text"], font=small_font, anchor="mt")
        y_pos += 40
        
        # Section headers and content
        sections = ["SUMMARY", "EXPERIENCE", "EDUCATION", "SKILLS"]
        for section in sections:
            # Section header
            draw.text((30, y_pos), section, 
                     fill=template_colors["accent"], font=text_font)
            y_pos += 25
            
            # Sample content lines
            for i in range(2):
                draw.text((40, y_pos), "■ Sample content for " + section.lower(), 
                         fill=template_colors["text"], font=small_font)
                y_pos += 15
            
            y_pos += 10
            
            if y_pos > height - 50:
                break
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
        
    except ImportError:
        print("PIL not available for simple preview generation")
        return None
    except Exception as e:
        print(f"Simple preview generation failed: {e}")
        return None


def _get_static_preview_image(template_id: str) -> Optional[bytes]:
    """
    Load static preview image if it exists
    """
    try:
        from pathlib import Path
        static_path = Path(__file__).parent.parent / "static" / "template-previews" / f"{template_id}.png"
        
        if static_path.exists():
            return static_path.read_bytes()
        return None
    except Exception as e:
        print(f"Failed to load static preview for {template_id}: {e}")
        return None


def _generate_placeholder_image(template_id: str) -> bytes:
    """
    Generate a simple colored placeholder image
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Template colors
        colors = {
            "modern": "#2f6fed",
            "classic": "#000000", 
            "creative": "#667eea",
            "technical": "#0066cc",
            "executive": "#8B0000"
        }
        
        color = colors.get(template_id, "#2f6fed")
        
        # Create simple colored rectangle
        width, height = 200, 280
        img = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(img)
        
        # Add template name
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw template name in white
        text = template_id.title()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill="white", font=font)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
        
    except Exception as e:
        print(f"Placeholder generation failed: {e}")
        # Return minimal 1x1 pixel image as absolute fallback
        try:
            from PIL import Image
            import io
            img = Image.new('RGB', (1, 1), "#cccccc")
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
        except:
            return b''


@router.get("/preview/{template_id}", response_model=None)
async def get_template_preview(
    template_id: str,
    format: str = Query("html", description="Response format: html, png, json"),
    use_sample: bool = Query(True, description="Use sample data for preview"),
    cache: bool = Query(True, description="Use cached preview if available")
):
    """
    Generate template preview with sample or custom data
    
    Args:
        template_id: Template identifier (e.g., 'modern', 'classic', 'creative')
        format: Response format - 'html' for HTML preview, 'png' for screenshot, 'json' for metadata
        use_sample: Whether to use sample data (True) or empty template (False)
        cache: Whether to use cached version if available
    
    Returns:
        HTML content, PNG image, or JSON metadata based on format parameter
    
    Raises:
        HTTPException: If template not found or generation fails
    """
    
    # Force to executive_compact only
    template_id = "executive_compact"
    # Validate template exists
    try:
        TemplateRegistry.validate(template_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Check cache if enabled
    cache_key = _get_cache_key(template_id, format, not use_sample)
    if cache and cache_key in _preview_cache and _is_cache_valid(_preview_cache[cache_key]):
        cached_data = _preview_cache[cache_key]
        
        if format == "html":
            return HTMLResponse(content=cached_data["content"])
        elif format == "png":
            if "screenshot" in cached_data:
                return Response(
                    content=base64.b64decode(cached_data["screenshot"]),
                    media_type="image/png"
                )
        elif format == "json":
            return JSONResponse(content=cached_data["content"])
    
    try:
        # Generate resume data
        if use_sample:
            resume_data = generate_sample_resume_data()
        else:
            # Use minimal data for empty template preview
            resume_data = {
                "name": "Your Name Here",
                "headline": "Your Professional Title",
                "contact": {
                    "email": "your.email@example.com",
                    "phone": "(555) 000-0000",
                    "location": "Your City, State",
                    "links": []
                },
                "summary": "Your professional summary will appear here...",
                "experience": [],
                "education": [],
                "skills": [],
                "projects": []
            }
        
        # Generate HTML preview
        html_content = TemplateEngine.render_preview(
            template_id="executive_compact",
            resume_json=resume_data,
        )
        
        # Handle different response formats
        if format == "html":
            # Cache HTML content
            if cache:
                _preview_cache[cache_key] = {
                    "content": html_content,
                    "timestamp": datetime.now().isoformat()
                }
            
            return HTMLResponse(content=html_content)
        
        elif format == "png":
            # Try static image first, then Playwright, then simple generation
            static_image = _get_static_preview_image(template_id)
            if static_image:
                return Response(content=static_image, media_type="image/png")
            
            # Try Playwright
            screenshot_bytes = await _generate_screenshot(html_content)
            
            if screenshot_bytes is None:
                # Fallback: Generate simple template preview image
                screenshot_bytes = _generate_simple_preview_image(template_id)
            
            if screenshot_bytes is None:
                # Final fallback: Return a placeholder image
                screenshot_bytes = _generate_placeholder_image(template_id)
            
            # Cache screenshot
            if cache and screenshot_bytes:
                _preview_cache[cache_key] = {
                    "screenshot": base64.b64encode(screenshot_bytes).decode(),
                    "timestamp": datetime.now().isoformat()
                }
            
            return Response(content=screenshot_bytes, media_type="image/png")
        
        elif format == "json":
            # Return template info with preview data
            template_meta = TemplateRegistry.get_meta(template_id)
            response_data = {
                "template": template_meta,
                "preview_data": resume_data,
                "html_length": len(html_content),
                "generated_at": datetime.now().isoformat()
            }
            
            # Cache JSON response
            if cache:
                _preview_cache[cache_key] = {
                    "content": response_data,
                    "timestamp": datetime.now().isoformat()
                }
            
            return JSONResponse(content=response_data)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
            
    except Exception as e:
        print(f"Preview generation error for template '{template_id}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate template preview: {str(e)}"
        )


@router.post("/preview/{template_id}", response_model=None)
async def create_custom_preview(
    template_id: str,
    request: PreviewRequest
):
    """
    Generate template preview with custom resume data
    
    Args:
        template_id: Template identifier
        request: Custom preview request with resume data and format
    
    Returns:
        Preview in requested format
    """
    
    # Validate template exists
    try:
        template_id = "executive_compact"
        TemplateRegistry.validate(template_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    try:
        # Use provided data or fall back to sample data
        resume_data = request.resume_data or generate_sample_resume_data()
        
        # Generate HTML preview
        html_content = TemplateEngine.render_preview(
            template_id="executive_compact",
            resume_json=resume_data,
        )
        
        # Return in requested format
        if request.format == "html":
            return HTMLResponse(content=html_content)
        elif request.format == "png":
            screenshot_bytes = await _generate_screenshot(html_content)
            if screenshot_bytes is None:
                raise HTTPException(status_code=503, detail="Screenshot generation not available")
            return Response(content=screenshot_bytes, media_type="image/png")
        elif request.format == "json":
            return JSONResponse(content={
                "html": html_content,
                "resume_data": resume_data,
                "generated_at": datetime.now().isoformat()
            })
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate custom preview: {str(e)}")


@router.get("/metadata")
async def get_all_templates_metadata(
    include_previews: bool = Query(False, description="Include preview URLs in response"),
    refresh_cache: bool = Query(False, description="Force refresh metadata cache")
) -> JSONResponse:
    """
    Get metadata for all available templates
    
    Args:
        include_previews: Whether to include preview URLs
        refresh_cache: Whether to force refresh the cache
    
    Returns:
        JSON with all template metadata
    """
    
    global _metadata_cache
    
    # Use cache if available and not refreshing
    if not refresh_cache and _metadata_cache is not None:
        return JSONResponse(content=_metadata_cache)
    
    try:
        templates = []
        template_ids = ["executive_compact"]
        
        for template_id in template_ids:
            try:
                # Get base metadata from meta.json
                meta = TemplateRegistry.get_meta(template_id)
                
                # Enhance with additional information
                template_info = {
                    "id": template_id,
                    "name": meta.get("name", template_id.title()),
                    "description": meta.get("description", f"Professional {template_id} template"),
                    "category": meta.get("category", "professional"),
                    "supports": meta.get("supports", ["html", "pdf"]),
                    "features": meta.get("features", []),
                    "created_at": meta.get("created_at"),
                    "updated_at": meta.get("updated_at"),
                    "version": meta.get("version", "1.0.0")
                }
                
                # Add preview URLs if requested
                if include_previews:
                    base_url = "/api/templates/preview"
                    template_info.update({
                        "preview_url": f"{base_url}/{template_id}?format=html",
                        "screenshot_url": f"{base_url}/{template_id}?format=png",
                        "json_url": f"{base_url}/{template_id}?format=json"
                    })
                
                templates.append(template_info)
                
            except Exception as e:
                print(f"Error loading metadata for template '{template_id}': {e}")
                # Include basic info even if meta.json is malformed
                templates.append({
                    "id": template_id,
                    "name": template_id.title(),
                    "description": f"Template {template_id}",
                    "category": "unknown",
                    "supports": ["html"],
                    "features": [],
                    "error": str(e)
                })
        
        response_data = {
            "templates": templates,
            "total_count": len(templates),
            "available_formats": ["html", "pdf", "png"],
            "generated_at": datetime.now().isoformat()
        }
        
        # Cache the response
        _metadata_cache = response_data
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load template metadata: {str(e)}")


@router.get("/metadata/{template_id}")
async def get_template_metadata(template_id: str) -> JSONResponse:
    """
    Get detailed metadata for a specific template
    
    Args:
        template_id: Template identifier
    
    Returns:
        JSON with template metadata and file information
    """
    
    # Validate template exists
    try:
        TemplateRegistry.validate(template_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    try:
        # Get base metadata
        meta = TemplateRegistry.get_meta(template_id)
        template_dir = TemplateRegistry.get_dir(template_id)
        
        # Get file information
        files_info = {}
        for required_file in TemplateRegistry.REQUIRED_FILES:
            file_path = template_dir / required_file
            if file_path.exists():
                stat = file_path.stat()
                files_info[required_file] = {
                    "exists": True,
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                files_info[required_file] = {"exists": False}
        
        # Build comprehensive metadata
        template_info = {
            "id": template_id,
            "name": meta.get("name", template_id.title()),
            "description": meta.get("description", f"Professional {template_id} template"),
            "category": meta.get("category", "professional"),
            "supports": meta.get("supports", ["html", "pdf"]),
            "features": meta.get("features", []),
            "version": meta.get("version", "1.0.0"),
            "author": meta.get("author"),
            "created_at": meta.get("created_at"),
            "updated_at": meta.get("updated_at"),
            "tags": meta.get("tags", []),
            "color_scheme": meta.get("color_scheme"),
            "layout_type": meta.get("layout_type"),
            "files": files_info,
            "preview_urls": {
                "html": f"/api/templates/preview/{template_id}?format=html",
                "png": f"/api/templates/preview/{template_id}?format=png",
                "json": f"/api/templates/preview/{template_id}?format=json"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return JSONResponse(content=template_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load template metadata: {str(e)}")


@router.delete("/cache")
async def clear_preview_cache() -> JSONResponse:
    """
    Clear the preview cache
    
    Returns:
        JSON confirmation of cache clearing
    """
    
    global _preview_cache, _metadata_cache
    
    cache_size = len(_preview_cache)
    _preview_cache.clear()
    _metadata_cache = None
    
    return JSONResponse(content={
        "message": "Preview cache cleared successfully",
        "cleared_entries": cache_size,
        "cleared_at": datetime.now().isoformat()
    })


@router.get("/cache/stats")
async def get_cache_stats() -> JSONResponse:
    """
    Get cache statistics
    
    Returns:
        JSON with cache statistics
    """
    
    valid_entries = 0
    expired_entries = 0
    
    for entry in _preview_cache.values():
        if _is_cache_valid(entry):
            valid_entries += 1
        else:
            expired_entries += 1
    
    return JSONResponse(content={
        "total_entries": len(_preview_cache),
        "valid_entries": valid_entries,
        "expired_entries": expired_entries,
        "metadata_cached": _metadata_cache is not None,
        "cache_ttl_hours": _cache_ttl.total_seconds() / 3600,
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "checked_at": datetime.now().isoformat()
    })
