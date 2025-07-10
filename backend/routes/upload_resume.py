from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
from utils.resume_editor import ResumeEditor

router = APIRouter()
resume_editor = ResumeEditor()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and process a resume file (PDF, DOCX, or TXT)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
            return JSONResponse({
                "success": False,
                "detail": "Only PDF, DOCX, and TXT files are supported"
            })
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"uploads/{unique_filename}"
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Extract text from file
        resume_text = resume_editor.extract_text_from_file(file_path)
        
        if not resume_text:
            # Clean up the uploaded file
            os.remove(file_path)
            return JSONResponse({
                "success": False,
                "detail": "Could not extract text from the uploaded file"
            })
        
        return JSONResponse({
            "success": True,
            "message": "Resume uploaded successfully",
            "file_id": unique_filename,
            "original_filename": file.filename,
            "resume_text": resume_text,
            "preview": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "detail": f"Error processing resume: {str(e)}"
        })

@router.get("/resume/{file_id}")
async def get_resume_text(file_id: str):
    """
    Get the full text content of an uploaded resume
    """
    try:
        file_path = f"uploads/{file_id}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        resume_text = resume_editor.extract_text_from_file(file_path)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        return JSONResponse({
            "file_id": file_id,
            "resume_text": resume_text
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resume: {str(e)}") 