import os
import re
from typing import Optional, List, Dict, Any, Set
from dotenv import load_dotenv

# Try to import LangChain components, fallback if not available (Python 3.13 compatibility)
LANGCHAIN_AVAILABLE = True
try:
    from langchain.chains import ConversationChain
    from langchain.memory import ConversationBufferWindowMemory
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain.schema import Document
    from langchain_community.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
except ImportError as e:
    print(f"⚠️ LangChain not available: {e}")
    print("   Running in fallback mode - some features will be limited")
    LANGCHAIN_AVAILABLE = False
    
    # Define minimal fallback classes
    class Document:
        def __init__(self, page_content="", metadata=None):
            self.page_content = page_content
            self.metadata = metadata or {}

# Standard imports
import json
import uuid
from datetime import datetime

class LangChainResumeProcessor:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.api_key = api_key
        self.langchain_available = LANGCHAIN_AVAILABLE
        
        if LANGCHAIN_AVAILABLE:
            # Initialize LangChain components
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                openai_api_key=api_key,
                max_tokens=8000
            )
            
            try:
                self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            except Exception as e:
                print(f"⚠️ OpenAI Embeddings not available: {e}")
                self.embeddings = None
            
            # Initialize memory for conversation tracking
            self.memory = ConversationBufferWindowMemory(
                k=5,  # Remember last 5 interactions
                return_messages=True
            )
        else:
            print("⚠️ LangChain not available - using fallback mode")
            self.llm = None
            self.embeddings = None
            self.memory = None
        
        # Initialize vector store for job descriptions
        self.job_vectorstore = None
        self.resume_history = {}  # Track resume versions
        
        # Create vector store directory
        os.makedirs("vector_stores", exist_ok=True)
    
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
        
    def initialize_job_vectorstore(self, job_descriptions: List[Dict[str, str]]):
        """Initialize FAISS vector store with job descriptions"""
        if not self.langchain_available or not self.embeddings:
            print("⚠️ Vector store not available - RAG features disabled")
            return False
            
        try:
            documents = []
            for job in job_descriptions:
                # Create document with metadata
                doc = Document(
                    page_content=job.get("job_description", ""),
                    metadata={
                        "job_id": job.get("id"),
                        "job_url": job.get("url", ""),
                        "job_title": job.get("job_title", ""),
                        "created_at": datetime.now().isoformat()
                    }
                )
                documents.append(doc)
            
            # Split documents for better retrieval
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,
                chunk_overlap=200,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
            )
            
            split_docs = text_splitter.split_documents(documents)
            
            # Create FAISS vector store
            self.job_vectorstore = FAISS.from_documents(
                split_docs, 
                self.embeddings
            )
            
            # Save vector store
            self.job_vectorstore.save_local("vector_stores/job_descriptions")
            
            return True
            
        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            return False
    
    def load_job_vectorstore(self):
        """Load existing job vector store"""
        if not self.langchain_available or not self.embeddings:
            return False
            
        try:
            if os.path.exists("vector_stores/job_descriptions"):
                self.job_vectorstore = FAISS.load_local(
                    "vector_stores/job_descriptions", 
                    self.embeddings
                )
                return True
            return False
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def retrieve_similar_jobs(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve similar job descriptions using RAG"""
        if not self.job_vectorstore:
            return []
        
        try:
            # Retrieve similar job descriptions
            similar_docs = self.job_vectorstore.similarity_search(query, k=k)
            return similar_docs
        except Exception as e:
            print(f"Error retrieving similar jobs: {str(e)}")
            return []
    
    def create_enhanced_tailoring_prompt(self, resume_text: str, job_description: str, job_title: str, similar_jobs: List[Document]) -> str:
        """Create enhanced prompt with RAG context"""
        
        # Extract insights from similar jobs
        similar_job_insights = ""
        if similar_jobs:
            similar_job_insights = "\n## SIMILAR JOB ANALYSIS:\n"
            for i, doc in enumerate(similar_jobs, 1):
                similar_job_insights += f"\nSimilar Job {i}:\n"
                similar_job_insights += f"- Content: {doc.page_content[:200]}...\n"
                similar_job_insights += f"- URL: {doc.metadata.get('job_url', 'N/A')}\n"
        
        prompt = f"""
🔥 AGGRESSIVELY TRANSFORM THIS RESUME FOR MAXIMUM JOB MATCH

You are a resume transformation specialist. Your job is to DRAMATICALLY rewrite this resume so it appears to be custom-made for this specific position. Every bullet point should be transformed to use the exact language, metrics, and focus areas from the job description.

CRITICAL FORMAT RULE: Output in PLAIN TEXT ONLY. No markdown, no asterisks (**), no special formatting. Match the exact format style of the original resume - same spacing, same bullet points, same structure.

{similar_job_insights}

TRANSFORMATION RULES:

1. **COMPLETE BULLET REWRITE**
   - Take each experience bullet and COMPLETELY reframe it
   - Use the EXACT terminology from the job posting
   - Make it sound like they've been doing THIS job already
   - Add metrics that align with what the employer values

2. **MIRROR JOB REQUIREMENTS**
   - If job wants "scalable solutions" → Everything they built is "scalable"
   - If job emphasizes "data-driven" → Every decision was "data-driven"
   - If job needs "stakeholder management" → Transform all communication into "stakeholder management"
   - Use their keywords in EVERY bullet point

3. **AGGRESSIVE REFRAMING**
   - Don't just edit - TRANSFORM completely
   - Generic experience → Industry-specific expertise
   - Basic tasks → Strategic initiatives
   - Team work → Cross-functional leadership
   - Problem solving → Data-driven decision making

4. **INDUSTRY ALIGNMENT**
   - Use insights from similar jobs to understand what matters
   - Position experience using industry-standard terminology
   - Emphasize metrics and KPIs common in this field
   - Show deep understanding of their specific challenges

5. **DRAMATIC EXAMPLES**
   - "Managed projects" → "Spearheaded cross-functional initiatives driving 45% efficiency gains"
   - "Worked with data" → "Leveraged advanced analytics to inform product strategy, resulting in 3x user engagement"
   - "Improved processes" → "Architected scalable workflows reducing time-to-market by 60%"

TARGET JOB:
Title: {job_title}
Description: {job_description}

ORIGINAL RESUME:
{resume_text}

CRITICAL: Transform the ENTIRE resume - all roles, all sections. Do not stop after the first job!

DELIVER: A completely transformed resume that looks custom-written for this exact role. Start with contact info and make every line count.
"""
        return prompt
    
    def tailor_resume_with_rag(self, resume_text: str, job_description: str, job_title: str = "Product Manager", optional_sections: dict = None) -> Optional[Dict[str, Any]]:
        """Tailor resume using RAG with similar job descriptions"""
        try:
            if not self.job_vectorstore:
                print("No job vectorstore available. Loading...")
                self.load_job_vectorstore()
            
            if not self.job_vectorstore:
                print("Warning: No job vectorstore available for RAG")
                return None
            
            # Search for similar job descriptions
            similar_jobs = self.job_vectorstore.similarity_search(
                job_description,
                k=min(3, self.job_vectorstore.index.ntotal) if hasattr(self.job_vectorstore, 'index') else 3
            )
            
            similar_jobs_context = ""
            if similar_jobs:
                for i, doc in enumerate(similar_jobs, 1):
                    similar_jobs_context += f"\n=== Similar Job {i} ===\n"
                    similar_jobs_context += f"Title: {doc.metadata.get('job_title', 'Unknown')}\n"
                    similar_jobs_context += f"Description: {doc.page_content[:500]}...\n"
            
            # Handle optional sections with intelligent detection
            optional_sections = optional_sections or {}
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
PROFESSIONAL SUMMARY (ENHANCE EXISTING):
The resume already has a professional summary section. ENHANCE and TRANSFORM it to be compelling and perfectly tailored for THIS role:
- Completely rewrite using keywords from the job description and similar jobs
- Highlight years of experience in relevant areas mentioned in the job posting
- Position them as already doing this type of work
- End with a value proposition that matches company needs
- Keep it as the top section but make it dramatically better

"""
                else:
                    optional_instructions += """
PROFESSIONAL SUMMARY (ADD NEW):
Add a compelling 3-4 line professional summary at the top that positions the candidate as perfect for THIS role:
- Use keywords from the job description and similar jobs
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
EDUCATION SECTION (ENHANCE EXISTING):
The resume already has education information. ENHANCE and IMPROVE the existing education section:
- Keep all existing education but reformat professionally
- Add any missing details from the provided information: {education_info if education_info else "No additional details provided"}
- Emphasize aspects most relevant to the target role
- Ensure proper formatting and presentation
- DO NOT duplicate education entries

"""
                else:
                    optional_instructions += f"""
EDUCATION SECTION (ADD NEW):
Add an education section with the following information:
{education_info if education_info else "Use relevant educational background that supports the role"}

"""
            
            if include_skills:
                if 'skills' in existing_sections:
                    optional_instructions += """
SKILLS SECTION (ENHANCE EXISTING):
The resume already has a skills section. ENHANCE and TRANSFORM it to be perfectly aligned with this job:
- Keep existing relevant skills but reorganize and prioritize based on job requirements
- Add technical skills mentioned in the job posting and similar jobs (in order of importance)
- Include programming languages, tools, platforms from the job descriptions
- Emphasize soft skills that the role emphasizes
- Add industry-specific competencies mentioned in the job posting
- Group skills logically (Technical, Leadership, Domain Expertise, etc.)
- Remove outdated or irrelevant skills and replace with job-relevant ones

"""
                else:
                    optional_instructions += """
SKILLS SECTION (ADD NEW):
Add a skills section that includes:
- Technical skills mentioned in the job posting and similar jobs (in order of importance)
- Programming languages, tools, platforms from the job descriptions
- Soft skills that the role emphasizes
- Industry-specific competencies
- Group skills logically (Technical, Leadership, Domain Expertise, etc.)

"""
            
            # Add section detection information
            detected_sections_info = ""
            if existing_sections:
                detected_sections_info = f"""
⚠️ IMPORTANT - EXISTING SECTIONS DETECTED:
The original resume already contains these sections: {', '.join(existing_sections).upper()}
- For existing sections: ENHANCE and IMPROVE them, do not duplicate
- For new sections: ADD them in appropriate locations
- Maintain the overall structure while improving content quality

"""
            
            # Create enhanced prompt using similar jobs
            rag_prompt = PromptTemplate(
                input_variables=["resume_text", "job_description", "job_title", "similar_jobs", "optional_instructions", "detected_sections_info"],
                template="""You are an elite resume transformation specialist with access to a database of similar job postings. Use this knowledge to create an exceptionally tailored resume with PROFESSIONAL FORMATTING.

CRITICAL FORMATTING RULE: Output in CLEAN, WELL-SPACED format with proper structure and spacing.

{detected_sections_info}

FORMATTING REQUIREMENTS:
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

TARGET JOB:
Title: {job_title}
Description: {job_description}

{optional_instructions}

SIMILAR JOBS CONTEXT (use these insights):
{similar_jobs}

TRANSFORMATION RULES:
1. Transform EVERY bullet point to directly address the requirements from the target job and patterns from similar jobs
2. Use the exact terminology and keywords from the job description
3. Emphasize skills and experiences that appear consistently across similar roles
4. Transform generic achievements into role-specific wins with relevant metrics
5. Make every line show direct relevance to what employers in this space are looking for
6. COMPLETE the entire resume - process ALL work experiences and sections
7. RESPECT the optional section preferences (enhance existing, add new as needed)
8. NEVER DUPLICATE SECTIONS - enhance what exists, add what's missing
9. ENSURE EXCELLENT VISUAL FORMATTING with proper spacing

FORMATTING STRUCTURE:
- Header: Name, title, contact info with proper spacing
- Professional Summary (if requested): 3-4 impactful lines with spacing
- Experience: Company | Location, Job Title | Dates, bullet points with consistent indentation
- Skills (if requested): Clear categories with proper spacing
- Education (if requested): Institution | Location, Degree | Year
- Blank lines between all major sections

ORIGINAL RESUME:
{resume_text}

Transform this resume to be a perfect match for the target job with PROFESSIONAL FORMATTING. Return ONLY the transformed resume text in clean, well-spaced format, starting with contact information."""
            )
            
            # Create chain and run
            chain = rag_prompt | self.llm | StrOutputParser()
            
            tailored_resume = chain.invoke({
                "resume_text": resume_text,
                "job_description": job_description,
                "job_title": job_title,
                "similar_jobs": similar_jobs_context,
                "optional_instructions": optional_instructions,
                "detected_sections_info": detected_sections_info
            })
            
            return {
                "tailored_resume": tailored_resume,
                "similar_jobs_found": len(similar_jobs),
                "rag_context": similar_jobs_context
            }
            
        except Exception as e:
            print(f"Error in RAG resume tailoring: {str(e)}")
            return None
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session history"""
        return self.resume_history.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, Any]:
        """Get all session history"""
        return self.resume_history 