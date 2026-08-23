from pathlib import Path

from reportlab.pdfgen import canvas

from gridpilot.ingestion.extractor import extract_fields_from_document
from gridpilot.ingestion.pdf import read_pdf


def create_extraction_test_bill(
    path: Path,
) -> None:
    """
    Create a synthetic electricity bill containing
    fields GridPilot should recognize.
    """

    pdf = canvas.Canvas(str(path))

    pdf.drawString(
        72,
        760,
        "GRIDPILOT EXTRACTION TEST BILL",
    )

    pdf.drawString(
        72,
        720,
        "Units Consumed: 92,482 kWh",
    )

    pdf.drawString(
        72,
        690,
        "Maximum Demand: 417 kVA",
    )

    pdf.drawString(
        72,
        660,
        "Average Power Factor: 0.89",
    )

    pdf.drawString(
        72,
        630,
        "PF Penalty: INR 24,000",
    )

    pdf.drawString(
        72,
        600,
        "Energy Charges: INR 310,000",
    )

    pdf.drawString(
        72,
        570,
        "Demand Charges: INR 112,000",
    )

    pdf.drawString(
        72,
        540,
        "Fixed Charges: INR 10,000",
    )

    pdf.drawString(
        72,
        510,
        "Amount Payable: INR 524,381",
    )

    pdf.save()


def test_extractor_finds_expected_fields(
    tmp_path: Path,
):
    pdf_path = tmp_path / "bill.pdf"

    create_extraction_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    field_names = {
        field.field_name
        for field in extraction.fields
    }

    assert "consumption_kwh" in field_names
    assert "maximum_demand_kva" in field_names
    assert "power_factor" in field_names
    assert "power_factor_penalty" in field_names
   assert "energy_charge" in field_names
assert "demand_charge" in field_names
assert "fixed_charge" in field_names
    assert "total_cost" in field_names


def test_extractor_normalizes_values(
    tmp_path: Path,
):
    pdf_path = tmp_path / "bill.pdf"

    create_extraction_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    fields = {
        field.field_name: field
        for field in extraction.fields
    }

    assert (
        fields["consumption_kwh"].normalized_value
        == 92482.0
    )

    assert (
        fields["maximum_demand_kva"].normalized_value
        == 417.0
    )

    assert (
        fields["power_factor"].normalized_value
        == 0.89
    )

    assert (
        fields["power_factor_penalty"].normalized_value
        == 24000.0
    )

    assert (
        fields["total_cost"].normalized_value
        == 524381.0
    )


def test_extractor_preserves_evidence(
    tmp_path: Path,
):
    pdf_path = tmp_path / "bill.pdf"

    create_extraction_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    fields = {
        field.field_name: field
        for field in extraction.fields
    }

    evidence = fields[
        "power_factor"
    ].evidence

    assert evidence is not None

    assert evidence.page == 1

    assert (
        evidence.raw_text
        == "Average Power Factor: 0.89"
    )

    assert (
        evidence.source_label
        == "Average Power Factor"
    )

    assert evidence.confidence == 1.0


def test_complete_bill_does_not_require_review(
    tmp_path: Path,
):
    pdf_path = tmp_path / "bill.pdf"

    create_extraction_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    assert extraction.missing_fields == []

    assert extraction.review_required is False


def test_missing_required_field_requires_review(
    tmp_path: Path,
):
    pdf_path = tmp_path / "incomplete_bill.pdf"

    pdf = canvas.Canvas(str(pdf_path))

    pdf.drawString(
        72,
        760,
        "Units Consumed: 50,000 kWh",
    )

    pdf.save()

    document = read_pdf(pdf_path)

    extraction = extract_fields_from_document(
        document
    )

    assert "total_cost" in extraction.missing_fields

    assert extraction.review_required is True
