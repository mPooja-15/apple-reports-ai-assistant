"""
File Service for handling file upload operations.
Provides business logic for file validation, storage, and management.
"""

import os
import shutil
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from app.config import get_settings
from app.models import FileUploadResponse
from app.exceptions import FileUploadError, ValidationError
from app.utils import (
    validate_file_upload,
    create_safe_filename,
    get_file_hash,
    ensure_directory_exists,
    log_error
)

logger = logging.getLogger(__name__)


class FileService:
    """Service class for handling file operations."""
    
    def __init__(self):
        """Initialize the file service."""
        self.settings = get_settings()
        self.upload_directory = self.settings.upload_directory
        self.max_file_size = self.settings.max_file_size
        self.allowed_types = self.settings.allowed_file_types
        
        # Ensure upload directory exists
        ensure_directory_exists(self.upload_directory)
    
    def upload_file(self, file_content: bytes, filename: str) -> FileUploadResponse:
        """
        Upload and validate a file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            FileUploadResponse with upload details
            
        Raises:
            FileUploadError: If upload fails
            ValidationError: If file validation fails
        """
        try:
            # Create safe filename
            safe_filename = create_safe_filename(filename)
            file_path = os.path.join(self.upload_directory, safe_filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                # Generate unique filename
                base_name, ext = os.path.splitext(safe_filename)
                counter = 1
                while os.path.exists(file_path):
                    safe_filename = f"{base_name}_{counter}{ext}"
                    file_path = os.path.join(self.upload_directory, safe_filename)
                    counter += 1
            
            # Write file content
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Validate uploaded file
            validate_file_upload(file_path, self.max_file_size, self.allowed_types)
            
            # Get file metadata
            file_size = os.path.getsize(file_path)
            file_hash = get_file_hash(file_path)
            
            logger.info(f"File uploaded successfully: {safe_filename} ({file_size} bytes)")
            
            return FileUploadResponse(
                success=True,
                message=f"File {safe_filename} uploaded successfully",
                file_path=file_path,
                file_size=file_size,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            # Clean up file if it was created
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up failed upload: {file_path}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up file {file_path}: {cleanup_error}")
            
            log_error(e, {
                'filename': filename,
                'file_size': len(file_content) if file_content else 0
            })
            
            if isinstance(e, (FileUploadError, ValidationError)):
                raise
            
            raise FileUploadError(f"Failed to upload file: {str(e)}")
    
    def validate_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate a file without saving it.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Check file size
            file_size = len(file_content)
            if file_size > self.max_file_size:
                raise ValidationError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            
            # Check file type
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in self.allowed_types:
                raise ValidationError(f"File type not allowed: {file_ext}")
            
            # Check if file is empty
            if file_size == 0:
                raise ValidationError("File is empty")
            
            return {
                "valid": True,
                "file_size": file_size,
                "file_type": file_ext,
                "filename": filename
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "file_size": len(file_content) if file_content else 0,
                "filename": filename
            }
    
    def list_uploaded_files(self) -> Dict[str, Any]:
        """
        List all uploaded files with metadata.
        
        Returns:
            Dictionary containing file list and metadata
        """
        try:
            if not os.path.exists(self.upload_directory):
                return {
                    "files": [],
                    "total_count": 0,
                    "total_size": 0
                }
            
            files = []
            total_size = 0
            
            for filename in os.listdir(self.upload_directory):
                file_path = os.path.join(self.upload_directory, filename)
                
                if os.path.isfile(file_path):
                    file_stats = os.stat(file_path)
                    file_info = {
                        "filename": filename,
                        "size": file_stats.st_size,
                        "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "file_hash": get_file_hash(file_path)
                    }
                    files.append(file_info)
                    total_size += file_stats.st_size
            
            return {
                "files": files,
                "total_count": len(files),
                "total_size": total_size
            }
            
        except Exception as e:
            logger.error(f"Error listing uploaded files: {e}")
            raise FileUploadError(f"Failed to list uploaded files: {str(e)}")
    
    def delete_file(self, filename: str) -> Dict[str, Any]:
        """
        Delete an uploaded file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Dictionary with deletion results
        """
        try:
            # Create safe filename
            safe_filename = create_safe_filename(filename)
            file_path = os.path.join(self.upload_directory, safe_filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileUploadError(f"File not found: {filename}")
            
            # Get file size before deletion
            file_size = os.path.getsize(file_path)
            
            # Delete file
            os.remove(file_path)
            
            logger.info(f"File deleted successfully: {filename}")
            
            return {
                "success": True,
                "message": f"File {filename} deleted successfully",
                "deleted_size": file_size
            }
            
        except Exception as e:
            log_error(e, {'filename': filename})
            
            if isinstance(e, FileUploadError):
                raise
            
            raise FileUploadError(f"Failed to delete file: {str(e)}")
    
    def get_upload_directory_info(self) -> Dict[str, Any]:
        """
        Get information about the upload directory.
        
        Returns:
            Dictionary with directory information
        """
        try:
            if not os.path.exists(self.upload_directory):
                return {
                    "exists": False,
                    "path": self.upload_directory,
                    "size": 0,
                    "file_count": 0
                }
            
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.upload_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                "exists": True,
                "path": self.upload_directory,
                "size": total_size,
                "file_count": file_count,
                "max_file_size": self.max_file_size,
                "allowed_types": self.allowed_types
            }
            
        except Exception as e:
            logger.error(f"Error getting upload directory info: {e}")
            raise FileUploadError(f"Failed to get upload directory info: {str(e)}")
    
    def cleanup_orphaned_files(self) -> Dict[str, Any]:
        """
        Clean up orphaned or invalid files.
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            if not os.path.exists(self.upload_directory):
                return {
                    "cleaned_files": [],
                    "cleaned_size": 0,
                    "total_cleaned": 0
                }
            
            cleaned_files = []
            cleaned_size = 0
            total_cleaned = 0
            
            for filename in os.listdir(self.upload_directory):
                file_path = os.path.join(self.upload_directory, filename)
                
                if os.path.isfile(file_path):
                    # Check if file is valid
                    try:
                        validate_file_upload(file_path, self.max_file_size, self.allowed_types)
                    except (FileUploadError, ValidationError):
                        # File is invalid, delete it
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        
                        cleaned_files.append(filename)
                        cleaned_size += file_size
                        total_cleaned += 1
                        
                        logger.info(f"Cleaned up invalid file: {filename}")
            
            return {
                "cleaned_files": cleaned_files,
                "cleaned_size": cleaned_size,
                "total_cleaned": total_cleaned
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up orphaned files: {e}")
            raise FileUploadError(f"Failed to clean up orphaned files: {str(e)}")


# Global file service instance
file_service = FileService()


def get_file_service() -> FileService:
    """Get the global file service instance."""
    return file_service
