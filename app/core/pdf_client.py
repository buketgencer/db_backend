import httpx
import json
from typing import List, Optional, Union
from pathlib import Path
import asyncio
from app.models.schemas import QuestionRequest, ProcessResponse, PreProcessResponse
from app.core.config import EXTERNAL_SERVICE_URL, EXTERNAL_SERVICE_TIMEOUT


class PDFProcessorClient:
    """Client for making requests to the PDF processing endpoint"""

    def __init__(self, base_url: str = EXTERNAL_SERVICE_URL):
        self.base_url = base_url.rstrip("/")
        self.process_endpoint = f"{self.base_url}/process"
        self.preprocess_endpoint = f"{self.base_url}/preprocess-pdf"

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
                response = await client.post(self.process_endpoint, files=files, data=data)
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

    async def preprocess_pdf_async(
        self,
        *,
        file_name: str,
        file_bytes: bytes,
        timeout: float = EXTERNAL_SERVICE_TIMEOUT,
    ) -> PreProcessResponse:
        """
        Asynchronously send a PDF file (as bytes) to the external
        preprocessing service.

        Args:
            file_name: Original filename to preserve in form-data.
            file_bytes: Raw bytes of the PDF.
            timeout: Request timeout in seconds.

        Returns:
            PreProcessResponse instance parsed from JSON.

        Raises:
            httpx.HTTPError: If the HTTP request fails or returns a ≥400 code.
        """
        files = {
            "pdf_file": (file_name, file_bytes, "application/pdf")
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(self.preprocess_endpoint, files=files)
                response.raise_for_status()
                return PreProcessResponse(**response.json())

            except httpx.HTTPStatusError as exc:
                raise httpx.HTTPError(
                    f"HTTP {exc.response.status_code}: {exc.response.text}"
                ) from exc


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
