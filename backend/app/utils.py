"""
Utility functions for the Apple Annual Reports QA System.
Provides helper functions for common operations with proper error handling.
"""

import os
import re
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import hashlib
from app.exceptions import ValidationError, FileUploadError

# Configure logging
logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
    
    return text


def extract_year_from_filename(filename: str) -> Optional[int]:
    """
    Extract year from filename using regex patterns.
    
    Args:
        filename: Name of the file
        
    Returns:
        Extracted year or None if not found
    """
    if not filename:
        return None
    
    # Common patterns for year extraction
    patterns = [
        r'(\d{4})',  # Basic 4-digit year
        r'(\d{2})',  # 2-digit year (assume 20xx)
        r'fiscal[_\s]*(\d{4})',  # Fiscal year
        r'annual[_\s]*(\d{4})',  # Annual year
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            year = int(match.group(1))
            # Handle 2-digit years
            if year < 100:
                year += 2000
            # Validate year range
            if 2000 <= year <= 2030:
                return year
    
    return None


def get_available_years(data_dir: str = "data") -> List[int]:
    """
    Get list of available years from data directory.
    
    Args:
        data_dir: Directory containing PDF and text files
        
    Returns:
        List of available years
    """
    try:
        if not os.path.exists(data_dir):
            return []
        
        years = set()
        for filename in os.listdir(data_dir):
            if filename.lower().endswith(('.pdf', '.txt')):
                year = extract_year_from_filename(filename)
                if year:
                    years.add(year)
        
        return sorted(list(years))
    except Exception as e:
        logger.error(f"Error getting available years: {e}")
        return []


def validate_year(year: int, available_years: List[int]) -> bool:
    """
    Validate if a year is available.
    
    Args:
        year: Year to validate
        available_years: List of available years
        
    Returns:
        True if year is valid and available
    """
    if not isinstance(year, int):
        return False
    
    if year < 2000 or year > 2030:
        return False
    
    return year in available_years


def get_pdf_paths(data_dir: str = "data") -> Dict[int, str]:
    """
    Get mapping of years to file paths.
    
    Args:
        data_dir: Directory containing PDF and text files
        
    Returns:
        Dictionary mapping years to file paths
    """
    try:
        if not os.path.exists(data_dir):
            return {}
        
        year_to_path = {}
        for filename in os.listdir(data_dir):
            if filename.lower().endswith(('.pdf', '.txt')):
                year = extract_year_from_filename(filename)
                if year:
                    file_path = os.path.join(data_dir, filename)
                    year_to_path[year] = file_path
        
        return year_to_path
    except Exception as e:
        logger.error(f"Error getting file paths: {e}")
        return {}


def load_text_file(file_path: str) -> str:
    """
    Load content from a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Content of the text file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading text file {file_path}: {e}")
        return ""


def format_citation(text: str, page: Optional[int] = None, source: str = "") -> str:
    """
    Format citation text with page number and source.
    
    Args:
        text: Citation text
        page: Page number (optional)
        source: Source document name
        
    Returns:
        Formatted citation string
    """
    citation = f'"{text}"'
    
    if page:
        citation += f" (Page {page})"
    
    if source:
        citation += f" - {source}"
    
    return citation


def calculate_confidence_score(num_chunks: int, similarity_scores: List[float]) -> float:
    """
    Calculate confidence score based on number of chunks and similarity scores.
    
    Args:
        num_chunks: Number of relevant chunks found
        similarity_scores: List of similarity scores
        
    Returns:
        Confidence score between 0 and 1
    """
    if not similarity_scores:
        return 0.0
    
    # Base confidence on average similarity
    avg_similarity = sum(similarity_scores) / len(similarity_scores)
    
    # Adjust based on number of chunks (more chunks = higher confidence)
    chunk_factor = min(num_chunks / 5.0, 1.0)  # Normalize to 0-1
    
    # Weighted combination
    confidence = (avg_similarity * 0.7) + (chunk_factor * 0.3)
    
    return min(max(confidence, 0.0), 1.0)


def validate_file_upload(file_path: str, max_size: int, allowed_types: List[str]) -> None:
    """
    Validate uploaded file.
    
    Args:
        file_path: Path to the uploaded file
        max_size: Maximum file size in bytes
        allowed_types: List of allowed file extensions
        
    Raises:
        FileUploadError: If validation fails
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileUploadError(f"File not found: {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            raise FileUploadError(f"File too large: {file_size} bytes (max: {max_size})")
        
        # Check file type
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in allowed_types:
            raise FileUploadError(f"File type not allowed: {file_ext}")
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            raise FileUploadError(f"File not readable: {file_path}")
            
    except Exception as e:
        if isinstance(e, FileUploadError):
            raise
        raise FileUploadError(f"File validation error: {str(e)}")


def create_safe_filename(original_filename: str) -> str:
    """
    Create a safe filename by removing special characters.
    
    Args:
        original_filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[^\w\-_\.]', '_', original_filename)
    
    # Ensure it doesn't start with a dot
    if safe_name.startswith('.'):
        safe_name = 'file_' + safe_name
    
    return safe_name


def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash string
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {e}")
        return ""


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Directory path to ensure exists
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        raise


def sanitize_query(query: str) -> str:
    """
    Sanitize user query for security.
    
    Args:
        query: Raw user query
        
    Returns:
        Sanitized query
    """
    if not query:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', query)
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized.strip()


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format timestamp for API responses.
    
    Args:
        timestamp: Datetime object (uses current time if None)
        
    Returns:
        ISO formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    return timestamp.isoformat() + "Z"


def log_api_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """
    Log API request details.
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration: Request duration in seconds
    """
    logger.info(
        f"API Request: {method} {endpoint} - Status: {status_code} - Duration: {duration:.3f}s"
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log error with context information.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        error_msg += f" - Context: {context}"
    
    logger.error(error_msg, exc_info=True)
