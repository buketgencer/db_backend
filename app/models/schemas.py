from pydantic import BaseModel, Field
from typing import List, Optional, Literal


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


class QuestionRequest(BaseModel):
    """Schema for individual question request to PDF processing service"""

    soru: str = Field(..., description="The question text")
    yordam: Optional[str] = Field(None, description="Optional custom method")


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


class ProcessRequest(BaseModel):
    """Schema for process request"""

    question_ids: List[str] = Field(..., description="List of question IDs to process")
    pdf_name: str = Field(..., description="Name of the PDF file to process")


class ProcessResult(BaseModel):
    """Schema for individual process result"""

    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="The answer text")
    status: Literal["answer_found", "answer_notfound"] = Field(
        ..., description="Status of the answer"
    )


class ProcessResponse(BaseModel):
    """Schema for process response"""

    results: List[ProcessResult] = Field(..., description="List of processed results")
    count: int = Field(..., description="Number of results")

class PreProcessResponse(BaseModel):
    """Schema for pre-process response"""

    status: Literal["completed", "failed"]

# todo : delete response objesi oluşturuulur preprocessresponse ile aynı olabilir.
class DeleteResponse(BaseModel):
    """Schema for delete response"""

    status: Literal["completed", "failed"]