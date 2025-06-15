import json
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from fastapi import HTTPException
from app.core.config import QUESTIONS_DB, PDF_DIR

# Thread safety for file operations
questions_lock = threading.Lock()


@contextmanager
def questions_file_lock():
    with questions_lock:
        yield


def ensure_data_directory():
    """Ensure data directory and files exist"""
    PDF_DIR.parent.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)

    if not QUESTIONS_DB.exists():
        QUESTIONS_DB.write_text("[]", encoding="utf-8")


def load_questions() -> list:
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
        raise HTTPException(
            status_code=500, detail=f"Error loading questions: {str(e)}"
        )


def save_questions(data: list) -> None:
    """Save questions to JSON file with thread safety"""
    try:
        with questions_file_lock():
            with open(QUESTIONS_DB, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving questions: {str(e)}")


def get_pdf_files() -> list:
    """Get list of all PDF files"""
    try:
        return [
            f
            for f in os.listdir(PDF_DIR)
            if os.path.isfile(os.path.join(PDF_DIR, f)) and f.lower().endswith(".pdf")
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def validate_pdf_filename(filename: str) -> str:
    """Validate PDF filename and prevent path traversal"""
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Security: Prevent path traversal and clean filename
    original_filename = os.path.basename(filename)
    if ".." in original_filename or not original_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    return original_filename


def get_pdf_file(filename: str) -> Path:
    """Get the full path to a PDF file by its name

    Args:
        filename (str): Name of the PDF file

    Returns:
        Path: Full path to the PDF file

    Raises:
        HTTPException: If file doesn't exist or filename is invalid
    """
    # Validate the filename
    valid_filename = validate_pdf_filename(filename)

    # Construct full path
    pdf_path = PDF_DIR / valid_filename

    # Check if file exists
    if not pdf_path.exists():
        raise HTTPException(
            status_code=404, detail=f"PDF file '{valid_filename}' not found"
        )

    return pdf_path
