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
                        "content": """You are an elite resume writer and career strategist with 15+ years of experience helping candidates land roles at Fortune 500 companies. You have expertise in ATS optimization, industry-specific keyword strategies, and psychological principles that make resumes compelling to hiring managers. You understand the nuances of different industries and know exactly how to position candidates for maximum impact while maintaining absolute factual integrity.

CRITICAL RULE: You create exceptional resumes using ONLY the information provided in the original resume. You NEVER add any information, contact details, education, certifications, or placeholder text that isn't explicitly stated in the original resume. You work with what exists and make it exceptional."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling GPT: {str(e)}")
            return None
    
    def _create_tailoring_prompt(self, resume_text: str, job_description: str, job_title: str = "") -> str:
        """
        Create a detailed prompt for world-class resume tailoring
        """
        return f"""
CRITICAL INSTRUCTION: Create a tailored resume using ONLY the information provided in the original resume. Do not add ANY information that is not explicitly stated.

RULES:
- NEVER fabricate information not in the original resume
- NEVER add placeholder text or brackets
- Use ONLY factual information from the provided resume
- Maintain 100% accuracy while enhancing presentation
- Return the resume in a clean, professional format
- Do NOT include conversational phrases like "Here's your resume" or "Sure!"

🚫 **NEVER ADD CONTACT INFORMATION NOT PROVIDED:**
- Do NOT add "[Your Address]", "[City, State, Zip]", "[Your Email]", "[Your Phone Number]"
- Do NOT add "[LinkedIn Profile]" or any placeholder contact details
- Use ONLY the exact contact information from the original resume

🚫 **NEVER ADD SECTIONS NOT IN ORIGINAL:**
- Do NOT add Education sections if not in original
- Do NOT add Certifications sections if not in original  
- Do NOT add References sections
- Do NOT add any placeholder text like "[Your Field]", "[University]", "[Year]"

🚫 **NEVER ADD SKILLS NOT DEMONSTRATED:**
- Do NOT add skills not shown in the work experience
- Do NOT add technologies not mentioned in the original
- Do NOT add certifications not explicitly stated

🚫 **NEVER ADD BRACKETS OR PLACEHOLDERS:**
- No [Your Name], [Your Address], [Your Field], [Company], [Year], [City], etc.
- No template language
- No placeholder text of any kind

## ✅ ADVANCED TAILORING STRATEGIES:

✅ **INDUSTRY-SPECIFIC POSITIONING:**
- Connect existing experience to target industry context
- Use industry terminology and concepts from job description
- Emphasize transferable skills relevant to the specific sector
- Highlight experience aspects most valued in the target industry

✅ **STRATEGIC SKILLS PRESENTATION:**
- ALWAYS include a Skills section if the original resume demonstrates multiple skills
- Prioritize skills most relevant to the job description first
- Group skills logically (Technical, Product Management, Leadership, etc.)
- Only include skills actually demonstrated in work experience

✅ **ENHANCED EXPERIENCE REFRAMING:**
- Rewrite achievements to emphasize outcomes valued by target company
- Connect existing metrics to business impact areas mentioned in job posting
- Use exact terminology from job description where it naturally fits existing experience
- Emphasize aspects of experience that solve target company's likely challenges

✅ **PROFESSIONAL FORMATTING:**
- Clean, ATS-friendly layout with clear section breaks
- Consistent formatting throughout
- Strategic section ordering (most relevant first)
- Professional language enhancement

## 📋 SPECIFIC INSTRUCTIONS:

**1. Contact Information:**
- Use EXACTLY the contact information provided in original resume
- Never use placeholder contact details

**2. Professional Summary:**
- Create compelling 3-4 line summary using only existing background
- Lead with most relevant experience for this specific role
- Include specific achievements that align with job requirements
- End with value proposition relevant to target company

**3. Experience Section:**
- Start each bullet with strong action verbs
- Reframe existing achievements to emphasize job-relevant impact
- Use terminology from job description naturally
- Prioritize most relevant experiences and achievements first
- Quantify results using existing metrics

**4. Skills Section (IMPORTANT):**
- If original resume shows multiple skills through experience, CREATE a Skills section
- List only skills demonstrated in actual work experience
- Prioritize skills most relevant to job posting
- Group into logical categories
- Never add skills not evidenced in experience

**5. Industry Context:**
- Connect existing experience to target industry/company context
- Use industry-specific language from job description
- Emphasize aspects of experience most relevant to target sector
- Show understanding of target company's challenges through existing experience

**Original Resume:**
{resume_text}

**Job Description:**
{job_description}

{f"**Job Title:** {job_title}" if job_title else ""}

## 🎯 OUTPUT REQUIREMENT:

Create a professional, tailored resume that:
1. Contains ZERO placeholder text or brackets
2. Uses ONLY information from the original resume
3. Is strategically optimized for this specific job and industry
4. Includes relevant Skills section if experience demonstrates multiple skills
5. Connects existing experience to target industry context
6. Has NO fabricated content whatsoever

**Remember: Transform existing experience to perfectly match the target role while maintaining complete factual accuracy.**
""" 