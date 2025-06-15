from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path("data")
PDF_DIR = BASE_DIR / "pdfs"
QUESTIONS_DB = BASE_DIR / "questions.json"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# External Service Configuration
EXTERNAL_SERVICE_URL = os.getenv("EXTERNAL_SERVICE_URL", "http://localhost:8001/v1")

# CORS Configuration
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"] 