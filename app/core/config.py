from pathlib import Path

# Base paths
BASE_DIR = Path("data")
PDF_DIR = BASE_DIR / "pdfs"
QUESTIONS_DB = BASE_DIR / "questions.json"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS Configuration
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"] 