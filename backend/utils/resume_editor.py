import os
import PyPDF2
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Optional, Tuple
import tempfile

class ResumeEditor:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for resume formatting"""
        self.styles.add(ParagraphStyle(
            name='ResumeHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ResumeSection',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='ResumeBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4
        ))
    
    def extract_text_from_file(self, file_path: str) -> Optional[str]:
        """
        Extract text from PDF or DOCX file
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return "\n".join(text).strip()
    
    def create_tailored_resume_pdf(self, tailored_text: str, output_path: str, job_title: str = "") -> bool:
        """
        Create a PDF from tailored resume text
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = []
            
            # Split text into sections
            sections = self._parse_resume_sections(tailored_text)
            
            for section_title, section_content in sections:
                if section_title:
                    # Add section heading
                    story.append(Paragraph(section_title, self.styles['ResumeSection']))
                    story.append(Spacer(1, 6))
                
                # Add section content
                paragraphs = section_content.split('\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), self.styles['ResumeBody']))
                        story.append(Spacer(1, 3))
                
                story.append(Spacer(1, 12))
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error creating PDF: {str(e)}")
            return False
    
    def create_tailored_resume_docx(self, tailored_text: str, output_path: str, job_title: str = "") -> bool:
        """
        Create a DOCX from tailored resume text
        """
        try:
            doc = Document()
            
            # Parse sections
            sections = self._parse_resume_sections(tailored_text)
            
            for section_title, section_content in sections:
                if section_title:
                    # Add section heading
                    heading = doc.add_heading(section_title, level=2)
                
                # Add section content
                paragraphs = section_content.split('\n')
                for para in paragraphs:
                    if para.strip():
                        doc.add_paragraph(para.strip())
            
            doc.save(output_path)
            return True
            
        except Exception as e:
            print(f"Error creating DOCX: {str(e)}")
            return False
    
    def _parse_resume_sections(self, text: str) -> list:
        """
        Parse resume text into sections
        """
        sections = []
        current_section = ""
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            if self._is_section_header(line):
                # Save previous section
                if current_section or current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                
                # Start new section
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Add the last section
        if current_section or current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """
        Determine if a line is likely a section header
        """
        common_headers = [
            'summary', 'objective', 'experience', 'work experience', 'employment',
            'education', 'skills', 'technical skills', 'certifications',
            'projects', 'achievements', 'awards', 'languages', 'interests',
            'contact', 'contact information', 'professional summary'
        ]
        
        line_lower = line.lower().strip()
        
        # Check if it matches common headers
        if any(header in line_lower for header in common_headers):
            return True
        
        # Check if it's all caps (common for headers)
        if line.isupper() and len(line) > 3:
            return True
        
        # Check if it's a short line (likely a header)
        if len(line) < 50 and ':' not in line and len(line.split()) <= 4:
            return True
        
        return False 