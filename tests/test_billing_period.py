from datetime import date
from pathlib import Path

from reportlab.pdfgen import canvas

from gridpilot.ingestion.extractor import extract_fields_from_document
from gridpilot.ingestion.mapper import extraction_to_bill
from gridpilot.ingestion.pdf import read_pdf


def create_bill_with_period(path: Path) -> None:
    """
    Create a synthetic electricity bill containing a billing period.
    """

    pdf = canvas.Canvas(str(path))

    pdf.drawString(
        72,
        760,
        "GRIDPILOT BILLING PERIOD TEST",
    )

    pdf.drawString(
        72,
        730,
        "Billing Period: 01/07/2026 - 31/07/2026",
    )

    pdf.drawString(
        72,
        700,
        "Units Consumed: 92,482 kWh",
    )

    pdf.drawString(
        72,
        670,
        "Maximum Demand: 417 kVA",
    )

    pdf.drawString(
        72,
        640,
        "Average Power Factor: 0.89",
    )

    pdf.drawString(
        72,
        610,
        "Energy Charges: INR 310,000",
    )

    pdf.drawString(
        72,
        580,
        "Demand Charges: INR 112,000",
    )

    pdf.drawString(
        72,
        550,
        "Amount Payable: INR 524,381",
    )

    pdf.save()


def test_extractor_reads_billing_period(tmp_path: Path):
    pdf_path = tmp_path / "bill.pdf"

    create_bill_with_period(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    assert (
        extraction.metadata.billing_period_start
        == date(2026, 7, 1)
    )

    assert (
        extraction.metadata.billing_period_end
        == date(2026, 7, 31)
    )


def test_billing_period_preserves_source_evidence(
    tmp_path: Path,
):
    pdf_path = tmp_path / "bill.pdf"

    create_bill_with_period(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    evidence = (
        extraction.metadata.billing_period_evidence
    )

    assert evidence is not None

    assert evidence.page == 1

    assert (
        evidence.raw_text
        == "Billing Period: 01/07/2026 - 31/07/2026"
    )

    assert evidence.source_label == "Billing Period"

    assert evidence.confidence == 1.0


def test_mapper_uses_extracted_billing_period(
    tmp_path: Path,
):
    pdf_path = tmp_path / "bill.pdf"

    create_bill_with_period(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    bill = extraction_to_bill(
        extraction,
        bill_id="GP-AUTO-DATE-001",
        facility_name="Demo Manufacturing Plant",
    )

    assert (
        bill.billing_period.start
        == date(2026, 7, 1)
    )

    assert (
        bill.billing_period.end
        == date(2026, 7, 31)
    )


def test_canonical_bill_preserves_billing_period_evidence(
    tmp_path: Path,
):
    pdf_path = tmp_path / "bill.pdf"

    create_bill_with_period(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    bill = extraction_to_bill(
        extraction,
        bill_id="GP-AUTO-DATE-002",
        facility_name="Demo Manufacturing Plant",
    )

    billing_evidence = [
        evidence
        for evidence in bill.evidence
        if evidence.field == "billing_period"
    ]

    assert len(billing_evidence) == 1

    assert billing_evidence[0].page == 1

    assert (
        billing_evidence[0].source_text
        == "Billing Period: 01/07/2026 - 31/07/2026"
    )
