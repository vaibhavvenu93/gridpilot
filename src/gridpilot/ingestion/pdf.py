from pathlib import Path

from pydantic import BaseModel, Field
from pypdf import PdfReader


class DocumentPage(BaseModel):
    """
    Text extracted from one page of a source document.

    Page numbers are one-based so they correspond to the
    page numbers a human reviewer sees.
    """

    page_number: int = Field(
        ge=1
    )

    text: str

    character_count: int = Field(
        ge=0
    )


class PDFDocument(BaseModel):
    """
    Evidence-preserving representation of an ingested PDF.

    GridPilot keeps pages separate so downstream extraction
    can link values back to their source page.
    """

    source_file: str

    page_count: int = Field(
        ge=1
    )

    pages: list[DocumentPage]

    warnings: list[str] = Field(
        default_factory=list
    )

    @property
    def full_text(self) -> str:
        """
        Combine page text when whole-document processing
        is required.
        """

        return "\n\n".join(
            page.text
            for page in self.pages
            if page.text
        )


def read_pdf(
    path: str | Path,
) -> PDFDocument:
    """
    Extract text from a digital PDF while preserving
    page-level evidence.

    This function intentionally does not perform OCR.

    Scanned or image-only PDFs should be detected and
    routed to a separate OCR pipeline rather than silently
    returning unreliable information.
    """

    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF does not exist: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, received: {pdf_path.suffix}"
        )

    reader = PdfReader(
        str(pdf_path)
    )

    if not reader.pages:
        raise ValueError(
            "PDF contains no pages."
        )

    pages: list[DocumentPage] = []
    warnings: list[str] = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        extracted_text = page.extract_text() or ""

        text = extracted_text.strip()

        pages.append(
            DocumentPage(
                page_number=page_number,
                text=text,
                character_count=len(text),
            )
        )

        if not text:
            warnings.append(
                f"Page {page_number} contains no extractable text."
            )

    if not any(page.text for page in pages):
        warnings.append(
            "No extractable text was found in the PDF. "
            "The document may require OCR."
        )

    return PDFDocument(
        source_file=pdf_path.name,
        page_count=len(pages),
        pages=pages,
        warnings=warnings,
    )
