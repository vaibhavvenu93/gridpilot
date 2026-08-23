from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceEvidence(BaseModel):
    """
    Evidence linking an extracted value back to the source document.

    GridPilot should preserve evidence wherever possible so that
    extracted financial and energy data can be audited.
    """

    page: int | None = None
    raw_text: str | None = None
    source_label: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class ExtractedField(BaseModel):
    """
    A field extracted from an electricity bill before normalization.
    """

    field_name: str

    raw_value: Any

    normalized_value: Any | None = None

    unit: str | None = None

    status: Literal[
        "EXTRACTED",
        "NORMALIZED",
        "REVIEW_REQUIRED",
        "MISSING",
    ] = "EXTRACTED"

    evidence: SourceEvidence | None = None
    

class BillingMetadata(BaseModel):
    """
    Bill-level metadata extracted from the source document.
    """

    billing_period_start: date | None = None
    billing_period_end: date | None = None

    billing_period_evidence: SourceEvidence | None = None
class BillExtraction(BaseModel):
    """
    Complete intermediate extraction produced from a source
    electricity bill.

    This object sits between document ingestion and the canonical
    ElectricityBill model.
    """

    source_file: str

    utility_name: str | None = None

        metadata: BillingMetadata = Field(
        default_factory=BillingMetadata
    )

    extraction_method: Literal[
        "MANUAL",
        "TEXT",
        "OCR",
        "AI",
        "HYBRID",
    ]

    fields: list[ExtractedField] = Field(
        default_factory=list
    )

    warnings: list[str] = Field(
        default_factory=list
    )

    missing_fields: list[str] = Field(
        default_factory=list
    )

    review_required: bool = False

    def get_field(
        self,
        field_name: str,
    ) -> ExtractedField | None:
        """
        Return an extracted field by canonical GridPilot field name.
        """

        for field in self.fields:
            if field.field_name == field_name:
                return field

        return None
