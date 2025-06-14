
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
import os
import json
import threading
from contextlib import contextmanager
from pathlib import Path

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Configuration
BASE_DIR = Path("data")
PDF_DIR = BASE_DIR / "pdfs"
QUESTIONS_DB = BASE_DIR / "questions.json"

# Thread safety for file operations
questions_lock = threading.Lock()

@contextmanager
def questions_file_lock():
    with questions_lock:
        yield

def ensure_data_directory():
    """Ensure data directory and files exist"""
    BASE_DIR.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    
    if not QUESTIONS_DB.exists():
        QUESTIONS_DB.write_text("[]", encoding="utf-8")

# Initialize data directory
ensure_data_directory()

# Pydantic Models/Schemas
class Question(BaseModel):
    """Complete Question schema with all fields"""
    id: str = Field(..., description="Unique identifier for the question")
    soru: str = Field(..., min_length=1, description="The question text")
    yordam: Optional[str] = Field(None, description="Optional procedure/method")

class QuestionCreate(BaseModel):
    """Schema for creating a new question (without id)"""
    soru: str = Field(..., min_length=1, description="The question text")
    yordam: Optional[str] = Field(None, description="Optional procedure/method")

class QuestionUpdate(BaseModel):
    """Schema for updating an existing question"""
    soru: str = Field(..., min_length=1, description="The question text")
    yordam: Optional[str] = Field(None, description="Optional procedure/method")

class QuestionsResponse(BaseModel):
    """Schema for questions list response"""
    questions: List[Question]
    count: int

class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str
    id: Optional[str] = None

class PDFListResponse(BaseModel):
    """Schema for PDF list response"""
    pdf_files: List[str]
    count: int

class PDFUploadResponse(BaseModel):
    """Schema for PDF upload response"""
    filename: str
    message: str

# Helper Functions
def load_questions() -> List[dict]:
    """Load questions from JSON file with thread safety"""
    try:
        with questions_file_lock():
            with open(QUESTIONS_DB, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure it's a list
                if not isinstance(data, list):
                    return []
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading questions: {str(e)}")

def save_questions(data: List[dict]) -> None:
    """Save questions to JSON file with thread safety"""
    try:
        with questions_file_lock():
            with open(QUESTIONS_DB, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving questions: {str(e)}")

def validate_question_data(question_dict: dict) -> Question:
    """Validate and convert dict to Question model"""
    try:
        return Question(**question_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid question data: {str(e)}")

# --- PDF Endpoints ---
@app.get("/pdfs", response_model=PDFListResponse)
def list_pdfs():
    """Get list of all uploaded PDF files"""
    try:
        files = [
            f for f in os.listdir(PDF_DIR)
            if os.path.isfile(os.path.join(PDF_DIR, f)) and f.lower().endswith(".pdf")
        ]
        return PDFListResponse(pdf_files=files, count=len(files))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file using original filename, prevent duplicates"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Security: Prevent path traversal and clean filename
    original_filename = os.path.basename(file.filename)
    if ".." in original_filename or not original_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    try:
        file_path = os.path.join(PDF_DIR, original_filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=409, 
                detail=f"File '{original_filename}' already exists. Please rename the file or delete the existing one."
            )

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        return PDFUploadResponse(
            filename=original_filename, 
            message=f"PDF '{original_filename}' uploaded successfully"
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 409 conflict)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
@app.get("/pdf/{filename}")
def get_pdf(filename: str):
    """Download a specific PDF file"""
    # Security: Prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(file_path, media_type="application/pdf")

# --- Question Endpoints ---
@app.get("/questions", response_model=QuestionsResponse)
def list_questions():
    """Get all questions"""
    questions_data = load_questions()
    questions = [validate_question_data(q) for q in questions_data]
    return QuestionsResponse(questions=questions, count=len(questions))

@app.post("/question", response_model=Question)
def add_question(q: QuestionCreate):
    """Create a new question"""
    questions = load_questions()
    
    new_question = {
        "id": str(uuid.uuid4()),
        "soru": q.soru,
        "yordam": q.yordam
    }
    
    questions.append(new_question)
    save_questions(questions)
    
    return validate_question_data(new_question)

@app.get("/question/{id}", response_model=Question)
def get_question(id: str):
    """Get a specific question by ID"""
    questions = load_questions()
    
    for q in questions:
        if q.get("id") == id:
            return validate_question_data(q)
    
    raise HTTPException(status_code=404, detail="Question not found")

@app.put("/question/{id}", response_model=Question)
def update_question(id: str, q: QuestionUpdate):
    """Update an existing question"""
    questions = load_questions()
    
    for idx, item in enumerate(questions):
        if item.get("id") == id:
            updated = {
                "id": id,
                "soru": q.soru,
                "yordam": q.yordam
            }
            questions[idx] = updated
            save_questions(questions)
            return validate_question_data(updated)
    
    raise HTTPException(status_code=404, detail="Question not found")

@app.delete("/question/{id}", response_model=MessageResponse)
def delete_question(id: str):
    """Delete a question by ID"""
    questions = load_questions()
    updated_questions = [q for q in questions if q.get("id") != id]
    
    if len(questions) == len(updated_questions):
        raise HTTPException(status_code=404, detail="Question not found")
    
    save_questions(updated_questions)
    return MessageResponse(message="Question deleted successfully", id=id)

# --- Health Check ---
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "question-pdf-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)