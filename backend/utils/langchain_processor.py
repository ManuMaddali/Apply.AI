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
    
    def tailor_resume_with_rag(self, resume_text: str, job_description: str, job_title: str) -> Optional[Dict[str, Any]]:
        """Enhanced resume tailoring with RAG capabilities"""
        if not self.langchain_available:
            print("⚠️ LangChain not available - using fallback mode")
            return None
            
        try:
            # Retrieve similar jobs for context
            similar_jobs = self.retrieve_similar_jobs(job_description, k=3)
            
            # Create enhanced prompt with RAG context
            prompt = self.create_enhanced_tailoring_prompt(
                resume_text, job_description, job_title, similar_jobs
            )
            
            # Create a custom prompt template for system instructions
            system_template = """You are a professional resume editor with access to industry intelligence. Return ONLY the tailored resume content without any conversational text, explanations, or preamble. Do not include phrases like 'Here's a resume' or 'Sure!' - just provide the clean, professional resume text.

{input}"""
            
            prompt_template = PromptTemplate(
                input_variables=["input"],
                template=system_template
            )
            
            # Create conversation chain with memory and custom prompt
            conversation = ConversationChain(
                llm=self.llm,
                memory=self.memory,
                prompt=prompt_template,
                verbose=False
            )
            
            # Generate tailored resume
            tailored_resume = conversation.predict(input=prompt)
            
            # Clean up any remaining conversational elements
            tailored_resume = tailored_resume.strip()
            # Remove common conversational starters
            conversational_starters = [
                "Sure! Here's", "Here's a", "Here is a", "I've created", 
                "Here's your", "Below is", "I'll help you", "Let me provide"
            ]
            for starter in conversational_starters:
                if tailored_resume.startswith(starter):
                    # Find the end of the sentence and remove it
                    first_sentence_end = tailored_resume.find('.')
                    if first_sentence_end != -1:
                        tailored_resume = tailored_resume[first_sentence_end + 1:].strip()
                    break
            
            # Store in session memory
            session_id = str(uuid.uuid4())
            self.resume_history[session_id] = {
                "original_resume": resume_text,
                "tailored_resume": tailored_resume,
                "job_description": job_description,
                "job_title": job_title,
                "similar_jobs_used": len(similar_jobs),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "session_id": session_id,
                "tailored_resume": tailored_resume,
                "similar_jobs_found": len(similar_jobs),
                "rag_insights": [doc.metadata for doc in similar_jobs],
                "processing_steps": [
                    "Retrieved similar job postings",
                    "Analyzed industry patterns", 
                    "Enhanced prompt with RAG context",
                    "Generated tailored resume",
                    "Stored session history"
                ]
            }
            
        except Exception as e:
            print(f"Error in RAG-enhanced tailoring: {str(e)}")
            return None
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session history"""
        return self.resume_history.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, Any]:
        """Get all session history"""
        return self.resume_history 