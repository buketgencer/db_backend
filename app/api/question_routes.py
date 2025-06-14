from fastapi import APIRouter, HTTPException
import uuid
from app.models.schemas import (
    Question, QuestionCreate, QuestionUpdate,
    QuestionsResponse, MessageResponse
)
from app.utils.file_utils import load_questions, save_questions

router = APIRouter()

def validate_question_data(question_dict: dict) -> Question:
    """Validate and convert dict to Question model"""
    try:
        return Question(**question_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid question data: {str(e)}")

@router.get("/questions", response_model=QuestionsResponse)
def list_questions():
    """Get all questions"""
    questions_data = load_questions()
    questions = [validate_question_data(q) for q in questions_data]
    return QuestionsResponse(questions=questions, count=len(questions))

@router.post("/question", response_model=Question)
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

@router.get("/question/{id}", response_model=Question)
def get_question(id: str):
    """Get a specific question by ID"""
    questions = load_questions()
    
    for q in questions:
        if q.get("id") == id:
            return validate_question_data(q)
    
    raise HTTPException(status_code=404, detail="Question not found")

@router.put("/question/{id}", response_model=Question)
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

@router.delete("/question/{id}", response_model=MessageResponse)
def delete_question(id: str):
    """Delete a question by ID"""
    questions = load_questions()
    updated_questions = [q for q in questions if q.get("id") != id]
    
    if len(questions) == len(updated_questions):
        raise HTTPException(status_code=404, detail="Question not found")
    
    save_questions(updated_questions)
    return MessageResponse(message="Question deleted successfully", id=id) 