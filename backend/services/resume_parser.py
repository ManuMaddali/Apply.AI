"""
Resume Parser Service
Comprehensive resume parser that extracts structured information from raw resume text.
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    A comprehensive resume parser that extracts structured information from raw resume text.
    """
    
    def __init__(self):
        """Initialize the resume parser with regex patterns."""
        self._initialize_patterns()
        self._initialize_section_headers()
    
    def _initialize_patterns(self):
        """Initialize all regex patterns for parsing."""
        # Contact Information Patterns
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        self.phone_pattern = re.compile(
            r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})|'
            r'(?:\+?1[-.\s]?)?([0-9]{3})[-.\s]([0-9]{3})[-.\s]([0-9]{4})|'
            r'\b\d{10}\b',
            re.IGNORECASE
        )
        
        self.linkedin_pattern = re.compile(
            r'(?:linkedin\.com/in/|linkedin\.com/pub/|linkedin:|linkedin\s*[-:]\s*)([A-Za-z0-9-]+)|'
            r'(?:www\.)?linkedin\.com/[^\s]+',
            re.IGNORECASE
        )
        
        self.github_pattern = re.compile(
            r'(?:github\.com/|github:|github\s*[-:]\s*)([A-Za-z0-9-]+)',
            re.IGNORECASE
        )
        
        # Location Pattern
        self.location_pattern = re.compile(
            r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s*([A-Z]{2})\b|'
            r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)|'
            r'(?:Location|Address|Based in|Located in):\s*([^\n]+)',
            re.MULTILINE
        )
        
        # Date Patterns
        self.date_pattern = re.compile(
            r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
            r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            r'[\s,]*(?:\d{4}|\d{2})|'
            r'\d{1,2}/\d{4}|\d{4}[-/]\d{1,2}|'
            r'(?:Present|Current|Now|Ongoing)',
            re.IGNORECASE
        )
        
        # Degree Patterns
        self.degree_pattern = re.compile(
            r'\b(?:Bachelor\'?s?|B\.?S\.?|B\.?A\.?|Master\'?s?|M\.?S\.?|M\.?A\.?|'
            r'M\.?B\.?A\.?|Ph\.?D\.?|Doctor(?:ate)?|Associate\'?s?|A\.?S\.?|A\.?A\.?)\b',
            re.IGNORECASE
        )
        
        # Company and Job Title Indicators
        self.company_indicators = re.compile(
            r'\b(?:Inc\.?|LLC|Ltd\.?|Corp(?:oration)?|Company|Co\.?|Group|Technologies|'
            r'Services|Solutions|Systems|Software|Consulting|Partners|Associates)\b',
            re.IGNORECASE
        )
        
        self.title_indicators = re.compile(
            r'\b(?:Engineer|Developer|Manager|Director|Analyst|Specialist|Consultant|'
            r'Coordinator|Administrator|Designer|Architect|Lead|Senior|Junior|Associate|'
            r'Executive|President|VP|Chief|Head|Supervisor|Team Lead|Intern|Trainee)\b',
            re.IGNORECASE
        )
    
    def _initialize_section_headers(self):
        """Initialize common section header patterns."""
        self.section_headers = {
            'summary': re.compile(
                r'^(?:Summary|Professional Summary|Executive Summary|Profile|'
                r'Career Summary|Objective|Career Objective|About Me?|Overview)'
                r'(?:\s*[-:])?',
                re.IGNORECASE | re.MULTILINE
            ),
            'experience': re.compile(
                r'^(?:Experience|Professional Experience|Work Experience|Employment|'
                r'Work History|Career History|Professional Background|Employment History)'
                r'(?:\s*[-:])?',
                re.IGNORECASE | re.MULTILINE
            ),
            'education': re.compile(
                r'^(?:Education|Academic Background|Academic Qualifications|'
                r'Educational Background|Qualifications|Academic History)'
                r'(?:\s*[-:])?',
                re.IGNORECASE | re.MULTILINE
            ),
            'skills': re.compile(
                r'^(?:Skills|Technical Skills|Core Competencies|Competencies|'
                r'Key Skills|Professional Skills|Areas of Expertise|Technologies|'
                r'Programming Languages|Tools|Certifications)'
                r'(?:\s*[-:])?',
                re.IGNORECASE | re.MULTILINE
            ),
            'projects': re.compile(
                r'^(?:Projects|Key Projects|Notable Projects|Personal Projects|'
                r'Academic Projects|Professional Projects)'
                r'(?:\s*[-:])?',
                re.IGNORECASE | re.MULTILINE
            ),
            'awards': re.compile(
                r'^(?:Awards|Achievements|Honors|Recognition|Accomplishments|'
                r'Awards and Honors|Certifications and Awards)'
                r'(?:\s*[-:])?',
                re.IGNORECASE | re.MULTILINE
            )
        }
    
    def parse(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse raw resume text and extract structured information.
        
        Args:
            resume_text: Raw text content of the resume
            
        Returns:
            Dictionary containing parsed resume information
        """
        try:
            if not resume_text or not resume_text.strip():
                raise ValueError("Resume text is empty or contains only whitespace")
            
            # Clean and normalize the text
            resume_text = self._clean_text(resume_text)
            
            # Extract sections
            sections = self._extract_sections(resume_text)
            
            # Parse individual components
            parsed_data = {
                'name': self._extract_name(resume_text),
                'email': self._extract_email(resume_text),
                'phone': self._extract_phone(resume_text),
                'location': self._extract_location(resume_text),
                'linkedin': self._extract_linkedin(resume_text),
                'github': self._extract_github(resume_text),
                'summary': self._extract_summary(sections),
                'experience': self._extract_experience(sections),
                'education': self._extract_education(sections),
                'skills': self._extract_skills(sections),
                'projects': self._extract_projects(sections),
                'awards': self._extract_awards(sections)
            }
            
            # Post-process and validate
            parsed_data = self._post_process(parsed_data)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return self._get_empty_structure()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize the resume text."""
        # Don't over-clean - preserve the structure
        # Just normalize line breaks and trim whitespace
        text = text.replace('\r\n', '\n')  # Normalize Windows line breaks
        text = text.replace('\r', '\n')    # Normalize Mac line breaks
        # Remove tabs but preserve other whitespace
        text = text.replace('\t', '    ')
        return text.strip()
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from the resume."""
        sections = {}
        lines = text.split('\n')
        
        # Find all section headers and their positions
        header_positions = []
        for section_name, pattern in self.section_headers.items():
            for i, line in enumerate(lines):
                if pattern.search(line):
                    header_positions.append((i, section_name, line))
        
        # Sort by position
        header_positions.sort(key=lambda x: x[0])
        
        # Extract content for each section
        for i, (pos, section_name, header_line) in enumerate(header_positions):
            start = pos + 1
            end = header_positions[i + 1][0] if i + 1 < len(header_positions) else len(lines)
            
            # Get section content
            section_content = '\n'.join(lines[start:end])
            sections[section_name] = section_content.strip()
        
        # If no sections were found, treat the entire text as content
        if not sections:
            sections['content'] = text
        
        return sections
    
    def _extract_name(self, text: str) -> str:
        """Extract the candidate's name from the resume."""
        try:
            lines = text.split('\n')
            
            # Look for the first non-empty line that doesn't contain contact info
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if not line:
                    continue
                
                # Skip lines with contact information patterns
                if (self.email_pattern.search(line) or 
                    self.phone_pattern.search(line) or
                    re.search(r'\b(?:http|www\.)', line, re.IGNORECASE)):
                    continue
                
                # If line contains both name-like text and contact info (like email), extract just the name
                if '|' in line or '@' in line:
                    # Try to extract name before the first separator
                    parts = re.split(r'[|@]', line)
                    if parts[0].strip():
                        potential_name = parts[0].strip()
                        # Check if it looks like a name
                        if re.match(r"^[A-Za-z][A-Za-z\s\-\.'&]+$", potential_name) and len(potential_name.split()) <= 5:
                            return potential_name
                    continue
                
                # Skip section headers
                if any(pattern.search(line) for pattern in self.section_headers.values()):
                    continue
                
                # Check if it looks like a name (now includes apostrophes and ampersands)
                if re.match(r"^[A-Za-z][A-Za-z\s\-\.'&]+$", line) and len(line.split()) <= 5:
                    return line
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting name: {str(e)}")
            return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from the resume."""
        try:
            match = self.email_pattern.search(text)
            return match.group(0) if match else ""
        except Exception as e:
            logger.error(f"Error extracting email: {str(e)}")
            return ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from the resume."""
        try:
            match = self.phone_pattern.search(text)
            if match:
                # Clean up the phone number
                phone = match.group(0)
                # Remove non-numeric characters except + for international
                phone = re.sub(r'[^\d+]', '', phone)
                return phone
            return ""
        except Exception as e:
            logger.error(f"Error extracting phone: {str(e)}")
            return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location from the resume."""
        try:
            # Look in the first few lines (header area)
            header_text = '\n'.join(text.split('\n')[:10])
            
            match = self.location_pattern.search(header_text)
            if match:
                # Return the first non-None group
                for group in match.groups():
                    if group:
                        return group.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting location: {str(e)}")
            return ""
    
    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile from the resume."""
        try:
            match = self.linkedin_pattern.search(text)
            if match:
                # Extract just the profile ID or full URL
                if match.group(1):
                    return f"linkedin.com/in/{match.group(1)}"
                return match.group(0)
            return ""
        except Exception as e:
            logger.error(f"Error extracting LinkedIn: {str(e)}")
            return ""
    
    def _extract_github(self, text: str) -> str:
        """Extract GitHub profile from the resume."""
        try:
            match = self.github_pattern.search(text)
            if match:
                if match.group(1):
                    return f"github.com/{match.group(1)}"
                return match.group(0)
            return ""
        except Exception as e:
            logger.error(f"Error extracting GitHub: {str(e)}")
            return ""
    
    def _extract_summary(self, sections: Dict[str, str]) -> str:
        """Extract professional summary from the resume."""
        try:
            if 'summary' in sections:
                return sections['summary']
            
            # If no dedicated summary section, look for it in content
            if 'content' in sections:
                lines = sections['content'].split('\n')
                # Look for paragraph-like text near the beginning
                for i, line in enumerate(lines[:20]):
                    if len(line) > 100:  # Likely a summary paragraph
                        return line
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting summary: {str(e)}")
            return ""
    
    def _extract_experience(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract work experience from the resume."""
        try:
            experience_list = []
            
            if 'experience' not in sections:
                return experience_list
            
            text = sections['experience']
            
            # Split by common delimiters for experience entries
            entries = re.split(r'\n(?=[A-Z])', text)
            
            for entry in entries:
                if not entry.strip():
                    continue
                
                exp_dict = self._parse_experience_entry(entry)
                if exp_dict and (exp_dict.get('title') or exp_dict.get('company')):
                    experience_list.append(exp_dict)
            
            return experience_list
            
        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}")
            return []
    
    def _parse_experience_entry(self, entry: str) -> Dict[str, Any]:
        """Parse a single experience entry."""
        try:
            lines = entry.strip().split('\n')
            exp_dict = {
                'title': '',
                'company': '',
                'dates': '',
                'location': '',
                'responsibilities': []
            }
            
            # First line often contains title and/or company
            if lines:
                first_line = lines[0]
                
                # Check for title indicators
                if self.title_indicators.search(first_line):
                    # Extract title and company
                    parts = re.split(r'\s+at\s+|\s+@\s+|\s+-\s+|\s+\|\s+', first_line, maxsplit=1)
                    exp_dict['title'] = parts[0].strip()
                    if len(parts) > 1:
                        exp_dict['company'] = parts[1].strip()
                elif self.company_indicators.search(first_line):
                    exp_dict['company'] = first_line.strip()
                else:
                    exp_dict['title'] = first_line.strip()
            
            # Look for dates
            for line in lines:
                dates = self.date_pattern.findall(line)
                if len(dates) >= 1:
                    exp_dict['dates'] = ' - '.join(dates[:2]) if len(dates) >= 2 else dates[0]
                    break
            
            # Extract responsibilities (bullet points or sentences)
            for line in lines[1:]:
                line = line.strip()
                if line and not self.date_pattern.search(line):
                    # Remove bullet point markers
                    line = re.sub(r'^[-•·▪■□*]\s*', '', line)
                    if line:
                        exp_dict['responsibilities'].append(line)
            
            return exp_dict
            
        except Exception as e:
            logger.error(f"Error parsing experience entry: {str(e)}")
            return {}
    
    def _extract_education(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract education information from the resume."""
        try:
            education_list = []
            
            if 'education' not in sections:
                return education_list
            
            text = sections['education']
            
            # Split by line breaks or common delimiters
            entries = re.split(r'\n(?=[A-Z])', text)
            
            for entry in entries:
                if not entry.strip():
                    continue
                
                edu_dict = self._parse_education_entry(entry)
                if edu_dict and (edu_dict.get('degree') or edu_dict.get('institution')):
                    education_list.append(edu_dict)
            
            return education_list
            
        except Exception as e:
            logger.error(f"Error extracting education: {str(e)}")
            return []
    
    def _parse_education_entry(self, entry: str) -> Dict[str, Any]:
        """Parse a single education entry."""
        try:
            lines = entry.strip().split('\n')
            edu_dict = {
                'degree': '',
                'field': '',
                'institution': '',
                'year': '',
                'gpa': ''
            }
            
            # Look for degree
            for line in lines:
                degree_match = self.degree_pattern.search(line)
                if degree_match:
                    edu_dict['degree'] = degree_match.group(0)
                    
                    # Extract field of study (text after degree)
                    remaining = line[degree_match.end():].strip()
                    if remaining and remaining[0] in ['i', 'o']:  # in/of
                        field_match = re.search(r'(?:in|of)\s+([^,\n]+)', remaining, re.IGNORECASE)
                        if field_match:
                            edu_dict['field'] = field_match.group(1).strip()
                    break
            
            # Look for institution (often contains University, College, Institute, School)
            for line in lines:
                inst_match = re.search(
                    r'(?:University|College|Institute|School|Academy)\s+(?:of\s+)?[A-Za-z\s]+|'
                    r'[A-Z][A-Za-z\s]+\s+(?:University|College|Institute|School)',
                    line,
                    re.IGNORECASE
                )
                if inst_match:
                    edu_dict['institution'] = inst_match.group(0).strip()
                    break
            
            # Look for year
            for line in lines:
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match:
                    edu_dict['year'] = year_match.group(0)
                    break
            
            # Look for GPA
            for line in lines:
                gpa_match = re.search(r'(?:GPA|Grade)[\s:]*([0-9]\.[0-9]+)', line, re.IGNORECASE)
                if gpa_match:
                    edu_dict['gpa'] = gpa_match.group(1)
                    break
            
            return edu_dict
            
        except Exception as e:
            logger.error(f"Error parsing education entry: {str(e)}")
            return {}
    
    def _extract_skills(self, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract skills from the resume."""
        try:
            skills_dict = {
                'technical': [],
                'languages': [],
                'tools': [],
                'soft': [],
                'other': []
            }
            
            if 'skills' not in sections:
                return skills_dict
            
            text = sections['skills']
            
            # Common skill categories
            technical_keywords = ['programming', 'technical', 'technologies', 'frameworks', 'databases']
            language_keywords = ['languages', 'programming languages']
            tool_keywords = ['tools', 'software', 'platforms', 'ide']
            soft_keywords = ['soft skills', 'interpersonal', 'communication', 'leadership']
            
            # Split by lines and process
            lines = text.split('\n')
            current_category = 'other'
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is a category header
                line_lower = line.lower()
                if any(kw in line_lower for kw in technical_keywords):
                    current_category = 'technical'
                    continue
                elif any(kw in line_lower for kw in language_keywords):
                    current_category = 'languages'
                    continue
                elif any(kw in line_lower for kw in tool_keywords):
                    current_category = 'tools'
                    continue
                elif any(kw in line_lower for kw in soft_keywords):
                    current_category = 'soft'
                    continue
                
                # Extract skills from the line
                # Remove bullet points and split by common delimiters
                line = re.sub(r'^[-•·▪■□*]\s*', '', line)
                skills = re.split(r'[,;|•·▪■□]', line)
                
                for skill in skills:
                    skill = skill.strip()
                    if skill and len(skill) > 1:
                        skills_dict[current_category].append(skill)
            
            # If no categorization was possible, put everything in 'other'
            if not any(skills_dict[cat] for cat in ['technical', 'languages', 'tools', 'soft']):
                all_skills = []
                for line in lines:
                    line = re.sub(r'^[-•·▪■□*]\s*', '', line.strip())
                    if line:
                        skills = re.split(r'[,;|•·▪■□]', line)
                        all_skills.extend([s.strip() for s in skills if s.strip()])
                skills_dict['other'] = all_skills
            
            return skills_dict
            
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
            return {'technical': [], 'languages': [], 'tools': [], 'soft': [], 'other': []}
    
    def _extract_projects(self, sections: Dict[str, str]) -> List[Dict[str, str]]:
        """Extract projects from the resume."""
        try:
            projects_list = []
            
            if 'projects' not in sections:
                return projects_list
            
            text = sections['projects']
            
            # Split by common project delimiters
            entries = re.split(r'\n(?=[A-Z])', text)
            
            for entry in entries:
                if not entry.strip():
                    continue
                
                lines = entry.strip().split('\n')
                if lines:
                    project_dict = {
                        'name': lines[0].strip(),
                        'description': ' '.join(lines[1:]).strip() if len(lines) > 1 else ''
                    }
                    
                    # Remove bullet points from description
                    project_dict['description'] = re.sub(r'^[-•·▪■□*]\s*', '', project_dict['description'])
                    
                    if project_dict['name']:
                        projects_list.append(project_dict)
            
            return projects_list
            
        except Exception as e:
            logger.error(f"Error extracting projects: {str(e)}")
            return []
    
    def _extract_awards(self, sections: Dict[str, str]) -> List[str]:
        """Extract awards and achievements from the resume."""
        try:
            awards_list = []
            
            if 'awards' not in sections:
                return awards_list
            
            text = sections['awards']
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line:
                    # Remove bullet points
                    line = re.sub(r'^[-•·▪■□*]\s*', '', line)
                    if line:
                        awards_list.append(line)
            
            return awards_list
            
        except Exception as e:
            logger.error(f"Error extracting awards: {str(e)}")
            return []
    
    def _post_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process and validate the extracted data."""
        try:
            # Clean up empty strings and None values
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.strip()
                elif isinstance(value, list):
                    # Remove empty items from lists
                    if value and isinstance(value[0], dict):
                        # List of dictionaries
                        data[key] = [item for item in value if any(item.values())]
                    else:
                        # List of strings
                        data[key] = [item for item in value if item and item.strip()]
                elif isinstance(value, dict):
                    # Clean up dictionary values
                    for k, v in value.items():
                        if isinstance(v, list):
                            value[k] = [item for item in v if item and item.strip()]
            
            # Ensure required fields exist
            required_fields = ['name', 'email', 'phone', 'location', 'summary', 
                             'experience', 'education', 'skills']
            for field in required_fields:
                if field not in data:
                    if field in ['experience', 'education']:
                        data[field] = []
                    elif field == 'skills':
                        data[field] = {'technical': [], 'languages': [], 'tools': [], 
                                     'soft': [], 'other': []}
                    else:
                        data[field] = ''
            
            return data
            
        except Exception as e:
            logger.error(f"Error in post-processing: {str(e)}")
            return data
    
    def _get_empty_structure(self) -> Dict[str, Any]:
        """Return an empty resume structure."""
        return {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'github': '',
            'summary': '',
            'experience': [],
            'education': [],
            'skills': {
                'technical': [],
                'languages': [],
                'tools': [],
                'soft': [],
                'other': []
            },
            'projects': [],
            'awards': []
        }
    
    def validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate the parsed resume data and return validation errors.
        
        Args:
            data: Parsed resume data
            
        Returns:
            Dictionary of validation errors by field
        """
        errors = {}
        
        # Check required fields
        if not data.get('name'):
            errors.setdefault('name', []).append('Name is required')
        
        if not data.get('email'):
            errors.setdefault('email', []).append('Email is required')
        elif not self.email_pattern.match(data['email']):
            errors.setdefault('email', []).append('Invalid email format')
        
        # Validate phone if present
        if data.get('phone'):
            # Check if it's a valid phone format
            if not re.match(r'^\+?\d{10,15}$', re.sub(r'[^\d+]', '', data['phone'])):
                errors.setdefault('phone', []).append('Invalid phone number format')
        
        # Check for at least some content
        if (not data.get('experience') and 
            not data.get('education') and 
            not data.get('summary')):
            errors.setdefault('content', []).append(
                'Resume must contain at least experience, education, or summary'
            )
        
        return errors


# Example usage and testing
if __name__ == "__main__":
    # Sample resume text for testing
    sample_resume = """
    John Doe
    john.doe@email.com | (555) 123-4567 | New York, NY
    linkedin.com/in/johndoe | github.com/johndoe
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years developing scalable web applications.
    Proven track record of delivering high-quality solutions and leading technical teams.
    
    WORK EXPERIENCE
    
    Senior Software Engineer at Tech Corp
    January 2020 - Present
    • Led development of microservices architecture serving 1M+ users
    • Mentored junior developers and conducted code reviews
    • Improved system performance by 40% through optimization
    
    Software Developer at StartupXYZ
    June 2018 - December 2019
    • Built RESTful APIs using Python and Flask
    • Implemented CI/CD pipelines using Jenkins and Docker
    • Collaborated with cross-functional teams in Agile environment
    
    EDUCATION
    
    Bachelor of Science in Computer Science
    University of Technology
    2018
    GPA: 3.8/4.0
    
    SKILLS
    Programming Languages: Python, JavaScript, Java, SQL
    Frameworks: Django, Flask, React, Node.js
    Tools: Docker, Kubernetes, Jenkins, Git
    Databases: PostgreSQL, MongoDB, Redis
    
    PROJECTS
    
    E-commerce Platform
    Developed a full-stack e-commerce solution with payment integration
    
    Task Management System
    Built a collaborative task management tool for remote teams
    
    AWARDS
    Employee of the Year 2021
    Best Innovation Award 2020
    Dean's List 2016-2018
    """
    
    # Test the parser
    parser = ResumeParser()
    result = parser.parse(sample_resume)
    
    # Print results
    import json
    print(json.dumps(result, indent=2))
    
    # Validate the parsed data
    validation_errors = parser.validate_parsed_data(result)
    if validation_errors:
        print("\nValidation Errors:")
        print(json.dumps(validation_errors, indent=2))
    else:
        print("\nValidation: All checks passed!")
