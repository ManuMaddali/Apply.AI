from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
import time
import os
import zipfile
import tempfile
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY
from utils.job_scraper import JobScraper
from utils.langchain_processor import LangChainResumeProcessor
from utils.gpt_prompt import GPTProcessor
from utils.resume_diff import ResumeDiffAnalyzer
from utils.resume_editor import ResumeEditor

router = APIRouter()

# Initialize processors
job_scraper = JobScraper()
langchain_processor = LangChainResumeProcessor()
fallback_processor = GPTProcessor()
diff_analyzer = ResumeDiffAnalyzer()
resume_editor = ResumeEditor()

# In-memory storage for batch jobs (consider using Redis or a database for production)
batch_jobs: Dict[str, Any] = {}
batch_results: Dict[str, List[Dict[str, Any]]] = {}

class BatchProcessRequest(BaseModel):
    resume_text: str
    job_urls: List[str]
    use_rag: Optional[bool] = True
    output_format: Optional[str] = "text"  # "text" or "files"
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

class PDFGenerateRequest(BaseModel):
    resume_text: str
    job_title: str
    filename: Optional[str] = None

class ZIPGenerateRequest(BaseModel):
    resumes: List[Dict[str, Any]]
    batch_id: str

def generate_pdf_from_text(resume_text: str, job_title: str) -> BytesIO:
    """Generate PDF using ResumeEditor for better formatting"""
    try:
        # Create temporary file for PDF
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)  # Close the file descriptor
        
        # Use ResumeEditor to create the PDF with proper formatting
        success = resume_editor.create_tailored_resume_pdf(
            tailored_text=resume_text,
            output_path=temp_path,
            job_title=job_title
        )
        
        if not success:
            raise Exception("Failed to create PDF with ResumeEditor")
        
        # Read the PDF into a BytesIO buffer
        buffer = BytesIO()
        with open(temp_path, 'rb') as f:
            buffer.write(f.read())
        
        # Clean up temp file
        os.unlink(temp_path)
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        # Fallback to basic PDF if ResumeEditor fails
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        content = [
            Paragraph(f"Resume for: {job_title}", styles['Title']),
            Paragraph("Error generating formatted PDF. Content:", styles['Normal']),
            Spacer(1, 12),
            Paragraph(resume_text[:1000] + "...", styles['Normal'])
        ]
        doc.build(content)
        buffer.seek(0)
        return buffer

class BatchJobStatus:
    def __init__(self, batch_id: str, total_jobs: int, optional_sections: Dict[str, Any] = None):
        self.batch_id = batch_id
        self.state = "pending"  # pending, processing, completed, failed
        self.total = total_jobs
        self.completed = 0
        self.failed = 0
        self.current_job = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results = []
        self.optional_sections = optional_sections or {
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

async def process_single_job(resume_text: str, job_url: str, use_rag: bool, optional_sections: Dict[str, Any], batch_id: str, job_index: int) -> Dict[str, Any]:
    """Process a single job and return the result"""
    try:
        # Update current job in status
        if batch_id in batch_jobs:
            batch_jobs[batch_id].current_job = f"Job {job_index + 1}: {job_url[:50]}..."
            batch_jobs[batch_id].updated_at = datetime.now()

        # Scrape job description
        job_description = job_scraper.scrape_job_description(job_url)
        if not job_description:
            return {
                "job_index": job_index,
                "job_url": job_url,
                "job_title": f"Job_{job_index + 1}",
                "status": "failed",
                "error": "Failed to scrape job description",
                "tailored_resume": None
            }

        # Extract job title
        job_title = job_scraper.extract_job_title(job_url) or f"Job_{job_index + 1}"

        # Tailor resume using RAG or fallback
        if use_rag:
            langchain_processor.load_job_vectorstore()
            rag_result = langchain_processor.tailor_resume_with_rag(
                resume_text=resume_text,
                job_description=job_description,
                job_title=job_title,
                optional_sections=optional_sections
            )
            
            if rag_result:
                tailored_resume = rag_result.get("tailored_resume")
                similar_jobs_found = rag_result.get("similar_jobs_found", 0)
            else:
                # Fallback to standard processing
                tailored_resume = fallback_processor.tailor_resume(
                    resume_text, job_description, job_title, optional_sections
                )
                similar_jobs_found = 0
        else:
            tailored_resume = fallback_processor.tailor_resume(
                resume_text, job_description, job_title, optional_sections
            )
            similar_jobs_found = 0

        if not tailored_resume:
            return {
                "job_index": job_index,
                "job_url": job_url,
                "job_title": job_title,
                "status": "failed",
                "error": "Failed to generate tailored resume",
                "tailored_resume": None
            }

        # Perform diff analysis
        diff_analysis = diff_analyzer.analyze_resume_diff(
            original_text=resume_text,
            tailored_text=tailored_resume,
            job_title=job_title
        )

        # Store job description for future RAG
        if job_description and job_url:
            job_data = [{
                "id": f"{batch_id}_{job_index}",
                "job_description": job_description,
                "job_title": job_title,
                "url": job_url
            }]
            langchain_processor.initialize_job_vectorstore(job_data)

        return {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": job_title,
            "job_description": job_description,
            "status": "success",
            "tailored_resume": tailored_resume,
            "similar_jobs_found": similar_jobs_found,
            "enhancement_score": diff_analysis.get("enhancement_score", {}).get("overall_score"),
            "diff_analysis": diff_analysis,
            "processing_time": time.time()
        }

    except Exception as e:
        return {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": f"Job_{job_index + 1}",
            "status": "failed",
            "error": str(e),
            "tailored_resume": None
        }

async def process_batch_jobs(batch_id: str, resume_text: str, job_urls: List[str], use_rag: bool, output_format: str, optional_sections: Dict[str, Any]):
    """Background task to process all jobs in a batch"""
    try:
        batch_jobs[batch_id].state = "processing"
        batch_jobs[batch_id].updated_at = datetime.now()
        
        results = []
        
        # Process jobs sequentially (could be made parallel for better performance)
        for i, job_url in enumerate(job_urls):
            result = await process_single_job(resume_text, job_url, use_rag, optional_sections, batch_id, i)
            results.append(result)
            
            # Update progress
            if batch_id in batch_jobs:
                batch_jobs[batch_id].completed += 1
                if result["status"] == "failed":
                    batch_jobs[batch_id].failed += 1
                batch_jobs[batch_id].updated_at = datetime.now()
                batch_jobs[batch_id].results.append(result)

        # Store final results
        batch_results[batch_id] = results
        
        # Mark as completed
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "completed"
            batch_jobs[batch_id].current_job = None
            batch_jobs[batch_id].updated_at = datetime.now()
            
    except Exception as e:
        # Mark as failed
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "failed"
            batch_jobs[batch_id].current_job = f"Error: {str(e)}"
            batch_jobs[batch_id].updated_at = datetime.now()

@router.post("/process")
async def start_batch_processing(request: BatchProcessRequest, background_tasks: BackgroundTasks):
    """Start batch processing of multiple job URLs"""
    try:
        # Validate input
        if len(request.job_urls) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 job URLs allowed")
        
        if len(request.job_urls) == 0:
            raise HTTPException(status_code=400, detail="At least one job URL is required")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Initialize batch status
        batch_status = BatchJobStatus(batch_id, len(request.job_urls), request.optional_sections)
        batch_jobs[batch_id] = batch_status
        
        # Start background processing
        background_tasks.add_task(
            process_batch_jobs,
            batch_id,
            request.resume_text,
            request.job_urls,
            request.use_rag,
            request.output_format,
            request.optional_sections
        )
        
        return JSONResponse({
            "success": True,
            "batch_job_id": batch_id,
            "message": f"Batch processing started for {len(request.job_urls)} jobs",
            "status": {
                "state": batch_status.state,
                "total": batch_status.total,
                "completed": batch_status.completed,
                "failed": batch_status.failed,
                "current_job": batch_status.current_job
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")

@router.post("/generate-pdf")
async def generate_single_pdf(request: PDFGenerateRequest):
    """Generate a single PDF from resume text"""
    try:
        # Generate PDF
        pdf_buffer = generate_pdf_from_text(request.resume_text, request.job_title)
        
        # Return PDF as response
        from fastapi.responses import Response
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename or 'resume.pdf'}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.post("/generate-zip")
async def generate_zip_file(request: ZIPGenerateRequest):
    """Generate a ZIP file containing multiple resume PDFs with improved error handling"""
    zip_path = None
    try:
        # Validate input
        if not request.resumes:
            raise HTTPException(status_code=400, detail="No resumes provided")
        
        if len(request.resumes) > 20:  # Safety limit
            raise HTTPException(status_code=400, detail="Too many resumes requested")
        
        # Create temporary file for ZIP
        import tempfile
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, f"batch_resumes_{request.batch_id[:8]}_{int(time.time())}.zip")
        
        successful_pdfs = 0
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for i, resume_data in enumerate(request.resumes):
                try:
                    # Validate resume data
                    if not resume_data.get('resume_text'):
                        print(f"Skipping resume {i+1}: No resume text")
                        continue
                    
                    if not resume_data.get('job_title'):
                        resume_data['job_title'] = f"Resume_{i+1}"
                    
                    # Generate PDF for this resume
                    pdf_buffer = generate_pdf_from_text(
                        resume_data['resume_text'], 
                        resume_data['job_title']
                    )
                    
                    # Create safe filename
                    job_title = resume_data['job_title']
                    safe_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()
                    if not safe_title:
                        safe_title = f"Resume_{i+1}"
                    safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
                    filename = f"{i+1:02d}_{safe_title}.pdf"
                    
                    # Add PDF to ZIP
                    zipf.writestr(filename, pdf_buffer.getvalue())
                    successful_pdfs += 1
                    
                    # Add summary file for this resume
                    summary_content = f"""Resume: {resume_data['job_title']}
Job URL: {resume_data.get('job_url', 'N/A')}
Enhancement Score: {resume_data.get('enhancement_score', 'N/A')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: Successfully generated
"""
                    
                    summary_filename = f"{i+1:02d}_{safe_title}_info.txt"
                    zipf.writestr(summary_filename, summary_content.encode('utf-8'))
                    
                except Exception as e:
                    print(f"Error processing resume {i+1}: {str(e)}")
                    # Add error info file instead
                    try:
                        error_content = f"""Resume: {resume_data.get('job_title', f'Resume_{i+1}')}
Job URL: {resume_data.get('job_url', 'N/A')}
Status: Failed to generate PDF
Error: {str(e)}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                        error_filename = f"{i+1:02d}_ERROR_{resume_data.get('job_title', f'Resume_{i+1}')[:20]}.txt"
                        zipf.writestr(error_filename, error_content.encode('utf-8'))
                    except:
                        pass  # Skip if even error file creation fails
                    continue
            
            # Add batch summary
            batch_summary = f"""BATCH PROCESSING SUMMARY
========================
Batch ID: {request.batch_id}
Total Resumes Requested: {len(request.resumes)}
Successful PDFs Generated: {successful_pdfs}
Failed: {len(request.resumes) - successful_pdfs}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This ZIP file contains:
- {successful_pdfs} successfully generated PDF resume(s)
- Info files with job details and enhancement scores
- Error logs for any failed generations
- This summary file

All resumes have been tailored using AI for specific job requirements.
RAG (Retrieval-Augmented Generation) and advanced diff analysis were applied.
"""
            zipf.writestr("BATCH_SUMMARY.txt", batch_summary.encode('utf-8'))
        
        # Verify ZIP file was created and has content
        if not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
            raise Exception("ZIP file was not created properly")
        
        if successful_pdfs == 0:
            raise Exception("No PDFs were successfully generated")
        
        # Return ZIP file
        def cleanup_file():
            try:
                if os.path.exists(zip_path):
                    os.unlink(zip_path)
            except Exception as e:
                print(f"Error cleaning up file: {e}")
        
        background_tasks = BackgroundTasks()
        background_tasks.add_task(cleanup_file)
        
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"batch_resumes_{request.batch_id[:8]}.zip",
            background=background_tasks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if zip_path and os.path.exists(zip_path):
            try:
                os.unlink(zip_path)
            except:
                pass
        
        print(f"ZIP generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ZIP file: {str(e)}")

@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get the current status of a batch job"""
    try:
        if batch_id not in batch_jobs:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        batch_status = batch_jobs[batch_id]
        
        return JSONResponse({
            "success": True,
            "batch_id": batch_id,
            "status": {
                "state": batch_status.state,
                "total": batch_status.total,
                "completed": batch_status.completed,
                "failed": batch_status.failed,
                "current_job": batch_status.current_job,
                "created_at": batch_status.created_at.isoformat(),
                "updated_at": batch_status.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch status: {str(e)}")

@router.get("/results/{batch_id}")
async def get_batch_results(batch_id: str):
    """Get the results of a completed batch job"""
    try:
        if batch_id not in batch_jobs:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        batch_status = batch_jobs[batch_id]
        
        # Return results from either batch_results or batch_status
        results = batch_results.get(batch_id, batch_status.results)
        
        return JSONResponse({
            "success": True,
            "batch_id": batch_id,
            "total_jobs": batch_status.total,
            "successful_jobs": len([r for r in results if r["status"] == "success"]),
            "failed_jobs": len([r for r in results if r["status"] == "failed"]),
            "results": results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get batch results: {str(e)}")

@router.get("/jobs")
async def list_batch_jobs():
    """List all batch jobs (for admin/debugging)"""
    try:
        jobs_summary = []
        for batch_id, batch_status in batch_jobs.items():
            jobs_summary.append({
                "batch_id": batch_id,
                "state": batch_status.state,
                "total": batch_status.total,
                "completed": batch_status.completed,
                "failed": batch_status.failed,
                "created_at": batch_status.created_at.isoformat(),
                "updated_at": batch_status.updated_at.isoformat()
            })
        
        return JSONResponse({
            "success": True,
            "total_batches": len(jobs_summary),
            "batches": jobs_summary
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list batch jobs: {str(e)}")

@router.delete("/jobs/{batch_id}")
async def delete_batch_job(batch_id: str):
    """Delete a batch job and its results"""
    try:
        if batch_id not in batch_jobs:
            raise HTTPException(status_code=404, detail="Batch job not found")
        
        # Remove from storage
        del batch_jobs[batch_id]
        if batch_id in batch_results:
            del batch_results[batch_id]
        
        return JSONResponse({
            "success": True,
            "message": f"Batch job {batch_id} deleted successfully"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete batch job: {str(e)}")

@router.get("/download/{result_id}")
async def download_batch_result(result_id: str):
    """Download a specific result file (if files were generated)"""
    try:
        # This would be implemented when file generation is added
        # For now, return a placeholder response
        raise HTTPException(status_code=501, detail="File download not yet implemented")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download result: {str(e)}") 