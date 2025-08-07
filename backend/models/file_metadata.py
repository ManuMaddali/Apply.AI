#!/usr/bin/env python3
"""
File Metadata Model
Tracks uploaded files for automatic cleanup after 24 hours
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.user import Base

class FileMetadata(Base):
    """Model to track uploaded files for privacy and cleanup purposes"""
    
    __tablename__ = "file_metadata"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File information
    file_path = Column(String(500), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False, default=0)
    file_type = Column(String(100), nullable=True)  # MIME type
    file_extension = Column(String(10), nullable=True)
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)  # For anonymous users
    
    # File purpose and context
    upload_purpose = Column(String(100), nullable=False, default="resume")  # resume, job_description, etc.
    processing_session_id = Column(String(100), nullable=True, index=True)  # Link to batch processing
    
    # Privacy and cleanup
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)  # Auto-calculated as created_at + 24 hours
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Metadata
    upload_ip = Column(String(45), nullable=True)  # IPv4/IPv6 address
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="uploaded_files")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Auto-calculate expiration time (24 hours from creation)
        if not self.expires_at and self.created_at:
            from datetime import timedelta
            self.expires_at = self.created_at + timedelta(hours=24)
        elif not self.expires_at:
            from datetime import timedelta
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def is_expired(self) -> bool:
        """Check if the file has expired and should be deleted"""
        return datetime.utcnow() > self.expires_at
    
    def time_until_deletion(self) -> str:
        """Get human-readable time until file deletion"""
        if self.is_expired():
            return "Expired"
        
        time_diff = self.expires_at - datetime.utcnow()
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "file_type": self.file_type,
            "upload_purpose": self.upload_purpose,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "time_until_deletion": self.time_until_deletion(),
            "is_expired": self.is_expired(),
            "is_deleted": self.is_deleted
        }
    
    def __repr__(self):
        return f"<FileMetadata(id={self.id}, filename={self.original_filename}, expires_at={self.expires_at})>"
