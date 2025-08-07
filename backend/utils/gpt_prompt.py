import os
import openai
import re
import time
from typing import Optional, Dict, Any, Set, TYPE_CHECKING
from dotenv import load_dotenv

if TYPE_CHECKING:
    from models.user import TailoringMode

load_dotenv()

class GPTProcessor:
    """Fallback GPT processor when LangChain is not available"""
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Defer actual initialization until first use
        self.client = None
        self._initialized = False
    
    def _lazy_init(self):
        """Initialize OpenAI client on first use to avoid blocking at import time"""
        if self._initialized:
            return
        
        self._initialized = True
        
        # Initialize OpenAI client with timeout configuration
        try:
            import httpx
            # Create HTTP client with reasonable timeout (60 seconds for OpenAI API)
            http_client = httpx.Client(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            self.client = openai.OpenAI(
                api_key=self.api_key,
                http_client=http_client,
                timeout=60.0  # 60 second timeout for API calls
            )
            print("✅ OpenAI client initialized with 60s timeout")
        except Exception as e:
            print(f"❌ OpenAI client initialization failed: {e}")
            # Create a minimal working client for development
            try:
                import httpx
                # Create basic HTTP client without any proxy settings
                http_client = httpx.Client()
                self.client = openai.OpenAI(api_key=self.api_key, http_client=http_client)
                print("✅ OpenAI client initialized with fallback HTTP client")
            except Exception as e2:
                print(f"❌ All OpenAI initialization methods failed: {e2}")
                print("⚠️ GPT processing will not be available")
                self.client = None
    
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

    def tailor_resume(self, resume_text: str, job_description: str, job_title: str = "Product Manager", optional_sections: Optional[Dict[str, Any]] = None, tailoring_mode: Optional['TailoringMode'] = None) -> Optional[str]:
        """Tailor resume using direct OpenAI API call"""
        try:
            if optional_sections is None:
                optional_sections = {}
            prompt = self._create_tailoring_prompt(resume_text, job_description, job_title, optional_sections, tailoring_mode)
            
            # Choose system prompt based on tailoring mode
            if tailoring_mode and tailoring_mode.value == 'light':
                system_content = """You are a professional resume optimizer focused on minimal ATS keyword optimization. Your goal is to make ONLY subtle keyword additions while preserving ALL original content, structure, and factual information exactly as provided.

YOUR MISSION: Add 3-5 relevant keywords naturally within existing bullet points. Make NO structural changes, NO content removal, NO metric changes, NO voice changes.

CRITICAL PRESERVATION REQUIREMENTS (NEVER CHANGE):
• ALL job titles exactly as written (Senior Product Manager, Product Manager, etc.)
• ALL company names and locations exactly as provided
• ALL employment dates exactly as provided
• ALL education details (degrees, schools, dates, GPA) exactly as provided
• ALL certifications exactly as provided
• ALL original metrics and percentages exactly as provided
• ALL section headers and structure exactly as provided
• ALL bullet points must remain (no removal or consolidation)
• Professional summary voice and style exactly as provided
• ALL achievements and accomplishments exactly as provided

LIGHT MODE CONSTRAINTS:
• Maximum 3-5 keyword additions total across entire resume
• Keywords must be naturally integrated within existing sentences
• NO new bullet points, NO removed bullet points
• NO structural changes to any sections
• NO changes to professional summary beyond 1-2 keyword additions
• NO changes to formatting, spacing, or organization
• NO changes to writing style or voice
• Word count increase should be under 50 words total

ALLOWED CHANGES ONLY:
• Add 1-2 relevant keywords within existing bullet points
• Add 1-2 keywords to professional summary if space allows
• Minor terminology alignment (e.g., "user experience" → "user experience (UX)")
• Nothing else is permitted

PROCESS STEPS:
1. Identify 3-5 most critical keywords from job description
2. Find natural places within existing sentences to add keywords
3. Integrate keywords without changing sentence structure or meaning
4. Verify ALL original content is preserved exactly
5. Ensure total changes are minimal and barely noticeable"""
            else:
                system_content = """You are an elite resume transformation specialist focused on aggressive content reframing while maintaining absolute factual accuracy. You dramatically rewrite bullet points and enhance content to align with job requirements, but you NEVER change factual information.

YOUR MISSION: Aggressively reframe and enhance existing experiences to show perfect alignment with the target role. Rewrite bullet points with job-relevant keywords and context while preserving ALL factual information exactly as provided.

CRITICAL PRESERVATION REQUIREMENTS (NEVER CHANGE):
• ALL job titles exactly as written (Senior Product Manager, Product Manager, etc.)
• ALL company names and locations exactly as provided
• ALL employment dates exactly as provided
• ALL education details (degrees, schools, dates, GPA) exactly as provided
• ALL certifications exactly as provided
• ALL original metrics and percentages exactly as provided (do NOT invent new metrics)
• ALL section headers and structure exactly as provided
• ALL achievements must be based on original content (no fabrication)

HEAVY MODE TRANSFORMATION APPROACH:
• Aggressively rewrite bullet points with job-relevant keywords and context
• Enhance professional summary to show strong alignment with target role
• Emphasize transferable skills and relevant aspects of existing experience
• Add industry-specific terminology and context to existing achievements
• Reframe accomplishments to highlight job-relevant impact
• Expand bullet points to 35-50 words with enhanced detail and context
• Maintain all original sections but enhance content within them

FORMATTING REQUIREMENTS:
• Name: ALL CAPS (preserve exactly as provided)
• Professional title: Use ORIGINAL title exactly as provided
• Section headers: ALL CAPS (e.g., PROFESSIONAL SUMMARY, PROFESSIONAL EXPERIENCE)
• Company/Job titles: Use ORIGINAL titles and companies exactly as provided
• Bullets: Capital start, sentence case after; 2-space indent; 35-50 words each
• Contact/Education/Skills: Normal case, preserve all original information
• Spacing: One blank line between sections/roles; professional presentation

PROFESSIONAL SUMMARY ENHANCEMENT:
• Rewrite to show strong alignment with target role and industry
• Maintain original career progression and achievements
• Add relevant keywords and industry context
• Show enthusiasm for target role without false claims
• Keep factual career timeline and accomplishments
• 100-150 words, written naturally

BULLET POINT ENHANCEMENT RULES:
• Rewrite each bullet to 35-50 words with job-relevant keywords
• Emphasize aspects of achievements that align with job requirements
• Add industry context and terminology to existing accomplishments
• Highlight transferable skills and relevant impact
• Use original metrics exactly - do NOT invent new percentages or numbers
• Frame existing experience to show relevance to target role

PROCESS STEPS FOR ETHICAL TRANSFORMATION:
1. Extract key skills, terms, and requirements from job description
2. Identify transferable aspects of each original experience
3. Rewrite bullet points with job-relevant keywords while preserving facts
4. Enhance professional summary to show alignment without false claims
5. Ensure all original factual information remains unchanged
6. Verify no new metrics or achievements have been invented
7. Confirm all job titles, companies, and dates are preserved exactly"""

            self._lazy_init()  # Initialize OpenAI client if needed
            
            # Add timeout protection for OpenAI API call
            import asyncio
            import concurrent.futures
            
            print(f"🤖 Making OpenAI API call with 60s timeout...")
            start_time = time.time()
            
            # Use ThreadPoolExecutor to add timeout to synchronous OpenAI call
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    self.client.chat.completions.create,
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": system_content
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=8000,
                    temperature=0.1,
                    timeout=60  # 60 second timeout
                )
                
                try:
                    # Wait for completion with timeout
                    response = future.result(timeout=65)  # 65s total timeout (5s buffer)
                    elapsed = time.time() - start_time
                    print(f"✅ OpenAI API call completed in {elapsed:.1f}s")
                except concurrent.futures.TimeoutError:
                    print(f"⏱️ OpenAI API call timed out after 65 seconds")
                    future.cancel()
                    return None
            
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
            
            self._lazy_init()  # Initialize OpenAI client if needed
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
    
    def _create_tailoring_prompt(self, resume_text: str, job_description: str, job_title: str = "", optional_sections: Optional[Dict[str, Any]] = None, tailoring_mode: Optional['TailoringMode'] = None) -> str:
        """
        Create a prompt for AGGRESSIVE resume transformation with intelligent section handling and tailoring mode differentiation
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
        
        # Handle tailoring mode instructions with enhanced differentiation
        tailoring_instructions = ""
        if tailoring_mode:
            # Import here to avoid circular imports
            from models.user import TailoringMode
            
            if tailoring_mode == TailoringMode.LIGHT:
                tailoring_instructions = """
🎯 LIGHT TAILORING MODE - BASIC KEYWORD OPTIMIZATION (FREE TIER):
Focus on minimal, essential changes for basic ATS compatibility while keeping the resume simple:

BASIC KEYWORD INTEGRATION:
- Identify 5-8 key terms from job description and add them naturally
- Replace 2-3 generic terms with job-specific terminology
- Add 1-2 relevant keywords per bullet point without major rewrites
- Keep skills section mostly unchanged, just reorder top 3-5 skills
- Make minimal terminology adjustments only
- Focus on simple keyword additions rather than comprehensive rewrites

MINIMAL CONTENT CHANGES:
- Keep original resume structure exactly as is
- Preserve all existing accomplishments and metrics unchanged
- Maintain candidate's original writing style completely
- Make only surface-level keyword additions
- NO rewriting of bullet points - only minor keyword enhancements
- Keep original bullet point count and length
- Preserve original professional summary if it exists

LIGHT TAILORING CONSTRAINTS (FREE TIER):
- Maximum 15% content change from original resume
- NO restructuring of any sections
- NO rewriting of experience descriptions
- NO dramatic improvements to bullet points
- Keep all original metrics and achievements exactly as stated
- Focus only on basic keyword optimization
- Maintain original resume length and format
- Make changes that are barely noticeable but ATS-friendly

LIGHT MODE APPROACH:
- Add keywords naturally without changing sentence structure
- Keep original action verbs unless easy synonym available
- Maintain all original accomplishments exactly
- Focus on terminology alignment only
- Preserve original bullet point structure completely
- Make minimal, conservative changes only

LIGHT MODE PROFESSIONAL SUMMARY:
- If summary exists, add only 1-2 keywords naturally
- If no summary exists, create basic 40-60 word summary
- Keep it simple and straightforward
- Focus on basic role alignment without dramatic positioning
- Maintain conservative, authentic tone

"""
            elif tailoring_mode == TailoringMode.HEAVY:
                tailoring_instructions = """
🔥 HEAVY TAILORING MODE - COMPREHENSIVE TRANSFORMATION:
Perform aggressive, strategic restructuring for maximum job alignment and impact:

COMPREHENSIVE REWRITING STRATEGY:
- Completely transform every bullet point to mirror job description priorities and language
- Restructure entire resume to emphasize most job-relevant experiences first
- Reframe ALL accomplishments using exact terminology and success metrics from job posting
- Create compelling professional summary that positions candidate as perfect fit (100-150 words)
- Reorganize skills section with job-critical competencies prominently featured
- Reorder work experience sections to highlight most relevant roles first
- Transform job titles to align with target role terminology when appropriate

ADVANCED OPTIMIZATION TECHNIQUES:
- Transform passive descriptions into dynamic, results-oriented power statements
- Integrate 15-25+ job-specific keywords throughout all sections naturally
- Reorder work experience to highlight most relevant roles prominently
- Enhance quantified achievements to align with job requirements (amplify existing metrics contextually)
- Create compelling narrative thread that demonstrates perfect role alignment
- Restructure bullet points to emphasize job-relevant accomplishments first
- Use industry-specific terminology and success metrics from job description

HEAVY TAILORING ENHANCEMENTS:
- Restructure content hierarchy to put most relevant information first
- Transform generic accomplishments into role-specific wins with targeted metrics
- Enhance professional summary with strategic storytelling that connects background to target role
- Optimize every section for both ATS scanning and human reader engagement
- Ensure every line demonstrates direct relevance to the specific job requirements
- Create maximum differentiation from original while maintaining factual accuracy
- Allow up to 70% content transformation from original resume
- Reframe experiences to show direct applicability to target role

HEAVY MODE BULLET POINT APPROACH:
- Completely rewrite bullets to emphasize job-relevant aspects and impact
- Lead with accomplishments that directly match job requirements and success criteria
- Transform generic tasks into strategic initiatives with measurable business impact
- Use exact terminology and success metrics from job description throughout
- Restructure experience to tell a compelling story of perfect role fit
- Amplify existing metrics to show greater impact and scale using industry context
- Create bullets that read as if candidate has been doing target role already

HEAVY MODE CONTENT RESTRUCTURING:
- Reorder sections to prioritize most job-relevant information prominently
- Move most applicable work experience to top positions for maximum impact
- Restructure bullets within roles to lead with most relevant accomplishments
- Transform job titles and descriptions to align with target role language
- Create seamless narrative flow that positions candidate as ideal fit
- Reorganize skills to match job requirements priority order
- Restructure professional summary to lead with most relevant experience

HEAVY MODE PROFESSIONAL SUMMARY:
- Completely rewrite to position candidate as perfect fit for target role
- Lead with most relevant experience and accomplishments
- Use job-specific terminology and industry language throughout
- Create compelling narrative that connects all experience to target role
- Include specific achievements that align with job success metrics
- Write as if candidate has been preparing for this exact role

"""
        else:
            # Default to Light mode behavior for backward compatibility
            tailoring_instructions = """
🎯 STANDARD TAILORING MODE - BALANCED APPROACH:
Apply moderate tailoring that balances optimization with authenticity:
- Incorporate relevant keywords and phrases from job description
- Adjust bullet points to highlight applicable experience and skills
- Enhance professional summary to align with role requirements
- Optimize existing content without dramatic restructuring
- Maintain candidate's authentic voice while improving job relevance

"""
        
        return f"""
🎯 TRANSFORM THIS RESUME TO PERFECTLY MATCH THE JOB

YOUR GOAL: Rewrite EVERY bullet and section to directly address JD requirements. Transform dramatically—use JD's exact phrases, emphasize relevant skills/metrics, and showcase problem-solving/impact.

{tailoring_instructions}

{detected_sections_info}

CRITICAL RULES:
• ONE-PAGE ONLY: Include 5 DETAILED bullets per role, 35-50 words per bullet. Prioritize high-impact, JD-relevant content with comprehensive metrics and achievements.
• PROFESSIONAL SUMMARY: Write 100-150 words in first person as a natural story. Start with where you've been, what you've learned, what you've accomplished, and where you're headed. Let it flow like you're explaining your career path to someone who asked "So what do you do?" No buzzwords, no forced enthusiasm - just your actual journey.
• BULLET POINT RULE: Each bullet MUST be 2 full lines (35-50 words). Start with capital letter and strong action verb. Include multiple specific quantifiable metrics (e.g., percentages, numbers) tied to JD KPIs.
• SKILLS: 3-4 categories max; compact list (e.g., Analytics: SQL, Python); no blanks between.
• EDUCATION: Degree on line 1, Institution | Year on line 2; no extras.
• Process ALL sections/roles/projects—enhance existing, add missing if JD-relevant (e.g., Skills if absent).
• Avoid mistakes: No invented details; natural keyword use; balance hard/soft skills; consistent timeline.

🚨 AGGRESSIVE TAILORING RULES:

1. **NATURAL PROFESSIONAL SUMMARY**: Write 100-150 words in first person. Sound human, not robotic. Skip corporate buzzwords and clichés. Just tell your story naturally.

2. **COMPREHENSIVE BULLET POINTS**: Each bullet MUST be 35-50 words (2 full lines) with multiple specific metrics and achievements. Include team sizes, budget figures, and specific technologies.

3. **MIRROR JD**: Use exact keywords/phrases; emphasize priorities like data-driven or collaboration.

4. **ADD CONTEXT**: Include scale, impact, verbs (Spearheaded, Architected, Optimized); tie to JD KPIs.

5. **STRUCTURE**: Header spacing; blank line after contact; between sections/roles; uniform bullets.

STATIC TEMPLATE EXAMPLE (FOLLOW EXACTLY):
[NAME IN ALL CAPS]
[Professional Title in Title Case]
[Contact info in normal case]

PROFESSIONAL SUMMARY
I started in product management five years ago working on consumer apps, then moved into enterprise software where I learned how different user needs can be. Along the way, I've launched products that generated over $25M in revenue and improved engagement by 200%. What I've discovered is that the best products come from really listening to users and working closely with engineering and design teams. I've gotten good at turning user feedback into features that actually solve problems. Now I'm looking to bring what I've learned to PrizePicks and help build products that users genuinely enjoy using.

PROFESSIONAL EXPERIENCE

Company Name | Location
Job Title | Date Range
• Spearheaded product strategy for music discovery features, enhancing engagement for over 400M users globally, resulting in a 35% increase in user interaction and satisfaction through implementation of advanced machine learning algorithms and personalized content delivery systems.
• Launched a personalized recommendation engine that significantly improved user retention and engagement metrics, contributing to a 25% increase in subscription renewals through sophisticated data modeling and predictive analytics that accurately identified user preferences and behaviors.
• Collaborated with engineering, design, and data science teams in an agile environment to deliver high-impact features on time, improving overall product delivery efficiency by 30% while maintaining quality standards and addressing critical user feedback from multiple market segments.
• Managed a comprehensive product roadmap, prioritizing features based on user research and data analysis, leading to a 40% reduction in feature development time while ensuring alignment with strategic business objectives and market demands.
• Defined and tracked key performance indicators (KPIs) for product success, utilizing data-driven insights to inform strategic decisions and enhance product offerings, resulting in 15% increase in user satisfaction and 20% growth in revenue.

EDUCATION                                                  SKILLS
Master of Business Administration (MBA)                    Analytics: SQL, Python, R
Stanford Graduate School of Business | 2018                Design: Figma, Sketch, Adobe Creative Suite
                                                          Project Management: Jira, Asana, Trello
Bachelor of Science in Computer Science                    Data Visualization: Tableau, Looker, Power BI
University of California, Berkeley | 2016

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