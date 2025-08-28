"""
QA Service for handling question-answering operations.
Provides business logic for query processing and result generation.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.config import get_settings
from app.models import QAResult, Citation
from app.exceptions import QueryProcessingError, OpenAIError, ValidationError
from app.utils import (
    sanitize_query, 
    calculate_confidence_score, 
    format_citation,
    log_error
)

# Import QA system components
from qa_system import QASystem

logger = logging.getLogger(__name__)


class QAService:
    """Service class for handling QA operations."""
    
    def __init__(self):
        """Initialize the QA service."""
        self.settings = get_settings()
        self.qa_system = None
        self._initialize_qa_system()
    
    def _initialize_qa_system(self) -> None:
        """Initialize the QA system."""
        try:
            self.qa_system = QASystem()
            logger.info("QA system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize QA system: {e}")
            raise QueryProcessingError(f"Failed to initialize QA system: {str(e)}")
    
    def process_query(
        self, 
        query: str, 
        year: Optional[int] = None, 
        search_all_years: bool = False
    ) -> Dict[str, Any]:
        """
        Process a query and return results.
        
        Args:
            query: The question to ask
            year: Specific year to search (if not searching all years)
            search_all_years: Whether to search across all years
            
        Returns:
            Dictionary containing query results
            
        Raises:
            QueryProcessingError: If query processing fails
            ValidationError: If input validation fails
        """
        start_time = time.time()
        
        try:
            # Validate and sanitize input
            if not query or not query.strip():
                raise ValidationError("Query cannot be empty")
            
            sanitized_query = sanitize_query(query)
            if len(sanitized_query) < 3:
                raise ValidationError("Query must be at least 3 characters long")
            
            logger.info(f"Processing query: {sanitized_query[:100]}...")
            
            if search_all_years:
                results = self._process_all_years_query(sanitized_query)
            else:
                if year is None:
                    raise ValidationError("Year is required when not searching all years")
                results = self._process_single_year_query(sanitized_query, year)
            
            processing_time = time.time() - start_time
            results['processing_time'] = processing_time
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return results
            
        except Exception as e:
            processing_time = time.time() - start_time
            log_error(e, {
                'query': query,
                'year': year,
                'search_all_years': search_all_years,
                'processing_time': processing_time
            })
            
            if isinstance(e, (ValidationError, QueryProcessingError)):
                raise
            
            raise QueryProcessingError(f"Failed to process query: {str(e)}")
    
    def _process_single_year_query(self, query: str, year: int) -> Dict[str, Any]:
        """
        Process a query for a specific year.
        
        Args:
            query: The question to ask
            year: Year to search
            
        Returns:
            Dictionary containing single year results
        """
        try:
            result = self.qa_system.ask_question(query, year)
            
            # Convert to structured format
            citations = []
            for citation_text in result.citations:
                citation = Citation(
                    text=citation_text,
                    source=f"apple_annual_report_{year}.pdf"
                )
                citations.append(citation)
            
            qa_result = QAResult(
                answer=result.answer,
                citations=citations,
                confidence=result.confidence,
                year=result.year,
                query=query
            )
            
            return {
                "query": query,
                "search_mode": "single_year",
                "year": year,
                "result": qa_result.dict()
            }
            
        except Exception as e:
            logger.error(f"Error processing single year query: {e}")
            raise QueryProcessingError(f"Failed to process query for year {year}: {str(e)}")
    
    def _process_all_years_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query across all available years.
        
        Args:
            query: The question to ask
            
        Returns:
            Dictionary containing results for all years
        """
        try:
            results = self.qa_system.ask_question_all_years(query)
            
            formatted_results = {}
            for year, result in results.items():
                citations = []
                for citation_text in result.citations:
                    citation = Citation(
                        text=citation_text,
                        source=f"apple_annual_report_{year}.pdf"
                    )
                    citations.append(citation)
                
                qa_result = QAResult(
                    answer=result.answer,
                    citations=citations,
                    confidence=result.confidence,
                    year=result.year,
                    query=query
                )
                
                formatted_results[str(year)] = qa_result.dict()
            
            return {
                "query": query,
                "search_mode": "all_years",
                "results": formatted_results
            }
            
        except Exception as e:
            logger.error(f"Error processing all years query: {e}")
            raise QueryProcessingError(f"Failed to process query across all years: {str(e)}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dictionary containing system statistics
        """
        try:
            stats = self.qa_system.get_summary_stats()
            
            # Add additional metadata
            stats['last_updated'] = datetime.utcnow().isoformat() + "Z"
            stats['service_status'] = 'healthy'
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            raise QueryProcessingError(f"Failed to get system statistics: {str(e)}")
    
    def initialize_data(self, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Initialize or reprocess the data.
        
        Args:
            force_reprocess: Whether to force reprocessing of existing data
            
        Returns:
            Dictionary containing initialization results
        """
        try:
            logger.info(f"Initializing data (force_reprocess: {force_reprocess})")
            
            self.qa_system.initialize_data(force_reprocess=force_reprocess)
            
            # Get updated stats
            stats = self.get_system_stats()
            
            logger.info("Data initialization completed successfully")
            
            return {
                "success": True,
                "message": "Data initialization complete",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error initializing data: {e}")
            raise QueryProcessingError(f"Failed to initialize data: {str(e)}")
    
    def get_example_queries(self) -> List[str]:
        """
        Get example queries for the frontend.
        
        Returns:
            List of example queries
        """
        return [
            "What was Apple's total revenue in 2023?",
            "How many employees did Apple have?",
            "What were Apple's main product categories?",
            "What was Apple's net income?",
            "What were Apple's research and development expenses?",
            "What was Apple's operating margin?",
            "What were Apple's geographic sales breakdown?",
            "What were Apple's key strategic initiatives?",
            "What was Apple's cash flow from operations?",
            "What were Apple's capital expenditures?"
        ]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the QA service.
        
        Returns:
            Dictionary containing health status
        """
        try:
            # Check if QA system is initialized
            if self.qa_system is None:
                return {
                    "status": "unhealthy",
                    "service": "qa-system",
                    "version": self.settings.api_version,
                    "error": "QA system not initialized"
                }
            
            # Check if we can get stats (basic functionality test)
            stats = self.get_system_stats()
            
            return {
                "status": "healthy",
                "service": "qa-system",
                "version": self.settings.api_version,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "qa-system",
                "version": self.settings.api_version,
                "error": str(e)
            }


# Global QA service instance
qa_service = QAService()


def get_qa_service() -> QAService:
    """Get the global QA service instance."""
    return qa_service
