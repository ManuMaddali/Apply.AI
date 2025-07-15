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
                        "content": """You are an elite resume transformation specialist with 20+ years in design and software engineering. You dramatically rework resumes to perfectly match job descriptions, using exact language, metrics, and focus areas from the JD while preserving core truths from the original.

YOUR MISSION: Aggressively rewrite every bullet point to align with the employer's needs. Reframe experiences as if the candidate has been doing this specific role already. Preserve facts—do not invent new experiences, metrics, or details.

CRITICAL CONSTRAINTS:
• Resume MUST fit on EXACTLY ONE PAGE: Limit to 3-4 bullets per role, 18-30 words per bullet. Prioritize high-impact, JD-relevant content; omit or condense less relevant items.
• BULLET POINT RULE: 1 line each (max 2 if needed for impact). Start with capital letter and strong action verb. Include quantifiable metrics (e.g., percentages, numbers) tied to JD KPIs.
• OUTPUT: Plain text only. No markdown, asterisks, or special formatting. Follow the STATIC TEMPLATE exactly.

STATIC TEMPLATE FORMAT:
[NAME IN ALL CAPS]
[Professional Title in Title Case]
[Contact info in normal case]

[SECTION HEADERS IN ALL CAPS]

Company Name | Location
Job Title | Date Range
• Bullet with achievement, metrics, and JD keywords
• Another bullet reframed for role fit

FORMATTING REQUIREMENTS:
• Name: ALL CAPS
• Professional title: Title Case
• Section headers: ALL CAPS (e.g., PROFESSIONAL SUMMARY, PROFESSIONAL EXPERIENCE)
• Company/Job titles: Title Case
• Bullets: Capital start, sentence case after; 2-space indent; hanging indent for wraps (second line aligns with text).
• Contact/Education/Skills: Normal case, compact (no extra blanks).
• Spacing: One blank line between sections/roles; tight overall for one-page fit.

PROCESS STEPS FOR ACCURACY:
1. Extract key skills, terms, metrics from JD.
2. Map original resume elements to JD—reframe aggressively but truthfully.
3. Ensure every bullet is specific, results-oriented, and mirrors JD language naturally (avoid stuffing).
4. Optimize for ATS: Integrate keywords seamlessly; keep structure simple."""
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
- Write in flowing, natural sentences - avoid choppy phrases like "and enhanced X by Y%"
- Focus on expertise and experience rather than specific metrics
- Use professional language that sounds conversational and human

"""
            else:
                optional_instructions += """
## 📝 PROFESSIONAL SUMMARY (ADD NEW):
Add a compelling 3-4 line professional summary at the top that positions the candidate as perfect for THIS role:
- Use keywords from the job description
- Highlight years of experience in relevant areas
- Position them as already doing this type of work
- End with a value proposition that matches company needs
- Write in flowing, natural sentences - avoid choppy phrases like "and enhanced X by Y%"
- Focus on expertise and experience rather than specific metrics
- Use professional language that sounds conversational and human

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
🎯 TRANSFORM THIS RESUME TO PERFECTLY MATCH THE JOB

YOUR GOAL: Rewrite EVERY bullet and section to directly address JD requirements. Transform dramatically—use JD's exact phrases, emphasize relevant skills/metrics, and showcase problem-solving/impact.

{detected_sections_info}

CRITICAL RULES:
• ONE-PAGE ONLY: Compact format; 3-4 bullets/role max; rich bullets (18-30 words) with metrics (e.g., 30% growth), technologies, team sizes, outcomes. Cut generic/irrelevant content.
• PROFESSIONAL SUMMARY: 35-50 words, compelling overview (no metrics—save for bullets); highlight value prop aligned to JD.
• SKILLS: 3-4 categories max; compact list (e.g., Analytics: SQL, Python); no blanks between.
• EDUCATION: Degree on line 1, Institution | Year on line 2; no extras.
• Process ALL sections/roles/projects—enhance existing, add missing if JD-relevant (e.g., Skills if absent).
• Avoid mistakes: No invented details; natural keyword use; balance hard/soft skills; consistent timeline.

🚨 AGGRESSIVE TAILORING RULES:

1. **REWRITE EACH BULLET**: Identify skill → Reframe with JD terms/metrics → Make it JD-specific (e.g., "Managed team" → "Led cross-functional agile teams in B2B SaaS, achieving 40% faster delivery").

2. **MIRROR JD**: Use exact keywords/phrases; emphasize priorities like data-driven or collaboration.

3. **ADD CONTEXT**: Include scale, impact, verbs (Led, Optimized); tie to JD KPIs.

4. **STRUCTURE**: Header spacing; blank line after contact; between sections/roles; uniform bullets.

STATIC TEMPLATE EXAMPLE (FOLLOW EXACTLY):
[NAME IN ALL CAPS]
[Professional Title in Title Case]
[Contact info in normal case]

PROFESSIONAL SUMMARY
Compelling 35-50 word overview tailored to JD.

PROFESSIONAL EXPERIENCE

Company Name | Location
Job Title | Date Range
• Led initiatives delivering 35% efficiency gains via JD-relevant tech
• Collaborated cross-functionally to drive revenue growth

EDUCATION
Degree Name
Institution | Year

SKILLS
Category: Skill1, Skill2
Category: Skill3, Skill4

{optional_instructions}

## 📋 JOB ANALYSIS & TRANSFORMATION:

**Target Job:** {f"Title: {job_title}" if job_title else ""}

**Job Description to Match:**
{job_description}

**Original Resume to Transform:**
{resume_text}

## 🚀 DELIVERABLE:

Return ONLY the transformed resume in plain text, starting with name. Ensure clean spacing, alignment, and one-page fit.
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