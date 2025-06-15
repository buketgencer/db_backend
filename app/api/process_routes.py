from fastapi import APIRouter, HTTPException
from app.models.schemas import ProcessRequest, ProcessResponse, ProcessResult, Question
from app.utils.file_utils import load_questions, get_pdf_file
from app.core.config import PDF_DIR, EXTERNAL_SERVICE_URL
from app.core.pdf_client import PDFProcessorClient, QuestionRequest
import os
import httpx
import json
from typing import List, Dict, Any
from pathlib import Path

router = APIRouter()


@router.post("/process", response_model=ProcessResponse)
async def process_questions(request: ProcessRequest):
    all_questions = load_questions()

    requested_questions = [
        Question(id=q["id"], soru=q["soru"], yordam=q.get("yordam"))
        for q in all_questions
        if q["id"] in request.question_ids
    ]
    pdf_path = get_pdf_file(request.pdf_name)

    # Convert questions to QuestionRequest format
    question_requests = [
        QuestionRequest(soru=q.soru, yordam=q.yordam) for q in requested_questions
    ]

    try:
        # Initialize the PDF processor client
        client = PDFProcessorClient(base_url=EXTERNAL_SERVICE_URL)

        # Process the PDF with questions
        response = await client.process_pdf_async(
            questions=question_requests, pdf_file_path=pdf_path
        )

        return response

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"External service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
