#!/usr/bin/env python3
"""
File Cleanup Service - Privacy Feature
Automatically deletes user files after 24 hours for privacy protection
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from config.database import SessionLocal
from models.user import User
from models.file_metadata import FileMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileCleanupService:
    """Service for automatically cleaning up old user files"""
    
    def __init__(self, upload_directory: str = "uploads"):
        self.upload_directory = Path(upload_directory)
        self.cleanup_age_hours = 24
        self.batch_size = 100  # Process files in batches to avoid memory issues
        
    async def cleanup_expired_files(self) -> Dict[str, int]:
        """
        Clean up files older than 24 hours
        Returns statistics about the cleanup operation
        """
        logger.info("🧹 Starting file cleanup process...")
        
        stats = {
            "files_checked": 0,
            "files_deleted": 0,
            "errors": 0,
            "space_freed_mb": 0
        }
        
        db = SessionLocal()
        try:
            # Calculate cutoff time (24 hours ago)
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_age_hours)
            logger.info(f"🕒 Cleaning up files older than: {cutoff_time}")
            
            # Get expired file metadata from database
            expired_files = db.query(FileMetadata).filter(
                FileMetadata.created_at < cutoff_time
            ).limit(self.batch_size).all()
            
            logger.info(f"📁 Found {len(expired_files)} expired files to clean up")
            
            for file_record in expired_files:
                stats["files_checked"] += 1
                
                try:
                    # Delete physical file
                    file_path = Path(file_record.file_path)
                    if file_path.exists():
                        file_size_mb = file_path.stat().st_size / (1024 * 1024)
                        file_path.unlink()
                        stats["space_freed_mb"] += file_size_mb
                        logger.info(f"🗑️  Deleted file: {file_path} ({file_size_mb:.2f} MB)")
                    
                    # Remove database record
                    db.delete(file_record)
                    stats["files_deleted"] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error deleting file {file_record.file_path}: {str(e)}")
                    stats["errors"] += 1
            
            # Commit database changes
            db.commit()
            
            # Also clean up orphaned files (files without database records)
            await self._cleanup_orphaned_files(stats)
            
            logger.info(f"✅ File cleanup completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ File cleanup failed: {str(e)}")
            db.rollback()
            stats["errors"] += 1
            return stats
        finally:
            db.close()
    
    async def _cleanup_orphaned_files(self, stats: Dict[str, int]) -> None:
        """Clean up physical files that don't have database records"""
        try:
            if not self.upload_directory.exists():
                return
            
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_age_hours)
            
            # Check all files in upload directory
            for file_path in self.upload_directory.rglob("*"):
                if file_path.is_file():
                    try:
                        # Check file age
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        if file_mtime < cutoff_time:
                            # Check if file has database record
                            db = SessionLocal()
                            try:
                                file_record = db.query(FileMetadata).filter(
                                    FileMetadata.file_path == str(file_path)
                                ).first()
                                
                                if not file_record:
                                    # Orphaned file - delete it
                                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                                    file_path.unlink()
                                    stats["files_deleted"] += 1
                                    stats["space_freed_mb"] += file_size_mb
                                    logger.info(f"🗑️  Deleted orphaned file: {file_path} ({file_size_mb:.2f} MB)")
                                    
                            finally:
                                db.close()
                                
                    except Exception as e:
                        logger.error(f"❌ Error processing file {file_path}: {str(e)}")
                        stats["errors"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Error during orphaned file cleanup: {str(e)}")
            stats["errors"] += 1
    
    async def get_cleanup_stats(self) -> Dict[str, any]:
        """Get statistics about files eligible for cleanup"""
        db = SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_age_hours)
            
            # Count expired files
            expired_count = db.query(FileMetadata).filter(
                FileMetadata.created_at < cutoff_time
            ).count()
            
            # Count total files
            total_count = db.query(FileMetadata).count()
            
            # Calculate total storage used
            total_size = 0
            expired_size = 0
            
            all_files = db.query(FileMetadata).all()
            for file_record in all_files:
                try:
                    file_path = Path(file_record.file_path)
                    if file_path.exists():
                        size = file_path.stat().st_size
                        total_size += size
                        
                        if file_record.created_at < cutoff_time:
                            expired_size += size
                except:
                    pass
            
            return {
                "total_files": total_count,
                "expired_files": expired_count,
                "total_size_mb": total_size / (1024 * 1024),
                "expired_size_mb": expired_size / (1024 * 1024),
                "cleanup_age_hours": self.cleanup_age_hours,
                "next_cleanup_eligible": cutoff_time.isoformat()
            }
            
        finally:
            db.close()
    
    def schedule_cleanup(self, interval_hours: int = 6) -> None:
        """Schedule periodic cleanup (for production use)"""
        async def cleanup_loop():
            while True:
                try:
                    await self.cleanup_expired_files()
                    await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
                except Exception as e:
                    logger.error(f"❌ Scheduled cleanup failed: {str(e)}")
                    await asyncio.sleep(3600)  # Wait 1 hour before retry
        
        # Start the cleanup loop
        asyncio.create_task(cleanup_loop())
        logger.info(f"📅 Scheduled file cleanup every {interval_hours} hours")

# Global service instance
file_cleanup_service = FileCleanupService()

async def run_file_cleanup():
    """Convenience function to run file cleanup"""
    return await file_cleanup_service.cleanup_expired_files()

if __name__ == "__main__":
    # For testing - run cleanup once
    asyncio.run(run_file_cleanup())
