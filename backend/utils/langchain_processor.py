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
                max_tokens=4000
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
INSTRUCTIONS: You are a professional resume editor with access to industry intelligence. Tailor this resume for the {job_title} position. Return ONLY the final resume content - no explanations, no conversational text, no preamble.

{similar_job_insights}

RULES:
- NEVER fabricate information not in the original resume
- NEVER add placeholder text or brackets
- Use ONLY factual information from the provided resume
- Maintain 100% accuracy while enhancing presentation
- Return the resume in a clean, professional format
- Do NOT include conversational phrases like "Here's your resume" or "Sure!"

ADVANCED TAILORING STRATEGIES:

1. RAG-ENHANCED POSITIONING:
- Use insights from similar job postings to understand industry expectations
- Identify common requirements across similar roles
- Position existing experience to match industry standards
- Emphasize skills and achievements most valued in this job category

2. MULTI-STEP ANALYSIS:
- Step 1: Analyze job requirements and extract key themes
- Step 2: Map existing experience to these themes
- Step 3: Identify transferable skills and achievements
- Step 4: Reframe content using industry-specific terminology
- Step 5: Optimize for ATS and human reviewers

3. INTELLIGENT SKILLS CURATION:
- Extract skills actually demonstrated in work experience
- Prioritize based on job requirements and similar job patterns
- Group into strategic categories (Technical, Leadership, Domain)
- Only include skills with evidence in experience

4. EXPERIENCE OPTIMIZATION:
- Rewrite achievements to emphasize outcomes valued by target industry
- Use exact terminology from job description where natural
- Quantify impact using existing metrics
- Connect experience to business value in target sector

TARGET JOB:
Title: {job_title}
Description: {job_description}

ORIGINAL RESUME:
{resume_text}

DELIVER: The tailored resume content only, starting with the name/contact info.
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