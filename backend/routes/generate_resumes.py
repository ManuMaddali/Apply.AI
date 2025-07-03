from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
import asyncio
import json
from utils.gpt_prompt import GPTProcessor
from utils.resume_editor import ResumeEditor
from utils.langchain_processor import LangChainResumeProcessor
from utils.resume_diff import ResumeDiffAnalyzer

router = APIRouter()

# Initialize processors
gpt_processor = GPTProcessor()  # Updated variable name
resume_editor = ResumeEditor()
langchain_processor = LangChainResumeProcessor()
diff_analyzer = ResumeDiffAnalyzer()
fallback_processor = GPTProcessor()  # Fallback for legacy mode

class GenerateRequest(BaseModel):
    file_id: str
    jobs: List[dict]
    output_format: str = "pdf"  # "pdf" or "docx"

class ResumeRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: str
    job_url: Optional[str] = ""
    use_rag: Optional[bool] = True  # Enable RAG by default
    compare_versions: Optional[bool] = True  # Enable diff analysis
    optional_sections: Optional[Dict[str, Any]] = {
        "includeSummary": False,
        "includeSkills": False,
        "includeEducation": False,
        "educationDetails": {
            "degree": "",
            "institution": "",
            "year": "",
            "gpa": ""
        }
    }

class DiffAnalysisRequest(BaseModel):
    original_resume: str
    tailored_resume: str
    job_title: Optional[str] = ""

@router.post("/generate-resumes")
async def generate_tailored_resumes(request: GenerateRequest):
    """
    Generate tailored resumes for multiple job descriptions
    """
    try:
        # Validate input
        if len(request.jobs) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 jobs allowed"
            )
        
        if request.output_format not in ["pdf", "docx"]:
            raise HTTPException(
                status_code=400,
                detail="Output format must be 'pdf' or 'docx'"
            )
        
        # Get original resume text
        resume_file_path = f"uploads/{request.file_id}"
        if not os.path.exists(resume_file_path):
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        original_resume_text = resume_editor.extract_text_from_file(resume_file_path)
        if not original_resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        generated_resumes = []
        
        for i, job in enumerate(request.jobs):
            if job.get("status") != "success" or not job.get("job_description"):
                continue
                
            try:
                # Extract job title from URL or use generic title
                job_title = f"Job_{i+1}"
                if "linkedin.com" in job.get("url", ""):
                    job_title = f"LinkedIn_Job_{i+1}"
                elif "indeed.com" in job.get("url", ""):
                    job_title = f"Indeed_Job_{i+1}"
                elif "greenhouse" in job.get("url", ""):
                    job_title = f"Greenhouse_Job_{i+1}"
                
                # Use GPT to tailor the resume
                tailored_resume_text = gpt_processor.tailor_resume(
                    original_resume_text, 
                    job["job_description"], 
                    job_title,
                    {"includeSummary": False, "includeSkills": False, "includeEducation": False, "educationDetails": {}}  # Default to no optional sections
                )
                
                if not tailored_resume_text:
                    generated_resumes.append({
                        "job_id": job.get("id", i+1),
                        "job_url": job.get("url", ""),
                        "status": "failed",
                        "error": "Failed to generate tailored resume with GPT"
                    })
                    continue
                
                # Generate output file
                output_filename = f"{uuid.uuid4()}_{job_title}.{request.output_format}"
                output_path = f"outputs/{output_filename}"
                
                # Create the tailored resume file
                if request.output_format == "pdf":
                    success = resume_editor.create_tailored_resume_pdf(
                        tailored_resume_text, output_path, job_title
                    )
                else:  # docx
                    success = resume_editor.create_tailored_resume_docx(
                        tailored_resume_text, output_path, job_title
                    )
                
                if success:
                    generated_resumes.append({
                        "job_id": job.get("id", i+1),
                        "job_title": job_title,
                        "job_url": job.get("url", ""),
                        "status": "success",
                        "filename": output_filename,
                        "download_url": f"/api/download/{output_filename}",
                        "preview": tailored_resume_text[:300] + "..." if len(tailored_resume_text) > 300 else tailored_resume_text
                    })
                else:
                    generated_resumes.append({
                        "job_id": job.get("id", i+1),
                        "job_url": job.get("url", ""),
                        "status": "failed",
                        "error": "Failed to create output file"
                    })
                    
            except Exception as e:
                generated_resumes.append({
                    "job_id": job.get("id", i+1),
                    "job_url": job.get("url", ""),
                    "status": "failed",
                    "error": str(e)
                })
        
        successful_resumes = [r for r in generated_resumes if r["status"] == "success"]
        
        return JSONResponse({
            "message": f"Generated {len(successful_resumes)} tailored resumes",
            "total_jobs": len(request.jobs),
            "successful_generations": len(successful_resumes),
            "failed_generations": len(generated_resumes) - len(successful_resumes),
            "resumes": generated_resumes
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resumes: {str(e)}")

@router.get("/download/{filename}")
async def download_resume(filename: str):
    """
    Download a generated resume file
    """
    try:
        file_path = f"outputs/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type based on file extension
        if filename.endswith('.pdf'):
            media_type = 'application/pdf'
        elif filename.endswith('.docx'):
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            media_type = 'application/octet-stream'
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.get("/list-generated")
async def list_generated_resumes():
    """
    List all generated resume files
    """
    try:
        if not os.path.exists("outputs"):
            return JSONResponse({"files": []})
        
        files = []
        for filename in os.listdir("outputs"):
            if filename.endswith(('.pdf', '.docx')):
                file_path = f"outputs/{filename}"
                file_stats = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": file_stats.st_size,
                    "created": file_stats.st_ctime,
                    "download_url": f"/api/download/{filename}"
                })
        
        return JSONResponse({"files": files})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.post("/tailor")
async def tailor_resume(request: ResumeRequest):
    """Enhanced resume tailoring with LangChain RAG and diff analysis"""
    try:
        # Load existing job vector store
        langchain_processor.load_job_vectorstore()
        
        if request.use_rag:
            # Use LangChain RAG-enhanced processing
            result = langchain_processor.tailor_resume_with_rag(
                resume_text=request.resume_text,
                job_description=request.job_description,
                job_title=request.job_title,
                optional_sections=request.optional_sections
            )
            
            if not result:
                # Fallback to standard GPT processing
                print("RAG processing failed, using fallback...")
                tailored_resume = fallback_processor.tailor_resume(
                    request.resume_text, 
                    request.job_description, 
                    request.job_title,
                    request.optional_sections
                )
                result = {
                    "session_id": "fallback",
                    "tailored_resume": tailored_resume,
                    "similar_jobs_found": 0,
                    "rag_insights": [],
                    "processing_steps": ["Used fallback GPT processing"]
                }
        else:
            # Use standard GPT processing
            tailored_resume = fallback_processor.tailor_resume(
                request.resume_text, 
                request.job_description, 
                request.job_title,
                request.optional_sections
            )
            result = {
                "session_id": "standard",
                "tailored_resume": tailored_resume,
                "similar_jobs_found": 0,
                "rag_insights": [],
                "processing_steps": ["Used standard GPT processing"]
            }

        # Perform diff analysis if requested
        diff_analysis = None
        if request.compare_versions and result.get("tailored_resume"):
            diff_analysis = diff_analyzer.analyze_resume_diff(
                original_text=request.resume_text,
                tailored_text=result["tailored_resume"],
                job_title=request.job_title
            )

        # Store job description in vector store for future RAG
        if request.job_description and request.job_url:
            job_data = [{
                "id": result.get("session_id", "unknown"),
                "job_description": request.job_description,
                "job_title": request.job_title,
                "url": request.job_url
            }]
            langchain_processor.initialize_job_vectorstore(job_data)

        response_data = {
            "success": True,
            "session_id": result.get("session_id"),
            "tailored_resume": result.get("tailored_resume"),
            "processing_mode": "RAG-Enhanced" if request.use_rag else "Standard",
            "rag_insights": {
                "similar_jobs_found": result.get("similar_jobs_found", 0),
                "insights": result.get("rag_insights", []),
                "processing_steps": result.get("processing_steps", [])
            }
        }

        # Add diff analysis if performed
        if diff_analysis:
            response_data["diff_analysis"] = diff_analysis
            response_data["diff_report"] = diff_analyzer.create_diff_report(diff_analysis)

        return JSONResponse(content=response_data)

    except Exception as e:
        print(f"Error in tailor_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resume tailoring failed: {str(e)}")

@router.post("/analyze-diff")
async def analyze_resume_diff(request: DiffAnalysisRequest):
    """Standalone diff analysis between two resume versions"""
    try:
        diff_analysis = diff_analyzer.analyze_resume_diff(
            original_text=request.original_resume,
            tailored_text=request.tailored_resume,
            job_title=request.job_title
        )
        
        diff_report = diff_analyzer.create_diff_report(diff_analysis)
        
        return JSONResponse(content={
            "success": True,
            "diff_analysis": diff_analysis,
            "diff_report": diff_report
        })
        
    except Exception as e:
        print(f"Error in analyze_resume_diff: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diff analysis failed: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Retrieve session history and analysis"""
    try:
        session_data = langchain_processor.get_session_history(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return JSONResponse(content={
            "success": True,
            "session_data": session_data
        })
        
    except Exception as e:
        print(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session retrieval failed: {str(e)}")

@router.get("/sessions")
async def get_all_sessions():
    """Get all session history"""
    try:
        all_sessions = langchain_processor.get_all_sessions()
        
        return JSONResponse(content={
            "success": True,
            "total_sessions": len(all_sessions),
            "sessions": all_sessions
        })
        
    except Exception as e:
        print(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sessions retrieval failed: {str(e)}")

@router.post("/initialize-rag")
async def initialize_rag_system(job_descriptions: list):
    """Initialize or update the RAG system with job descriptions"""
    try:
        success = langchain_processor.initialize_job_vectorstore(job_descriptions)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"RAG system initialized with {len(job_descriptions)} job descriptions"
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize RAG system")
            
    except Exception as e:
        print(f"Error initializing RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG initialization failed: {str(e)}")

@router.get("/rag-status")
async def get_rag_status():
    """Get status of RAG system"""
    try:
        vector_store_exists = langchain_processor.load_job_vectorstore()
        
        return JSONResponse(content={
            "success": True,
            "rag_available": vector_store_exists,
            "vector_store_path": "vector_stores/job_descriptions"
        })
        
    except Exception as e:
        print(f"Error checking RAG status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG status check failed: {str(e)}") 