from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from app.core.config import PDF_DIR
from app.models.schemas import PDFListResponse, PDFUploadResponse
from app.utils.file_utils import get_pdf_files, validate_pdf_filename

router = APIRouter()

@router.get("/pdfs", response_model=PDFListResponse)
def list_pdfs():
    """Get list of all uploaded PDF files"""
    files = get_pdf_files()
    return PDFListResponse(pdf_files=files, count=len(files))

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file using original filename, prevent duplicates"""
    original_filename = validate_pdf_filename(file.filename)
    
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
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/pdf/{filename}")
def get_pdf(filename: str):
    """Download a specific PDF file"""
    # Security: Prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(file_path, media_type="application/pdf") 