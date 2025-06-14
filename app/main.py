from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import (
    CORS_ORIGINS, CORS_CREDENTIALS,
    CORS_METHODS, CORS_HEADERS
)
from app.api import pdf_routes, question_routes, process_routes
from app.utils.file_utils import ensure_data_directory

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Include routers
app.include_router(pdf_routes.router)
app.include_router(question_routes.router)
app.include_router(process_routes.router)

# Initialize data directory
ensure_data_directory()

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "question-pdf-api"} 