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
    
    def tailor_resume(self, resume_text: str, job_description: str, job_title: str = "Product Manager") -> Optional[str]:
        """Tailor resume using direct OpenAI API call"""
        try:
            prompt = self._create_tailoring_prompt(resume_text, job_description, job_title)
            
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
    
    def _create_tailoring_prompt(self, resume_text: str, job_description: str, job_title: str = "") -> str:
        """
        Create a prompt for AGGRESSIVE resume transformation
        """
        return f"""
🎯 TRANSFORM THIS RESUME TO BE A PERFECT MATCH FOR THE JOB

YOUR GOAL: Take every single bullet point and DRAMATICALLY rewrite it to speak directly to what this employer wants. Don't just tweak - TRANSFORM.

⚠️ CRITICAL FORMATTING REQUIREMENTS:
- Output in PLAIN TEXT ONLY - no markdown, no asterisks, no special characters
- Match the EXACT format of the original resume
- Use the same indentation and bullet style as the original
- NO ** or * for emphasis - just plain text
- Keep the same section structure and spacing

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

5. **SECTION-BY-SECTION TRANSFORMATION**

   **Professional Summary:**
   - Write 3-4 lines that make them sound PERFECT for THIS EXACT ROLE
   - Use keywords from the job title and top requirements
   - Position them as already doing this type of work
   - End with a value prop that matches company needs

   **Experience Bullets:**
   - Start with power verbs that match the job's level (Led, Drove, Architected, Pioneered)
   - Include industry-specific terminology from the job posting
   - Transform generic achievements into role-specific wins
   - Add context that shows understanding of their industry/challenges

   **Skills Section:**
   - List skills in the EXACT order of importance from job posting
   - Use their exact terminology (if they say "Python" don't write "Programming")
   - Group into categories that match how they structure requirements
   - Include both technical and soft skills they emphasize

## 📋 JOB ANALYSIS & TRANSFORMATION:

**Target Job:**
{f"Title: {job_title}" if job_title else ""}

**Job Description to Match:**
{job_description}

**Original Resume to Transform:**
{resume_text}

## 🚀 DELIVERABLE:

Create a resume that looks like it was WRITTEN SPECIFICALLY for this job. Every line should make the hiring manager think "This person has been doing exactly what we need."

CRITICAL: Process the ENTIRE resume including ALL work experiences (INCOMM, KRISHNA AI, OKTA, etc.), education, projects - everything. Do not stop after the first role!

REMEMBER:
- Transform aggressively while keeping core truths
- Use their exact language and terminology
- Make it impossible to ignore
- Format cleanly with clear sections
- NO generic bullets - everything tailored to THIS job
- COMPLETE THE ENTIRE RESUME - all sections, all roles

Return ONLY the transformed resume text, starting with contact information.
""" 