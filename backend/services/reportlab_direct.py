from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from io import BytesIO
import re

def get_template_config(template: str) -> dict:
    """Get template-specific configuration for colors, fonts, and sizes"""
    
    configs = {
        "olive": {
            "accent_color": "#6b8b6f",  # Light olive green
            "name_font": "Times-Bold",
            "header_font": "Times-Bold",
            "job_title_font": "Times-BoldItalic",
            "body_font": "Times-Roman",
            "name_size": 24,
            "contact_size": 10.5,
            "header_size": 12.5,
            "job_title_size": 11,
            "body_size": 10.5
        },
        "modern": {
            "accent_color": "#2f6fed",  # Blue accent from modern template
            "name_font": "Helvetica-Bold",
            "header_font": "Helvetica-Bold", 
            "job_title_font": "Helvetica-Bold",
            "body_font": "Helvetica",
            "name_size": 22,
            "contact_size": 10.5,
            "header_size": 11.5,
            "job_title_size": 11,
            "body_size": 10.75
        },
        "classic": {
            "accent_color": "#111111",  # Black accent from classic template
            "name_font": "Times-Bold",
            "header_font": "Times-Bold",
            "job_title_font": "Times-Bold", 
            "body_font": "Times-Roman",
            "name_size": 21,
            "contact_size": 10.5,
            "header_size": 12,
            "job_title_size": 11,
            "body_size": 11
        },
        "creative": {
            "accent_color": "#2f6fed",  # Inherits from modern
            "name_font": "Helvetica-Bold",
            "header_font": "Helvetica-Bold",
            "job_title_font": "Helvetica-Bold",
            "body_font": "Helvetica",
            "name_size": 22,
            "contact_size": 10.5,
            "header_size": 11.5,
            "job_title_size": 11,
            "body_size": 10.75
        },
        "executive": {
            "accent_color": "#111111",  # Inherits from classic
            "name_font": "Times-Bold",
            "header_font": "Times-Bold",
            "job_title_font": "Times-Bold",
            "body_font": "Times-Roman",
            "name_size": 21,
            "contact_size": 10.5,
            "header_size": 12,
            "job_title_size": 11,
            "body_size": 11
        },
        "technical": {
            "accent_color": "#2f6fed",  # Inherits from modern
            "name_font": "Helvetica-Bold",
            "header_font": "Helvetica-Bold",
            "job_title_font": "Helvetica-Bold",
            "body_font": "Helvetica",
            "name_size": 22,
            "contact_size": 10.5,
            "header_size": 11.5,
            "job_title_size": 11,
            "body_size": 10.75
        },
        "executive_compact": {
            "accent_color": "#111111",
            "name_font": "Helvetica-Bold",
            "header_font": "Helvetica-Bold",
            "job_title_font": "Helvetica-Bold",
            "body_font": "Helvetica",
            "name_size": 20,
            "contact_size": 10.5,
            "header_size": 11.5,
            "job_title_size": 11,
            "body_size": 10.5
        }
    }
    
    return configs.get(template, configs["modern"])

def generate_pdf_directly(resume_text: str, template: str = "executive_compact") -> bytes:
    """Generate clean PDF using ReportLab directly with template-specific styling"""
    print(f"🚀 DIRECT REPORTLAB: Generating PDF from {len(resume_text)} chars with template: {template}")
    
    # Clean the text first - remove duplicates
    cleaned_text = clean_resume_text(resume_text)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    
    # Template-specific colors and fonts
    template_config = get_template_config(template)
    
    # Professional styles with template-specific colors
    styles.add(ParagraphStyle(
        name='Name',
        fontSize=template_config['name_size'],
        textColor=HexColor(template_config['accent_color']),
        spaceAfter=4,
        alignment=1,
        fontName=template_config['name_font']
    ))
    
    styles.add(ParagraphStyle(
        name='Contact',
        fontSize=template_config['contact_size'],
        spaceAfter=8,
        alignment=1,
        fontName=template_config['body_font']
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=template_config['header_size'],
        textColor=HexColor(template_config['accent_color']),
        spaceBefore=10,
        spaceAfter=4,
        fontName=template_config['header_font']
    ))
    
    styles.add(ParagraphStyle(
        name='JobTitle',
        fontSize=template_config['job_title_size'],
        spaceAfter=4,
        fontName=template_config.get('job_title_font', template_config['header_font']),
        textColor=HexColor('#000000')
    ))
    
    styles.add(ParagraphStyle(
        name='Company',
        fontSize=template_config['body_size'],
        spaceAfter=1,
        fontName=template_config['body_font'],
        textColor=HexColor('#666666'),
        alignment=TA_LEFT
    ))
    
    styles.add(ParagraphStyle(
        name='Dates',
        fontSize=template_config['body_size'] - 0.5,
        spaceAfter=1,
        fontName=template_config['body_font'],
        textColor=HexColor('#6b8b6f') if template == 'olive' else HexColor('#666666'),
        alignment=TA_LEFT
    ))
    
    styles.add(ParagraphStyle(
        name='Body',
        fontSize=template_config['body_size'],
        spaceAfter=2,
        fontName=template_config['body_font'],
        lineHeight=template_config['body_size'] * 1.3
    ))
    
    styles.add(ParagraphStyle(
        name='CustomBullet',
        fontSize=template_config['body_size'],
        leftIndent=0,
        spaceAfter=2,
        fontName=template_config['body_font'],
        lineHeight=template_config['body_size'] * 1.3
    ))
    
    story = []
    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    
    # Parse resume structure properly
    parsed_sections = parse_resume_structure(lines)
    
    # Professional header with name and contact
    if parsed_sections.get('name'):
        story.append(Paragraph(parsed_sections['name'], styles['Name']))
        story.append(Spacer(1, 2))
    
    # Add contact info
    if parsed_sections.get('contact'):
        story.append(Paragraph(parsed_sections['contact'], styles['Contact']))
        story.append(Spacer(1, 6))
    
    # Add summary
    if parsed_sections.get('summary'):
        story.append(Paragraph('PROFESSIONAL SUMMARY', styles['SectionHeader']))
        story.append(Spacer(1, 4))
        for para in parsed_sections['summary']:
            story.append(Paragraph(para, styles['Body']))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 6))
    
    # Add experience with professional two-column layout
    if parsed_sections.get('experience'):
        story.append(Paragraph('WORK EXPERIENCE', styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        for job in parsed_sections['experience']:
            # Extract job title, company, and dates
            title_company = job.get('title_company', '')
            dates = job.get('dates', '')
            bullets = job.get('bullets', [])
            
            # Parse title and company
            job_title = ''
            company = ''
            
            if '|' in title_company:
                parts = title_company.split('|')
                job_title = parts[0].strip()
                if len(parts) > 1:
                    company = parts[1].strip()
            elif ' at ' in title_company:
                parts = title_company.split(' at ')
                job_title = parts[0].strip()
                if len(parts) > 1:
                    company = parts[1].strip()
            else:
                job_title = title_company
            
            # Compact single-column layout (ATS-safe, no tables)
            if job_title or company:
                if job_title:
                    story.append(Paragraph(job_title + (f" | {company}" if company else ""), styles['JobTitle']))
                elif company:
                    story.append(Paragraph(company, styles['JobTitle']))
                if dates:
                    story.append(Paragraph(dates, styles['Dates']))
                for bullet in bullets[:5]:  # Limit to 5 bullets per job
                    if bullet.strip():
                        story.append(Paragraph(f"• {bullet.strip()}", styles['CustomBullet']))
                story.append(Spacer(1, 6))
    
    # Add education
    if parsed_sections.get('education'):
        story.append(Paragraph('EDUCATION', styles['SectionHeader']))
        story.append(Spacer(1, 4))
        for edu in parsed_sections['education']:
            story.append(Paragraph(edu, styles['Body']))
            story.append(Spacer(1, 2))
        story.append(Spacer(1, 6))
    
    # Add skills
    if parsed_sections.get('skills'):
        story.append(Paragraph('SKILLS', styles['SectionHeader']))
        story.append(Spacer(1, 4))
        for skill_line in parsed_sections['skills']:
            story.append(Paragraph(skill_line, styles['Body']))
            story.append(Spacer(1, 2))
    
    # If no structured content was found, add the text in a readable format
    if not any([parsed_sections.get('name'), parsed_sections.get('experience'), 
                parsed_sections.get('education'), parsed_sections.get('skills')]):
        print("⚠️ No structured content found, using fallback text formatting")
        
        # Split the text into manageable chunks
        text_chunks = []
        words = cleaned_text.split()
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            # Break chunks at reasonable lengths (about 10-12 words per line)
            if len(current_chunk) >= 12 or word.endswith('.') or word.endswith('!'):
                text_chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        # Add remaining words
        if current_chunk:
            text_chunks.append(' '.join(current_chunk))
        
        # Add chunks as paragraphs
        story.append(Paragraph('RESUME', styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        for chunk in text_chunks:
            if chunk.strip():
                story.append(Paragraph(chunk.strip(), styles['Body']))
                story.append(Spacer(1, 4))
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    print(f"✅ DIRECT REPORTLAB: Generated {len(pdf_bytes)} bytes")
    return pdf_bytes

def clean_resume_text(text: str) -> str:
    """Remove duplicate content and clean up text"""
    lines = text.split('\n')
    
    # Remove the "LIGHT MODE TAILORED RESUME" header if present
    cleaned_lines = []
    skip_next = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip tailoring mode headers
        if 'LIGHT MODE TAILORED RESUME' in line.upper():
            skip_next = True
            continue
        if skip_next and '---' in line:
            skip_next = False
            continue
        if 'KEYWORD OPTIMIZATION APPLIED' in line:
            break  # Stop before the duplicate section
            
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def parse_resume_structure(lines):
    """Parse resume lines into structured sections - handles text that may be in paragraph form"""
    print(f"🔍 PARSING: Received {len(lines)} lines")
    
    # If we only have 1-2 lines, the text is likely in paragraph form - split it better
    if len(lines) <= 2:
        print("⚠️ Text appears to be in paragraph form, attempting to split by sentences")
        full_text = ' '.join(lines)
        # Split by common resume section indicators
        parts = re.split(r'(Summary|Experience|Education|Skills|Professional Experience|Work Experience)', full_text, flags=re.IGNORECASE)
        lines = []
        for part in parts:
            if part.strip():
                # Split long paragraphs into sentences
                sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', part.strip())
                lines.extend(sentences)
    
    print(f"🔍 After processing: {len(lines)} lines")
    for i, line in enumerate(lines[:10]):  # Show first 10 lines
        print(f"   Line {i}: {line[:100]}...")
    
    sections = {
        'name': '',
        'contact': '',
        'summary': [],
        'experience': [],
        'education': [],
        'skills': []
    }
    
    # Extract name from the very beginning
    full_text = ' '.join(lines)
    name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', full_text)
    if name_match:
        sections['name'] = name_match.group(1)
        print(f"✅ Extracted name: {sections['name']}")
    
    # Extract contact info
    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', full_text)
    phone_match = re.search(r'(\(\d{3}\) \d{3}-\d{4})', full_text)
    location_match = re.search(r'(Atlanta, GA)', full_text)
    
    contact_parts = []
    if location_match:
        contact_parts.append(location_match.group(1))
    if email_match:
        contact_parts.append(email_match.group(1))
    if phone_match:
        contact_parts.append(phone_match.group(1))
    
    if contact_parts:
        sections['contact'] = ' • '.join(contact_parts)
        print(f"✅ Extracted contact: {sections['contact']}")
    
    # Extract summary
    summary_match = re.search(r'Summary\s+(.+?)(?=Experience|Education|Skills|$)', full_text, re.DOTALL | re.IGNORECASE)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        # Split into sentences for better formatting
        summary_sentences = re.split(r'(?<=[.!?])\s+', summary_text)
        sections['summary'] = [s.strip() for s in summary_sentences if s.strip()]
        print(f"✅ Extracted summary: {len(sections['summary'])} sentences")
    
    # Extract experience section
    exp_match = re.search(r'(?:Professional\s+)?Experience\s+(.+?)(?=Education|Skills|Personal Projects|$)', full_text, re.DOTALL | re.IGNORECASE)
    if exp_match:
        exp_text = exp_match.group(1).strip()
        print(f"✅ Found experience section: {len(exp_text)} chars")
        
        # Look for job titles and companies - be more selective
        job_indicators = [
            r'Product Manager.*?(?:June|May|January|February|March|April|July|August|September|October|November|December)\s+\d{4}[–-](?:Present|\w+\s+\d{4})',
            r'(?:Senior|Lead|Junior)?\s*(?:Product Manager|Software Engineer|Developer|Analyst).*?(?:at|@)\s+[A-Z][a-zA-Z\s&,]+',
            r'[A-Z][a-zA-Z\s&,]+\s+(?:June|May|January|February|March|April|July|August|September|October|November|December)\s+\d{4}[–-](?:Present|\w+\s+\d{4})'
        ]
        
        jobs_found = []
        for pattern in job_indicators:
            matches = re.finditer(pattern, exp_text, re.IGNORECASE)
            for match in matches:
                job_text = match.group(0)
                if len(job_text) > 30:  # Substantial job description
                    jobs_found.append((match.start(), job_text))
        
        # Sort by position and take unique jobs
        jobs_found.sort()
        unique_jobs = []
        last_pos = -1
        
        for pos, job_text in jobs_found:
            if pos > last_pos + 100:  # Avoid overlapping matches
                unique_jobs.append(job_text)
                last_pos = pos
        
        print(f"🔍 Found {len(unique_jobs)} unique job entries")
        
        # Process each unique job
        for i, job_text in enumerate(unique_jobs[:5]):  # Limit to 5 jobs max
            job = {
                'title_company': job_text[:100],  # First 100 chars as title/company
                'dates': '',
                'bullets': []
            }
            
            # Extract dates from the job text
            date_match = re.search(r'((?:January|February|March|April|May|June|July|August|September|October|November|December|\d+)\s+\d{4}[–-](?:Present|\w+\s+\d{4}))', job_text)
            if date_match:
                job['dates'] = date_match.group(1)
            
            # Find bullet points after this job (look ahead in the text)
            job_end_pos = exp_text.find(job_text) + len(job_text)
            next_job_pos = len(exp_text)
            
            # Find where next job starts
            if i + 1 < len(unique_jobs):
                next_job_pos = exp_text.find(unique_jobs[i + 1])
            
            # Extract text between this job and next job
            job_section = exp_text[job_end_pos:next_job_pos]
            
            # Extract bullets from this section
            bullet_matches = re.findall(r'●\s*([^●]+)', job_section)
            for bullet in bullet_matches[:8]:  # Max 8 bullets per job
                clean_bullet = bullet.strip()
                if len(clean_bullet) > 20:  # Substantial bullet
                    job['bullets'].append(clean_bullet)
            
            if job['title_company']:
                sections['experience'].append(job)
                print(f"   Job {i+1}: {job['title_company'][:50]}... ({len(job['bullets'])} bullets)")
        
        print(f"✅ Final experience entries: {len(sections['experience'])}")
        
        print(f"✅ Extracted {len(sections['experience'])} experience entries")
    
    # Extract education
    edu_match = re.search(r'Education\s+(.+?)(?=Skills|Personal Projects|$)', full_text, re.DOTALL | re.IGNORECASE)
    if edu_match:
        edu_text = edu_match.group(1).strip()
        # Split by degree indicators
        edu_parts = re.split(r'●', edu_text)
        for part in edu_parts:
            if part.strip() and len(part.strip()) > 10:
                sections['education'].append(part.strip())
        print(f"✅ Extracted {len(sections['education'])} education entries")
    
    # Extract skills
    skills_match = re.search(r'Skills\s+(.+?)(?=Personal Projects|$)', full_text, re.DOTALL | re.IGNORECASE)
    if skills_match:
        skills_text = skills_match.group(1).strip()
        # Split by categories or bullets
        skill_parts = re.split(r'●', skills_text)
        for part in skill_parts:
            if part.strip() and len(part.strip()) > 5:
                sections['skills'].append(part.strip())
        print(f"✅ Extracted {len(sections['skills'])} skill entries")
    
    return sections
