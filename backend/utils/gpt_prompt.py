import os
import openai
import re
from typing import Optional, Dict, Any, Set
from dotenv import load_dotenv

load_dotenv()

class GPTProcessor:
    """Fallback GPT processor when LangChain is not available"""
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=api_key)
    
    def _detect_existing_sections(self, resume_text: str) -> Set[str]:
        """
        Robustly detect existing sections in a resume.
        Returns a set of normalized section names that exist.
        """
        existing_sections = set()
        text_lower = resume_text.lower()
        
        # Comprehensive section patterns - covers all common variations
        section_patterns = {
            'summary': [
                r'\b(professional\s+summary|summary|career\s+summary|profile|objective|career\s+objective|professional\s+profile|executive\s+summary|personal\s+statement|overview)\b',
                r'\b(qualifications\s+summary|career\s+highlights|professional\s+overview)\b'
            ],
            'skills': [
                r'\b(skills|technical\s+skills|core\s+competencies|competencies|expertise|technical\s+expertise|key\s+skills|professional\s+skills)\b',
                r'\b(technologies|tools\s+and\s+technologies|programming\s+languages|software\s+skills|technical\s+proficiencies)\b',
                r'\b(core\s+skills|relevant\s+skills|technical\s+competencies)\b'
            ],
            'education': [
                r'\b(education|academic\s+background|educational\s+background|qualifications|academic\s+qualifications)\b',
                r'\b(degrees|certifications\s+and\s+education|training\s+and\s+education|academic\s+credentials)\b',
                r'\b(university|college|bachelor|master|phd|degree)\b'
            ]
        }
        
        # Check each section type
        for section_type, patterns in section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    existing_sections.add(section_type)
                    break  # Found this section type, move to next
        
        # Additional heuristic checks for edge cases
        lines = resume_text.split('\n')
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            line_lower = line_clean.lower()
            
            # Check for section headers (lines that are short, uppercase, or end with colon)
            if len(line_clean) < 50 and (
                line_clean.isupper() or 
                line_clean.endswith(':') or 
                (len(line_clean.split()) <= 3 and any(word.capitalize() == word for word in line_clean.split()))
            ):
                # Check if it matches any section patterns
                for section_type, patterns in section_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line_lower):
                            existing_sections.add(section_type)
                            break
        
        # Special detection for common degree patterns (for education)
        degree_patterns = [
            r'\b(b\.?s\.?|bachelor|b\.?a\.?|master|m\.?s\.?|m\.?a\.?|phd|ph\.?d\.?|doctorate|mba)\b',
            r'\b(associate|diploma|certificate)\b.*\b(degree|program)\b',
            r'\b\d{4}\b.*\b(graduated|graduation|degree|university|college)\b'
        ]
        
        for pattern in degree_patterns:
            if re.search(pattern, text_lower):
                existing_sections.add('education')
                break
        
        return existing_sections

    def tailor_resume(self, resume_text: str, job_description: str, job_title: str = "Product Manager", optional_sections: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Tailor resume using direct OpenAI API call"""
        try:
            if optional_sections is None:
                optional_sections = {}
            prompt = self._create_tailoring_prompt(resume_text, job_description, job_title, optional_sections)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an elite resume transformation specialist who dramatically morphs resumes to perfectly match job descriptions. You understand that modern job seekers need resumes that speak DIRECTLY to each specific role, using the exact language, metrics, and focus areas that hiring managers are looking for.

YOUR MISSION: Transform this resume into a PERFECT match for the target job by aggressively rewriting every single bullet point to align with what the employer wants to see. You maintain the core truth while completely reimagining how it's presented.

CRITICAL FORMATTING RULE: Output in PLAIN TEXT only. No markdown, no asterisks (**), no special formatting. Match the exact format style of the original resume."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=8000,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content
            
            # Log the AI response for debugging
            print("=" * 80)
            print("🤖 AI GENERATED RESPONSE:")
            print("=" * 80)
            print(repr(ai_response))
            print("=" * 80)
            print("📝 AI RESPONSE (FORMATTED):")
            print("=" * 80)
            print(ai_response)
            print("=" * 80)
            
            return ai_response
            
        except Exception as e:
            print(f"Error calling GPT: {str(e)}")
            return None

    def generate_cover_letter(self, resume_text: str, job_description: str, job_title: str = "", cover_letter_options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a personalized cover letter using OpenAI API"""
        try:
            if cover_letter_options is None:
                cover_letter_options = {}
            prompt = self._create_cover_letter_prompt(resume_text, job_description, job_title, cover_letter_options)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional cover letter specialist who creates compelling, personalized cover letters that perfectly complement tailored resumes. Your cover letters are engaging, authentic, and demonstrate genuine interest in both the role and the company.

YOUR MISSION: Create a cover letter that tells a compelling story connecting the candidate's background to this specific opportunity. The cover letter should feel personal, show research about the role, and position the candidate as the ideal fit.

FORMATTING RULES:
- Write in a professional business letter format
- Use proper paragraph structure with clear spacing
- Keep it concise but impactful (3-4 paragraphs maximum)
- NO placeholder text like [Your Name] or [Company Name] 
- Write as if it's a complete letter ready to send
- Use proper greeting and closing"""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating cover letter: {str(e)}")
            return None
    
    def _create_tailoring_prompt(self, resume_text: str, job_description: str, job_title: str = "", optional_sections: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a prompt for AGGRESSIVE resume transformation with intelligent section handling
        """
        
        # Handle optional sections
        if optional_sections is None:
            optional_sections = {}
        include_summary = optional_sections.get("includeSummary", False)
        include_skills = optional_sections.get("includeSkills", False)
        include_education = optional_sections.get("includeEducation", False)
        education_details = optional_sections.get("educationDetails", {})
        
        # Detect existing sections
        existing_sections = self._detect_existing_sections(resume_text)
        
        # Build intelligent optional sections instructions
        optional_instructions = ""
        
        if include_summary:
            if 'summary' in existing_sections:
                optional_instructions += """
## 📝 PROFESSIONAL SUMMARY (ENHANCE EXISTING):
The resume already has a professional summary section. ENHANCE and TRANSFORM it to be compelling and perfectly tailored for THIS role:
- Completely rewrite using keywords from the job description
- Highlight years of experience in relevant areas mentioned in the job posting
- Position them as already doing this type of work
- End with a value proposition that matches company needs
- Keep it as the top section but make it dramatically better

"""
            else:
                optional_instructions += """
## 📝 PROFESSIONAL SUMMARY (ADD NEW):
Add a compelling 3-4 line professional summary at the top that positions the candidate as perfect for THIS role:
- Use keywords from the job description
- Highlight years of experience in relevant areas
- Position them as already doing this type of work
- End with a value proposition that matches company needs

"""
        
        if include_education:
            education_info = ""
            if education_details.get("degree"):
                education_info += f"Degree: {education_details['degree']}\n"
            if education_details.get("institution"):
                education_info += f"Institution: {education_details['institution']}\n"
            if education_details.get("year"):
                education_info += f"Graduation Year: {education_details['year']}\n"
            if education_details.get("gpa"):
                education_info += f"GPA: {education_details['gpa']}\n"
            
            if 'education' in existing_sections:
                optional_instructions += f"""
## 🎓 EDUCATION SECTION (ENHANCE EXISTING):
The resume already has education information. ENHANCE and IMPROVE the existing education section:
- Keep all existing education but reformat professionally
- Add any missing details from the provided information: {education_info if education_info else "No additional details provided"}
- Emphasize aspects most relevant to the target role
- Ensure proper formatting and presentation
- DO NOT duplicate education entries

"""
            else:
                optional_instructions += f"""
## 🎓 EDUCATION SECTION (ADD NEW):
Add an education section with the following information:
{education_info if education_info else "Use relevant educational background that supports the role"}

"""
        
        if include_skills:
            if 'skills' in existing_sections:
                optional_instructions += """
## 🛠️ SKILLS SECTION (ENHANCE EXISTING):
The resume already has a skills section. ENHANCE and TRANSFORM it to be perfectly aligned with this job:
- Keep existing relevant skills but reorganize and prioritize based on job requirements
- Add technical skills mentioned in the job posting (in order of importance)
- Include programming languages, tools, platforms from the job description
- Emphasize soft skills that the role emphasizes
- Add industry-specific competencies mentioned in the job posting
- Group skills logically (Technical, Leadership, Domain Expertise, etc.)
- Remove outdated or irrelevant skills and replace with job-relevant ones

"""
            else:
                optional_instructions += """
## 🛠️ SKILLS SECTION (ADD NEW):
Add a skills section that includes:
- Technical skills mentioned in the job posting (in order of importance)
- Programming languages, tools, platforms from the job description
- Soft skills that the role emphasizes
- Industry-specific competencies
- Group skills logically (Technical, Leadership, Domain Expertise, etc.)

"""
        
        # Add section detection information to the prompt
        detected_sections_info = ""
        if existing_sections:
            detected_sections_info = f"""
⚠️ IMPORTANT - EXISTING SECTIONS DETECTED:
The original resume already contains these sections: {', '.join(existing_sections).upper()}
- For existing sections: ENHANCE and IMPROVE them, do not duplicate
- For new sections: ADD them in appropriate locations
- Maintain the overall structure while improving content quality

"""
        
        return f"""
🎯 TRANSFORM THIS RESUME TO BE A PERFECT MATCH FOR THE JOB

YOUR GOAL: Take every single bullet point and DRAMATICALLY rewrite it to speak directly to what this employer wants. Don't just tweak - TRANSFORM.

{detected_sections_info}

⚠️ CRITICAL FORMATTING REQUIREMENTS:
- Output in CLEAN, WELL-SPACED format
- Use proper line breaks and spacing between sections
- Each bullet point should be on its own line with proper indentation
- Add blank lines between major sections for readability
- Use consistent formatting throughout
- NO markdown syntax (**bold**, *italic*) - use plain text only
- Maintain professional resume structure
- Always leave one blank line between the name and contact information
- Use consistent bullet points (•) with uniform spacing
- Do not mix tabs and spaces; use 2 spaces for bullet indent
- Keep all bullet points vertically aligned
- Add consistent margins between sections

FORMATTING EXAMPLE:
Name
Professional Title
City, State | Email | Phone

[BLANK LINE]

PROFESSIONAL EXPERIENCE

[BLANK LINE]

Company Name | Location
Job Title | Start Date - End Date
• First achievement bullet point with proper spacing
• Second achievement bullet point with clear formatting
• Third achievement showing impact and metrics

[BLANK LINE]

Next Company Name | Location
Job Title | Start Date - End Date
• Achievement one with professional formatting
• Achievement two with clear structure

{optional_instructions}

## 🔥 AGGRESSIVE TAILORING RULES:

1. **COMPLETE TRANSFORMATION OF EACH BULLET**
   - Read what they did → Figure out what skill/experience it demonstrates
   - Rewrite it using the EXACT terminology from the job description
   - Make it sound like they've been doing THIS SPECIFIC JOB already
   - Use the metrics and KPIs mentioned in the job posting

2. **MIRROR THE JOB DESCRIPTION LANGUAGE**
   - If job says "B2B SaaS" → Transform their experience to emphasize B2B SaaS
   - If job wants "data-driven" → Make every achievement data-driven
   - If job needs "cross-functional leadership" → Reframe all teamwork as cross-functional leadership
   - Use their EXACT phrases and keywords throughout

3. **DRAMATIC REFRAMING EXAMPLES:**
   - Original: "Managed product development"
   - Job wants: "Led agile teams in B2B SaaS"
   - Transform to: "Led agile product teams in developing B2B SaaS solutions, driving 40% faster time-to-market"

   - Original: "Worked with engineering team"
   - Job wants: "Cross-functional collaboration"
   - Transform to: "Orchestrated cross-functional collaboration between engineering, design, and GTM teams"

4. **ADD RELEVANT CONTEXT & METRICS**
   - If they managed something → Add impressive metrics (30-50% improvements)
   - If they built something → Emphasize scale and impact
   - If they led something → Highlight team size and business outcomes
   - Make metrics relevant to what the job posting emphasizes

5. **PROPER FORMATTING STRUCTURE:**

   **Header Section:**
   - Name (largest text)
   - Professional title aligned with target role
   - Contact information clearly formatted
   - Proper spacing after header

   **Professional Summary (if requested):**
   - 3-4 impactful lines
   - Proper spacing before and after

   **Experience Section:**
   - Company | Location format
   - Job Title | Date range
   - Bullet points with consistent indentation
   - Blank line between different companies
   - Start each bullet with strong action verbs

   **Skills Section (if requested):**
   - Clear categories
   - Properly spaced skill groups
   - Easy to scan format

   **Education Section (if requested):**
   - Institution | Location
   - Degree | Graduation year
   - Additional details if provided

## 📋 JOB ANALYSIS & TRANSFORMATION:

**Target Job:**
{f"Title: {job_title}" if job_title else ""}

**Job Description to Match:**
{job_description}

**Original Resume to Transform:**
{resume_text}

## 🚀 DELIVERABLE:

Create a resume that looks like it was WRITTEN SPECIFICALLY for this job with PROFESSIONAL FORMATTING:

FORMATTING CHECKLIST:
✅ Proper spacing between sections
✅ Consistent bullet point formatting
✅ Clear section headers
✅ Professional layout structure
✅ Easy to read and scan
✅ Blank lines for visual separation
✅ Consistent indentation

CRITICAL: Process the ENTIRE resume including ALL work experiences, projects - everything. Do not stop after the first role!

REMEMBER:
- Transform aggressively while keeping core truths
- Use their exact language and terminology
- Make it impossible to ignore with CLEAN formatting
- Professional structure with proper spacing
- NO generic bullets - everything tailored to THIS job
- COMPLETE THE ENTIRE RESUME - all sections, all roles
- RESPECT the optional section preferences (enhance existing, add new as needed)
- NEVER DUPLICATE SECTIONS - enhance what exists, add what's missing
- ENSURE EXCELLENT VISUAL FORMATTING

Return ONLY the transformed resume text with proper formatting, starting with contact information.
"""

    def _create_cover_letter_prompt(self, resume_text: str, job_description: str, job_title: str = "", cover_letter_options: Optional[Dict[str, Any]] = None) -> str:
        """Create a prompt for generating personalized cover letters"""
        
        # Handle cover letter options
        if cover_letter_options is None:
            cover_letter_options = {}
        cover_letter_details = cover_letter_options.get("coverLetterDetails", {})
        tone = cover_letter_details.get("tone", "professional")
        emphasize = cover_letter_details.get("emphasize", "experience")
        additional_info = cover_letter_details.get("additionalInfo", "")
        
        # Tone guidelines
        tone_guidelines = {
            "professional": "Maintain a formal, business-appropriate tone throughout. Use sophisticated language and demonstrate professionalism.",
            "enthusiastic": "Show genuine excitement and passion for the role and company. Use energetic language while remaining professional.",
            "confident": "Display strong confidence in your abilities and value proposition. Be assertive about your qualifications and fit.",
            "friendly": "Use a warm, approachable tone that shows personality while maintaining professionalism. Be personable and authentic."
        }
        
        # Emphasis guidelines
        emphasis_guidelines = {
            "experience": "Focus heavily on relevant work experience and professional accomplishments. Highlight career progression and impact.",
            "skills": "Emphasize technical abilities, competencies, and skill sets that directly match the job requirements.",
            "achievements": "Showcase specific accomplishments, awards, recognitions, and measurable successes.",
            "education": "Highlight educational background, relevant coursework, academic achievements, and learning experiences."
        }
        
        return f"""
📝 CREATE A COMPELLING COVER LETTER

YOUR MISSION: Write a personalized cover letter that perfectly complements the tailored resume and positions this candidate as the ideal choice for the role.

## 🎯 COVER LETTER REQUIREMENTS:

**TONE:** {tone_guidelines.get(tone, tone_guidelines["professional"])}

**PRIMARY FOCUS:** {emphasis_guidelines.get(emphasize, emphasis_guidelines["experience"])}

**STRUCTURE:**
1. **Opening Paragraph:**
   - Hook the reader with genuine interest in the specific role
   - Briefly mention how you learned about the opportunity
   - Provide a compelling reason why you're interested in THIS company/role

2. **Body Paragraph(s):**
   - Connect your background to the job requirements
   - Highlight 2-3 most relevant experiences/achievements that match their needs
   - Show understanding of the company's challenges/goals
   - Demonstrate value you'd bring to the team

3. **Closing Paragraph:**
   - Reiterate your enthusiasm for the opportunity
   - Include a call to action (interview request)
   - Professional closing

## 🔥 PERSONALIZATION GUIDELINES:

1. **RESEARCH-DRIVEN APPROACH:**
   - Reference specific aspects of the job description
   - Show understanding of the company/role requirements
   - Use language and terminology from the job posting

2. **STORYTELLING:**
   - Tell a compelling narrative that connects your experience to their needs
   - Use specific examples and metrics when possible
   - Make it personal but professional

3. **VALUE PROPOSITION:**
   - Clearly articulate what unique value you bring
   - Focus on outcomes and impact you can deliver
   - Address pain points mentioned in the job description

## 📊 KEY INFORMATION:

**Target Position:** {job_title}

**Job Description:** 
{job_description}

**Candidate's Background (from resume):**
{resume_text}

**Additional Context to Include:**
{additional_info if additional_info else "No additional information provided."}

## 🚀 DELIVERABLE:

Write a complete, professional cover letter that:

✅ Uses the specified tone ({tone})
✅ Emphasizes the requested focus area ({emphasize})
✅ Is 3-4 paragraphs in length
✅ Includes specific examples from their background
✅ References the job requirements naturally
✅ Shows genuine interest in the role/company
✅ Includes a professional greeting and closing
✅ Is ready to send (no placeholder text)
✅ Complements the tailored resume perfectly

**FORMATTING NOTES:**
- Start directly with the greeting (e.g., "Dear Hiring Manager,")
- DO NOT include sender's contact information at the top (name, address, phone, email)
- DO NOT include recipient's address information
- Use proper paragraph spacing
- No placeholder text (write as if complete)
- Professional but engaging tone
- Approximately 250-400 words

**CRITICAL:** Make this cover letter feel authentic and specifically written for THIS opportunity. Avoid generic language and make every sentence count.

Generate ONLY the cover letter text, ready to be used. Start with the greeting, NOT with contact information.
"""