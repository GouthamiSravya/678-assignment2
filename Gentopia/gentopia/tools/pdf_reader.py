from typing import Optional, Type, Any
from pydantic import BaseModel, Field
import requests
import PyPDF2
from io import BytesIO
from gentopia.tools.basetool import BaseTool

class PDFReaderArgs(BaseModel):
    url: str = Field(..., description="URL of the PDF file")

class PDFReader(BaseTool):
    name = "pdf_reader"
    description = ("Fetches a PDF file from a provided URL and extracts its text and metadata. "
                   "Input should be the URL of the PDF file.")
    args_schema: Optional[Type[BaseModel]] = PDFReaderArgs

    def _run(self, url: str) -> str:
        try:
            return self.retrieve_pdf_text(url)
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            return f"Unexpected error occurred: {str(e)}"

    def retrieve_pdf_text(self, url: str) -> str:
        pdf_content = self.download_pdf(url)
        if not pdf_content:
            return "Failed to fetch PDF."
        
        return self.extract_text_from_pdf(pdf_content)

    def download_pdf(self, url: str) -> Optional[bytes]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise ValueError(f"Error fetching the PDF: {str(e)}")

    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        try:
            with BytesIO(pdf_content) as file:
                reader = PyPDF2.PdfReader(file)
                return self.aggregate_text(reader).strip()
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

    def aggregate_text(self, reader: PyPDF2.PdfReader) -> str:
        text = ''
        for page in reader.pages:
            page_text = page.extract_text() or ''
            text += page_text + '\n'
        return text

    def retrieve_pdf_metadata(self, pdf_content: bytes) -> dict:
        try:
            with BytesIO(pdf_content) as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata
                return {key: metadata[key] for key in metadata if key}
        except Exception as e:
            return {"error": f"Failed to extract metadata: {str(e)}"}

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

if __name__ == "_main_":
    pdf_reader = PDFReader()
    pdf_url = "https://ijrpr.com/uploads/V4ISSUE6/IJRPR144687.pdf"
    metadata = pdf_reader.retrieve_pdf_metadata(pdf_content)
    print("PDF Metadata: /n", metadata)
