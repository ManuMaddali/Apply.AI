from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
from utils.resume_editor import ResumeEditor
from utils.file_tracker import FileTracker
from utils.auth import AuthManager
from utils.advanced_file_validator import file_validator, validate_uploaded_file
from models.user import User
from config.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()
resume_editor = ResumeEditor()

@router.post("/upload")
async def upload_resume(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process a resume file (PDF, DOCX, or TXT)
    """
    try:
        # Advanced file validation with python-magic
        if not file.filename:
            return JSONResponse({
                "success": False,
                "detail": "No filename provided"
            })
        
        # Save file temporarily for validation
        temp_content = await file.read()
        await file.seek(0)  # Reset file pointer for later use
        
        # Validate file using advanced validator
        validation_result = file_validator.validate_file(
            file_path="temp_validation",  # Placeholder path
            original_filename=file.filename,
            file_content=temp_content
        )
        
        if not validation_result.is_valid:
            error_details = {
                "success": False,
                "detail": "File validation failed",
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "detected_type": validation_result.detected_type,
                "security_score": validation_result.security_score
            }
            return JSONResponse(error_details, status_code=400)
        
        # Log validation success
        print(f"✅ File validation passed: {validation_result.mime_type} (security score: {validation_result.security_score})")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename or "")[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"uploads/{unique_filename}"
        
        # Get current user (optional for file tracking)
        current_user = None
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from fastapi.security import HTTPAuthorizationCredentials
                credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_header[7:])
                current_user = AuthManager.verify_token(credentials, db)
        except Exception:
            # User not authenticated, continue as anonymous
            pass
        
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
        
        # Track the uploaded file for auto-deletion
        try:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            request_info = {
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": validation_result.mime_type,
                "detected_type": validation_result.detected_type,
                "security_score": validation_result.security_score,
                "file_size_bytes": validation_result.file_size,
                "validation_warnings": validation_result.warnings
            }
            
            FileTracker.track_file_upload(
                file_path=file_path,
                original_filename=file.filename or "unknown",
                user=current_user,
                upload_purpose="resume",
                request_info=request_info
            )
        except Exception as e:
            # Log the error but don't fail the upload
            print(f"Warning: Failed to track file upload: {e}")
        
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