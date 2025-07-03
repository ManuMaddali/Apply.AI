import os
import openai
from typing import Optional
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
    
    def tailor_resume(self, resume_text: str, job_description: str, job_title: str = "Product Manager", optional_sections: dict = None) -> Optional[str]:
        """Tailor resume using direct OpenAI API call"""
        try:
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
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling GPT: {str(e)}")
            return None
    
    def _create_tailoring_prompt(self, resume_text: str, job_description: str, job_title: str = "", optional_sections: dict = None) -> str:
        """
        Create a prompt for AGGRESSIVE resume transformation
        """
        
        # Handle optional sections
        optional_sections = optional_sections or {}
        include_summary = optional_sections.get("includeSummary", False)
        include_skills = optional_sections.get("includeSkills", False)
        include_education = optional_sections.get("includeEducation", False)
        education_details = optional_sections.get("educationDetails", {})
        
        # Build optional sections instructions
        optional_instructions = ""
        
        if include_summary:
            optional_instructions += """
## 📝 PROFESSIONAL SUMMARY (REQUIRED):
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
            
            optional_instructions += f"""
## 🎓 EDUCATION SECTION (REQUIRED):
Add an education section with the following information:
{education_info if education_info else "Use relevant educational background that supports the role"}

"""
        
        if include_skills:
            optional_instructions += """
## 🛠️ SKILLS SECTION (REQUIRED):
Add a skills section that includes:
- Technical skills mentioned in the job posting (in order of importance)
- Programming languages, tools, platforms from the job description
- Soft skills that the role emphasizes
- Industry-specific competencies
- Group skills logically (Technical, Leadership, Domain Expertise, etc.)

"""
        
        return f"""
🎯 TRANSFORM THIS RESUME TO BE A PERFECT MATCH FOR THE JOB

YOUR GOAL: Take every single bullet point and DRAMATICALLY rewrite it to speak directly to what this employer wants. Don't just tweak - TRANSFORM.

⚠️ CRITICAL FORMATTING REQUIREMENTS:
- Output in CLEAN, WELL-SPACED format
- Use proper line breaks and spacing between sections
- Each bullet point should be on its own line with proper indentation
- Add blank lines between major sections for readability
- Use consistent formatting throughout
- NO markdown syntax (**bold**, *italic*) - use plain text only
- Maintain professional resume structure

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
- RESPECT the optional section preferences (only add what was requested)
- ENSURE EXCELLENT VISUAL FORMATTING

Return ONLY the transformed resume text with proper formatting, starting with contact information.
"""