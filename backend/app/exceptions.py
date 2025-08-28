"""
Custom exception classes for the Apple Annual Reports QA System.
Provides structured error handling and meaningful error messages.
"""

from typing import Optional, Dict, Any


class QASystemException(Exception):
    """Base exception for QA system errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(QASystemException):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class DataProcessingError(QASystemException):
    """Raised when there's an error processing data."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATA_PROCESSING_ERROR", details)


class FileUploadError(QASystemException):
    """Raised when there's an error uploading files."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "FILE_UPLOAD_ERROR", details)


class QueryProcessingError(QASystemException):
    """Raised when there's an error processing queries."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "QUERY_PROCESSING_ERROR", details)


class VectorDatabaseError(QASystemException):
    """Raised when there's an error with vector database operations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VECTOR_DB_ERROR", details)


class OpenAIError(QASystemException):
    """Raised when there's an error with OpenAI API calls."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "OPENAI_ERROR", details)


class ValidationError(QASystemException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class ResourceNotFoundError(QASystemException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RESOURCE_NOT_FOUND", details)


class ServiceUnavailableError(QASystemException):
    """Raised when a required service is unavailable."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SERVICE_UNAVAILABLE", details)


# Error message constants
ERROR_MESSAGES = {
    "CONFIGURATION_ERROR": "Configuration error occurred",
    "DATA_PROCESSING_ERROR": "Error processing data",
    "FILE_UPLOAD_ERROR": "Error uploading file",
    "QUERY_PROCESSING_ERROR": "Error processing query",
    "VECTOR_DB_ERROR": "Vector database error",
    "OPENAI_ERROR": "OpenAI API error",
    "VALIDATION_ERROR": "Validation error",
    "RESOURCE_NOT_FOUND": "Resource not found",
    "SERVICE_UNAVAILABLE": "Service unavailable"
}


def get_error_message(error_code: str, default_message: str = "An error occurred") -> str:
    """Get a user-friendly error message for the given error code."""
    return ERROR_MESSAGES.get(error_code, default_message)
