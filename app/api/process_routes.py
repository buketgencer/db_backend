from fastapi import APIRouter, HTTPException
from app.models.schemas import ProcessRequest, ProcessResponse, ProcessResult
from app.utils.file_utils import load_questions, validate_pdf_filename
from app.core.config import PDF_DIR
import os
import random
import time

router = APIRouter()

@router.post("/process", response_model=ProcessResponse)
def process_questions(request: ProcessRequest):
    """
    Process a list of questions against a PDF file.
    Returns answers and their status for each question.
    """
    # Validate PDF file exists
    pdf_filename = validate_pdf_filename(request.pdf_name)
    pdf_path = os.path.join(PDF_DIR, pdf_filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF file '{pdf_filename}' not found")

    # Load questions
    questions_data = load_questions()
    questions_dict = {q["id"]: q for q in questions_data}
    questions_array = [{"soru": q["soru"], "yordam": q["yordam"]} for q in questions_data]

    print(f"Processing {questions_array} questions")
    print(f"PDF file: {pdf_filename}")

    # Process each question
    results = []
    dummy_answers = [
        "This is a sample answer for the question.",
        "Based on the document, the answer is provided here.",
        "The analysis shows that this is the correct response.",
        "According to the text, this is the solution.",
        "The document indicates this as the answer.",
        "This is the result of processing the question.",
        "The answer has been extracted from the document.",
        "Here is the response based on the analysis.",
        "The text suggests this as the answer.",
        "This is the conclusion drawn from the document."
    ]

    for question_id in request.question_ids:
        if question_id not in questions_dict:
            raise HTTPException(
                status_code=404,
                detail=f"Question with ID '{question_id}' not found"
            )
        
        question = questions_dict[question_id]

        # add timeout to simulate processing time
        time.sleep(random.randint(1, 3))
        
        # Generate dummy result
        result = ProcessResult(
            question=question["soru"],
            answer=random.choice(dummy_answers),
            status=random.choice(["answer_found", "answer_notfound"])
        )
        results.append(result)

    return ProcessResponse(results=results, count=len(results)) 