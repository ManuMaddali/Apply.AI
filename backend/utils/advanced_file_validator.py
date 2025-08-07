#!/usr/bin/env python3
"""
Advanced File Validation with python-magic
Provides comprehensive file type detection and security validation
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

# Try to import python-magic, fall back to basic validation if not available
try:
    import magic
    MAGIC_AVAILABLE = True
    logger.info("✅ python-magic library available - using advanced file validation")
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("⚠️ python-magic not available - falling back to basic file validation")

@dataclass
class FileValidationResult:
    """Result of file validation"""
    is_valid: bool
    detected_type: str
    mime_type: str
    file_extension: str
    file_size: int
    security_score: int  # 0-100, higher is safer
    warnings: List[str]
    errors: List[str]

class AdvancedFileValidator:
    """Advanced file validation using python-magic and security checks"""
    
    # Supported file types for resume processing
    SUPPORTED_MIME_TYPES = {
        'application/pdf': {
            'extensions': ['.pdf'],
            'description': 'PDF Document',
            'max_size_mb': 10,
            'security_level': 'high'
        },
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {
            'extensions': ['.docx'],
            'description': 'Microsoft Word Document (DOCX)',
            'max_size_mb': 10,
            'security_level': 'medium'
        },
        'application/msword': {
            'extensions': ['.doc'],
            'description': 'Microsoft Word Document (DOC)',
            'max_size_mb': 10,
            'security_level': 'medium'
        },
        'text/plain': {
            'extensions': ['.txt'],
            'description': 'Plain Text',
            'max_size_mb': 5,
            'security_level': 'high'
        },
        'text/rtf': {
            'extensions': ['.rtf'],
            'description': 'Rich Text Format',
            'max_size_mb': 5,
            'security_level': 'medium'
        }
    }
    
    # Dangerous file types to reject
    DANGEROUS_MIME_TYPES = {
        'application/x-executable',
        'application/x-msdos-program',
        'application/x-msdownload',
        'application/x-dosexec',
        'application/vnd.microsoft.portable-executable',
        'application/x-sharedlib',
        'application/x-shellscript',
        'text/x-shellscript',
        'application/javascript',
        'text/javascript',
        'application/x-php',
        'text/x-php'
    }
    
    def __init__(self):
        """Initialize the file validator"""
        self.magic_mime = None
        self.magic_type = None
        
        if MAGIC_AVAILABLE:
            try:
                # Initialize magic for MIME type detection
                self.magic_mime = magic.Magic(mime=True)
                # Initialize magic for file type description
                self.magic_type = magic.Magic()
                logger.info("✅ Advanced file validation initialized with python-magic")
            except Exception as e:
                logger.error(f"❌ Failed to initialize python-magic: {e}")
                self.magic_mime = None
                self.magic_type = None
    
    def validate_file(self, file_path: Union[str, Path], 
                     original_filename: Optional[str] = None,
                     file_content: Optional[bytes] = None) -> FileValidationResult:
        """
        Comprehensive file validation
        
        Args:
            file_path: Path to the file to validate
            original_filename: Original filename (for extension checking)
            file_content: File content bytes (optional, will read from file if not provided)
        
        Returns:
            FileValidationResult with validation details
        """
        file_path = Path(file_path)
        warnings = []
        errors = []
        
        # Get file info
        try:
            file_size = file_path.stat().st_size if file_path.exists() else 0
            file_extension = file_path.suffix.lower()
            
            # Use original filename extension if provided
            if original_filename:
                original_ext = Path(original_filename).suffix.lower()
                if original_ext != file_extension:
                    warnings.append(f"Extension mismatch: file has {file_extension}, original was {original_ext}")
                    file_extension = original_ext
                    
        except Exception as e:
            errors.append(f"Failed to get file info: {str(e)}")
            return FileValidationResult(
                is_valid=False,
                detected_type="unknown",
                mime_type="unknown",
                file_extension="",
                file_size=0,
                security_score=0,
                warnings=warnings,
                errors=errors
            )
        
        # Read file content if not provided
        if file_content is None and file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    # Read first 2MB for magic detection (sufficient for file type detection)
                    file_content = f.read(2 * 1024 * 1024)
            except Exception as e:
                errors.append(f"Failed to read file content: {str(e)}")
                file_content = b""
        
        # Detect file type using python-magic (if available)
        if MAGIC_AVAILABLE and self.magic_mime and file_content:
            try:
                detected_mime = self.magic_mime.from_buffer(file_content) if self.magic_mime else "unknown"
                detected_type = self.magic_type.from_buffer(file_content) if self.magic_type else "unknown"
                logger.info(f"🔍 Detected file type: {detected_mime} ({detected_type})")
            except Exception as e:
                logger.warning(f"⚠️ Magic detection failed: {e}")
                detected_mime, detected_type = self._basic_type_detection(file_extension)
        else:
            # Fall back to basic detection
            detected_mime, detected_type = self._basic_type_detection(file_extension)
        
        # Validate against supported types
        is_supported = detected_mime in self.SUPPORTED_MIME_TYPES
        if not is_supported:
            errors.append(f"Unsupported file type: {detected_mime}")
        
        # Security checks
        security_score = self._calculate_security_score(
            detected_mime, file_extension, file_size, file_content or b""
        )
        
        # Check for dangerous file types
        if detected_mime in self.DANGEROUS_MIME_TYPES:
            errors.append(f"Dangerous file type detected: {detected_mime}")
            security_score = 0
        
        # Size validation
        if is_supported:
            max_size = self.SUPPORTED_MIME_TYPES[detected_mime]['max_size_mb'] * 1024 * 1024
            if file_size > max_size:
                errors.append(f"File too large: {file_size / (1024*1024):.1f}MB > {max_size / (1024*1024)}MB")
        
        # Extension validation
        if is_supported:
            expected_extensions = self.SUPPORTED_MIME_TYPES[detected_mime]['extensions']
            if file_extension not in expected_extensions:
                warnings.append(f"Extension {file_extension} not typical for {detected_mime}")
        
        # Overall validation result
        is_valid = len(errors) == 0 and is_supported and security_score >= 50
        
        return FileValidationResult(
            is_valid=is_valid,
            detected_type=detected_type,
            mime_type=detected_mime,
            file_extension=file_extension,
            file_size=file_size,
            security_score=security_score,
            warnings=warnings,
            errors=errors
        )
    
    def _basic_type_detection(self, file_extension: str) -> Tuple[str, str]:
        """Basic file type detection based on extension"""
        extension_map = {
            '.pdf': ('application/pdf', 'PDF document'),
            '.docx': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'Microsoft Word document'),
            '.doc': ('application/msword', 'Microsoft Word document'),
            '.txt': ('text/plain', 'ASCII text'),
            '.rtf': ('text/rtf', 'Rich Text Format')
        }
        
        return extension_map.get(file_extension, ('application/octet-stream', 'Unknown file type'))
    
    def _calculate_security_score(self, mime_type: str, extension: str, 
                                file_size: int, content: bytes) -> int:
        """Calculate security score (0-100)"""
        score = 100
        
        # Penalize unknown types
        if mime_type not in self.SUPPORTED_MIME_TYPES:
            score -= 50
        
        # Penalize very large files
        if file_size > 20 * 1024 * 1024:  # 20MB
            score -= 30
        elif file_size > 10 * 1024 * 1024:  # 10MB
            score -= 15
        
        # Check for suspicious content patterns
        if content:
            suspicious_patterns = [
                b'<script',
                b'javascript:',
                b'vbscript:',
                b'<?php',
                b'#!/bin/',
                b'MZ\x90\x00',  # PE executable header
                b'\x7fELF',     # ELF executable header
            ]
            
            for pattern in suspicious_patterns:
                if pattern in content[:1024]:  # Check first 1KB
                    score -= 40
                    break
        
        # Bonus for well-known safe types
        if mime_type in ['text/plain', 'application/pdf']:
            score += 10
        
        return max(0, min(100, score))
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict:
        """Get detailed file information"""
        validation_result = self.validate_file(file_path)
        
        return {
            'is_valid': validation_result.is_valid,
            'mime_type': validation_result.mime_type,
            'detected_type': validation_result.detected_type,
            'file_extension': validation_result.file_extension,
            'file_size_bytes': validation_result.file_size,
            'file_size_mb': round(validation_result.file_size / (1024 * 1024), 2),
            'security_score': validation_result.security_score,
            'warnings': validation_result.warnings,
            'errors': validation_result.errors,
            'magic_available': MAGIC_AVAILABLE
        }

# Global validator instance
file_validator = AdvancedFileValidator()

# Convenience functions
def validate_uploaded_file(file_path: str, original_filename: str = None) -> FileValidationResult:
    """Validate an uploaded file"""
    return file_validator.validate_file(file_path, original_filename)

def is_safe_file(file_path: str, original_filename: str = None) -> bool:
    """Quick check if file is safe to process"""
    result = validate_uploaded_file(file_path, original_filename)
    return result.is_valid and result.security_score >= 70

def get_supported_file_types() -> Dict:
    """Get list of supported file types"""
    return AdvancedFileValidator.SUPPORTED_MIME_TYPES
