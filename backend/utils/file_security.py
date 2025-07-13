from fastapi import UploadFile, HTTPException
import hashlib
import os
import tempfile
import shutil
from typing import List, Optional
from datetime import datetime
import mimetypes
import logging

# Try to import python-magic, fall back to mimetypes if not available
try:
    import magic
    MAGIC_AVAILABLE = True
    print("✅ Advanced file validation with python-magic enabled")
except ImportError:
    MAGIC_AVAILABLE = False
    print("⚠️  python-magic not available, using basic file validation")

class FileSecurityManager:
    """Secure file upload and validation manager"""
    
    # Security configurations
    ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.doc'}
    ALLOWED_MIME_TYPES = {
        'text/plain',
        'application/pdf', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_FILE_SIZE = 100  # 100 bytes
    
    # Security patterns to check for
    DANGEROUS_PATTERNS = [
        b'<script',
        b'javascript:',
        b'vbscript:',
        b'onload=',
        b'onerror=',
        b'eval(',
        b'exec(',
        b'system(',
        b'shell_exec',
        b'<?php',
        b'<%',
        b'#!/bin/',
        b'#!/usr/bin/',
        b'cmd.exe',
        b'powershell'
    ]
    
    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """Comprehensive file validation"""
        
        # Check if file object is valid
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        if file.size is None:
            raise HTTPException(status_code=400, detail="Cannot determine file size")
        
        if file.size > FileSecurityManager.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {FileSecurityManager.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        if file.size < FileSecurityManager.MIN_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too small")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in FileSecurityManager.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(FileSecurityManager.ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content for validation
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        # Check MIME type - use python-magic if available, otherwise use mimetypes
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
            except Exception:
                # Fallback to mimetypes if magic fails
                mime_type, _ = mimetypes.guess_type(file.filename)
        else:
            # Use mimetypes as primary method when magic is not available
            mime_type, _ = mimetypes.guess_type(file.filename)
        
        if mime_type not in FileSecurityManager.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file content type: {mime_type}"
            )
        
        # Scan for dangerous patterns
        if not FileSecurityManager._scan_content_patterns(file_content):
            raise HTTPException(
                status_code=400, 
                detail="File contains potentially dangerous content"
            )
        
        return True
    
    @staticmethod
    def _scan_content_patterns(content: bytes) -> bool:
        """Scan file content for dangerous patterns"""
        content_lower = content.lower()
        
        for pattern in FileSecurityManager.DANGEROUS_PATTERNS:
            if pattern in content_lower:
                # Log security event
                FileSecurityManager._log_security_event(
                    "dangerous_pattern_detected",
                    {"pattern": pattern.decode('utf-8', errors='ignore')},
                    "high"
                )
                return False
        
        return True
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate secure filename with timestamp and hash"""
        # Get file extension
        file_ext = os.path.splitext(original_filename)[1].lower()
        
        # Generate hash
        hash_obj = hashlib.sha256()
        hash_obj.update(original_filename.encode('utf-8'))
        hash_obj.update(str(datetime.now()).encode('utf-8'))
        
        # Create secure filename
        secure_name = hash_obj.hexdigest()[:16]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{timestamp}_{secure_name}{file_ext}"
    
    @staticmethod
    def save_file_securely(file: UploadFile, upload_dir: str = "uploads") -> str:
        """Save file securely with validation"""
        
        # Validate file first
        FileSecurityManager.validate_file(file)
        
        # Ensure upload directory exists
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate secure filename
        secure_filename = FileSecurityManager.generate_secure_filename(file.filename)
        file_path = os.path.join(upload_dir, secure_filename)
        
        # Save file with temporary name first
        temp_path = file_path + ".tmp"
        
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Perform additional security checks on saved file
            if FileSecurityManager._additional_file_checks(temp_path):
                # Move from temp to final location
                shutil.move(temp_path, file_path)
                
                # Log successful upload
                FileSecurityManager._log_security_event(
                    "file_uploaded",
                    {
                        "original_filename": file.filename,
                        "secure_filename": secure_filename,
                        "file_size": file.size,
                        "file_path": file_path
                    },
                    "info"
                )
                
                return file_path
            else:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise HTTPException(
                    status_code=400,
                    detail="File failed additional security checks"
                )
                
        except Exception as e:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise HTTPException(
                status_code=500,
                detail=f"Error saving file: {str(e)}"
            )
    
    @staticmethod
    def _additional_file_checks(file_path: str) -> bool:
        """Additional security checks on saved file"""
        try:
            # Check file size again
            file_size = os.path.getsize(file_path)
            if file_size > FileSecurityManager.MAX_FILE_SIZE:
                return False
            
            # Check file permissions
            os.chmod(file_path, 0o644)  # Read-only for group and others
            
            # For PDF files, perform additional checks
            if file_path.lower().endswith('.pdf'):
                return FileSecurityManager._check_pdf_security(file_path)
            
            return True
            
        except Exception as e:
            FileSecurityManager._log_security_event(
                "file_check_error",
                {"file_path": file_path, "error": str(e)},
                "error"
            )
            return False
    
    @staticmethod
    def _check_pdf_security(file_path: str) -> bool:
        """Basic PDF security checks"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Read first 1KB
                
                # Check for PDF header
                if not content.startswith(b'%PDF-'):
                    return False
                
                # Check for suspicious PDF content
                suspicious_pdf_patterns = [
                    b'/JavaScript',
                    b'/JS',
                    b'/OpenAction',
                    b'/Launch',
                    b'/EmbeddedFile'
                ]
                
                for pattern in suspicious_pdf_patterns:
                    if pattern in content:
                        FileSecurityManager._log_security_event(
                            "suspicious_pdf_content",
                            {"file_path": file_path, "pattern": pattern.decode('utf-8')},
                            "warning"
                        )
                        return False
                
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def clean_old_files(upload_dir: str = "uploads", max_age_hours: int = 24):
        """Clean up old uploaded files"""
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                
                # Get file creation time
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                # Check if file is older than max_age_hours
                if (current_time - file_time).total_seconds() > max_age_hours * 3600:
                    os.unlink(file_path)
                    
                    FileSecurityManager._log_security_event(
                        "old_file_cleaned",
                        {"file_path": file_path, "age_hours": (current_time - file_time).total_seconds() / 3600},
                        "info"
                    )
                    
        except Exception as e:
            FileSecurityManager._log_security_event(
                "file_cleanup_error",
                {"error": str(e)},
                "error"
            )
    
    @staticmethod
    def _log_security_event(event_type: str, details: dict, severity: str = "info"):
        """Log security events"""
        import json
        
        security_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        logger = logging.getLogger("file_security")
        getattr(logger, severity.lower())(json.dumps(security_event))
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get secure file information"""
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
                "is_safe": os.path.exists(file_path) and stat.st_size <= FileSecurityManager.MAX_FILE_SIZE
            }
        except Exception:
            return {"error": "Cannot access file information"}

# Utility functions for file operations
def validate_and_save_resume(file: UploadFile) -> str:
    """Convenience function to validate and save resume file"""
    return FileSecurityManager.save_file_securely(file)

def cleanup_temp_files():
    """Cleanup temporary files"""
    FileSecurityManager.clean_old_files()
    
    # Also cleanup temp directory
    temp_dir = tempfile.gettempdir()
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith("tmp") and filename.endswith(".pdf"):
                file_path = os.path.join(temp_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if (datetime.now() - file_time).total_seconds() > 3600:  # 1 hour
                    os.unlink(file_path)
    except Exception:
        pass  # Ignore errors in temp cleanup 