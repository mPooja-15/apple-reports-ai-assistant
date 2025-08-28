"""
Main FastAPI application for the Apple Annual Reports QA System.
Provides RESTful API endpoints with comprehensive error handling and logging.
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.config import get_settings
from app.models import (
    QueryRequest, 
    QueryResponse, 
    SystemStats, 
    HealthResponse, 
    ErrorResponse,
    FileUploadResponse
)
from app.exceptions import (
    QASystemException, 
    ValidationError, 
    QueryProcessingError, 
    FileUploadError
)
from app.services.qa_service import get_qa_service
from app.services.file_service import get_file_service
from app.utils import (
    setup_logging, 
    log_api_request, 
    log_error, 
    get_available_years,
    validate_year
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Apple Annual Reports QA System API")
    logger.info(f"Environment: {settings.api_version}")
    
    try:
        # Initialize services
        qa_service = get_qa_service()
        file_service = get_file_service()
        
        # Perform health check
        health_status = qa_service.health_check()
        if health_status["status"] == "healthy":
            logger.info("All services initialized successfully")
        else:
            logger.warning(f"Service health check failed: {health_status.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Apple Annual Reports QA System API")


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url=settings.api_docs_url,
    redoc_url=settings.api_redoc_url,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log API request
    log_api_request(
        method=request.method,
        endpoint=str(request.url.path),
        status_code=response.status_code,
        duration=process_time
    )
    
    return response


# Dependency injection
def get_qa_service_dependency():
    """Dependency for QA service."""
    return get_qa_service()


def get_file_service_dependency():
    """Dependency for file service."""
    return get_file_service()


# Error handlers
@app.exception_handler(QASystemException)
async def qa_system_exception_handler(request: Request, exc: QASystemException):
    """Handle custom QA system exceptions."""
    error_response = ErrorResponse(
        error=exc.message,
        error_code=exc.error_code
    )
    
    log_error(exc, {
        'request_path': str(request.url.path),
        'request_method': request.method,
        'error_code': exc.error_code
    })
    
    return JSONResponse(
        status_code=400,
        content=error_response.dict()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    error_response = ErrorResponse(
        error=str(exc),
        error_code="VALIDATION_ERROR"
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    error_response = ErrorResponse(
        error="Endpoint not found",
        error_code="NOT_FOUND"
    )
    
    return JSONResponse(
        status_code=404,
        content=error_response.dict()
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle internal server errors."""
    error_response = ErrorResponse(
        error="Internal server error",
        error_code="INTERNAL_ERROR"
    )
    
    log_error(exc, {
        'request_path': str(request.url.path),
        'request_method': request.method
    })
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


# Health check endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Apple Annual Reports QA System API",
        "status": "running",
        "version": settings.api_version
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        qa_service = get_qa_service()
        health_status = qa_service.health_check()
        
        return HealthResponse(
            status=health_status["status"],
            service=health_status["service"],
            version=health_status["version"],
            timestamp=time.time()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            service="qa-system",
            version=settings.api_version,
            timestamp=time.time()
        )


# API endpoints
@app.get("/api/stats", response_model=SystemStats)
async def get_stats():
    """Get system statistics."""
    try:
        qa_service = get_qa_service()
        stats = qa_service.get_system_stats()
        return SystemStats(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/api/years")
async def get_years():
    """Get list of available years."""
    try:
        years = get_available_years()
        return {"years": years}
    except Exception as e:
        logger.error(f"Error getting years: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting years: {str(e)}")


@app.post("/api/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    qa_service=Depends(get_qa_service_dependency)
):
    """Query the QA system."""
    try:
        results = qa_service.process_query(
            query=request.query,
            year=request.year,
            search_all_years=request.search_all_years
        )
        
        return QueryResponse(
            success=True,
            data=results,
            error=None
        )
        
    except ValidationError as e:
        return QueryResponse(
            success=False,
            data=None,
            error=str(e)
        )
    except QueryProcessingError as e:
        logger.error(f"Query processing error: {e}")
        return QueryResponse(
            success=False,
            data=None,
            error=str(e),
            timestamp=time.time()
        )
    except Exception as e:
        logger.error(f"Unexpected error in query: {e}")
        return QueryResponse(
            success=False,
            data=None,
            error="An unexpected error occurred",
            timestamp=time.time()
        )


@app.post("/api/init-data")
async def initialize_data(
    force_reprocess: bool = False,
    qa_service=Depends(get_qa_service_dependency)
):
    """Initialize or reprocess the data."""
    try:
        result = qa_service.initialize_data(force_reprocess=force_reprocess)
        return result
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error initializing data: {str(e)}")


@app.post("/api/upload-pdf", response_model=FileUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    file_service=Depends(get_file_service_dependency)
):
    """Upload a PDF file."""
    try:
        # Read file content
        content = await file.read()
        
        # Upload file
        result = file_service.upload_file(content, file.filename)
        return result
        
    except FileUploadError as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in file upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


@app.get("/api/example-queries")
async def get_example_queries(
    qa_service=Depends(get_qa_service_dependency)
):
    """Get example queries for the frontend."""
    try:
        examples = qa_service.get_example_queries()
        return {"examples": examples}
    except Exception as e:
        logger.error(f"Error getting example queries: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting example queries: {str(e)}")


@app.get("/api/files")
async def list_files(
    file_service=Depends(get_file_service_dependency)
):
    """List uploaded files."""
    try:
        files = file_service.list_uploaded_files()
        return files
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@app.delete("/api/files/{filename}")
async def delete_file(
    filename: str,
    file_service=Depends(get_file_service_dependency)
):
    """Delete an uploaded file."""
    try:
        result = file_service.delete_file(filename)
        return result
    except FileUploadError as e:
        logger.error(f"File deletion error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in file deletion: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")


@app.post("/api/files/cleanup")
async def cleanup_files(
    file_service=Depends(get_file_service_dependency)
):
    """Clean up orphaned files."""
    try:
        result = file_service.cleanup_orphaned_files()
        return result
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")
        raise HTTPException(status_code=500, detail=f"Error cleaning up files: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level
    )
