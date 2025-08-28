# 🍎 Apple Annual Reports QA System - Backend

A high-quality, production-ready FastAPI backend for the Apple Annual Reports QA System with comprehensive error handling, logging, and best practices.

## 🏗️ **Architecture Overview**

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── models.py          # Pydantic models
│   ├── exceptions.py      # Custom exceptions
│   ├── utils.py           # Utility functions
│   └── services/
│       ├── __init__.py
│       ├── qa_service.py  # QA business logic
│       └── file_service.py # File operations
├── main.py                # FastAPI application
├── requirements.txt       # Dependencies
└── README_BACKEND.md      # This file
```

## 🚀 **Quick Start**

### **1. Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env
# Edit .env and add your OpenAI API key
```

### **2. Configuration**
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_LLM_MODEL=gpt-3.5-turbo
```

### **3. Run the Application**
```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📋 **API Endpoints**

### **Health & Status**
- `GET /` - Root endpoint with API information
- `GET /health` - Health check with service status

### **QA Operations**
- `POST /api/query` - Query the QA system
- `GET /api/stats` - Get system statistics
- `GET /api/years` - Get available years
- `POST /api/init-data` - Initialize/reprocess data
- `GET /api/example-queries` - Get example queries

### **File Management**
- `POST /api/upload-pdf` - Upload PDF file
- `GET /api/files` - List uploaded files
- `DELETE /api/files/{filename}` - Delete file
- `POST /api/files/cleanup` - Clean up orphaned files



### **Docker Support**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🚀 **Deployment**

### **Production Configuration**
```bash
# Environment variables
export OPENAI_API_KEY="your_production_key"
export LOG_LEVEL="WARNING"
export CORS_ORIGINS="https://yourdomain.com"

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Docker Deployment**
```bash
# Build image
docker build -t apple-qa-backend .

# Run container
docker run -p 8000:8000 apple-qa-backend
```

### **Kubernetes Deployment**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apple-qa-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: apple-qa-backend
  template:
    metadata:
      labels:
        app: apple-qa-backend
    spec:
      containers:
      - name: backend
        image: apple-qa-backend:latest
        ports:
        - containerPort: 8000
```

## 📚 **API Documentation**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### **Example Requests**
```bash
# Health check
curl http://localhost:8000/health

# Query the system
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What was Apple revenue in 2023?", "year": 2023}'

# Upload file
curl -X POST http://localhost:8000/api/upload-pdf \
  -F "file=@apple_report_2023.pdf"
```
