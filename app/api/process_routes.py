from fastapi import APIRouter, HTTPException
from app.models.schemas import ProcessRequest, ProcessResponse, ProcessResult
from app.utils.file_utils import load_questions, validate_pdf_filename
from app.core.config import PDF_DIR, EXTERNAL_SERVICE_URL
import os
import httpx
import json
from typing import List, Dict, Any
from pathlib import Path

router = APIRouter()

async def query_process_endpoint(
    base_url: str,
    questions: List[Dict[str, Any]],
    pdf_file_path: str,
    timeout: float = 30.0
) -> Dict[str, Any]:
    
    process_request = {
        "questions": questions
    }
    
    pdf_path = Path(pdf_file_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        with open(pdf_path, "rb") as pdf_file:
            files = {
                "pdf_file": ("document.pdf", pdf_file, "application/pdf")
            }
            data = {
                "request": json.dumps(process_request)
            }
            
            response = await client.post(
                f"{base_url}/process",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

@router.post("/process", response_model=ProcessResponse)
async def process_questions(request: ProcessRequest):
    pdf_filename = validate_pdf_filename(request.pdf_name)
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF file '{pdf_filename}' not found")

    questions_data = load_questions()
    questions_dict = {q["id"]: q for q in questions_data}

    questions_to_process = []
    for question_id in request.question_ids:
        if question_id not in questions_dict:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID '{question_id}' not found"
            )
        question = questions_dict[question_id]
        questions_to_process.append({
            "soru": question["soru"],
            "yordam": question["yordam"]
        })

    try:
        response_data = await query_process_endpoint(
            base_url=EXTERNAL_SERVICE_URL,
            questions=questions_to_process,
            pdf_file_path=pdf_path
        )
        
        results = []
        for result_item in response_data["results"]:
            result = ProcessResult(
                question=result_item["question"],
                answer=result_item["answer"],
                status=result_item["status"]
            )
            results.append(result)
        
        return ProcessResponse(
            results=results,
            count=len(results)
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"External service unavailable: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"External service error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")