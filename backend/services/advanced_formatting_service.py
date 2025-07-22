"""
Advanced Formatting Service - Pro-only PDF formatting with multiple layout options

This service provides:
- Multiple professional layout templates
- Custom font, color, and section arrangement capabilities
- Pro-only formatting templates and styles
- ATS compatibility validation
- Fallback to standard formatting for Free users and failures
- Integration with existing PDF generation endpoints
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging
import os
import tempfile
from io import BytesIO

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white, blue
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


class FormattingTemplate(Enum):
    """Available formatting templates"""
    STANDARD = "standard"           # Default template for Free users
    MODERN = "modern"              # Clean, modern design (Pro)
    EXECUTIVE = "executive"        # Professional executive style (Pro)
    CREATIVE = "creative"          # Creative design with colors (Pro)
    MINIMAL = "minimal"            # Minimalist design (Pro)
    ACADEMIC = "academic"          # Academic/research focused (Pro)
    TECHNICAL = "technical"        # Technical/engineering focused (Pro)


class ColorScheme(Enum):
    """Available color schemes"""
    CLASSIC_BLUE = "classic_blue"      # Professional blue
    MODERN_GRAY = "modern_gray"        # Modern gray tones
    EXECUTIVE_BLACK = "executive_black" # Black and white professional
    CREATIVE_TEAL = "creative_teal"    # Teal accent colors
    WARM_BROWN = "warm_brown"          # Warm brown tones
    TECH_GREEN = "tech_green"          # Technology green


class FontFamily(Enum):
    """Available font families"""
    HELVETICA = "helvetica"        # Clean, professional
    TIMES = "times"               # Traditional, academic
    CALIBRI = "calibri"           # Modern, readable
    ARIAL = "arial"               # Universal, ATS-friendly
    GARAMOND = "garamond"         # Elegant, executive


@dataclass
class FormattingOptions:
    """Configuration options for advanced formatting"""
    template: FormattingTemplate = FormattingTemplate.STANDARD
    color_scheme: ColorScheme = ColorScheme.CLASSIC_BLUE
    font_family: FontFamily = FontFamily.HELVETICA
    font_size: int = 10
    line_spacing: float = 1.2
    margin_size: float = 0.5  # inches
    section_spacing: float = 12  # points
    use_two_columns: bool = False
    include_border: bool = False
    header_style: str = "underline"  # "underline", "background", "bold"
    bullet_style: str = "circle"     # "circle", "square", "dash"
    page_size: str = "letter"        # "letter", "a4"
    
    # Custom overrides
    custom_colors: Optional[Dict[str, str]] = None
    custom_fonts: Optional[Dict[str, str]] = None
    section_order: Optional[List[str]] = None


class AdvancedFormattingService:
    """Service for creating advanced PDF formatting for Pro users"""
    
    def __init__(self):
        self.color_schemes = self._initialize_color_schemes()
        self.font_mappings = self._initialize_font_mappings()
        self.template_configs = self._initialize_template_configs()
    
    def _initialize_color_schemes(self) -> Dict[ColorScheme, Dict[str, HexColor]]:
        """Initialize color scheme definitions"""
        return {
            ColorScheme.CLASSIC_BLUE: {
                "primary": HexColor("#2c5aa0"),
                "secondary": HexColor("#4a7bc8"),
                "accent": HexColor("#1e3d72"),
                "text": HexColor("#333333"),
                "light": HexColor("#f8f9fa")
            },
            ColorScheme.MODERN_GRAY: {
                "primary": HexColor("#495057"),
                "secondary": HexColor("#6c757d"),
                "accent": HexColor("#343a40"),
                "text": HexColor("#212529"),
                "light": HexColor("#f8f9fa")
            },
            ColorScheme.EXECUTIVE_BLACK: {
                "primary": HexColor("#000000"),
                "secondary": HexColor("#333333"),
                "accent": HexColor("#666666"),
                "text": HexColor("#000000"),
                "light": HexColor("#ffffff")
            },
            ColorScheme.CREATIVE_TEAL: {
                "primary": HexColor("#20c997"),
                "secondary": HexColor("#17a2b8"),
                "accent": HexColor("#138496"),
                "text": HexColor("#212529"),
                "light": HexColor("#e9ecef")
            },
            ColorScheme.WARM_BROWN: {
                "primary": HexColor("#8b4513"),
                "secondary": HexColor("#a0522d"),
                "accent": HexColor("#654321"),
                "text": HexColor("#2f1b14"),
                "light": HexColor("#f5f5dc")
            },
            ColorScheme.TECH_GREEN: {
                "primary": HexColor("#28a745"),
                "secondary": HexColor("#20c997"),
                "accent": HexColor("#155724"),
                "text": HexColor("#212529"),
                "light": HexColor("#d4edda")
            }
        }
    
    def _initialize_font_mappings(self) -> Dict[FontFamily, Dict[str, str]]:
        """Initialize font family mappings"""
        return {
            FontFamily.HELVETICA: {
                "regular": "Helvetica",
                "bold": "Helvetica-Bold",
                "italic": "Helvetica-Oblique",
                "bold_italic": "Helvetica-BoldOblique"
            },
            FontFamily.TIMES: {
                "regular": "Times-Roman",
                "bold": "Times-Bold",
                "italic": "Times-Italic",
                "bold_italic": "Times-BoldItalic"
            },
            FontFamily.CALIBRI: {
                "regular": "Helvetica",  # Fallback to Helvetica
                "bold": "Helvetica-Bold",
                "italic": "Helvetica-Oblique",
                "bold_italic": "Helvetica-BoldOblique"
            },
            FontFamily.ARIAL: {
                "regular": "Helvetica",  # Fallback to Helvetica
                "bold": "Helvetica-Bold",
                "italic": "Helvetica-Oblique",
                "bold_italic": "Helvetica-BoldOblique"
            },
            FontFamily.GARAMOND: {
                "regular": "Times-Roman",  # Fallback to Times
                "bold": "Times-Bold",
                "italic": "Times-Italic",
                "bold_italic": "Times-BoldItalic"
            }
        }
    
    def _initialize_template_configs(self) -> Dict[FormattingTemplate, Dict]:
        """Initialize template-specific configurations"""
        return {
            FormattingTemplate.STANDARD: {
                "name_font_size": 16,
                "section_font_size": 12,
                "body_font_size": 10,
                "use_borders": False,
                "section_style": "underline",
                "spacing_multiplier": 1.0
            },
            FormattingTemplate.MODERN: {
                "name_font_size": 18,
                "section_font_size": 13,
                "body_font_size": 10,
                "use_borders": True,
                "section_style": "background",
                "spacing_multiplier": 1.1
            },
            FormattingTemplate.EXECUTIVE: {
                "name_font_size": 20,
                "section_font_size": 14,
                "body_font_size": 11,
                "use_borders": False,
                "section_style": "bold",
                "spacing_multiplier": 1.2
            },
            FormattingTemplate.CREATIVE: {
                "name_font_size": 22,
                "section_font_size": 14,
                "body_font_size": 10,
                "use_borders": True,
                "section_style": "background",
                "spacing_multiplier": 1.0
            },
            FormattingTemplate.MINIMAL: {
                "name_font_size": 16,
                "section_font_size": 11,
                "body_font_size": 9,
                "use_borders": False,
                "section_style": "bold",
                "spacing_multiplier": 0.9
            },
            FormattingTemplate.ACADEMIC: {
                "name_font_size": 18,
                "section_font_size": 12,
                "body_font_size": 11,
                "use_borders": False,
                "section_style": "underline",
                "spacing_multiplier": 1.3
            },
            FormattingTemplate.TECHNICAL: {
                "name_font_size": 16,
                "section_font_size": 12,
                "body_font_size": 10,
                "use_borders": True,
                "section_style": "background",
                "spacing_multiplier": 1.0
            }
        }
    
    def create_advanced_formatted_resume(
        self,
        resume_text: str,
        formatting_options: FormattingOptions,
        output_path: str,
        job_title: str = ""
    ) -> bool:
        """Create an advanced formatted resume PDF"""
        try:
            logger.info(f"Creating advanced formatted resume with template: {formatting_options.template.value}")
            
            # Validate ATS compatibility
            if not self._validate_ats_compatibility(formatting_options):
                logger.warning("Formatting options may not be ATS compatible, applying adjustments")
                formatting_options = self._adjust_for_ats_compatibility(formatting_options)
            
            # Parse resume content
            resume_data = self._parse_resume_content(resume_text)
            
            # Create PDF based on template
            success = self._create_pdf_with_template(
                resume_data, formatting_options, output_path, job_title
            )
            
            if success:
                logger.info(f"Successfully created advanced formatted resume: {output_path}")
            else:
                logger.error("Failed to create advanced formatted resume")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating advanced formatted resume: {e}")
            return False
    
    def create_standard_formatted_resume(
        self,
        resume_text: str,
        output_path: str,
        job_title: str = ""
    ) -> bool:
        """Create a standard formatted resume (fallback for Free users)"""
        try:
            logger.info("Creating standard formatted resume (fallback)")
            
            # Use standard formatting options
            standard_options = FormattingOptions(
                template=FormattingTemplate.STANDARD,
                color_scheme=ColorScheme.CLASSIC_BLUE,
                font_family=FontFamily.HELVETICA
            )
            
            return self.create_advanced_formatted_resume(
                resume_text, standard_options, output_path, job_title
            )
            
        except Exception as e:
            logger.error(f"Error creating standard formatted resume: {e}")
            return False
    
    def _validate_ats_compatibility(self, options: FormattingOptions) -> bool:
        """Validate that formatting options are ATS compatible"""
        # ATS compatibility checks
        ats_issues = []
        
        # Font size should be readable
        if options.font_size < 9 or options.font_size > 12:
            ats_issues.append("Font size should be between 9-12 points")
        
        # Avoid overly creative templates for ATS
        if options.template in [FormattingTemplate.CREATIVE]:
            ats_issues.append("Creative templates may not be ATS compatible")
        
        # Two-column layouts can be problematic for ATS
        if options.use_two_columns:
            ats_issues.append("Two-column layouts may not parse correctly in ATS")
        
        # Complex borders can interfere with parsing
        if options.include_border and options.template == FormattingTemplate.CREATIVE:
            ats_issues.append("Complex borders may interfere with ATS parsing")
        
        if ats_issues:
            logger.warning(f"ATS compatibility issues found: {ats_issues}")
            return False
        
        return True
    
    def _adjust_for_ats_compatibility(self, options: FormattingOptions) -> FormattingOptions:
        """Adjust formatting options for better ATS compatibility"""
        # Create a copy to avoid modifying the original
        adjusted = FormattingOptions(
            template=options.template,
            color_scheme=options.color_scheme,
            font_family=options.font_family,
            font_size=max(9, min(12, options.font_size)),  # Clamp font size
            line_spacing=options.line_spacing,
            margin_size=options.margin_size,
            section_spacing=options.section_spacing,
            use_two_columns=False,  # Disable two columns for ATS
            include_border=False if options.template == FormattingTemplate.CREATIVE else options.include_border,
            header_style=options.header_style,
            bullet_style=options.bullet_style,
            page_size=options.page_size,
            custom_colors=options.custom_colors,
            custom_fonts=options.custom_fonts,
            section_order=options.section_order
        )
        
        # Use more ATS-friendly template if needed
        if options.template == FormattingTemplate.CREATIVE:
            adjusted.template = FormattingTemplate.MODERN
        
        return adjusted
    
    def _parse_resume_content(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text into structured data"""
        lines = resume_text.split('\n')
        resume_data = {
            'name': '',
            'contact': [],
            'sections': []
        }
        
        current_section = None
        current_content = []
        name_detected = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # Detect name (first substantial line)
            if not name_detected and i < 5:
                if (not any(char in stripped.lower() for char in ['@', '.com', 'phone', 'email', '(', ')', 'linkedin', 'http']) and 
                    len(stripped) < 60 and len(stripped) > 5 and 
                    not stripped.isupper() and not stripped.startswith('•')):
                    resume_data['name'] = stripped
                    name_detected = True
                    continue
            
            # Detect contact info
            if (any(indicator in stripped.lower() for indicator in ['@', '.com', 'phone', '(', ')', 'email', 'linkedin', 'http']) or 
                re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', stripped)):
                resume_data['contact'].append(stripped)
                continue
            
            # Detect section headers
            if self._is_section_header(stripped):
                # Save previous section
                if current_section:
                    resume_data['sections'].append({
                        'title': current_section,
                        'content': current_content
                    })
                # Start new section
                current_section = stripped
                current_content = []
                continue
            
            # Add to current section
            current_content.append(stripped)
        
        # Add the last section
        if current_section:
            resume_data['sections'].append({
                'title': current_section,
                'content': current_content
            })
        
        return resume_data
    
    def _is_section_header(self, line: str) -> bool:
        """Determine if a line is a section header"""
        # Common section headers
        common_sections = [
            'experience', 'education', 'skills', 'summary', 'objective',
            'projects', 'certifications', 'awards', 'publications',
            'professional experience', 'work experience', 'employment',
            'technical skills', 'core competencies', 'achievements'
        ]
        
        line_lower = line.lower().strip()
        
        # Check if it's all caps (common for headers)
        if line.isupper() and len(line) > 2:
            return True
        
        # Check if it matches common section names
        if any(section in line_lower for section in common_sections):
            return True
        
        # Check if it's a short line that could be a header
        if len(line) < 30 and not line.startswith('•') and ':' not in line:
            words = line.split()
            if len(words) <= 3 and all(word.isalpha() or word.isdigit() for word in words):
                return True
        
        return False
    
    def _create_pdf_with_template(
        self,
        resume_data: Dict[str, Any],
        options: FormattingOptions,
        output_path: str,
        job_title: str
    ) -> bool:
        """Create PDF using the specified template"""
        try:
            # Get template configuration
            template_config = self.template_configs[options.template]
            colors = self.color_schemes[options.color_scheme]
            fonts = self.font_mappings[options.font_family]
            
            # Set page size
            page_size = A4 if options.page_size == "a4" else letter
            
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=page_size,
                rightMargin=options.margin_size * inch,
                leftMargin=options.margin_size * inch,
                topMargin=options.margin_size * inch,
                bottomMargin=options.margin_size * inch
            )
            
            # Create styles
            styles = self._create_custom_styles(options, template_config, colors, fonts)
            
            # Build content
            story = []
            
            # Add name
            if resume_data['name']:
                story.append(Paragraph(resume_data['name'], styles['name']))
                story.append(Spacer(1, 6))
            
            # Add contact information
            if resume_data['contact']:
                contact_text = ' | '.join(resume_data['contact'])
                story.append(Paragraph(contact_text, styles['contact']))
                story.append(Spacer(1, options.section_spacing))
            
            # Add sections
            for section in resume_data['sections']:
                # Section header
                story.append(Paragraph(section['title'].upper(), styles['section_header']))
                story.append(Spacer(1, 4))
                
                # Section content
                for content_line in section['content']:
                    if content_line.strip().startswith('•'):
                        # Bullet point
                        story.append(Paragraph(content_line, styles['bullet']))
                    else:
                        # Regular content
                        story.append(Paragraph(content_line, styles['body']))
                
                story.append(Spacer(1, options.section_spacing))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            logger.error(f"Error creating PDF with template {options.template.value}: {e}")
            return False
    
    def _create_custom_styles(
        self,
        options: FormattingOptions,
        template_config: Dict,
        colors: Dict[str, HexColor],
        fonts: Dict[str, str]
    ) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles based on formatting options"""
        base_styles = getSampleStyleSheet()
        
        # Name style
        name_style = ParagraphStyle(
            'CustomName',
            parent=base_styles['Normal'],
            fontSize=template_config['name_font_size'],
            textColor=colors['primary'],
            fontName=fonts['bold'],
            alignment=TA_CENTER if options.template == FormattingTemplate.CREATIVE else TA_LEFT,
            spaceAfter=6,
            spaceBefore=0
        )
        
        # Contact style
        contact_style = ParagraphStyle(
            'CustomContact',
            parent=base_styles['Normal'],
            fontSize=options.font_size - 1,
            textColor=colors['text'],
            fontName=fonts['regular'],
            alignment=TA_CENTER if options.template == FormattingTemplate.CREATIVE else TA_LEFT,
            spaceAfter=4,
            spaceBefore=0
        )
        
        # Section header style
        section_header_style = ParagraphStyle(
            'CustomSectionHeader',
            parent=base_styles['Normal'],
            fontSize=template_config['section_font_size'],
            textColor=colors['primary'],
            fontName=fonts['bold'],
            alignment=TA_LEFT,
            spaceAfter=2,
            spaceBefore=4,
            borderWidth=1 if template_config['section_style'] == 'underline' else 0,
            borderColor=colors['primary'] if template_config['section_style'] == 'underline' else None,
            backColor=colors['light'] if template_config['section_style'] == 'background' else None
        )
        
        # Body text style
        body_style = ParagraphStyle(
            'CustomBody',
            parent=base_styles['Normal'],
            fontSize=template_config['body_font_size'],
            textColor=colors['text'],
            fontName=fonts['regular'],
            alignment=TA_LEFT,
            spaceAfter=2,
            spaceBefore=0,
            lineHeight=options.line_spacing * template_config['body_font_size']
        )
        
        # Bullet style
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=body_style,
            leftIndent=12,
            firstLineIndent=-12,
            bulletIndent=0,
            spaceAfter=1
        )
        
        return {
            'name': name_style,
            'contact': contact_style,
            'section_header': section_header_style,
            'body': body_style,
            'bullet': bullet_style
        }
    
    def get_available_templates(self, is_pro: bool = False) -> List[Dict[str, Any]]:
        """Get list of available templates based on user subscription"""
        templates = []
        
        # Standard template is always available
        templates.append({
            'id': FormattingTemplate.STANDARD.value,
            'name': 'Standard Professional',
            'description': 'Clean, professional format suitable for all industries',
            'preview_url': '/static/templates/standard_preview.png',
            'pro_only': False
        })
        
        if is_pro:
            templates.extend([
                {
                    'id': FormattingTemplate.MODERN.value,
                    'name': 'Modern',
                    'description': 'Contemporary design with subtle colors and clean lines',
                    'preview_url': '/static/templates/modern_preview.png',
                    'pro_only': True
                },
                {
                    'id': FormattingTemplate.EXECUTIVE.value,
                    'name': 'Executive',
                    'description': 'Sophisticated design for senior-level positions',
                    'preview_url': '/static/templates/executive_preview.png',
                    'pro_only': True
                },
                {
                    'id': FormattingTemplate.CREATIVE.value,
                    'name': 'Creative',
                    'description': 'Eye-catching design for creative industries',
                    'preview_url': '/static/templates/creative_preview.png',
                    'pro_only': True
                },
                {
                    'id': FormattingTemplate.MINIMAL.value,
                    'name': 'Minimal',
                    'description': 'Clean, minimalist design with maximum content focus',
                    'preview_url': '/static/templates/minimal_preview.png',
                    'pro_only': True
                },
                {
                    'id': FormattingTemplate.ACADEMIC.value,
                    'name': 'Academic',
                    'description': 'Traditional format ideal for academic and research positions',
                    'preview_url': '/static/templates/academic_preview.png',
                    'pro_only': True
                },
                {
                    'id': FormattingTemplate.TECHNICAL.value,
                    'name': 'Technical',
                    'description': 'Structured format optimized for technical roles',
                    'preview_url': '/static/templates/technical_preview.png',
                    'pro_only': True
                }
            ])
        
        return templates
    
    def get_available_color_schemes(self) -> List[Dict[str, Any]]:
        """Get list of available color schemes"""
        return [
            {
                'id': ColorScheme.CLASSIC_BLUE.value,
                'name': 'Classic Blue',
                'description': 'Professional blue tones',
                'primary_color': '#2c5aa0'
            },
            {
                'id': ColorScheme.MODERN_GRAY.value,
                'name': 'Modern Gray',
                'description': 'Contemporary gray palette',
                'primary_color': '#495057'
            },
            {
                'id': ColorScheme.EXECUTIVE_BLACK.value,
                'name': 'Executive Black',
                'description': 'Timeless black and white',
                'primary_color': '#000000'
            },
            {
                'id': ColorScheme.CREATIVE_TEAL.value,
                'name': 'Creative Teal',
                'description': 'Vibrant teal accents',
                'primary_color': '#20c997'
            },
            {
                'id': ColorScheme.WARM_BROWN.value,
                'name': 'Warm Brown',
                'description': 'Warm, earthy tones',
                'primary_color': '#8b4513'
            },
            {
                'id': ColorScheme.TECH_GREEN.value,
                'name': 'Tech Green',
                'description': 'Modern green for tech roles',
                'primary_color': '#28a745'
            }
        ]
    
    def validate_formatting_request(
        self,
        template: str,
        color_scheme: str,
        font_family: str,
        is_pro: bool
    ) -> Tuple[bool, str]:
        """Validate formatting request parameters"""
        try:
            # Validate template
            try:
                template_enum = FormattingTemplate(template)
            except ValueError:
                return False, f"Invalid template: {template}"
            
            # Check Pro-only templates
            if template_enum != FormattingTemplate.STANDARD and not is_pro:
                return False, f"Template '{template}' requires Pro subscription"
            
            # Validate color scheme
            try:
                ColorScheme(color_scheme)
            except ValueError:
                return False, f"Invalid color scheme: {color_scheme}"
            
            # Validate font family
            try:
                FontFamily(font_family)
            except ValueError:
                return False, f"Invalid font family: {font_family}"
            
            return True, "Valid formatting request"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Import regex for section header detection
import re