"""
Professional Output Service - Phase 2 Advanced Features
Provides ATS-optimized PDF/Word generation with professional templates
"""

from typing import Dict, List, Optional, Tuple, Any
import os
import re
from io import BytesIO
from datetime import datetime

# Import existing components
try:
    from utils.resume_editor import ResumeEditor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.shared import OxmlElement, qn
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

class ATSScorer:
    """ATS Compatibility Scoring System"""
    
    def __init__(self):
        self.ats_keywords = {
            'technical': ['python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical'],
            'experience': ['years', 'experience', 'developed', 'managed', 'led', 'implemented'],
            'education': ['degree', 'bachelor', 'master', 'university', 'college', 'certification']
        }
    
    def calculate_ats_score(self, resume_text: str, job_description: str = "") -> Dict[str, Any]:
        """Calculate comprehensive ATS compatibility score (0-100)"""
        try:
            score_components = {
                'keyword_match': self._score_keyword_match(resume_text, job_description),
                'formatting': self._score_formatting(resume_text),
                'structure': self._score_structure(resume_text),
                'readability': self._score_readability(resume_text),
                'completeness': self._score_completeness(resume_text)
            }
            
            # Weighted scoring
            weights = {
                'keyword_match': 0.35,
                'formatting': 0.20,
                'structure': 0.20,
                'readability': 0.15,
                'completeness': 0.10
            }
            
            total_score = sum(score_components[key] * weights[key] for key in weights)
            
            return {
                'total_score': min(100, max(0, int(total_score))),
                'components': score_components,
                'recommendations': self._generate_recommendations(score_components),
                'grade': self._get_grade(total_score)
            }
        except Exception as e:
            return {'total_score': 75, 'error': str(e), 'grade': 'B'}
    
    def _score_keyword_match(self, resume_text: str, job_description: str) -> float:
        """Score keyword matching with job description"""
        if not job_description:
            return 70.0  # Default score when no job description
        
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        # Extract keywords from job description
        job_keywords = set(re.findall(r'\b\w+\b', job_lower))
        job_keywords = {word for word in job_keywords if len(word) > 3}
        
        # Count matches
        matches = sum(1 for keyword in job_keywords if keyword in resume_lower)
        match_ratio = matches / len(job_keywords) if job_keywords else 0
        
        return min(100, match_ratio * 100)
    
    def _score_formatting(self, resume_text: str) -> float:
        """Score formatting quality"""
        score = 100.0
        
        # Check for common formatting issues
        if '\\bullet' in resume_text:
            score -= 15  # Literal bullet text
        if resume_text.count('\n\n') < 3:
            score -= 10  # Insufficient spacing
        if len(re.findall(r'[A-Z]{2,}', resume_text)) > 10:
            score -= 5   # Too much ALL CAPS
        
        return max(0, score)
    
    def _score_structure(self, resume_text: str) -> float:
        """Score resume structure"""
        score = 0.0
        sections = ['experience', 'education', 'skills', 'summary']
        
        for section in sections:
            if any(keyword in resume_text.lower() for keyword in [section, section.replace('e', 'a')]):
                score += 25
        
        return min(100, score)
    
    def _score_readability(self, resume_text: str) -> float:
        """Score readability"""
        lines = resume_text.split('\n')
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        
        # Optimal line length is 60-80 characters
        if 60 <= avg_line_length <= 80:
            return 100.0
        elif 40 <= avg_line_length <= 100:
            return 80.0
        else:
            return 60.0
    
    def _score_completeness(self, resume_text: str) -> float:
        """Score resume completeness"""
        required_elements = ['email', 'phone', 'experience', 'skills']
        score = 0.0
        
        for element in required_elements:
            if element in resume_text.lower():
                score += 25
        
        return min(100, score)
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if scores['keyword_match'] < 70:
            recommendations.append("Add more job-specific keywords from the job description")
        if scores['formatting'] < 80:
            recommendations.append("Improve formatting consistency and remove literal bullet text")
        if scores['structure'] < 80:
            recommendations.append("Ensure all major sections (Experience, Education, Skills) are present")
        if scores['readability'] < 70:
            recommendations.append("Optimize line length and paragraph structure for better readability")
        
        return recommendations
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'B+'
        elif score >= 75: return 'B'
        elif score >= 70: return 'C+'
        elif score >= 65: return 'C'
        else: return 'D'

class ProfessionalTemplateEngine:
    """Professional template system with multiple ATS-optimized layouts"""
    
    def __init__(self):
        self.templates = {
            'executive': self._executive_template,
            'technical': self._technical_template,
            'creative': self._creative_template,
            'modern': self._modern_template,
            'classic': self._classic_template
        }
    
    def get_template_styles(self, template_name: str) -> Dict[str, ParagraphStyle]:
        """Get styles for specific template"""
        if template_name not in self.templates:
            template_name = 'modern'
        
        return self.templates[template_name]()
    
    def _executive_template(self) -> Dict[str, ParagraphStyle]:
        """Executive template - Conservative, professional"""
        blue = HexColor('#1f4e79')
        return {
            'name': ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=20, textColor=blue, spaceAfter=3),
            'title': ParagraphStyle('Title', fontName='Helvetica', fontSize=14, textColor=blue, spaceAfter=8),
            'contact': ParagraphStyle('Contact', fontName='Helvetica', fontSize=10, spaceAfter=12),
            'section': ParagraphStyle('Section', fontName='Helvetica-Bold', fontSize=12, textColor=blue, spaceBefore=15, spaceAfter=8),
            'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=10, spaceAfter=6),
            'bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10, leftIndent=15, firstLineIndent=-15, spaceAfter=4)
        }
    
    def _technical_template(self) -> Dict[str, ParagraphStyle]:
        """Technical template - Clean, modern"""
        green = HexColor('#2d5016')
        return {
            'name': ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=18, textColor=green, spaceAfter=2),
            'title': ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=13, textColor=green, spaceAfter=6),
            'contact': ParagraphStyle('Contact', fontName='Helvetica', fontSize=9, spaceAfter=10),
            'section': ParagraphStyle('Section', fontName='Helvetica-Bold', fontSize=11, textColor=green, spaceBefore=12, spaceAfter=6),
            'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=10, spaceAfter=5),
            'bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10, leftIndent=12, firstLineIndent=-12, spaceAfter=3)
        }
    
    def _creative_template(self) -> Dict[str, ParagraphStyle]:
        """Creative template - Modern with color"""
        purple = HexColor('#663399')
        return {
            'name': ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=19, textColor=purple, spaceAfter=3),
            'title': ParagraphStyle('Title', fontName='Helvetica-Oblique', fontSize=13, textColor=purple, spaceAfter=7),
            'contact': ParagraphStyle('Contact', fontName='Helvetica', fontSize=10, spaceAfter=11),
            'section': ParagraphStyle('Section', fontName='Helvetica-Bold', fontSize=12, textColor=purple, spaceBefore=14, spaceAfter=7),
            'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=10, spaceAfter=6),
            'bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10, leftIndent=14, firstLineIndent=-14, spaceAfter=4)
        }
    
    def _modern_template(self) -> Dict[str, ParagraphStyle]:
        """Modern template - Your current reference style"""
        blue = HexColor('#4472C4')
        return {
            'name': ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=18, textColor=blue, spaceAfter=2),
            'title': ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=14, textColor=blue, spaceAfter=6),
            'contact': ParagraphStyle('Contact', fontName='Helvetica', fontSize=10, spaceAfter=12),
            'section': ParagraphStyle('Section', fontName='Helvetica-Bold', fontSize=11, textColor=blue, spaceBefore=12, spaceAfter=6),
            'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=10, spaceAfter=6),
            'bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10, leftIndent=12, firstLineIndent=-12, spaceAfter=3)
        }
    
    def _classic_template(self) -> Dict[str, ParagraphStyle]:
        """Classic template - Traditional black and white"""
        return {
            'name': ParagraphStyle('Name', fontName='Times-Bold', fontSize=18, spaceAfter=3),
            'title': ParagraphStyle('Title', fontName='Times-Italic', fontSize=14, spaceAfter=8),
            'contact': ParagraphStyle('Contact', fontName='Times-Roman', fontSize=10, spaceAfter=12),
            'section': ParagraphStyle('Section', fontName='Times-Bold', fontSize=12, spaceBefore=15, spaceAfter=8),
            'body': ParagraphStyle('Body', fontName='Times-Roman', fontSize=10, spaceAfter=6),
            'bullet': ParagraphStyle('Bullet', fontName='Times-Roman', fontSize=10, leftIndent=15, firstLineIndent=-15, spaceAfter=4)
        }

class ProfessionalOutputService:
    """Main service for professional PDF/Word output with ATS optimization"""
    
    def __init__(self):
        self.resume_editor = ResumeEditor() if DEPENDENCIES_AVAILABLE else None
        self.ats_scorer = ATSScorer()
        self.template_engine = ProfessionalTemplateEngine()
    
    def generate_professional_pdf(
        self, 
        resume_text: str, 
        job_description: str = "",
        template: str = "modern",
        ats_optimize: bool = True
    ) -> Dict[str, Any]:
        """Generate professional PDF with ATS optimization"""
        try:
            # Calculate ATS score
            ats_results = self.ats_scorer.calculate_ats_score(resume_text, job_description)
            
            # Apply ATS optimizations if requested
            if ats_optimize:
                resume_text = self._apply_ats_optimizations(resume_text, ats_results)
            
            # Generate PDF using existing infrastructure
            output_path = f"/tmp/professional_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            if self.resume_editor:
                success = self.resume_editor.create_tailored_resume_pdf_improved(
                    resume_text, output_path, "Professional Resume"
                )
                
                if success:
                    # Read PDF content
                    with open(output_path, 'rb') as f:
                        pdf_content = f.read()
                    
                    # Clean up temp file
                    os.remove(output_path)
                    
                    return {
                        'success': True,
                        'pdf_content': pdf_content,
                        'ats_score': ats_results,
                        'template_used': template,
                        'optimizations_applied': ats_optimize
                    }
            
            return {'success': False, 'error': 'PDF generation failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_professional_docx(self, resume_text: str, template: str = "modern") -> Dict[str, Any]:
        """Generate professional DOCX with template styling"""
        try:
            if not DEPENDENCIES_AVAILABLE:
                return {'success': False, 'error': 'DOCX dependencies not available'}
            
            # Create document
            doc = Document()
            
            # Apply template styling
            self._apply_docx_template(doc, resume_text, template)
            
            # Save to BytesIO
            docx_buffer = BytesIO()
            doc.save(docx_buffer)
            docx_buffer.seek(0)
            
            return {
                'success': True,
                'docx_content': docx_buffer.getvalue(),
                'template_used': template
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_ats_optimizations(self, resume_text: str, ats_results: Dict[str, Any]) -> str:
        """Apply ATS optimizations based on scoring results"""
        optimized_text = resume_text
        
        # Fix bullet text issues
        optimized_text = re.sub(r'\\bullet', '•', optimized_text)
        
        # Improve section headers
        optimized_text = re.sub(r'^([A-Z\s]+):?\s*$', r'\1', optimized_text, flags=re.MULTILINE)
        
        # Add spacing for better structure
        optimized_text = re.sub(r'\n([A-Z][A-Z\s]+)\n', r'\n\n\1\n', optimized_text)
        
        return optimized_text
    
    def _apply_docx_template(self, doc: Document, resume_text: str, template: str):
        """Apply template styling to DOCX document"""
        # Parse resume sections
        sections = self._parse_resume_sections(resume_text)
        
        # Apply template-specific formatting
        for section_name, content in sections.items():
            if section_name == 'header':
                self._add_docx_header(doc, content, template)
            else:
                self._add_docx_section(doc, section_name, content, template)
    
    def _parse_resume_sections(self, text: str) -> Dict[str, List[str]]:
        """Parse resume into sections"""
        sections = {'header': [], 'experience': [], 'education': [], 'skills': [], 'other': []}
        current_section = 'header'
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if any(keyword in line.lower() for keyword in ['experience', 'education', 'skills', 'summary']):
                if 'experience' in line.lower():
                    current_section = 'experience'
                elif 'education' in line.lower():
                    current_section = 'education'
                elif 'skills' in line.lower():
                    current_section = 'skills'
                else:
                    current_section = 'other'
                continue
            
            sections[current_section].append(line)
        
        return sections
    
    def _add_docx_header(self, doc: Document, content: List[str], template: str):
        """Add header section to DOCX"""
        if content:
            # Name (first line, larger font)
            name_para = doc.add_paragraph()
            name_run = name_para.add_run(content[0])
            name_run.font.size = Pt(18)
            name_run.font.bold = True
            name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Contact info
            for line in content[1:]:
                contact_para = doc.add_paragraph()
                contact_run = contact_para.add_run(line)
                contact_run.font.size = Pt(10)
                contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def _add_docx_section(self, doc: Document, section_name: str, content: List[str], template: str):
        """Add content section to DOCX"""
        if not content:
            return
        
        # Section header
        header_para = doc.add_paragraph()
        header_run = header_para.add_run(section_name.upper())
        header_run.font.size = Pt(12)
        header_run.font.bold = True
        
        # Section content
        for line in content:
            content_para = doc.add_paragraph()
            content_run = content_para.add_run(line)
            content_run.font.size = Pt(10)
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates"""
        return [
            {'name': 'modern', 'description': 'Modern professional template (default)'},
            {'name': 'executive', 'description': 'Conservative executive template'},
            {'name': 'technical', 'description': 'Clean technical template'},
            {'name': 'creative', 'description': 'Creative template with color accents'},
            {'name': 'classic', 'description': 'Traditional black and white template'}
        ]
