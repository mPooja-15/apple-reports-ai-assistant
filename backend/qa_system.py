"""
Core QA System for Apple Annual Reports.
Handles PDF processing, embeddings, and question answering.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader

from app.config import get_settings
from app.utils import clean_text, extract_year_from_filename, get_pdf_paths

logger = logging.getLogger(__name__)


@dataclass
class QAResult:
    """Result from QA system query."""
    answer: str
    citations: List[str]
    confidence: float
    year: int
    query: str


class QASystem:
    """Main QA system for processing Apple annual reports."""
    
    def __init__(self):
        """Initialize the QA system."""
        self.settings = get_settings()
        self.embeddings = None
        self.llm = None
        self.vector_stores = {}
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )
        self._initialize_models()
        # Load existing vector databases if they exist
        self._load_existing_vector_databases()
    
    def _initialize_models(self):
        """Initialize OpenAI models."""
        try:
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                model=self.settings.openai_embedding_model,
                openai_api_key=self.settings.openai_api_key
            )
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model=self.settings.openai_llm_model,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens,
                openai_api_key=self.settings.openai_api_key
            )
            
            logger.info("OpenAI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI models: {e}")
            raise
    
    def _load_existing_vector_databases(self):
        """Load existing vector databases if they exist."""
        try:
            logger.info("Loading existing vector databases...")
            
            # Check for existing vector databases
            available_years = [2021, 2022, 2023]  # Based on the sample data
            
            for year in available_years:
                vector_db_path = f"{self.settings.vector_db_directory}_{year}"
                
                if os.path.exists(vector_db_path):
                    try:
                        logger.info(f"Loading vector database for year {year}")
                        self.vector_stores[year] = FAISS.load_local(
                            vector_db_path, 
                            self.embeddings,
                            allow_dangerous_deserialization=True
                        )
                        logger.info(f"Successfully loaded vector database for year {year}")
                    except Exception as e:
                        logger.error(f"Failed to load vector database for year {year}: {e}")
                else:
                    logger.warning(f"Vector database not found for year {year}: {vector_db_path}")
            
            if self.vector_stores:
                logger.info(f"Loaded {len(self.vector_stores)} vector databases")
            else:
                logger.warning("No vector databases loaded")
                
        except Exception as e:
            logger.error(f"Error loading vector databases: {e}")
            # Don't raise here, as we want the system to start even if vector DBs fail to load
    
    def initialize_data(self, force_reprocess: bool = False):
        """Initialize or reprocess the data."""
        try:
            logger.info("Initializing QA system data...")
            
            # Get PDF paths
            pdf_paths = get_pdf_paths(self.settings.upload_directory)
            
            if not pdf_paths:
                logger.warning("No PDF files found in data directory")
                return
            
            # Process each year
            for year, pdf_path in pdf_paths.items():
                vector_db_path = f"{self.settings.vector_db_directory}_{year}"
                
                # Check if vector database already exists
                if os.path.exists(vector_db_path) and not force_reprocess:
                    logger.info(f"Loading existing vector database for year {year}")
                    self.vector_stores[year] = FAISS.load_local(
                        vector_db_path, 
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                else:
                    logger.info(f"Processing PDF for year {year}: {pdf_path}")
                    self._process_pdf_for_year(year, pdf_path, vector_db_path)
            
            logger.info("Data initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error initializing data: {e}")
            raise
    
    def _process_pdf_for_year(self, year: int, file_path: str, vector_db_path: str):
        """Process a file (PDF or text) for a specific year."""
        try:
            documents = []
            
            # Handle different file types
            if file_path.lower().endswith('.pdf'):
                # Load PDF
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                
                # Clean and split text
                for page in pages:
                    cleaned_text = clean_text(page.page_content)
                    if cleaned_text.strip():
                        doc = Document(
                            page_content=cleaned_text,
                            metadata={
                                'source': file_path,
                                'page': page.metadata.get('page', 0),
                                'year': year
                            }
                        )
                        documents.append(doc)
            elif file_path.lower().endswith('.txt'):
                # Load text file
                from app.utils import load_text_file
                content = load_text_file(file_path)
                if content.strip():
                    cleaned_text = clean_text(content)
                    doc = Document(
                        page_content=cleaned_text,
                        metadata={
                            'source': file_path,
                            'page': 1,
                            'year': year
                        }
                    )
                    documents.append(doc)
            
            if not documents:
                logger.warning(f"No content found in file for year {year}")
                return
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks for year {year}")
            
            # Create vector store
            vector_store = FAISS.from_documents(chunks, self.embeddings)
            
            # Save vector store
            vector_db_dir = os.path.dirname(vector_db_path)
            if vector_db_dir:  # Only create directory if there's a directory component
                os.makedirs(vector_db_dir, exist_ok=True)
            vector_store.save_local(vector_db_path)
            
            # Store in memory
            self.vector_stores[year] = vector_store
            
            logger.info(f"Vector database created for year {year}")
            
        except Exception as e:
            logger.error(f"Error processing file for year {year}: {e}")
            raise
    
    def ask_question(self, query: str, year: int) -> QAResult:
        """Ask a question for a specific year."""
        try:
            if year not in self.vector_stores:
                raise ValueError(f"No data available for year {year}")
            
            # Retrieve relevant chunks
            vector_store = self.vector_stores[year]
            docs = vector_store.similarity_search_with_score(
                query, 
                k=self.settings.max_chunks_per_query
            )
            
            # Extract citations
            citations = [doc[0].page_content for doc in docs]
            similarity_scores = [1 - doc[1] for doc in docs]  # Convert distance to similarity
            
            # Generate answer
            answer = self._generate_answer(query, citations)
            
            # Calculate confidence
            confidence = self._calculate_confidence(len(citations), similarity_scores)
            
            return QAResult(
                answer=answer,
                citations=citations,
                confidence=confidence,
                year=year,
                query=query
            )
            
        except Exception as e:
            logger.error(f"Error asking question for year {year}: {e}")
            raise
    
    def ask_question_all_years(self, query: str) -> Dict[int, QAResult]:
        """Ask a question across all available years."""
        try:
            results = {}
            
            for year in self.vector_stores.keys():
                try:
                    result = self.ask_question(query, year)
                    results[year] = result
                except Exception as e:
                    logger.warning(f"Failed to process query for year {year}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error asking question across all years: {e}")
            raise
    
    def _generate_answer(self, query: str, citations: List[str]) -> str:
        """Generate answer using LLM."""
        try:
            # Create prompt template
            template = """
            You are a helpful assistant that answers questions about Apple's annual reports.
            Use only the provided context to answer the question. If the answer cannot be found in the context, say "I cannot find information about this in the provided context."
            
            Context:
            {context}
            
            Question: {question}
            
            Answer:"""
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Format context
            context = "\n\n".join(citations)
            
            # Generate response
            messages = prompt.format_messages(
                context=context,
                question=query
            )
            
            response = self.llm(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I encountered an error while generating the answer."
    
    def _calculate_confidence(self, num_chunks: int, similarity_scores: List[float]) -> float:
        """Calculate confidence score."""
        if not similarity_scores:
            return 0.0
        
        # Base confidence on average similarity
        avg_similarity = sum(similarity_scores) / len(similarity_scores)
        
        # Adjust based on number of chunks (more chunks = higher confidence)
        chunk_factor = min(num_chunks / 5.0, 1.0)  # Normalize to 0-1
        
        # Weighted combination
        confidence = (avg_similarity * 0.7) + (chunk_factor * 0.3)
        
        return min(max(confidence, 0.0), 1.0)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        try:
            available_years = list(self.vector_stores.keys())
            processed_years = available_years.copy()
            
            # Count total documents and chunks
            total_documents = len(available_years)
            total_chunks = sum(
                len(vector_store.index_to_docstore_id) 
                for vector_store in self.vector_stores.values()
            )
            
            return {
                "available_years": available_years,
                "total_years": total_documents,
                "processed_years": processed_years,
                "total_documents": total_documents,
                "total_chunks": total_chunks,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Error getting summary stats: {e}")
            return {
                "available_years": [],
                "total_years": 0,
                "processed_years": [],
                "total_documents": 0,
                "total_chunks": 0,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
