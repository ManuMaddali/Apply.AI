import os
import re
import PyPDF2
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from typing import Optional, Tuple
import tempfile
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        """Extract text from PDF file using pdfplumber for better layout preservation"""
        
        # Method 1: Try pdfplumber first (best for layout preservation)
        try:
            text = self._extract_pdf_with_pdfplumber(file_path)
            if text and len(text.strip()) > 50:
                print(f"Successfully extracted PDF with pdfplumber: {len(text)} chars")
                return text
        except Exception as e:
            print(f"Pdfplumber extraction failed: {e}")
        
        # Method 2: Fall back to PyPDF2 with aggressive defragmentation
        try:
            text = self._extract_pdf_method1(file_path)
            if text and len(text.strip()) > 50:
                # Apply aggressive defragmentation
                text = self._fix_character_level_fragmentation(text)
                return self._clean_extracted_text(text)
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
        
        return ""
    
    def _extract_pdf_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber which preserves layout better"""
        all_text = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text with layout preservation
                page_text = page.extract_text(layout=True, x_tolerance=3, y_tolerance=3)
                
                if page_text:
                    # Clean up excessive whitespace while preserving structure
                    lines = page_text.split('\n')
                    cleaned_lines = []
                    
                    for line in lines:
                        # Remove trailing spaces but preserve indentation
                        cleaned_line = line.rstrip()
                        if cleaned_line:  # Only keep non-empty lines
                            # Normalize multiple spaces to single space within the line
                            # but preserve leading spaces for indentation
                            parts = cleaned_line.split()
                            if parts:
                                leading_spaces = len(cleaned_line) - len(cleaned_line.lstrip())
                                cleaned_line = ' ' * min(leading_spaces, 4) + ' '.join(parts)
                            cleaned_lines.append(cleaned_line)
                    
                    page_text = '\n'.join(cleaned_lines)
                    all_text.append(page_text)
        
        # Join pages with double newline
        full_text = '\n\n'.join(all_text)
        
        # Apply minimal post-processing to fix common issues
        full_text = self._minimal_text_cleanup(full_text)
        
        return full_text
    
    def _minimal_text_cleanup(self, text: str) -> str:
        """Minimal cleanup to fix obvious issues without destroying layout"""
        if not text:
            return ""
        
        # Fix email addresses that might be split
        text = re.sub(r'(\w+)\s+@\s+(\w+)\s*\.\s*(\w+)', r'\1@\2.\3', text)
        
        # Fix phone numbers that might be split
        text = re.sub(r'(\d{3})\s*[-.\s]\s*(\d{3})\s*[-.\s]\s*(\d{4})', r'\1-\2-\3', text)
        
        # Remove excessive blank lines (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Ensure consistent line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def _extract_pdf_method1(self, file_path: str) -> str:
        """Standard PyPDF2 extraction with character-level reconstruction"""
        text_parts = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    # Try to reconstruct proper text from fragments
                    reconstructed = self._reconstruct_text_from_fragments(page_text)
                    text_parts.append(reconstructed)
        
        return "\n\n".join(text_parts)
    
    def _reconstruct_text_from_fragments(self, raw_text: str) -> str:
        """Reconstruct proper text from fragmented PDF extraction"""
        if not raw_text:
            return ""
        
        # Split into lines and clean
        lines = raw_text.split('\n')
        reconstructed_lines = []
        current_line = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_line:
                    reconstructed_lines.append(current_line)
                    current_line = ""
                continue
            
            # Check if this line should be joined with the previous
            if current_line and self._should_join_lines(current_line, line):
                current_line += " " + line
            else:
                if current_line:
                    reconstructed_lines.append(current_line)
                current_line = line
        
        # Add the last line
        if current_line:
            reconstructed_lines.append(current_line)
        
        return "\n".join(reconstructed_lines)
    
    def _should_join_lines(self, current_line: str, next_line: str) -> bool:
        """Determine if two lines should be joined together"""
        # Don't join if current line ends with clear sentence endings
        if current_line.endswith(('.', ':', '•', '-')):
            return False
        
        # Don't join if next line starts with bullet point or section header
        if next_line.startswith(('•', '-', '*')) or next_line.isupper():
            return False
        
        # Don't join if next line looks like a date or location
        if re.match(r'^\d{4}|^[A-Z][a-z]+,\s*[A-Z]{2}', next_line):
            return False
        
        # Join if current line seems incomplete (very short or doesn't end properly)
        if len(current_line) < 10 or not current_line[-1].isalnum():
            return True
        
        # Join if next line starts with lowercase (continuation)
        if next_line and next_line[0].islower():
            return True
        
        return False
    
    def _process_raw_pdf_text(self, raw_text: str) -> str:
        """Process raw PDF text with different logic"""
        # Remove excessive whitespace first
        cleaned = re.sub(r'\s+', ' ', raw_text)
        
        # Try to identify and separate sections
        sections = []
        current_section = ""
        
        # Split by potential section boundaries
        parts = re.split(r'([A-Z\s]{3,}(?:\n|$))', cleaned)
        
        for part in parts:
            part = part.strip()
            if part:
                if part.isupper() and len(part) > 2:
                    # This looks like a section header
                    if current_section:
                        sections.append(current_section)
                    current_section = part + "\n"
                else:
                    current_section += part + " "
        
        if current_section:
            sections.append(current_section)
        
        return "\n\n".join(sections)
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file with better formatting"""
        try:
            doc = Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                para_text = paragraph.text.strip()
                if para_text:  # Only add non-empty paragraphs
                    text_parts.append(para_text)
            
            # Join paragraphs with single line breaks
            full_text = "\n".join(text_parts)
            return self._clean_extracted_text(full_text)
            
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean up extracted text to fix common formatting issues"""
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize line breaks
        lines = []
        for line in text.split('\n'):
            # Strip whitespace but preserve meaningful content
            clean_line = ' '.join(line.split())  # Normalize internal spaces
            if clean_line:  # Only keep non-empty lines
                lines.append(clean_line)
        
        # Join lines back together with proper spacing
        cleaned_text = '\n'.join(lines)
        
        # Fix common PDF extraction issues
        cleaned_text = self._fix_pdf_extraction_issues(cleaned_text)
        
        return cleaned_text.strip()
    
    def _fix_pdf_extraction_issues(self, text: str) -> str:
        """Fix common issues from PDF text extraction"""
        # Replace multiple consecutive line breaks with double line breaks
        
        # Fix cases where contact info gets split
        text = re.sub(r'\n(\+?\d)', r' \1', text)  # Fix phone numbers
        text = re.sub(r'\n(@)', r'\1', text)  # Fix email addresses
        text = re.sub(r'(\w)\n(\w)', r'\1 \2', text)  # Join broken words
        
        # Normalize section headers
        text = re.sub(r'\n([A-Z\s]{2,})\n', r'\n\n\1\n', text)  # Section headers
        
        # Clean up excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', r'\n\n', text)  # Max 2 consecutive line breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces
        
        return text
    
    def _fix_character_level_fragmentation(self, text: str) -> str:
        """Fix PDFs where characters are split by spaces or newlines"""
        if not text:
            return ""
        
        # First pass: fix obvious character-level splits
        # Pattern to find single/double character fragments that should be joined
        # e.g., "P RO F" -> "PROF", "RE C" -> "REC"
        
        # Replace patterns like "P R O F" with "PROF"
        text = re.sub(r'\b([A-Z])\s+([A-Z])\s+([A-Z])\s+([A-Z])\b', r'\1\2\3\4', text)
        text = re.sub(r'\b([A-Z])\s+([A-Z])\s+([A-Z])\b', r'\1\2\3', text)
        text = re.sub(r'\b([A-Z])\s+([A-Z])\b', r'\1\2', text)
        
        # Fix split words with lowercase too
        text = re.sub(r'\b(\w)\s+(\w)\s+(\w)\s+(\w)\s+(\w)\b', lambda m: 
                     ''.join(m.groups()) if len(''.join(m.groups())) <= 10 else m.group(0), text)
        text = re.sub(r'\b(\w)\s+(\w)\s+(\w)\s+(\w)\b', lambda m: 
                     ''.join(m.groups()) if len(''.join(m.groups())) <= 8 else m.group(0), text)
        text = re.sub(r'\b(\w)\s+(\w)\s+(\w)\b', lambda m: 
                     ''.join(m.groups()) if len(''.join(m.groups())) <= 6 else m.group(0), text)
        
        # Second pass: reconstruct lines
        lines = text.split('\n')
        reconstructed = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                reconstructed.append('')
                i += 1
                continue
            
            # Check if this line and following lines should be merged
            merged_line = line
            j = i + 1
            
            # Look ahead to see if we should merge lines
            while j < len(lines) and j < i + 5:  # Look up to 5 lines ahead
                next_line = lines[j].strip()
                if not next_line:
                    break
                
                # Check if lines should be merged
                if self._should_merge_fragmented_lines(merged_line, next_line):
                    # If the next line is very short and looks like a continuation
                    if len(next_line) < 20 or next_line[0].islower():
                        merged_line += ' ' + next_line
                        j += 1
                    else:
                        break
                else:
                    break
            
            reconstructed.append(merged_line)
            i = j if j > i + 1 else i + 1
        
        # Join and do final cleanup
        result = '\n'.join(reconstructed)
        
        # Fix common patterns
        result = self._fix_common_resume_patterns(result)
        
        return result
    
    def _should_merge_fragmented_lines(self, current: str, next_line: str) -> bool:
        """Determine if fragmented lines should be merged"""
        # Very short current line likely needs continuation
        if len(current) < 10:
            return True
        
        # Line doesn't end with proper punctuation
        if current and not current[-1] in '.,:;!?':
            # Next line starts with lowercase
            if next_line and next_line[0].islower():
                return True
            # Current line ends with a word fragment
            if len(current.split()[-1]) < 3:
                return True
        
        return False
    
    def _fix_common_resume_patterns(self, text: str) -> str:
        """Fix common resume-specific patterns"""
        # Fix date patterns
        text = re.sub(r'(\d{4})\s*-\s*(\d{4})', r'\1-\2', text)
        text = re.sub(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', r'\1 \2', text)
        
        # Fix location patterns
        text = re.sub(r'([A-Z][a-z]+)\s*,\s*([A-Z]{2})\s+(\d{5})', r'\1, \2 \3', text)
        
        # Fix email patterns
        text = re.sub(r'(\w+)\s*@\s*(\w+)\s*\.\s*(\w+)', r'\1@\2.\3', text)
        
        # Fix phone patterns
        text = re.sub(r'\(\s*(\d{3})\s*\)\s*(\d{3})\s*-\s*(\d{4})', r'(\1) \2-\3', text)
        
        # Fix bullet points
        text = re.sub(r'^\s*[•·▪▫◦‣⁃]\s*', '• ', text, flags=re.MULTILINE)
        
        return text
    
    def create_tailored_resume_pdf(self, tailored_text: str, output_path: str, job_title: str = "") -> bool:
        """
        Create a PDF that preserves exact text formatting with proper wrapping
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Create a canvas
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            # Set font to Courier (monospace) - smaller to fit more text
            font_size = 8  # Reduced to fit more text
            c.setFont("Courier", font_size)
            
            # Calculate available width for text
            left_margin = 30
            right_margin = 30
            available_width = width - left_margin - right_margin
            
            # Starting position from top
            y_position = height - 40
            line_height = 10  # Reduced line height
            
            # Character width in Courier font (approximation)
            char_width = font_size * 0.6  # Courier is roughly 60% of font size width
            max_chars_per_line = int(available_width / char_width)
            
            # Split text into lines
            lines = tailored_text.split('\n')
            
            def wrap_line(line, max_chars):
                """Wrap a line if it's too long, preserving indentation"""
                if len(line) <= max_chars:
                    return [line]
                
                # Find indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                content = line.lstrip()
                
                wrapped_lines = []
                while len(content) > max_chars - indent:
                    # Find the last space before max_chars
                    break_point = max_chars - indent
                    space_pos = content.rfind(' ', 0, break_point)
                    
                    if space_pos == -1:  # No space found, break at max_chars
                        space_pos = break_point
                    
                    wrapped_lines.append(indent_str + content[:space_pos])
                    content = content[space_pos:].lstrip()
                
                # Add remaining content
                if content:
                    wrapped_lines.append(indent_str + content)
                
                return wrapped_lines
            
            for line in lines:
                # Check if we need a new page
                if y_position < 50:
                    c.showPage()
                    c.setFont("Courier", font_size)
                    y_position = height - 40
                
                # Handle empty lines
                if not line.strip():
                    y_position -= line_height * 0.5  # Smaller gap for empty lines
                    continue
                
                # Replace bullet points for proper rendering
                display_line = line.replace('•', '·').replace('●', '·')  # Use middle dot (smaller bullet)
                
                # Check if this is a header (all caps, no bullets)
                is_header = (line.strip().isupper() and 
                           len(line.strip()) > 3 and 
                           not any(char in line for char in ['●', '•', '-', '·']) and
                           len(line.strip()) < 50)  # Headers are usually shorter
                
                if is_header:
                    c.setFont("Courier-Bold", font_size + 1)
                    # Center headers or keep them left-aligned
                    c.drawString(left_margin, y_position, display_line.strip())
                    c.setFont("Courier", font_size)
                    y_position -= line_height
                else:
                    # Wrap long lines
                    wrapped_lines = wrap_line(display_line, max_chars_per_line)
                    
                    for wrapped_line in wrapped_lines:
                        # Check for new page again
                        if y_position < 50:
                            c.showPage()
                            c.setFont("Courier", font_size)
                            y_position = height - 40
                        
                        # Preserve exact indentation
                        leading_spaces = 0
                        for char in wrapped_line:
                            if char == ' ':
                                leading_spaces += 1
                            elif char == '\t':
                                leading_spaces += 4
                            else:
                                break
                        
                        # Special handling for bullet points
                        line_content = wrapped_line.lstrip()
                        x_position = left_margin + (leading_spaces * char_width)
                        
                        if line_content.startswith('·'):
                            # Draw bullet at smaller size and then draw the rest
                            c.setFont("Courier", font_size - 1)  # Smaller font for bullet
                            c.drawString(x_position, y_position, '•')  # Use smaller bullet
                            c.setFont("Courier", font_size)
                            # Draw the rest of the text after the bullet
                            rest_of_line = line_content[1:].lstrip()
                            if rest_of_line:
                                bullet_width = char_width * 0.8  # Approximate bullet width
                                c.drawString(x_position + bullet_width, y_position, ' ' + rest_of_line)
                        else:
                            # Regular text
                            c.drawString(x_position, y_position, line_content)
                        
                        y_position -= line_height
            
            # Save the PDF
            c.save()
            return True
            
        except Exception as e:
            print(f"Error creating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
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