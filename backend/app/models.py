"""
Pydantic models for request/response validation and data structures.
Defines the API contract and data validation rules.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for querying the QA system."""
    
    query: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    year: Optional[int] = Field(None, ge=2000, le=2030, description="Specific year to search")
    search_all_years: bool = Field(False, description="Whether to search across all years")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate query is not empty and contains meaningful content."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        if len(v.strip()) < 3:
            raise ValueError("Query must be at least 3 characters long")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What was Apple's total revenue in 2023?",
                "year": 2023,
                "search_all_years": False
            }
        }


class Citation(BaseModel):
    """Model for citation information."""
    
    text: str = Field(..., description="The cited text snippet")
    page: Optional[int] = Field(None, description="Page number if available")
    source: str = Field(..., description="Source document name")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Net sales for fiscal 2023 were $394.33 billion, a decrease of 2.8% from fiscal 2022.",
                "page": 23,
                "source": "apple_annual_report_2023.pdf"
            }
        }


class QAResult(BaseModel):
    """Model for QA result data."""
    
    answer: str = Field(..., description="The generated answer")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    year: int = Field(..., ge=2000, le=2030, description="Year of the data")
    query: str = Field(..., description="Original query")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "Apple's total revenue in 2023 was $394.33 billion, representing a 2.8% decrease from the previous year.",
                "citations": [
                    {
                        "text": "Net sales for fiscal 2023 were $394.33 billion, a decrease of 2.8% from fiscal 2022.",
                        "page": 23,
                        "source": "apple_annual_report_2023.pdf"
                    }
                ],
                "confidence": 0.85,
                "year": 2023,
                "query": "What was Apple's total revenue in 2023?",
                "processing_time": 2.34
            }
        }


class QueryResponse(BaseModel):
    """Response model for query results."""
    
    success: bool = Field(..., description="Whether the query was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Query results data")
    error: Optional[str] = Field(None, description="Error message if query failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "query": "What was Apple's total revenue in 2023?",
                    "search_mode": "single_year",
                    "year": 2023,
                    "result": {
                        "answer": "Apple's total revenue in 2023 was $394.33 billion...",
                        "citations": [...],
                        "confidence": 0.85,
                        "year": 2023,
                        "query": "What was Apple's total revenue in 2023?"
                    }
                },
                "error": None,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class SystemStats(BaseModel):
    """Model for system statistics."""
    
    available_years: List[int] = Field(..., description="List of available years")
    total_years: int = Field(..., ge=0, description="Total number of available years")
    processed_years: List[int] = Field(..., description="List of processed years")
    total_documents: int = Field(..., ge=0, description="Total number of documents")
    total_chunks: int = Field(..., ge=0, description="Total number of text chunks")
    last_updated: Optional[datetime] = Field(None, description="Last data update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "available_years": [2020, 2021, 2022, 2023, 2024],
                "total_years": 5,
                "processed_years": [2020, 2021, 2022, 2023, 2024],
                "total_documents": 5,
                "total_chunks": 1250,
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }


class FileUploadResponse(BaseModel):
    """Response model for file upload operations."""
    
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Upload status message")
    file_path: Optional[str] = Field(None, description="Path to the uploaded file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "File apple_annual_report_2023.pdf uploaded successfully",
                "file_path": "data/apple_annual_report_2023.pdf",
                "file_size": 2048576,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "qa-system",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "uptime": 3600.5
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for categorization")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid query format",
                "error_code": "INVALID_QUERY",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
