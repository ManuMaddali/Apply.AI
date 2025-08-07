import os
import re
from typing import Optional, List, Dict, Any, Set, TYPE_CHECKING
from dotenv import load_dotenv

if TYPE_CHECKING:
    from models.user import TailoringMode

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
    from langchain_core.output_parsers import StrOutputParser
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
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Defer actual initialization until first use
        self.llm = None
        self.embeddings = None
        self.memory = None
        self._initialized = False
        
        self.langchain_available = LANGCHAIN_AVAILABLE
        
        # Initialize vector store for job descriptions
        self.job_vectorstore = None
        self.resume_history = {}  # Track resume versions
        
        # Create vector store directory
        os.makedirs("vector_stores", exist_ok=True)
    
    def _lazy_init(self):
        """Initialize OpenAI components on first use to avoid blocking at import time"""
        if self._initialized:
            return
        
        self._initialized = True
        
        if not LANGCHAIN_AVAILABLE:
            print("⚠️ LangChain not available - using fallback mode")
            return
        
        try:
            # Initialize with timeout configuration
            import httpx
            # Create HTTP client with reasonable timeout
            http_client = httpx.Client(
                timeout=httpx.Timeout(60.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=self.api_key,
                max_tokens=8000,
                request_timeout=60,  # 60 second timeout
                max_retries=2  # Retry up to 2 times on failure
            )
            print("✅ LangChain OpenAI initialized with 60s timeout")
        except Exception as e:
            print(f"⚠️  LangChain OpenAI initialization failed: {e}")
            print("⚠️  Using fallback - resume generation may not work properly")
            self.llm = None
        
        if self.llm is not None:
            # Initialize LangChain components
            try:
                # Initialize embeddings without custom HTTP client
                self.embeddings = OpenAIEmbeddings(
                    api_key=self.api_key
                )
                print("✅ OpenAI Embeddings initialized successfully")
            except Exception as e:
                print(f"⚠️ OpenAI Embeddings not available: {e}")
                self.embeddings = None
            
            # Initialize memory for conversation tracking
            self.memory = ConversationBufferWindowMemory(
                k=5,  # Remember last 5 interactions
                return_messages=True
            )
    
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
        self._lazy_init()  # Initialize OpenAI components if needed
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
        self._lazy_init()  # Initialize OpenAI components if needed
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

ENHANCED RESUME FORMATTING RULES:
• PROFESSIONAL PRESENTATION: Create a detailed, impactful resume that showcases expertise and achievements
• PROFESSIONAL SUMMARY: Write 100-150 words in first person as a natural story. Start with where you've been, what you've learned, what you've accomplished, and where you're headed. Let it flow like you're explaining your career path to someone who asked "So what do you do?" No buzzwords, no forced enthusiasm - just your actual journey.
• BULLET POINTS: EXACTLY 5 detailed bullets per role, each 35-50 words (2 full lines) with multiple specific metrics and achievements
• DETAILED CONTENT: Focus on impact, scale, and results - make every bullet count with comprehensive details
• PROFESSIONAL LANGUAGE: Use sophisticated, industry-appropriate terminology
• QUANTIFIED RESULTS: Include multiple specific metrics, percentages, numbers, and measurable outcomes in EVERY bullet
• SKILLS INTEGRATION: Seamlessly incorporate job-relevant skills and technologies
• OUTPUT: Plain text only. No markdown, asterisks, or special formatting. Follow the STATIC TEMPLATE exactly.

{similar_job_insights}

🚨 ENHANCED TRANSFORMATION RULES:

1. **COMPREHENSIVE BULLET REWRITE**
   - Create 4-5 detailed bullets per role showing progression and impact
   - Each bullet should be 25-40 words with specific context and measurable results
   - Use power verbs (Spearheaded, Architected, Optimized, Delivered, Established)
   - Include team sizes, budget figures, time frames, and success metrics

2. **NATURAL PROFESSIONAL SUMMARY**
   - Write 100-150 words in first person as a natural story
   - Start with where you've been, what you've learned, what you've accomplished, and where you're headed
   - Include specific industry context and relevant achievements
   - Use sophisticated language that demonstrates professionalism

3. **SOPHISTICATED LANGUAGE & METRICS**
   - Use industry-specific terminology from the job description
   - Include precise metrics (percentages, dollar amounts, user numbers, time savings)
   - Show progression and increasing responsibility
   - Demonstrate strategic thinking and leadership capabilities

4. **MIRROR JOB REQUIREMENTS**
   - If job wants "scalable solutions" → Everything they built is "scalable"
   - If job emphasizes "data-driven" → Every decision was "data-driven"
   - If job needs "stakeholder management" → Transform all communication into "stakeholder management"
   - Use their keywords in EVERY bullet point with sophisticated context

5. **AGGRESSIVE REFRAMING WITH DETAIL**
   - Don't just edit - TRANSFORM completely with comprehensive detail
   - Generic experience → Industry-specific expertise with measurable impact
   - Basic tasks → Strategic initiatives with quantified results
   - Team work → Cross-functional leadership with team sizes and outcomes
   - Problem solving → Data-driven decision making with specific metrics

6. **INDUSTRY ALIGNMENT**
   - Use insights from similar jobs to understand what matters
   - Position experience using industry-standard terminology
   - Emphasize metrics and KPIs common in this field
   - Show deep understanding of their specific challenges

7. **ENHANCED EXAMPLES**
   - "Managed projects" → "Spearheaded cross-functional initiatives across 3 departments, driving 45% efficiency gains and delivering $2M in cost savings"
   - "Worked with data" → "Leveraged advanced analytics and machine learning algorithms to inform product strategy, resulting in 3x user engagement and 25% revenue growth"
   - "Improved processes" → "Architected scalable workflows and automation systems reducing time-to-market by 60% while maintaining 99.9% quality standards"

TARGET JOB:
Title: {job_title}
Description: {job_description}

ORIGINAL RESUME:
{resume_text}

CRITICAL: Transform the ENTIRE resume - all roles, all sections. Create 4-5 detailed, impactful bullets per role with comprehensive metrics and achievements. Do not stop after the first job!

DELIVER: A completely transformed, detailed resume that looks custom-written for this exact role. Start with contact info and make every line count with sophisticated language and measurable impact.
"""
        return prompt
    
    def tailor_resume_with_rag(self, resume_text: str, job_description: str, job_title: str = "Product Manager", optional_sections: dict = None, tailoring_mode: Optional['TailoringMode'] = None) -> Optional[Dict[str, Any]]:
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
- Make it 100-150 words as a natural story
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
PROFESSIONAL SUMMARY (ADD NEW):
Add a compelling 100-150 word professional summary at the top that positions the candidate as perfect for THIS role:
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
SKILLS SECTION (ENHANCE EXISTING):
The resume already has skills information. ENHANCE and IMPROVE it:
- Keep all existing skills but reorganize and prioritize based on job requirements
- Add any missing skills that are crucial for the target role
- Group skills logically by category (Technical, Leadership, etc.)
- Ensure skills match the job description keywords

"""
                else:
                    optional_instructions += """
SKILLS SECTION (ADD NEW):
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
EDUCATION SECTION (ENHANCE EXISTING):
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
EDUCATION SECTION (ADD NEW):
Add an education section with the following information:
{education_info if education_info else "Use relevant educational background that supports the role"}
- Format education entries as: Degree Name, Institution | Year (GPA: X.X/4.0 if provided)
- Include GPA as part of the education entry, not as a separate prominent element
- Keep formatting clean and professional

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
            
            # Handle tailoring mode instructions with enhanced differentiation
            tailoring_instructions = ""
            if tailoring_mode:
                # Import here to avoid circular imports
                from models.user import TailoringMode
                
                if tailoring_mode == TailoringMode.LIGHT:
                    tailoring_instructions = """
🎯 LIGHT TAILORING MODE - TARGETED KEYWORD OPTIMIZATION WITH RAG INSIGHTS:
Focus on strategic, minimal changes that maximize ATS compatibility while preserving authenticity:

KEYWORD INTEGRATION STRATEGY:
- Identify 8-12 key terms from job description and similar jobs, integrate them naturally
- Replace generic terms with job-specific terminology (e.g., "managed" → "orchestrated stakeholder relationships")
- Adjust existing bullet points to include 2-3 relevant keywords per bullet without changing core meaning
- Reorder skills section to prioritize job-relevant competencies first
- Use RAG insights to identify commonly valued skills across similar roles
- Maintain original sentence structure while enhancing with targeted keywords
- Focus on natural terminology alignment rather than dramatic rewrites

CONTENT PRESERVATION APPROACH:
- Maintain original resume structure and flow completely
- Keep existing accomplishments but enhance with job-relevant context from similar roles
- Preserve candidate's authentic voice and writing style
- Make subtle adjustments to professional summary (add 2-3 targeted keywords naturally)
- Focus on surface-level optimizations that improve keyword density
- Leverage similar job patterns to make natural enhancements
- Preserve all original metrics and achievements exactly as stated
- Maintain original bullet point count and structure

LIGHT TAILORING CONSTRAINTS:
- NO major restructuring of sections or content hierarchy
- NO dramatic rewriting of experience descriptions
- Minimal changes to bullet point structure (enhance existing, don't rewrite)
- Preserve original metrics and achievements exactly as stated
- Keep changes feeling natural and authentic to the candidate's experience
- Use RAG context to validate keyword choices against industry standards
- Maximum 25% content change from original resume
- Focus on keyword optimization and terminology alignment
- Maintain original professional summary length and tone

LIGHT MODE BULLET POINT APPROACH:
- Keep original bullet structure and flow intact
- Add 1-2 job-relevant keywords per bullet naturally
- Enhance existing action verbs with more specific alternatives from job description
- Maintain original accomplishments and metrics exactly
- Focus on terminology alignment rather than content restructuring
- Use similar job insights to validate keyword choices
- Preserve original bullet point count per role
- Make changes that feel like natural improvements, not rewrites

LIGHT MODE PROFESSIONAL SUMMARY:
- Keep original summary structure and length if it exists
- Add 2-3 job-relevant keywords naturally using RAG insights
- Maintain candidate's authentic voice and tone
- Focus on terminology enhancement rather than content restructuring
- Preserve original achievements and experience mentions
- If no summary exists, create a brief 50-75 word summary with light keyword integration

"""
                elif tailoring_mode == TailoringMode.HEAVY:
                    tailoring_instructions = """
🔥 HEAVY TAILORING MODE - COMPREHENSIVE TRANSFORMATION WITH RAG ENHANCEMENT:
Perform aggressive, strategic restructuring for maximum job alignment using similar job insights:

COMPREHENSIVE REWRITING STRATEGY:
- Completely transform every bullet point to mirror job description priorities and language patterns from similar roles
- Restructure entire resume to emphasize most job-relevant experiences first, informed by RAG insights
- Reframe ALL accomplishments using exact terminology and success metrics from job posting and similar positions
- Create compelling professional summary that positions candidate as perfect fit (100-150 words) using industry-standard language
- Reorganize skills section with job-critical competencies prominently featured, validated by similar job requirements
- Reorder work experience sections to highlight most relevant roles first
- Transform job titles to align with target role terminology when appropriate

ADVANCED OPTIMIZATION TECHNIQUES WITH RAG:
- Transform passive descriptions into dynamic, results-oriented power statements using proven industry language
- Integrate 15-25+ job-specific keywords throughout all sections naturally, validated against similar successful roles
- Reorder work experience to highlight most relevant roles prominently based on similar job priorities
- Enhance quantified achievements to align with job requirements (amplify existing metrics contextually using industry benchmarks)
- Create compelling narrative thread that demonstrates perfect role alignment using proven success patterns
- Restructure bullet points to emphasize job-relevant accomplishments first
- Use industry-specific terminology and success metrics from job description and similar roles

HEAVY TAILORING ENHANCEMENTS:
- Restructure content hierarchy to put most relevant information first based on similar job analysis
- Transform generic accomplishments into role-specific wins with targeted metrics from industry standards
- Enhance professional summary with strategic storytelling that connects background to target role using proven narratives
- Optimize every section for both ATS scanning and human reader engagement using RAG-informed best practices
- Ensure every line demonstrates direct relevance to the specific job requirements and industry expectations
- Create maximum differentiation from original while maintaining factual accuracy and industry credibility
- Leverage similar job insights to anticipate hiring manager expectations and preferences
- Allow up to 70% content transformation from original resume
- Reframe experiences to show direct applicability to target role

HEAVY MODE BULLET POINT APPROACH:
- Completely rewrite bullets to emphasize job-relevant aspects and impact
- Lead with accomplishments that directly match job requirements and success criteria
- Transform generic tasks into strategic initiatives with measurable business impact
- Use exact terminology and success metrics from job description and similar roles throughout
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
                tailoring_instructions = """
🎯 STANDARD TAILORING MODE - BALANCED APPROACH:
Apply moderate tailoring that balances optimization with authenticity:
- Incorporate relevant keywords and phrases from job description
- Adjust bullet points to highlight applicable experience and skills
- Enhance professional summary to align with role requirements
- Optimize existing content without dramatic restructuring
- Maintain candidate's authentic voice while improving job relevance

"""
                tailoring_instructions = """
🎯 STANDARD TAILORING MODE - BALANCED APPROACH:
Apply moderate tailoring that balances optimization with authenticity:
- Incorporate relevant keywords and phrases from job description
- Adjust bullet points to highlight applicable experience and skills
- Enhance professional summary to align with role requirements
- Optimize existing content without dramatic restructuring
- Maintain candidate's authentic voice while improving job relevance

"""
                tailoring_instructions = """
🎯 STANDARD TAILORING MODE - BALANCED APPROACH:
Apply moderate tailoring that balances optimization with authenticity:
- Incorporate relevant keywords and phrases from job description and similar roles
- Adjust bullet points to highlight applicable experience and skills
- Enhance professional summary to align with role requirements
- Optimize existing content without dramatic restructuring
- Maintain candidate's authentic voice while improving job relevance
- Use RAG insights to validate optimization choices

"""
            
            # Create enhanced prompt using similar jobs
            rag_prompt = PromptTemplate(
                input_variables=["resume_text", "job_description", "job_title", "similar_jobs", "optional_instructions", "detected_sections_info", "tailoring_instructions"],
                template="""You are an elite resume transformation specialist with 20+ years in design and software engineering. You dramatically rework resumes to perfectly match job descriptions, using exact language, metrics, and focus areas from the JD while preserving core truths from the original.

YOUR MISSION: Aggressively rewrite every bullet point to align with the employer's needs. Reframe experiences as if the candidate has been doing this specific role already. Preserve facts—do not invent new experiences, metrics, or details.

ENHANCED RESUME FORMATTING RULES:
• PROFESSIONAL PRESENTATION: Create a detailed, impactful resume that showcases expertise and achievements
• PROFESSIONAL SUMMARY: Write 100-150 words in first person as a natural story. Start with where you've been, what you've learned, what you've accomplished, and where you're headed. Let it flow like you're explaining your career path to someone who asked "So what do you do?" No buzzwords, no forced enthusiasm - just your actual journey.
• BULLET POINTS: EXACTLY 5 detailed bullets per role, each 35-50 words (2 full lines) with multiple specific metrics and achievements
• DETAILED CONTENT: Focus on impact, scale, and results - make every bullet count with comprehensive details
• PROFESSIONAL LANGUAGE: Use sophisticated, industry-appropriate terminology
• QUANTIFIED RESULTS: Include multiple specific metrics, percentages, numbers, and measurable outcomes in EVERY bullet
• SKILLS INTEGRATION: Seamlessly incorporate job-relevant skills and technologies
• OUTPUT: Plain text only. No markdown, asterisks, or special formatting. Follow the STATIC TEMPLATE exactly.
• EDUCATION FORMATTING: Always format as "Degree Name, Institution | Year (GPA: X.X/4.0 if applicable)" - never separate GPA

STATIC TEMPLATE FORMAT:
[NAME IN ALL CAPS]
[Professional Title in Title Case]
[Contact info in normal case]

[SECTION HEADERS IN ALL CAPS]

Company Name | Location
Job Title | Date Range
• Detailed bullet with specific achievement, comprehensive metrics, and JD keywords
• Another detailed bullet showcasing impact and measurable results

FORMATTING REQUIREMENTS:
• Name: ALL CAPS
• Professional title: Title Case
• Section headers: ALL CAPS (e.g., PROFESSIONAL SUMMARY, PROFESSIONAL EXPERIENCE)
• Company/Job titles: Title Case
• Bullets: Capital start, sentence case after; 2-space indent; hanging indent for wraps (second line aligns with text).
• Contact/Education/Skills: Normal case, compact (no extra blanks).
• Spacing: One blank line between sections/roles; professional presentation.

PROCESS STEPS FOR ACCURACY:
1. Extract key skills, terms, metrics from JD and similar jobs context.
2. Map original resume elements to JD—reframe aggressively but truthfully.
3. Ensure every bullet is specific, results-oriented, and mirrors JD language naturally (avoid stuffing).
4. Optimize for ATS: Integrate keywords seamlessly; keep structure simple.

{detected_sections_info}

{tailoring_instructions}

🎯 TRANSFORM THIS RESUME TO PERFECTLY MATCH THE JOB

YOUR GOAL: Rewrite EVERY bullet and section to directly address JD requirements. Transform dramatically—use JD's exact phrases, emphasize relevant skills/metrics, and showcase problem-solving/impact.

🚨 CRITICAL CONTENT CONSISTENCY RULES:
• MANDATORY MINIMUM CONTENT: Every resume MUST have the same detailed structure regardless of job description quality
• NEVER REMOVE CONTENT: Transform and adapt ALL original experiences - do not skip or shorten sections
• CONSISTENT BULLET COUNT: Each role must have EXACTLY 4-5 detailed bullets (never fewer than 4)
• CONSISTENT WORD COUNT: Each bullet must be 30-45 words with specific metrics and context for fuller 2-line bullets
• PRESERVE ALL ROLES: Include ALL work experiences from original resume - transform them, don't skip them
• MANDATORY SECTIONS: Every resume must include Professional Summary, Professional Experience, Education, Skills
• CONTENT EXPANSION: If job description is vague/short, use your expertise to create detailed, relevant content

🚨 ENHANCED TAILORING RULES:

1. **COMPREHENSIVE BULLET REWRITE** (MANDATORY 5 BULLETS PER ROLE):
   - Create EXACTLY 5 detailed bullets per role showing progression and impact
   - Each bullet MUST be 35-50 words for fuller 2-line bullets with multiple specific metrics and achievements
   - Use power verbs (Spearheaded, Architected, Optimized, Delivered, Established)
   - Include team sizes, budget figures, time frames, and success metrics with rich context
   - If original bullet is vague, ADD specific details that align with job requirements

2. **NATURAL PROFESSIONAL SUMMARY** (MANDATORY 100-150 WORDS):
   - Write EXACTLY 100-150 words as a comprehensive, detailed narrative that covers all aspects of professional background
   - Tell a compelling story about the candidate's journey and expertise
   - AVOID robotic formulas like "Results-driven [Role] with X years of experience"
   - AVOID choppy phrases like "Skilled in X, Y, and Z" or "Proven track record in..."
   - AVOID formulaic language like "Dynamic [Role] with over X years of experience"
   - Instead, create an authentic narrative that reads like a compelling story
   - Use varied sentence structure and natural transitions between ideas
   - Connect their background to the target role organically through storytelling
   - Make it sound like how a confident professional would describe themselves in conversation
   - If job description is vague, use industry best practices to create compelling content

3. **SOPHISTICATED LANGUAGE & METRICS** (MANDATORY FOR ALL BULLETS):
   - Use industry-specific terminology from the job description
   - Include precise metrics (percentages, dollar amounts, user numbers, time savings)
   - Show progression and increasing responsibility with detailed context
   - Demonstrate strategic thinking and leadership capabilities
   - If no metrics provided, intelligently add realistic, impressive metrics

4. **PROFESSIONAL STRUCTURE** (MANDATORY COMPLETENESS):
   - Clean, readable formatting with proper spacing
   - Consistent structure across all sections
   - Emphasize most relevant experiences first
   - Show clear career progression and growth
   - NEVER skip roles or experiences - adapt them instead

5. **CONTENT EXPANSION FOR POOR JOB DESCRIPTIONS**:
   - If job description is short/vague, use your expertise to create detailed, relevant content
   - Draw from industry standards and best practices for the role
   - Create realistic, impressive achievements that align with the position level
   - Ensure every resume has the same level of detail and impact

6. **MIRROR JOB REQUIREMENTS** (WITH CONTENT CONSISTENCY):
   - If job wants "scalable solutions" → Everything they built is "scalable"
   - If job emphasizes "data-driven" → Every decision was "data-driven"
   - If job needs "stakeholder management" → Transform all communication into "stakeholder management"
   - Use their keywords in EVERY bullet point with sophisticated context
   - NEVER remove content - always adapt and enhance instead

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

ORIGINAL RESUME:
{resume_text}

Return ONLY the transformed resume in plain text, starting with name. Create a detailed, impactful resume that showcases the candidate's expertise and achievements with natural, flowing language that sounds human and authentic. Focus on professional presentation, comprehensive content, and measurable results that align perfectly with the target role.
            """)
            
            
            # Create chain and run
            self._lazy_init()  # Initialize OpenAI components if needed
            chain = rag_prompt | self.llm | StrOutputParser()
            
            tailored_resume = chain.invoke({
                "resume_text": resume_text,
                "job_description": job_description,
                "job_title": job_title,
                "similar_jobs": similar_jobs_context,
                "optional_instructions": optional_instructions,
                "detected_sections_info": detected_sections_info,
                "tailoring_instructions": tailoring_instructions
            })
            
            # Log the AI response for debugging
            print("=" * 80)
            print("🤖 LANGCHAIN AI GENERATED RESPONSE:")
            print("=" * 80)
            print(repr(tailored_resume))
            print("=" * 80)
            print("📝 LANGCHAIN AI RESPONSE (FORMATTED):")
            print("=" * 80)
            print(tailored_resume)
            print("=" * 80)
            
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