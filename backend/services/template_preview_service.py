"""
Template Preview Service

A comprehensive service for generating, caching, and managing template previews.
Handles screenshot generation, metadata collection, and fallback mechanisms.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from io import BytesIO
import base64

from pydantic import BaseModel

from services.template_engine import TemplateEngine
from services.template_registry import TemplateRegistry
from models.resume_schema import Resume

# Optional dependencies
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class TemplateMetadata(BaseModel):
    """Enhanced template metadata model"""
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    features: List[str]
    supports: List[str]
    color_scheme: Optional[str] = None
    layout_type: Optional[str] = None
    industry_focus: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    version: str = "1.0.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    author: Optional[str] = None
    preview_generated_at: Optional[str] = None
    screenshot_available: bool = False
    html_preview_available: bool = True


class PreviewResult(BaseModel):
    """Result of preview generation"""
    template_id: str
    format: str  # 'png', 'html', 'json'
    success: bool
    data: Optional[Union[str, bytes, Dict[str, Any]]] = None
    error_message: Optional[str] = None
    fallback_used: bool = False
    generation_time_ms: Optional[int] = None
    cache_hit: bool = False


class TemplatePreviewService:
    """
    Comprehensive template preview service with screenshot generation,
    caching, metadata management, and fallback mechanisms.
    """
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        memory_cache_size: int = 100,
        disk_cache_ttl_hours: int = 24,
        screenshot_timeout: int = 30000,
        viewport_width: int = 1200,
        viewport_height: int = 1600
    ):
        """
        Initialize the template preview service
        
        Args:
            cache_dir: Directory for disk cache (defaults to ./cache/previews)
            memory_cache_size: Maximum number of items in memory cache
            disk_cache_ttl_hours: Time-to-live for disk cache in hours
            screenshot_timeout: Playwright timeout in milliseconds
            viewport_width: Screenshot viewport width
            viewport_height: Screenshot viewport height
        """
        self.cache_dir = cache_dir or Path("cache/previews")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache settings
        self.memory_cache_size = memory_cache_size
        self.disk_cache_ttl = timedelta(hours=disk_cache_ttl_hours)
        
        # Screenshot settings
        self.screenshot_timeout = screenshot_timeout
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        
        # In-memory caches
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._metadata_cache: Dict[str, TemplateMetadata] = {}
        
        # Browser instance for reuse
        self._browser: Optional[Browser] = None
        self._browser_lock = asyncio.Lock()
        
        logger.info(f"TemplatePreviewService initialized with cache_dir: {self.cache_dir}")
        logger.info(f"Playwright available: {PLAYWRIGHT_AVAILABLE}")
        logger.info(f"PIL available: {PIL_AVAILABLE}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_browser()
    
    async def _ensure_browser(self) -> Optional[Browser]:
        """Ensure browser is available for screenshot generation"""
        if not PLAYWRIGHT_AVAILABLE:
            return None
        
        async with self._browser_lock:
            if self._browser is None:
                try:
                    playwright = await async_playwright().start()
                    self._browser = await playwright.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-accelerated-2d-canvas',
                            '--disable-gpu'
                        ]
                    )
                    logger.info("Browser launched successfully")
                except Exception as e:
                    logger.error(f"Failed to launch browser: {e}")
                    self._browser = None
            
            return self._browser
    
    async def _close_browser(self):
        """Close browser instance"""
        async with self._browser_lock:
            if self._browser:
                try:
                    await self._browser.close()
                    logger.info("Browser closed successfully")
                except Exception as e:
                    logger.error(f"Error closing browser: {e}")
                finally:
                    self._browser = None
    
    def _get_cache_key(self, template_id: str, format_type: str, sample_data_hash: str = "") -> str:
        """Generate cache key for preview"""
        base_key = f"{template_id}:{format_type}:{sample_data_hash}"
        return hashlib.md5(base_key.encode()).hexdigest()
    
    def _get_disk_cache_path(self, cache_key: str, format_type: str) -> Path:
        """Get disk cache file path"""
        extension = "png" if format_type == "png" else "html"
        return self.cache_dir / f"{cache_key}.{extension}"
    
    def _is_disk_cache_valid(self, cache_path: Path) -> bool:
        """Check if disk cache file is still valid"""
        if not cache_path.exists():
            return False
        
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - file_time < self.disk_cache_ttl
    
    def _cleanup_memory_cache(self):
        """Clean up memory cache if it exceeds size limit"""
        if len(self._memory_cache) > self.memory_cache_size:
            # Remove oldest entries
            sorted_items = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1].get('timestamp', datetime.min.isoformat())
            )
            items_to_remove = len(sorted_items) - self.memory_cache_size + 10  # Remove extra to avoid frequent cleanup
            
            for i in range(items_to_remove):
                key, _ = sorted_items[i]
                del self._memory_cache[key]
    
    def generate_template_specific_sample_data(self, template_id: str) -> Dict[str, Any]:
        """
        Generate sample data tailored to showcase specific template features
        """
        base_data = {
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
            "summary": "Innovative Senior Software Engineer with 8+ years of experience building scalable web applications and leading high-performing development teams. Expertise in full-stack development, cloud architecture, and agile methodologies.",
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
                        "Mentored 5 junior developers and established code review best practices"
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
                        "Achieved 99.9% uptime through robust error handling and monitoring"
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
                {"name": "JavaScript"}, {"name": "TypeScript"}, {"name": "Python"},
                {"name": "React"}, {"name": "Node.js"}, {"name": "AWS"},
                {"name": "Docker"}, {"name": "Kubernetes"}, {"name": "PostgreSQL"}
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Full-stack e-commerce solution with real-time inventory management",
                    "bullets": [
                        "Built with React, Node.js, PostgreSQL, Redis, and Stripe",
                        "Implemented real-time inventory tracking and management"
                    ]
                }
            ]
        }
        
        # Customize data based on template
        if template_id == "executive":
            base_data.update({
                "name": "Robert Sterling",
                "headline": "Chief Technology Officer & VP of Engineering",
                "summary": "Accomplished technology executive with 15+ years of experience leading large-scale digital transformations and building world-class engineering teams. Proven track record of driving innovation and delivering results in Fortune 500 companies.",
                "experience": [
                    {
                        "title": "Chief Technology Officer",
                        "company": "Global Finance Corp",
                        "location": "New York, NY",
                        "start": "2020-01",
                        "end": None,
                        "bullets": [
                            "Led digital transformation initiative resulting in $50M annual cost savings",
                            "Built and managed engineering teams of 200+ across 5 countries",
                            "Architected cloud-native platform serving 10M+ customers globally"
                        ]
                    }
                ]
            })
        
        elif template_id == "creative":
            base_data.update({
                "name": "Maya Chen",
                "headline": "Creative Director & UX Design Lead",
                "summary": "Award-winning creative professional with expertise in brand design, user experience, and digital storytelling. Passionate about creating meaningful connections between brands and users through innovative design solutions.",
                "skills": [
                    {"name": "Figma"}, {"name": "Adobe Creative Suite"}, {"name": "Sketch"},
                    {"name": "Prototyping"}, {"name": "User Research"}, {"name": "Brand Design"},
                    {"name": "Typography"}, {"name": "Color Theory"}, {"name": "Design Systems"}
                ],
                "projects": [
                    {
                        "name": "Brand Redesign Campaign",
                        "description": "Complete visual identity overhaul for Fortune 500 company",
                        "bullets": [
                            "Led cross-functional team of 12 designers and developers",
                            "Increased brand recognition by 65% and user engagement by 40%"
                        ]
                    }
                ]
            })
        
        elif template_id == "technical":
            base_data.update({
                "skills": [
                    {"name": "Python"}, {"name": "Go"}, {"name": "Rust"}, {"name": "C++"},
                    {"name": "Kubernetes"}, {"name": "Docker"}, {"name": "Terraform"},
                    {"name": "AWS"}, {"name": "GCP"}, {"name": "Linux"}, {"name": "Git"},
                    {"name": "CI/CD"}, {"name": "Monitoring"}, {"name": "Security"}
                ],
                "projects": [
                    {
                        "name": "Distributed Systems Architecture",
                        "description": "High-performance microservices platform with auto-scaling",
                        "bullets": [
                            "Designed system handling 1B+ requests per day with 99.99% uptime",
                            "Implemented advanced caching and load balancing strategies"
                        ]
                    },
                    {
                        "name": "ML Pipeline Optimization",
                        "description": "Automated machine learning pipeline for real-time predictions",
                        "bullets": [
                            "Reduced model training time by 80% using distributed computing",
                            "Achieved sub-100ms inference latency for production models"
                        ]
                    }
                ]
            })
        
        elif template_id == "classic":
            # Conservative, traditional formatting
            base_data.update({
                "name": "James Richardson",
                "headline": "Senior Financial Analyst",
                "summary": "Experienced financial professional with demonstrated expertise in corporate finance, investment analysis, and strategic planning. Strong analytical skills with a track record of supporting executive decision-making in complex business environments.",
                "experience": [
                    {
                        "title": "Senior Financial Analyst",
                        "company": "Goldman Sachs",
                        "location": "New York, NY",
                        "start": "2019-06",
                        "end": None,
                        "bullets": [
                            "Performed comprehensive financial analysis for M&A transactions totaling $2.5B",
                            "Developed sophisticated financial models for valuation and risk assessment",
                            "Collaborated with senior management on strategic planning initiatives"
                        ]
                    }
                ]
            })
        
        return base_data
    
    async def generate_screenshot(
        self, 
        html_content: str, 
        template_id: str,
        retries: int = 2
    ) -> Optional[bytes]:
        """
        Generate PNG screenshot from HTML content using Playwright
        
        Args:
            html_content: HTML content to screenshot
            template_id: Template identifier for logging
            retries: Number of retry attempts
            
        Returns:
            PNG screenshot bytes or None if failed
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available for screenshot generation")
            return None
        
        browser = await self._ensure_browser()
        if not browser:
            logger.error("Failed to initialize browser")
            return None
        
        for attempt in range(retries + 1):
            try:
                page = await browser.new_page()
                
                # Set viewport for consistent screenshots
                await page.set_viewport_size({
                    "width": self.viewport_width,
                    "height": self.viewport_height
                })
                
                # Load HTML content with timeout
                await page.set_content(
                    html_content,
                    wait_until="networkidle",
                    timeout=self.screenshot_timeout
                )
                
                # Wait a bit more for any CSS animations or fonts to load
                await asyncio.sleep(1)
                
                # Take screenshot with specific settings
                screenshot_bytes = await page.screenshot(
                    type="png",
                    full_page=True,
                    clip={
                        "x": 0,
                        "y": 0,
                        "width": self.viewport_width,
                        "height": min(self.viewport_height, 2000)  # Limit height for performance
                    },
                    timeout=self.screenshot_timeout
                )
                
                await page.close()
                logger.info(f"Screenshot generated successfully for template '{template_id}' (attempt {attempt + 1})")
                return screenshot_bytes
                
            except Exception as e:
                logger.error(f"Screenshot attempt {attempt + 1} failed for template '{template_id}': {e}")
                try:
                    await page.close()
                except:
                    pass
                
                if attempt < retries:
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    logger.error(f"All screenshot attempts failed for template '{template_id}'")
                    return None
        
        return None
    
    def generate_fallback_image(self, template_id: str, width: int = 800, height: int = 1000) -> Optional[bytes]:
        """
        Generate a fallback preview image when screenshot fails
        
        Args:
            template_id: Template identifier
            width: Image width
            height: Image height
            
        Returns:
            PNG image bytes or None if PIL not available
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            # Create image with template-specific colors
            color_schemes = {
                "modern": ("#667eea", "#764ba2"),
                "classic": ("#000000", "#333333"),
                "creative": ("#f093fb", "#f5576c"),
                "executive": ("#1f4e79", "#2d5aa0"),
                "technical": ("#2c3e50", "#34495e")
            }
            
            primary_color, secondary_color = color_schemes.get(template_id, ("#667eea", "#764ba2"))
            
            # Create gradient background
            image = Image.new("RGB", (width, height), primary_color)
            draw = ImageDraw.Draw(image)
            
            # Add gradient effect (simplified)
            for i in range(height // 3):
                alpha = i / (height // 3)
                color = self._blend_colors(primary_color, secondary_color, alpha)
                draw.rectangle([0, i, width, i + 1], fill=color)
            
            # Add template name
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            template_name = template_id.title() + " Template"
            bbox = draw.textbbox((0, 0), template_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            draw.text(
                ((width - text_width) // 2, (height - text_height) // 2),
                template_name,
                fill="white",
                font=font
            )
            
            # Add "Preview Not Available" text
            try:
                small_font = ImageFont.truetype("arial.ttf", 24)
            except:
                small_font = ImageFont.load_default()
            
            subtitle = "Preview Not Available"
            bbox = draw.textbbox((0, 0), subtitle, font=small_font)
            text_width = bbox[2] - bbox[0]
            
            draw.text(
                ((width - text_width) // 2, (height // 2) + 60),
                subtitle,
                fill="white",
                font=small_font
            )
            
            # Convert to bytes
            buffer = BytesIO()
            image.save(buffer, format="PNG", quality=95)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to generate fallback image: {e}")
            return None
    
    def _blend_colors(self, color1: str, color2: str, alpha: float) -> str:
        """Blend two hex colors with alpha"""
        try:
            # Convert hex to RGB
            c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
            c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
            
            # Blend
            blended = tuple(int(c1[i] * (1 - alpha) + c2[i] * alpha) for i in range(3))
            
            # Convert back to hex
            return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"
        except:
            return color1
    
    async def get_template_metadata(self, template_id: str, refresh: bool = False) -> Optional[TemplateMetadata]:
        """
        Get comprehensive metadata for a template
        
        Args:
            template_id: Template identifier
            refresh: Whether to refresh cached metadata
            
        Returns:
            Template metadata or None if not found
        """
        # Check cache first
        if not refresh and template_id in self._metadata_cache:
            return self._metadata_cache[template_id]
        
        try:
            # Validate template exists
            TemplateRegistry.validate(template_id)
            
            # Get base metadata from meta.json
            try:
                base_meta = TemplateRegistry.get_meta(template_id)
            except FileNotFoundError:
                # Create default metadata if meta.json is missing
                base_meta = {}
            
            # Enhanced metadata with intelligent defaults
            metadata_map = {
                "classic": {
                    "name": "Classic Professional",
                    "description": "Traditional, conservative resume template perfect for law, finance, and corporate environments",
                    "category": "professional",
                    "tags": ["traditional", "conservative", "formal", "ats-friendly"],
                    "features": ["Clean typography", "Traditional layout", "ATS-optimized", "Print-friendly"],
                    "color_scheme": "monochrome",
                    "layout_type": "single-column",
                    "industry_focus": ["finance", "law", "consulting", "government"],
                    "difficulty_level": "beginner"
                },
                "modern": {
                    "name": "Modern Professional",
                    "description": "Contemporary design with clean lines and modern typography, suitable for tech and creative industries",
                    "category": "modern",
                    "tags": ["modern", "clean", "minimalist", "tech-friendly"],
                    "features": ["Modern typography", "Gradient accents", "Responsive design", "Icon support"],
                    "color_scheme": "blue-gradient",
                    "layout_type": "single-column",
                    "industry_focus": ["technology", "startups", "marketing", "design"],
                    "difficulty_level": "intermediate"
                },
                "creative": {
                    "name": "Creative Professional",
                    "description": "Vibrant and creative design with colorful elements, perfect for creative professionals and designers",
                    "category": "creative",
                    "tags": ["creative", "colorful", "vibrant", "design-focused"],
                    "features": ["Colorful gradients", "Sidebar layout", "Visual elements", "Modern cards"],
                    "color_scheme": "multi-color",
                    "layout_type": "sidebar",
                    "industry_focus": ["design", "marketing", "media", "arts"],
                    "difficulty_level": "advanced"
                },
                "executive": {
                    "name": "Executive Professional",
                    "description": "Sophisticated template designed for senior executives and leadership positions",
                    "category": "executive",
                    "tags": ["executive", "sophisticated", "leadership", "premium"],
                    "features": ["Premium typography", "Executive styling", "Leadership focus", "Results-oriented"],
                    "color_scheme": "navy-blue",
                    "layout_type": "single-column",
                    "industry_focus": ["executive", "management", "consulting", "finance"],
                    "difficulty_level": "expert"
                },
                "technical": {
                    "name": "Technical Professional",
                    "description": "Technical-focused template optimized for software engineers and technical professionals",
                    "category": "technical",
                    "tags": ["technical", "engineering", "skills-focused", "github-ready"],
                    "features": ["Skills highlighting", "Project showcase", "Technical formatting", "Code-friendly"],
                    "color_scheme": "tech-blue",
                    "layout_type": "single-column",
                    "industry_focus": ["software", "engineering", "data-science", "devops"],
                    "difficulty_level": "intermediate"
                }
            }
            
            # Get template-specific defaults
            template_defaults = metadata_map.get(template_id, {
                "name": template_id.title(),
                "description": f"Professional {template_id} template",
                "category": "professional",
                "tags": [template_id],
                "features": ["Professional design"],
                "color_scheme": "default",
                "layout_type": "single-column",
                "industry_focus": ["general"],
                "difficulty_level": "intermediate"
            })
            
            # Merge with base metadata
            metadata = TemplateMetadata(
                id=template_id,
                name=base_meta.get("name", template_defaults["name"]),
                description=base_meta.get("description", template_defaults["description"]),
                category=base_meta.get("category", template_defaults["category"]),
                tags=base_meta.get("tags", template_defaults["tags"]),
                features=base_meta.get("features", template_defaults["features"]),
                supports=base_meta.get("supports", ["html", "pdf"]),
                color_scheme=base_meta.get("color_scheme", template_defaults["color_scheme"]),
                layout_type=base_meta.get("layout_type", template_defaults["layout_type"]),
                industry_focus=base_meta.get("industry_focus", template_defaults["industry_focus"]),
                difficulty_level=base_meta.get("difficulty_level", template_defaults["difficulty_level"]),
                version=base_meta.get("version", "1.0.0"),
                created_at=base_meta.get("created_at"),
                updated_at=base_meta.get("updated_at"),
                author=base_meta.get("author"),
                screenshot_available=PLAYWRIGHT_AVAILABLE,
                html_preview_available=True
            )
            
            # Cache metadata
            self._metadata_cache[template_id] = metadata
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for template '{template_id}': {e}")
            return None
    
    async def generate_preview(
        self,
        template_id: str,
        format_type: str = "png",
        use_cache: bool = True,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> PreviewResult:
        """
        Generate template preview in specified format
        
        Args:
            template_id: Template identifier
            format_type: Output format ('png', 'html', 'json')
            use_cache: Whether to use cached results
            custom_data: Custom resume data (uses template-specific sample if None)
            
        Returns:
            PreviewResult with generated preview or error information
        """
        start_time = datetime.now()
        
        try:
            # Validate template
            TemplateRegistry.validate(template_id)
            
            # Generate sample data
            if custom_data:
                resume_data = custom_data
                sample_data_hash = hashlib.md5(json.dumps(custom_data, sort_keys=True).encode()).hexdigest()
            else:
                resume_data = self.generate_template_specific_sample_data(template_id)
                sample_data_hash = "default"
            
            # Check caches
            cache_key = self._get_cache_key(template_id, format_type, sample_data_hash)
            
            # Check memory cache
            if use_cache and cache_key in self._memory_cache:
                cached_data = self._memory_cache[cache_key]
                generation_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return PreviewResult(
                    template_id=template_id,
                    format=format_type,
                    success=True,
                    data=cached_data.get("data"),
                    cache_hit=True,
                    generation_time_ms=int(generation_time)
                )
            
            # Check disk cache
            if use_cache and format_type in ["png", "html"]:
                disk_cache_path = self._get_disk_cache_path(cache_key, format_type)
                if self._is_disk_cache_valid(disk_cache_path):
                    try:
                        if format_type == "png":
                            data = disk_cache_path.read_bytes()
                        else:
                            data = disk_cache_path.read_text(encoding="utf-8")
                        
                        # Cache in memory
                        self._memory_cache[cache_key] = {
                            "data": data,
                            "timestamp": datetime.now().isoformat()
                        }
                        self._cleanup_memory_cache()
                        
                        generation_time = (datetime.now() - start_time).total_seconds() * 1000
                        
                        return PreviewResult(
                            template_id=template_id,
                            format=format_type,
                            success=True,
                            data=data,
                            cache_hit=True,
                            generation_time_ms=int(generation_time)
                        )
                    except Exception as e:
                        logger.warning(f"Failed to read disk cache: {e}")
            
            # Generate new preview
            if format_type == "html":
                # Generate HTML preview
                html_content = TemplateEngine.render_preview(
                    template_id=template_id,
                    resume_json=resume_data
                )
                
                # Cache results
                if use_cache:
                    # Memory cache
                    self._memory_cache[cache_key] = {
                        "data": html_content,
                        "timestamp": datetime.now().isoformat()
                    }
                    self._cleanup_memory_cache()
                    
                    # Disk cache
                    try:
                        disk_cache_path = self._get_disk_cache_path(cache_key, format_type)
                        disk_cache_path.write_text(html_content, encoding="utf-8")
                    except Exception as e:
                        logger.warning(f"Failed to write HTML to disk cache: {e}")
                
                generation_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return PreviewResult(
                    template_id=template_id,
                    format=format_type,
                    success=True,
                    data=html_content,
                    generation_time_ms=int(generation_time)
                )
            
            elif format_type == "png":
                # Generate HTML first
                html_content = TemplateEngine.render_preview(
                    template_id=template_id,
                    resume_json=resume_data
                )
                
                # Try to generate screenshot
                screenshot_bytes = await self.generate_screenshot(html_content, template_id)
                fallback_used = False
                
                # Use fallback if screenshot failed
                if screenshot_bytes is None:
                    screenshot_bytes = self.generate_fallback_image(template_id)
                    fallback_used = True
                    
                    if screenshot_bytes is None:
                        generation_time = (datetime.now() - start_time).total_seconds() * 1000
                        return PreviewResult(
                            template_id=template_id,
                            format=format_type,
                            success=False,
                            error_message="Screenshot generation failed and fallback unavailable",
                            generation_time_ms=int(generation_time)
                        )
                
                # Cache results
                if use_cache and screenshot_bytes:
                    # Memory cache
                    self._memory_cache[cache_key] = {
                        "data": screenshot_bytes,
                        "timestamp": datetime.now().isoformat()
                    }
                    self._cleanup_memory_cache()
                    
                    # Disk cache
                    try:
                        disk_cache_path = self._get_disk_cache_path(cache_key, format_type)
                        disk_cache_path.write_bytes(screenshot_bytes)
                    except Exception as e:
                        logger.warning(f"Failed to write PNG to disk cache: {e}")
                
                generation_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return PreviewResult(
                    template_id=template_id,
                    format=format_type,
                    success=True,
                    data=screenshot_bytes,
                    fallback_used=fallback_used,
                    generation_time_ms=int(generation_time)
                )
            
            elif format_type == "json":
                # Generate metadata response
                metadata = await self.get_template_metadata(template_id)
                html_content = TemplateEngine.render_preview(
                    template_id=template_id,
                    resume_json=resume_data
                )
                
                json_data = {
                    "template_id": template_id,
                    "metadata": metadata.dict() if metadata else None,
                    "sample_data": resume_data,
                    "html_preview": html_content,
                    "html_length": len(html_content),
                    "generated_at": datetime.now().isoformat(),
                    "playwright_available": PLAYWRIGHT_AVAILABLE,
                    "pil_available": PIL_AVAILABLE
                }
                
                generation_time = (datetime.now() - start_time).total_seconds() * 1000
                
                return PreviewResult(
                    template_id=template_id,
                    format=format_type,
                    success=True,
                    data=json_data,
                    generation_time_ms=int(generation_time)
                )
            
            else:
                generation_time = (datetime.now() - start_time).total_seconds() * 1000
                return PreviewResult(
                    template_id=template_id,
                    format=format_type,
                    success=False,
                    error_message=f"Unsupported format: {format_type}",
                    generation_time_ms=int(generation_time)
                )
        
        except FileNotFoundError as e:
            generation_time = (datetime.now() - start_time).total_seconds() * 1000
            return PreviewResult(
                template_id=template_id,
                format=format_type,
                success=False,
                error_message=f"Template not found: {str(e)}",
                generation_time_ms=int(generation_time)
            )
        
        except Exception as e:
            generation_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Preview generation failed for template '{template_id}': {e}")
            return PreviewResult(
                template_id=template_id,
                format=format_type,
                success=False,
                error_message=str(e),
                generation_time_ms=int(generation_time)
            )
    
    async def generate_all_previews(
        self,
        format_type: str = "png",
        use_cache: bool = True,
        max_concurrent: int = 3
    ) -> Dict[str, PreviewResult]:
        """
        Generate previews for all available templates
        
        Args:
            format_type: Output format for all previews
            use_cache: Whether to use cached results
            max_concurrent: Maximum concurrent generations
            
        Returns:
            Dictionary mapping template_id to PreviewResult
        """
        template_ids = TemplateRegistry.list_ids()
        
        # Filter out non-resume templates
        resume_templates = [tid for tid in template_ids if tid not in ["emails"]]
        
        # Semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(template_id: str) -> Tuple[str, PreviewResult]:
            async with semaphore:
                result = await self.generate_preview(template_id, format_type, use_cache)
                return template_id, result
        
        # Generate all previews concurrently
        tasks = [generate_with_semaphore(tid) for tid in resume_templates]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        preview_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Preview generation task failed: {result}")
                continue
            
            template_id, preview_result = result
            preview_results[template_id] = preview_result
        
        return preview_results
    
    async def get_all_metadata(self, refresh: bool = False) -> Dict[str, TemplateMetadata]:
        """
        Get metadata for all available templates
        
        Args:
            refresh: Whether to refresh cached metadata
            
        Returns:
            Dictionary mapping template_id to TemplateMetadata
        """
        template_ids = TemplateRegistry.list_ids()
        resume_templates = [tid for tid in template_ids if tid not in ["emails"]]
        
        metadata_results = {}
        for template_id in resume_templates:
            metadata = await self.get_template_metadata(template_id, refresh)
            if metadata:
                metadata_results[template_id] = metadata
        
        return metadata_results
    
    def clear_cache(self, memory: bool = True, disk: bool = False) -> Dict[str, int]:
        """
        Clear preview caches
        
        Args:
            memory: Whether to clear memory cache
            disk: Whether to clear disk cache
            
        Returns:
            Dictionary with cleared counts
        """
        cleared_counts = {"memory": 0, "disk": 0}
        
        if memory:
            cleared_counts["memory"] = len(self._memory_cache)
            self._memory_cache.clear()
            self._metadata_cache.clear()
        
        if disk:
            try:
                for cache_file in self.cache_dir.glob("*"):
                    if cache_file.is_file():
                        cache_file.unlink()
                        cleared_counts["disk"] += 1
            except Exception as e:
                logger.error(f"Failed to clear disk cache: {e}")
        
        return cleared_counts
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        disk_files = 0
        disk_size = 0
        
        try:
            for cache_file in self.cache_dir.glob("*"):
                if cache_file.is_file():
                    disk_files += 1
                    disk_size += cache_file.stat().st_size
        except Exception as e:
            logger.error(f"Failed to get disk cache stats: {e}")
        
        return {
            "memory_cache_size": len(self._memory_cache),
            "metadata_cache_size": len(self._metadata_cache),
            "disk_cache_files": disk_files,
            "disk_cache_size_bytes": disk_size,
            "cache_dir": str(self.cache_dir),
            "playwright_available": PLAYWRIGHT_AVAILABLE,
            "pil_available": PIL_AVAILABLE,
            "browser_initialized": self._browser is not None
        }
