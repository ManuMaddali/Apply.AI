from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
import time
from datetime import datetime

router = APIRouter()

# Simple in-memory storage for batch jobs
batch_jobs: Dict[str, Any] = {}
batch_results: Dict[str, List[Dict[str, Any]]] = {}

class SimpleBatchRequest(BaseModel):
    resume_text: str
    job_urls: List[str]
    use_rag: Optional[bool] = True
    output_format: Optional[str] = "text"
    tailoring_mode: Optional[str] = "light"
    optional_sections: Optional[Dict[str, Any]] = {}
    cover_letter_options: Optional[Dict[str, Any]] = {}

class SimpleBatchStatus:
    def __init__(self, batch_id: str, total_jobs: int):
        self.batch_id = batch_id
        self.state = "pending"  # pending, processing, completed, failed
        self.total = total_jobs
        self.completed = 0
        self.failed = 0
        self.current_job = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results = []

    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "state": self.state,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "current_job": self.current_job,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

def simple_job_scraper(url: str) -> Dict[str, Any]:
    """Simple mock job scraper"""
    return {
        "title": f"Job Title from {url}",
        "company": "Sample Company",
        "description": "This is a sample job description for testing purposes.",
        "requirements": ["Sample requirement 1", "Sample requirement 2"]
    }

def simple_resume_processor(resume_text: str, job_data: Dict[str, Any]) -> str:
    """Simple resume processor"""
    job_title = job_data.get('title', 'Unknown Position')
    company = job_data.get('company', 'Unknown Company')
    
    tailored_resume = f"""TAILORED RESUME FOR {job_title.upper()} AT {company.upper()}

{resume_text}

--- TAILORED SECTIONS ---

RELEVANT SKILLS FOR THIS POSITION:
• Skill relevant to {job_title}
• Experience with {company} type of work
• Additional qualifications for this role

CUSTOMIZED SUMMARY:
Experienced professional seeking the {job_title} position at {company}. 
Ready to contribute to your team's success.

[This resume has been automatically tailored for the {job_title} position]
"""
    return tailored_resume

async def process_single_job_simple(resume_text: str, job_url: str, job_index: int, batch_id: str) -> Dict[str, Any]:
    """Process a single job - simplified version"""
    try:
        print(f"🔄 Processing job {job_index + 1}: {job_url}")
        
        # Update batch status
        if batch_id in batch_jobs:
            batch_jobs[batch_id].current_job = f"Processing job {job_index + 1}: {job_url}"
            batch_jobs[batch_id].updated_at = datetime.now()
        
        # Simulate some processing time
        await asyncio.sleep(2)
        
        # Scrape job (mock)
        job_data = simple_job_scraper(job_url)
        
        # Process resume
        tailored_resume = simple_resume_processor(resume_text, job_data)
        
        # Generate cover letter (simple)
        cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_data['title']} position at {job_data['company']}.

Based on the job requirements, I believe my background makes me an ideal candidate for this role.

Best regards,
[Your Name]"""
        
        result = {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": job_data['title'],
            "company": job_data['company'],
            "status": "completed",
            "tailored_resume": tailored_resume,
            "cover_letter": cover_letter,
            "processing_time": 2.0
        }
        
        print(f"✅ Completed job {job_index + 1}: {job_data['title']}")
        return result
        
    except Exception as e:
        print(f"❌ Error processing job {job_index + 1}: {str(e)}")
        return {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": f"Job_{job_index + 1}",
            "status": "failed",
            "error": str(e),
            "tailored_resume": None,
            "cover_letter": None
        }

async def process_batch_simple(batch_id: str, resume_text: str, job_urls: List[str]):
    """Process batch jobs - simplified version"""
    try:
        print(f"🚀 Starting batch processing for {len(job_urls)} jobs")
        
        if batch_id not in batch_jobs:
            print(f"❌ Batch ID {batch_id} not found!")
            return
        
        batch_jobs[batch_id].state = "processing"
        batch_jobs[batch_id].updated_at = datetime.now()
        
        results = []
        
        # Process jobs sequentially for simplicity
        for i, job_url in enumerate(job_urls):
            result = await process_single_job_simple(resume_text, job_url, i, batch_id)
            results.append(result)
            
            # Update progress
            if batch_id in batch_jobs:
                if result["status"] == "completed":
                    batch_jobs[batch_id].completed += 1
                else:
                    batch_jobs[batch_id].failed += 1
                batch_jobs[batch_id].updated_at = datetime.now()
        
        # Mark as completed
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "completed"
            batch_jobs[batch_id].current_job = "All jobs completed"
            batch_jobs[batch_id].results = results
            batch_jobs[batch_id].updated_at = datetime.now()
        
        # Store results
        batch_results[batch_id] = results
        
        print(f"🎉 Batch processing completed! {len(results)} jobs processed")
        
    except Exception as e:
        print(f"❌ Batch processing failed: {str(e)}")
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "failed"
            batch_jobs[batch_id].current_job = f"Failed: {str(e)}"
            batch_jobs[batch_id].updated_at = datetime.now()

@router.post("/process")
async def start_simple_batch_processing(request: SimpleBatchRequest, background_tasks: BackgroundTasks):
    """Start simple batch processing"""
    try:
        print(f"🚨 SIMPLE BATCH PROCESSING STARTED!")
        print(f"📋 Resume length: {len(request.resume_text)}")
        print(f"📋 Job URLs: {request.job_urls}")
        
        if not request.job_urls:
            raise HTTPException(status_code=400, detail="At least one job URL is required")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Initialize batch status
        batch_status = SimpleBatchStatus(batch_id, len(request.job_urls))
        batch_jobs[batch_id] = batch_status
        
        # Start background processing
        background_tasks.add_task(
            process_batch_simple,
            batch_id,
            request.resume_text,
            request.job_urls
        )
        
        return JSONResponse({
            "success": True,
            "batch_job_id": batch_id,
            "message": f"Simple batch processing started for {len(request.job_urls)} jobs",
            "status": batch_status.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Failed to start batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")

@router.get("/status/{batch_id}")
async def get_simple_batch_status(batch_id: str):
    """Get batch status"""
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    batch_status = batch_jobs[batch_id]
    return JSONResponse({
        "success": True,
        "status": batch_status.to_dict()
    })

@router.get("/results/{batch_id}")
async def get_simple_batch_results(batch_id: str):
    """Get batch results"""
    if batch_id not in batch_results:
        raise HTTPException(status_code=404, detail="Batch results not found")
    
    results = batch_results[batch_id]
    return JSONResponse({
        "success": True,
        "results": results,
        "total": len(results)
    })

@router.get("/test")
async def test_simple_batch():
    """Test endpoint"""
    return {"status": "ok", "message": "Simple batch processing is working!"}
