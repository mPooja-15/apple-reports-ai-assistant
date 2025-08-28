#!/usr/bin/env python3
"""
Initialize the QA system with existing data.
"""

import os
import sys
from pathlib import Path

def init_qa_system():
    """Initialize the QA system with data."""
    try:
        print("🔧 Initializing QA system...")
        
        # Import the QA system
        from qa_system import QASystem
        
        # Create QA system instance
        qa_system = QASystem()
        
        print("📊 Initializing data...")
        # Initialize data (this will process the text files and create embeddings)
        qa_system.initialize_data(force_reprocess=True)
        
        print("✅ QA system initialized successfully!")
        
        # Test with a simple query
        print("\n🧪 Testing with a sample query...")
        result = qa_system.ask_question("What was Apple's total revenue in 2023?", 2023)
        
        print(f"✅ Test successful!")
        print(f"   Answer: {result.answer[:100]}...")
        print(f"   Confidence: {result.confidence:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing QA system: {e}")
        return False

if __name__ == "__main__":
    success = init_qa_system()
    sys.exit(0 if success else 1)
