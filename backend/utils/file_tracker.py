#!/usr/bin/env python3
"""
File Tracking Utility
Tracks uploaded files for automatic cleanup after 24 hours
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from models.file_metadata import FileMetadata
from models.user import User
from config.database import SessionLocal

class FileTracker:
    """Utility class for tracking uploaded files"""
    
    @staticmethod
    def track_file_upload(
        file_path: str,
        original_filename: str,
        user: Optional[User] = None,
        user_email: Optional[str] = None,
        upload_purpose: str = "resume",
        processing_session_id: Optional[str] = None,
        request_info: Optional[Dict[str, Any]] = None
    ) -> FileMetadata:
        """
        Track a newly uploaded file for automatic cleanup
        
        Args:
            file_path: Full path to the uploaded file
            original_filename: Original name of the uploaded file
            user: User object (if authenticated)
            user_email: User email (for anonymous users)
            upload_purpose: Purpose of the upload (resume, job_description, etc.)
            processing_session_id: ID linking to batch processing session
            request_info: Additional request information (IP, user agent, etc.)
        
        Returns:
            FileMetadata: The created file metadata record
        """
        db = SessionLocal()
        try:
            # Get file information
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 0
            file_extension = file_path_obj.suffix.lower()
            
            # Determine MIME type based on extension
            mime_types = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.txt': 'text/plain',
                '.rtf': 'application/rtf'
            }
            file_type = mime_types.get(file_extension, 'application/octet-stream')
            
            # Create file metadata record
            file_metadata = FileMetadata(
                file_path=str(file_path),
                original_filename=original_filename,
                file_size_bytes=file_size,
                file_type=file_type,
                file_extension=file_extension,
                user_id=user.id if user else None,
                user_email=user_email or (user.email if user else None),
                upload_purpose=upload_purpose,
                processing_session_id=processing_session_id,
                upload_ip=request_info.get('ip') if request_info else None,
                user_agent=request_info.get('user_agent') if request_info else None
            )
            
            db.add(file_metadata)
            db.commit()
            db.refresh(file_metadata)
            
            return file_metadata
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to track file upload: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def get_user_files(user: User, include_expired: bool = True) -> list[FileMetadata]:
        """Get all files uploaded by a user"""
        db = SessionLocal()
        try:
            query = db.query(FileMetadata).filter(FileMetadata.user_id == user.id)
            
            if not include_expired:
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                query = query.filter(FileMetadata.created_at >= cutoff_time)
            
            return query.order_by(FileMetadata.created_at.desc()).all()
            
        finally:
            db.close()
    
    @staticmethod
    def cleanup_user_files(user: User) -> Dict[str, Any]:
        """Clean up expired files for a specific user"""
        db = SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # Get expired files
            expired_files = db.query(FileMetadata).filter(
                FileMetadata.user_id == user.id,
                FileMetadata.created_at < cutoff_time,
                FileMetadata.is_deleted == False
            ).all()
            
            deleted_count = 0
            space_freed = 0
            errors = []
            
            for file_record in expired_files:
                try:
                    # Delete physical file
                    file_path = Path(file_record.file_path)
                    if file_path.exists():
                        space_freed += file_path.stat().st_size
                        file_path.unlink()
                    
                    # Mark as deleted in database
                    file_record.is_deleted = True
                    file_record.deleted_at = datetime.utcnow()
                    deleted_count += 1
                    
                except Exception as e:
                    errors.append(f"Failed to delete {file_record.original_filename}: {str(e)}")
            
            db.commit()
            
            return {
                "deleted_count": deleted_count,
                "space_freed_bytes": space_freed,
                "errors": errors
            }
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to cleanup user files: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def get_file_info(file_id: str, user: Optional[User] = None) -> Optional[FileMetadata]:
        """Get information about a specific file"""
        db = SessionLocal()
        try:
            query = db.query(FileMetadata).filter(FileMetadata.id == file_id)
            
            # If user is provided, ensure they own the file
            if user:
                query = query.filter(FileMetadata.user_id == user.id)
            
            return query.first()
            
        finally:
            db.close()
    
    @staticmethod
    def delete_file(file_id: str, user: User) -> bool:
        """Delete a specific file (user can only delete their own files)"""
        db = SessionLocal()
        try:
            file_record = db.query(FileMetadata).filter(
                FileMetadata.id == file_id,
                FileMetadata.user_id == user.id,
                FileMetadata.is_deleted == False
            ).first()
            
            if not file_record:
                return False
            
            # Delete physical file
            file_path = Path(file_record.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Mark as deleted
            file_record.is_deleted = True
            file_record.deleted_at = datetime.utcnow()
            
            db.commit()
            return True
            
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

# Global instance
file_tracker = FileTracker()

# Convenience functions
def track_upload(file_path: str, filename: str, user: Optional[User] = None, **kwargs) -> FileMetadata:
    """Convenience function to track file upload"""
    return file_tracker.track_file_upload(file_path, filename, user, **kwargs)

def get_user_files(user: User, include_expired: bool = True) -> list[FileMetadata]:
    """Convenience function to get user files"""
    return file_tracker.get_user_files(user, include_expired)

def cleanup_user_files(user: User) -> Dict[str, Any]:
    """Convenience function to cleanup user files"""
    return file_tracker.cleanup_user_files(user)
