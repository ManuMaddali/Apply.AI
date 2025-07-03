import os
from typing import Optional, List, Dict, Any
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
PROFESSIONAL SUMMARY (REQUIRED):
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
                
                optional_instructions += f"""
EDUCATION SECTION (REQUIRED):
Add an education section with the following information:
{education_info if education_info else "Use relevant educational background that supports the role"}

"""
            
            if include_skills:
                optional_instructions += """
SKILLS SECTION (REQUIRED):
Add a skills section that includes:
- Technical skills mentioned in the job posting and similar jobs (in order of importance)
- Programming languages, tools, platforms from the job descriptions
- Soft skills that the role emphasizes
- Industry-specific competencies
- Group skills logically (Technical, Leadership, Domain Expertise, etc.)

"""
            
            # Create enhanced prompt using similar jobs
            rag_prompt = PromptTemplate(
                input_variables=["resume_text", "job_description", "job_title", "similar_jobs", "optional_instructions"],
                template="""You are an elite resume transformation specialist with access to a database of similar job postings. Use this knowledge to create an exceptionally tailored resume with PROFESSIONAL FORMATTING.

CRITICAL FORMATTING RULE: Output in CLEAN, WELL-SPACED format with proper structure and spacing.

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
7. RESPECT the optional section preferences (only add what was requested)
8. ENSURE EXCELLENT VISUAL FORMATTING with proper spacing

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
                "optional_instructions": optional_instructions
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