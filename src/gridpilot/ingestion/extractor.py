import re

from gridpilot.ingestion.models import (
    BillExtraction,
    ExtractedField,
    SourceEvidence,
)
from gridpilot.ingestion.normalizer import normalize_field
from gridpilot.ingestion.pdf import PDFDocument


FIELD_PATTERNS: list[tuple[str, str]] = [
    (
        "Units Consumed",
        r"(?i)\bUnits\s+Consumed\s*[:\-]?\s*([0-9,.]+)\s*(kWh)?",
    ),
    (
        "Maximum Demand KVA",
        r"(?i)\bMaximum\s+Demand\s*[:\-]?\s*([0-9,.]+)\s*(kVA)\b",
    ),
    (
        "Maximum Demand KW",
        r"(?i)\bMaximum\s+Demand\s*[:\-]?\s*([0-9,.]+)\s*(kW)\b",
    ),
    (
        "Average Power Factor",
        r"(?i)\bAverage\s+Power\s+Factor\s*[:\-]?\s*([0-9.]+)",
    ),
    (
        "PF Penalty",
        r"(?i)\bPF\s+Penalty\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,.]+)",
    ),
    (
        "Demand Charges",
        r"(?i)\bDemand\s+Charges?\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,.]+)",
    ),
    (
        "Energy Charges",
        r"(?i)\bEnergy\s+Charges?\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,.]+)",
    ),
    (
        "Fixed Charges",
        r"(?i)\bFixed\s+Charges?\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,.]+)",
    ),
    (
        "Amount Payable",
        r"(?i)\bAmount\s+Payable\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([0-9,.]+)",
    ),
]


def _unit_from_match(
    match: re.Match[str],
) -> str | None:
    """
    Return the optional unit captured by a field pattern.
    """

    if match.lastindex is None or match.lastindex < 2:
        return None

    return match.group(2)


def extract_fields_from_document(
    document: PDFDocument,
) -> BillExtraction:
    """
    Extract known electricity-bill fields from page-level PDF text.

    This is intentionally a deterministic first-pass extractor.

    AI extraction can later be used as a fallback for fields that
    deterministic parsing cannot confidently identify.
    """

    fields: list[ExtractedField] = []
    warnings = list(document.warnings)

    seen_fields: set[str] = set()

    for page in document.pages:
        for source_label, pattern in FIELD_PATTERNS:
            match = re.search(
                pattern,
                page.text,
            )

            if match is None:
                continue

            raw_value = match.group(1)
            unit = _unit_from_match(match)

            normalized = normalize_field(
                source_label=source_label,
                raw_value=raw_value,
                unit=unit,
            )

            if normalized.field_name in seen_fields:
                warnings.append(
                    "Duplicate field detected for "
                    f"{normalized.field_name} on page "
                    f"{page.page_number}."
                )
                continue

            normalized.evidence = SourceEvidence(
                page=page.page_number,
                raw_text=match.group(0),
                source_label=source_label,
                confidence=1.0,
            )

            fields.append(normalized)

            seen_fields.add(
                normalized.field_name
            )

    required_fields = {
        "consumption_kwh",
        "total_cost",
    }

    extracted_names = {
        field.field_name
        for field in fields
    }

    missing_fields = sorted(
        required_fields - extracted_names
    )

    review_required = bool(
        missing_fields
        or any(
            field.status == "REVIEW_REQUIRED"
            for field in fields
        )
    )

    if missing_fields:
        warnings.append(
            "Required GridPilot fields are missing: "
            + ", ".join(missing_fields)
        )

    return BillExtraction(
        source_file=document.source_file,
        extraction_method="TEXT",
        fields=fields,
        warnings=warnings,
        missing_fields=missing_fields,
        review_required=review_required,
    )
