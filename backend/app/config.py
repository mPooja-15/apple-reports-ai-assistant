"""
Configuration management for the Apple Annual Reports QA System.
Handles environment variables, settings, and configuration validation.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # API Configuration
    api_title: str = "Apple Annual Reports QA System API"
    api_description: str = "A retrieval-augmented question-answering system for Apple's annual reports"
    api_version: str = "1.0.0"
    api_docs_url: str = "/docs"
    api_redoc_url: str = "/redoc"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: str = "info"
    
    # CORS Configuration
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_llm_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 500
    
    # Data Processing Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunks_per_query: int = 5
    
    # File Upload Configuration
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf"]
    upload_directory: str = "data"
    
    # Vector Database Configuration
    vector_db_directory: str = "vector_db"
    similarity_threshold: float = 0.7
    
    @validator("openai_api_key")
    def validate_openai_api_key(cls, v):
        """Validate OpenAI API key is provided."""
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        return v
    
    @validator("cors_origins")
    def validate_cors_origins(cls, v):
        """Validate CORS origins are provided."""
        if not v:
            raise ValueError("At least one CORS origin is required")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
