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

🚨 CRITICAL CONTENT CONSISTENCY RULES:
• MANDATORY MINIMUM CONTENT: Every resume MUST have the same detailed structure regardless of job description quality
• NEVER REMOVE CONTENT: Transform and adapt ALL original experiences - do not skip or shorten sections
• CONSISTENT BULLET COUNT: Each role must have EXACTLY 4-5 detailed bullets (never fewer than 4)
• CONSISTENT WORD COUNT: Each bullet must be 30-45 words with specific metrics and context for fuller 2-line bullets
• PRESERVE ALL ROLES: Include ALL work experiences from original resume - transform them, don't skip them
• MANDATORY SECTIONS: Every resume must include Professional Summary, Professional Experience, Education, Skills
• CONTENT EXPANSION: If job description is vague/short, use your expertise to create detailed, relevant content

ENHANCED RESUME FORMATTING RULES:
• PROFESSIONAL PRESENTATION: Create a detailed, impactful resume that showcases expertise and achievements
• PROFESSIONAL SUMMARY: 80-100 words, natural flowing narrative that tells a compelling story about the candidate - AVOID robotic formulas like "Results-driven [Role] with X years of experience"
• BULLET POINTS: 4-5 detailed bullets per role, each 30-45 words for fuller 2-line bullets with more content on second line
• DETAILED CONTENT: Focus on impact, scale, and results - make every bullet count with comprehensive context
• PROFESSIONAL LANGUAGE: Use sophisticated, industry-appropriate terminology
• QUANTIFIED RESULTS: Include specific metrics, percentages, numbers, and measurable outcomes
• SKILLS INTEGRATION: Seamlessly incorporate job-relevant skills and technologies
• OUTPUT: Plain text only. No markdown, asterisks, or special formatting. Follow the STATIC TEMPLATE exactly.
• EDUCATION FORMATTING: Always format as "Degree Name, Institution | Year (GPA: X.X/4.0 if applicable)" - never separate GPA

ENHANCED TAILORING RULES:
1. **COMPREHENSIVE BULLET REWRITE**: Create EXACTLY 4-5 detailed bullets per role, each 30-45 words for fuller 2-line bullets
2. **NATURAL PROFESSIONAL SUMMARY**: Write EXACTLY 80-100 words as a compelling, authentic narrative - like telling your career story to a friend over coffee - AVOID robotic phrases
3. **SOPHISTICATED LANGUAGE & METRICS**: Use industry-specific terminology with precise metrics and detailed context
4. **PROFESSIONAL STRUCTURE**: Clean, readable formatting with proper spacing
5. **CONTENT EXPANSION**: If job description is poor/short, use expertise to create detailed, relevant content

Create detailed, impactful resumes that showcase expertise and achievements with comprehensive content and measurable results. NEVER produce shorter resumes due to poor job descriptions - always maintain consistent detail and impact. Make summaries sound natural and human, not robotic. Always integrate GPA into education entries, never as separate elements.
"""
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
    
    def validate_resume_content_consistency(self, resume_text: str) -> dict:
        """
        Validate that the generated resume meets consistency requirements
        Returns a detailed analysis of content quality and consistency
        """
        try:
            lines = resume_text.split('\n')
            
            # Initialize analysis
            analysis = {
                'is_consistent': True,
                'issues': [],
                'summary_word_count': 0,
                'bullet_counts_by_role': {},
                'total_bullet_count': 0,
                'sections_found': [],
                'missing_sections': [],
                'recommendations': []
            }
            
            # Find sections
            current_section = None
            current_company = None
            bullet_count = 0
            summary_text = ""
            in_summary = False
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Detect section headers
                if stripped.isupper() and len(stripped) > 3:
                    if any(section in stripped for section in ['PROFESSIONAL SUMMARY', 'SUMMARY']):
                        current_section = 'SUMMARY'
                        in_summary = True
                        analysis['sections_found'].append('PROFESSIONAL SUMMARY')
                    elif 'EXPERIENCE' in stripped:
                        current_section = 'EXPERIENCE'
                        in_summary = False
                        analysis['sections_found'].append('PROFESSIONAL EXPERIENCE')
                    elif 'EDUCATION' in stripped:
                        current_section = 'EDUCATION'
                        in_summary = False
                        analysis['sections_found'].append('EDUCATION')
                    elif 'SKILLS' in stripped:
                        current_section = 'SKILLS'
                        in_summary = False
                        analysis['sections_found'].append('SKILLS')
                    continue
                
                # Count summary words
                if in_summary and current_section == 'SUMMARY':
                    summary_text += " " + stripped
                
                # Detect company headers (Company | Location format)
                if current_section == 'EXPERIENCE' and '|' in stripped and not stripped.startswith('•'):
                    if current_company:
                        analysis['bullet_counts_by_role'][current_company] = bullet_count
                    current_company = stripped
                    bullet_count = 0
                    continue
                
                # Count bullets
                if stripped.startswith('•'):
                    bullet_count += 1
                    analysis['total_bullet_count'] += 1
                    
                    # Check bullet length (updated for 30-45 words for fuller 2-line bullets)
                    bullet_words = len(stripped.split())
                    if bullet_words < 25:  # Approximate minimum for 30-45 word requirement
                        analysis['issues'].append(f"Short bullet found: {stripped[:50]}...")
                    elif bullet_words > 50:  # Approximate maximum for 30-45 word requirement
                        analysis['issues'].append(f"Long bullet found: {stripped[:50]}...")
            
            # Final role bullet count
            if current_company:
                analysis['bullet_counts_by_role'][current_company] = bullet_count
            
            # Analyze summary
            if summary_text:
                analysis['summary_word_count'] = len(summary_text.split())
                if analysis['summary_word_count'] < 70:
                    analysis['issues'].append(f"Professional summary too short: {analysis['summary_word_count']} words (should be 80-100)")
                    analysis['is_consistent'] = False
                elif analysis['summary_word_count'] > 110:
                    analysis['issues'].append(f"Professional summary too long: {analysis['summary_word_count']} words (should be 80-100)")
                
                # Check for robotic language patterns
                robotic_patterns = [
                    "Results-driven [Role] with over",
                    "Demonstrated success in [key achievement",
                    "Seeking to leverage [specific expertise]",
                    "Proven track record of [measurable impact]"
                ]
                
                for pattern in robotic_patterns:
                    if pattern.lower() in summary_text.lower():
                        analysis['issues'].append(f"Robotic language detected in summary: {pattern}")
                        analysis['is_consistent'] = False
                        
            else:
                analysis['issues'].append("No professional summary found")
                analysis['is_consistent'] = False
            
            # Check bullet counts per role
            for company, count in analysis['bullet_counts_by_role'].items():
                if count < 4:
                    analysis['issues'].append(f"Insufficient bullets for {company}: {count} bullets (should be 4-5)")
                    analysis['is_consistent'] = False
                elif count > 5:
                    analysis['issues'].append(f"Too many bullets for {company}: {count} bullets (should be 4-5)")
            
            # Check for required sections
            required_sections = ['PROFESSIONAL SUMMARY', 'PROFESSIONAL EXPERIENCE', 'EDUCATION', 'SKILLS']
            for section in required_sections:
                if section not in analysis['sections_found']:
                    analysis['missing_sections'].append(section)
                    analysis['is_consistent'] = False
            
            # Generate recommendations
            if analysis['issues']:
                analysis['recommendations'] = [
                    "Regenerate resume with explicit content requirements",
                    "Check job description quality - poor JDs may cause shorter content",
                    "Ensure all transformation rules are being followed",
                    "Consider using a more detailed base resume template"
                ]
            
            return analysis
            
        except Exception as e:
            return {
                'is_consistent': False,
                'issues': [f"Error analyzing resume: {str(e)}"],
                'recommendations': ["Manual review required"]
            }

    def _create_tailoring_prompt(self, resume_text: str, job_description: str, job_title: str = "", optional_sections: Optional[Dict[str, Any]] = None) -> str:
        """Create the tailoring prompt with enhanced instructions"""
        if optional_sections is None:
            optional_sections = {}
        
        # Extract optional section preferences
        include_summary = optional_sections.get("includeSummary", False)
        include_skills = optional_sections.get("includeSkills", False)
        include_education = optional_sections.get("includeEducation", False)
        education_details = optional_sections.get("educationDetails", {})
        
        # Detect existing sections
        existing_sections = self._detect_existing_sections(resume_text)
        
        # Build detected sections information
        detected_sections_info = f"DETECTED EXISTING SECTIONS: {', '.join(existing_sections).upper()}"
        
        # Build optional instructions
        optional_instructions = ""
        
        if include_summary:
            if 'summary' in existing_sections:
                optional_instructions += """
## 📝 PROFESSIONAL SUMMARY (ENHANCE EXISTING):
The resume already has a professional summary section. ENHANCE and TRANSFORM it to be compelling and perfectly tailored for THIS role:
- Completely rewrite using keywords from the job description
- Make it 80-100 words for maximum impact and detail
- Write as a natural, flowing story about the candidate's journey and expertise
- AVOID robotic formulas like "Results-driven [Role] with X years of experience"
- AVOID choppy phrases like "Skilled in X, Y, and Z" or "Proven track record in..."
- Instead, create an authentic narrative that reads like a compelling story
- Use varied sentence structure and natural transitions between ideas
- Connect their background to the target role organically through storytelling
- Include specific achievements and measurable impact woven naturally into the narrative
- Make it sound like how a confident professional would describe themselves in conversation

"""
            else:
                optional_instructions += """
## 📝 PROFESSIONAL SUMMARY (ADD NEW):
Add a compelling 80-100 word professional summary at the top that positions the candidate as perfect for THIS role:
- Write as a natural, flowing story about the candidate's journey and expertise
- AVOID robotic formulas like "Results-driven [Role] with X years of experience"
- AVOID choppy phrases like "Skilled in X, Y, and Z" or "Proven track record in..."
- Instead, create an authentic narrative that reads like a compelling story
- Use varied sentence structure and natural transitions between ideas
- Connect their background to the target role organically through storytelling
- Include specific achievements and measurable impact woven naturally into the narrative
- Make it sound like how a confident professional would describe themselves in conversation

"""
        
        if include_skills:
            if 'skills' in existing_sections:
                optional_instructions += """
## 🛠️ SKILLS SECTION (ENHANCE EXISTING):
The resume already has skills information. ENHANCE and IMPROVE it:
- Keep all existing skills but reorganize and prioritize based on job requirements
- Add any missing skills that are crucial for the target role
- Group skills logically by category (Technical, Leadership, etc.)
- Ensure skills match the job description keywords

"""
            else:
                optional_instructions += """
## 🛠️ SKILLS SECTION (ADD NEW):
Add a skills section with job-relevant skills organized by category:
- Technical skills that match the job requirements
- Leadership and soft skills relevant to the role
- Industry-specific competencies
- Tools and technologies mentioned in the job description

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
- Keep all existing education but reformat professionally and compactly
- Add any missing details from the provided information: {education_info if education_info else "No additional details provided"}
- Format education entries as: Degree Name, Institution | Year (GPA: X.X/4.0 if provided)
- Include GPA as part of the education entry, not as a separate prominent element
- Emphasize aspects most relevant to the target role
- Ensure proper formatting and presentation
- DO NOT duplicate education entries

"""
            else:
                optional_instructions += f"""
## 🎓 EDUCATION SECTION (ADD NEW):
Add an education section with the following information:
{education_info if education_info else "Use relevant educational background that supports the role"}
- Format education entries as: Degree Name, Institution | Year (GPA: X.X/4.0 if provided)
- Include GPA as part of the education entry, not as a separate prominent element
- Keep formatting clean and professional

"""
        
        # Build the main prompt
        main_prompt = """
🎯 TRANSFORM THIS RESUME TO PERFECTLY MATCH THE JOB

YOUR GOAL: Rewrite EVERY bullet and section to directly address JD requirements. Transform dramatically—use JD's exact phrases, emphasize relevant skills/metrics, and showcase problem-solving/impact.

{detected_sections_info}

🚨 CRITICAL CONTENT CONSISTENCY RULES:
• MANDATORY MINIMUM CONTENT: Every resume MUST have the same detailed structure regardless of job description quality
• NEVER REMOVE CONTENT: Transform and adapt ALL original experiences - do not skip or shorten sections
• CONSISTENT BULLET COUNT: Each role must have EXACTLY 4-5 detailed bullets (never fewer than 4)
• CONSISTENT WORD COUNT: Each bullet must be 30-45 words with specific metrics and context for fuller 2-line bullets
• PRESERVE ALL ROLES: Include ALL work experiences from original resume - transform them, don't skip them
• MANDATORY SECTIONS: Every resume must include Professional Summary, Professional Experience, Education, Skills
• CONTENT EXPANSION: If job description is vague/short, use your expertise to create detailed, relevant content

ENHANCED RESUME FORMATTING RULES:
• PROFESSIONAL PRESENTATION: Create a detailed, impactful resume that showcases expertise and achievements
• PROFESSIONAL SUMMARY: 80-100 words, natural flowing narrative that tells a compelling story about the candidate - AVOID robotic formulas like "Results-driven [Role] with X years of experience"
• BULLET POINTS: 4-5 detailed bullets per role, each 30-45 words for fuller 2-line bullets with more content on second line
• DETAILED CONTENT: Focus on impact, scale, and results - make every bullet count with comprehensive context
• PROFESSIONAL LANGUAGE: Use sophisticated, industry-appropriate terminology
• QUANTIFIED RESULTS: Include specific metrics, percentages, numbers, and measurable outcomes
• SKILLS INTEGRATION: Seamlessly incorporate job-relevant skills and technologies
• OUTPUT: Plain text only. No markdown, asterisks, or special formatting. Follow the STATIC TEMPLATE exactly.
• EDUCATION FORMATTING: Always format as "Degree Name, Institution | Year (GPA: X.X/4.0 if applicable)" - never separate GPA

ENHANCED TAILORING RULES:
1. **COMPREHENSIVE BULLET REWRITE**: Create EXACTLY 4-5 detailed bullets per role, each 30-45 words for fuller 2-line bullets
2. **NATURAL PROFESSIONAL SUMMARY**: Write EXACTLY 80-100 words as a compelling, authentic narrative - like telling your career story to a friend over coffee - AVOID robotic phrases
3. **SOPHISTICATED LANGUAGE & METRICS**: Use industry-specific terminology with precise metrics and detailed context
4. **PROFESSIONAL STRUCTURE**: Clean, readable formatting with proper spacing
5. **CONTENT EXPANSION**: If job description is poor/short, use expertise to create detailed, relevant content

Create detailed, impactful resumes that showcase expertise and achievements with comprehensive content and measurable results. NEVER produce shorter resumes due to poor job descriptions - always maintain consistent detail and impact. Make summaries sound natural and human, not robotic. Always integrate GPA into education entries, never as separate elements.

ENHANCED TEMPLATE EXAMPLE (FOLLOW THIS STYLE):
[NAME IN ALL CAPS]
[Professional Title in Title Case]
[Contact info in normal case]

PROFESSIONAL SUMMARY
Write a natural, flowing narrative about the candidate's journey and expertise that sounds like how they would describe themselves in conversation. Start with their background, weave in their achievements and skills naturally, and connect it to their career goals. Avoid robotic formulas and choppy phrases - make it read like a story that engages the reader and showcases their personality and expertise.

PROFESSIONAL EXPERIENCE

Company Name | Location
Job Title | Date Range
• Spearheaded [specific initiative] that delivered [comprehensive measurable outcome], enhancing [business impact] for [detailed context] and achieving [additional quantified results]
• Architected and implemented [technical solution/process] that transformed [specific area], resulting in [detailed results] and improving [business metrics] by [percentage]
• Led cross-functional team of [number] professionals to [specific goal], achieving [measurable success] through [detailed methodology] and delivering [additional benefits]
• Established [framework/system/process] that [specific impact], contributing to [larger business objective] and [additional benefits] through [implementation approach]
• Optimized [specific area] through [detailed approach], resulting in [quantified improvement] and [additional positive outcomes] while [maintaining context]

EDUCATION
Degree Name, Institution | Year (GPA: X.X/4.0 if applicable)

SKILLS
Category: Skill1, Skill2, Skill3
Category: Skill4, Skill5, Skill6

TARGET JOB:
Title: {job_title}
Description: {job_description}

{optional_instructions}

ORIGINAL RESUME:
{resume_text}

Return ONLY the transformed resume in plain text, starting with name. Create a detailed, impactful resume that showcases the candidate's expertise and achievements with natural, flowing language that sounds human and authentic.
"""
        
        return main_prompt.format(
            detected_sections_info=detected_sections_info,
            job_title=job_title,
            job_description=job_description,
            optional_instructions=optional_instructions,
            resume_text=resume_text
        )

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