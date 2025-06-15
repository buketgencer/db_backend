import httpx
import json
from typing import List, Optional, Union
from pathlib import Path
import asyncio
from app.models.schemas import QuestionRequest, ProcessResponse
from app.core.config import EXTERNAL_SERVICE_URL, EXTERNAL_SERVICE_TIMEOUT


class PDFProcessorClient:
    """Client for making requests to the PDF processing endpoint"""

    def __init__(self, base_url: str = EXTERNAL_SERVICE_URL):
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/process"

    async def process_pdf_async(
        self,
        questions: List[QuestionRequest],
        pdf_file_path: Union[str, Path],
        timeout: float = EXTERNAL_SERVICE_TIMEOUT,
    ) -> ProcessResponse:
        """
        Asynchronously process PDF with questions

        Args:
            questions: List of QuestionRequest objects
            pdf_file_path: Path to the PDF file
            timeout: Request timeout in seconds

        Returns:
            ProcessResponse object

        Raises:
            httpx.HTTPError: If request fails
            FileNotFoundError: If PDF file doesn't exist
        """
        pdf_path = Path(pdf_file_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Convert questions to JSON string
        questions_data = [q.dict() for q in questions]
        questions_json = json.dumps(questions_data)

        async with httpx.AsyncClient(timeout=timeout) as client:
            # Prepare the multipart form data
            files = {
                "pdf_file": (pdf_path.name, pdf_path.open("rb"), "application/pdf")
            }
            data = {"questions": questions_json}

            try:
                response = await client.post(self.endpoint, files=files, data=data)
                response.raise_for_status()

                # Parse and return the response
                response_data = response.json()
                return ProcessResponse(**response_data)

            except httpx.HTTPStatusError as e:
                raise httpx.HTTPError(
                    f"HTTP {e.response.status_code}: {e.response.text}"
                )
            finally:
                # Close the file
                files["pdf_file"][1].close()


# Convenience functions for direct usage
async def process_pdf_questions_async(
    questions: List[QuestionRequest],
    pdf_file_path: Union[str, Path],
    base_url: str = EXTERNAL_SERVICE_URL,
    timeout: float = EXTERNAL_SERVICE_TIMEOUT,
) -> ProcessResponse:
    """
    Convenience function for async PDF processing
    """
    client = PDFProcessorClient(base_url)
    return await client.process_pdf_async(questions, pdf_file_path, timeout)
