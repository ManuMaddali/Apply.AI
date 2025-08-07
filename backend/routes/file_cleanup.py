#!/usr/bin/env python3
"""
File Cleanup API Routes
Provides endpoints for managing automatic file deletion after 24 hours
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from config.database import get_db
from models.user import User
from models.file_metadata import FileMetadata
from services.file_cleanup_service import file_cleanup_service
from utils.auth import AuthManager
from utils.rate_limiter import limiter
from fastapi import Request

router = APIRouter(prefix="/file-cleanup", tags=["file-cleanup"])

@router.get("/stats")
@limiter.limit("10/minute")
async def get_cleanup_stats(
    request: Request,
    current_user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """Get file cleanup statistics for the current user"""
    try:
        # Get user-specific file statistics
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Count user's files
        user_files = db.query(FileMetadata).filter(
            FileMetadata.user_id == current_user.id
        ).all()
        
        expired_files = [f for f in user_files if f.created_at < cutoff_time]
        
        total_size = sum(f.file_size_bytes for f in user_files)
        expired_size = sum(f.file_size_bytes for f in expired_files)
        
        return {
            "success": True,
            "stats": {
                "total_files": len(user_files),
                "expired_files": len(expired_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "expired_size_mb": round(expired_size / (1024 * 1024), 2),
                "cleanup_age_hours": 24,
                "files": [f.to_dict() for f in user_files]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cleanup stats: {str(e)}"
        )

@router.post("/cleanup-user-files")
@limiter.limit("5/minute")
async def cleanup_user_files(
    request: Request,
    current_user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """Manually trigger cleanup of current user's expired files"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Get user's expired files
        expired_files = db.query(FileMetadata).filter(
            FileMetadata.user_id == current_user.id,
            FileMetadata.created_at < cutoff_time
        ).all()
        
        deleted_count = 0
        space_freed = 0
        errors = []
        
        for file_record in expired_files:
            try:
                # Delete physical file
                from pathlib import Path
                file_path = Path(file_record.file_path)
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    space_freed += file_size
                
                # Remove database record
                db.delete(file_record)
                deleted_count += 1
                
            except Exception as e:
                errors.append(f"Failed to delete {file_record.original_filename}: {str(e)}")
        
        # Commit changes
        db.commit()
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} expired files",
            "stats": {
                "files_deleted": deleted_count,
                "space_freed_mb": round(space_freed / (1024 * 1024), 2),
                "errors": errors
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup user files: {str(e)}"
        )

@router.post("/run-global-cleanup")
@limiter.limit("1/minute")
async def run_global_cleanup(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(AuthManager.verify_token)
):
    """Trigger global file cleanup (admin only)"""
    # Check if user is admin (you can implement admin role checking)
    if not current_user.role or current_user.role.value != "admin":
        # For now, allow Pro users to trigger global cleanup
        if not (current_user.subscription_tier and current_user.subscription_tier.value == "pro"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Pro users can trigger global cleanup"
            )
    
    try:
        # Run cleanup in background
        background_tasks.add_task(file_cleanup_service.cleanup_expired_files)
        
        return {
            "success": True,
            "message": "Global file cleanup started in background"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start global cleanup: {str(e)}"
        )

@router.get("/system-stats")
@limiter.limit("5/minute")
async def get_system_cleanup_stats(
    request: Request,
    current_user: User = Depends(AuthManager.verify_token)
):
    """Get system-wide cleanup statistics (Pro users only)"""
    if not (current_user.subscription_tier and current_user.subscription_tier.value == "pro"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a Pro subscription"
        )
    
    try:
        stats = await file_cleanup_service.get_cleanup_stats()
        
        return {
            "success": True,
            "system_stats": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system stats: {str(e)}"
        )

@router.delete("/file/{file_id}")
@limiter.limit("10/minute")
async def delete_specific_file(
    request: Request,
    file_id: str,
    current_user: User = Depends(AuthManager.verify_token),
    db: Session = Depends(get_db)
):
    """Delete a specific file by ID (user can only delete their own files)"""
    try:
        # Find the file
        file_record = db.query(FileMetadata).filter(
            FileMetadata.id == file_id,
            FileMetadata.user_id == current_user.id
        ).first()
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or access denied"
            )
        
        # Delete physical file
        from pathlib import Path
        file_path = Path(file_record.file_path)
        space_freed = 0
        
        if file_path.exists():
            space_freed = file_path.stat().st_size
            file_path.unlink()
        
        # Remove database record
        filename = file_record.original_filename
        db.delete(file_record)
        db.commit()
        
        return {
            "success": True,
            "message": f"File '{filename}' deleted successfully",
            "space_freed_mb": round(space_freed / (1024 * 1024), 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
