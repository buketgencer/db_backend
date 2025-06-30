from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from app.core.config import PDF_DIR,  EXTERNAL_SERVICE_URL
from app.models.schemas import PDFListResponse, PDFUploadResponse
from app.utils.file_utils import get_pdf_files, validate_pdf_filename, get_pdf_file
from app.core.pdf_client import PDFProcessorClient
import httpx


router = APIRouter()


@router.get("/pdfs", response_model=PDFListResponse)
def list_pdfs():
    """Get list of all uploaded PDF files"""
    files = get_pdf_files()
    return PDFListResponse(pdf_files=files, count=len(files))


# routes.py (veya benzeri FastAPI modülü)

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file using the original filename, prevent duplicates,
    store it on disk, and immediately forward the content to the
    external preprocessing service.
    """
    original_filename = validate_pdf_filename(file.filename)
    file_path = os.path.join(PDF_DIR, original_filename)

    # Çakışma kontrolü
    if os.path.exists(file_path):
        raise HTTPException(
            status_code=409,
            detail=f"File '{original_filename}' already exists. "
                   "Please rename the file or delete the existing one.",
        )

    try:
        # Dosyayı sadece *bir kez* oku
        file_bytes = await file.read()

        # Diske kaydet
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Haricî servise ilet
        client = PDFProcessorClient(base_url=EXTERNAL_SERVICE_URL)
        await client.preprocess_pdf_async(
            file_name=original_filename,
            file_bytes=file_bytes,
        )

        return PDFUploadResponse(
            filename=original_filename,
            message=f"PDF '{original_filename}' uploaded successfully",
        )

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"External service error: {str(exc)}"
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(exc)}"
        ) from exc

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


@router.delete("/pdf/{filename}")
def delete_pdf(filename: str):
    # upload pdf teki gibi pdf._client.pyda todo diye arat orda delete yazılacak burdan çağrılacak
    """Delete a specific PDF file"""
    # Security: Prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found.")

    try:
        os.remove(file_path)
        return {"message": f"PDF '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

