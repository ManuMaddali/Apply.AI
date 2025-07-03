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
from reportlab.lib.colors import black, darkblue

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
        Create a compact, one-page PDF with proper formatting and text wrapping
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Create a canvas
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            # More compact font sizes to fit everything on one page
            name_font_size = 16
            section_font_size = 11
            body_font_size = 10
            small_font_size = 9
            
            # Tighter margins for more content space
            left_margin = 36  # 0.5 inch
            right_margin = 36
            top_margin = 36
            bottom_margin = 36
            available_width = width - left_margin - right_margin
            
            # Starting position from top
            y_position = height - top_margin
            
            # Compact line heights
            name_line_height = 18
            section_line_height = 14
            body_line_height = 12
            small_line_height = 10
            
            # Calculate character width for better text wrapping
            char_width = body_font_size * 0.6
            max_chars_per_line = int(available_width / char_width)
            
            # Parse and format the resume content
            sections = self._parse_resume_for_compact_formatting(tailored_text)
            
            for section_type, content in sections:
                # Conservative page break check
                if y_position < bottom_margin + 50:
                    break  # Stop adding content to keep it on one page
                
                if section_type == "name":
                    # Name formatting
                    c.setFont("Helvetica-Bold", name_font_size)
                    c.setFillColor(darkblue)
                    c.drawString(left_margin, y_position, content.strip())
                    c.setFillColor(black)
                    y_position -= name_line_height
                    
                elif section_type == "contact":
                    # Contact info
                    c.setFont("Helvetica", small_font_size)
                    c.drawString(left_margin, y_position, content.strip())
                    y_position -= small_line_height + 6
                    
                elif section_type == "section_header":
                    # Section headers
                    y_position -= 4
                    c.setFont("Helvetica-Bold", section_font_size)
                    c.setFillColor(darkblue)
                    c.drawString(left_margin, y_position, content.strip().upper())
                    c.setFillColor(black)
                    y_position -= section_line_height
                    
                elif section_type == "company_header":
                    # Company/job headers
                    y_position -= 2
                    c.setFont("Helvetica-Bold", body_font_size)
                    wrapped_lines = self._smart_wrap_text(content.strip(), max_chars_per_line)
                    for line in wrapped_lines:
                        if y_position < bottom_margin + 30:
                            break
                        c.drawString(left_margin, y_position, line)
                        y_position -= body_line_height
                    
                elif section_type == "bullet_point":
                    # Consistent bullet point formatting
                    c.setFont("Helvetica", body_font_size)
                    c.setFillColor(black)
                    
                    # Remove existing bullet symbols
                    clean_content = content.strip()
                    while clean_content and clean_content[0] in ['•', '●', '·', '-', '*']:
                        clean_content = clean_content[1:].strip()
                    
                    if not clean_content:
                        continue
                    
                    # Text wrapping
                    bullet_max_chars = max_chars_per_line - 6
                    wrapped_lines = self._smart_wrap_text(clean_content, bullet_max_chars)
                    
                    for i, line in enumerate(wrapped_lines):
                        if y_position < bottom_margin + 20:
                            break
                        
                        c.setFont("Helvetica", body_font_size)  # Ensure consistent font
                        c.setFillColor(black)
                        
                        if i == 0:
                            # First line with bullet
                            c.drawString(left_margin + 10, y_position, "•")
                            c.drawString(left_margin + 20, y_position, line)
                        else:
                            # Continuation lines
                            c.drawString(left_margin + 20, y_position, line)
                        
                        y_position -= body_line_height
                    
                elif section_type == "body_text":
                    # Regular body text
                    c.setFont("Helvetica", body_font_size)
                    c.setFillColor(black)
                    wrapped_lines = self._smart_wrap_text(content.strip(), max_chars_per_line)
                    
                    for line in wrapped_lines:
                        if y_position < bottom_margin + 20:
                            break
                        c.drawString(left_margin, y_position, line)
                        y_position -= body_line_height
                    
                elif section_type == "spacing":
                    spacing = min(int(content), 6)
                    y_position -= spacing
            
            # Save the PDF
            c.save()
            return True
            
        except Exception as e:
            print(f"Error creating compact PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_resume_for_compact_formatting(self, text: str) -> list:
        """Parse resume text for compact formatting with comprehensive bullet detection"""
        lines = text.split('\n')
        sections = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                # Empty line - add minimal spacing
                sections.append(("spacing", "4"))
                continue
            
            # Debug what we're classifying
            print(f"Line {i}: '{stripped[:50]}...' -> ", end="")
            
            # Detect name (first substantial line)
            if i < 3 and len([s for s in sections if s[0] == "name"]) == 0:
                if (not any(char in stripped.lower() for char in ['@', '.com', 'phone', 'email', '(', ')']) and 
                    len(stripped) < 60 and len(stripped) > 5):
                    print("NAME")
                    sections.append(("name", stripped))
                    continue
            
            # Detect contact info
            if any(indicator in stripped.lower() for indicator in ['@', '.com', 'phone', '(', ')', 'email', 'linkedin']) or re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', stripped):
                print("CONTACT")
                sections.append(("contact", stripped))
                continue
            
            # Detect section headers
            if (stripped.isupper() and 5 < len(stripped) < 35 and 
                not any(char in stripped for char in ['•', '●', '·', '@', '(', ')'])):
                print("SECTION_HEADER")
                sections.append(("section_header", stripped))
                continue
            
            # Detect company/job headers (very strict)
            if ('|' in stripped and re.search(r'\b\d{4}\b', stripped)):
                print("COMPANY_HEADER")
                sections.append(("company_header", stripped))
                continue
            
            # COMPREHENSIVE bullet detection - catch everything that could be bullet content
            is_bullet = False
            
            # 1. Direct bullet symbols
            if any(stripped.startswith(char) for char in ['•', '●', '·', '-', '*']):
                is_bullet = True
                print("BULLET_POINT (symbol)")
            
            # 2. Action verbs
            elif stripped.split():
                first_word = stripped.split()[0].lower()
                action_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 'designed', 'built', 
                               'achieved', 'increased', 'decreased', 'improved', 'optimized', 'coordinated', 
                               'collaborated', 'established', 'launched', 'delivered', 'executed', 'analyzed', 
                               'drove', 'spearheaded', 'acted', 'served', 'translated', 'automated', 'worked',
                               'focused', 'specialized', 'utilized', 'leveraged', 'maintained', 'supported',
                               'facilitated', 'streamlined', 'enhanced', 'engineered', 'architected']
                if first_word in action_verbs:
                    is_bullet = True
                    print(f"BULLET_POINT (action verb: {first_word})")
            
            # 3. Lines with metrics/achievements
            if not is_bullet and re.search(r'\d+%|\d+x|increase|decrease|improve|reduce|result', stripped.lower()):
                is_bullet = True
                print("BULLET_POINT (metrics/achievement)")
            
            # 4. Indented lines or lines that look like bullet continuations
            if not is_bullet and len(line) - len(line.lstrip()) > 2:
                is_bullet = True
                print("BULLET_POINT (indented)")
            
            if is_bullet:
                sections.append(("bullet_point", stripped))
                continue
            
            # Everything else is body text
            print("BODY_TEXT")
            sections.append(("body_text", stripped))
        
        return sections
    
    def _smart_wrap_text(self, text: str, max_chars: int) -> list:
        """Smart text wrapping that preserves meaning and avoids awkward breaks"""
        if len(text) <= max_chars:
            return [text]
        
        # Split into words
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Test if adding this word would exceed the limit
            test_line = current_line + (" " if current_line else "") + word
            
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                # Current line is full, start a new one
                if current_line:
                    lines.append(current_line)
                
                # If single word is too long, we need to break it
                if len(word) > max_chars:
                    # Break the long word
                    while len(word) > max_chars:
                        lines.append(word[:max_chars-1] + "-")
                        word = word[max_chars-1:]
                    current_line = word
                else:
                    current_line = word
        
        # Add the last line if it has content
        if current_line:
            lines.append(current_line)
        
        return lines
    
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