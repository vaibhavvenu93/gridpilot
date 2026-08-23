from datetime import date
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from gridpilot.ingestion.extractor import extract_fields_from_document
from gridpilot.ingestion.mapper import BillMappingError, extraction_to_bill
from gridpilot.ingestion.pdf import read_pdf


TEST_PERIOD_START = date(2026, 7, 1)
TEST_PERIOD_END = date(2026, 7, 31)


def create_mapper_test_bill(path: Path) -> None:
    """Create a synthetic electricity bill for mapper testing."""

    pdf = canvas.Canvas(str(path))

    pdf.drawString(72, 760, "GRIDPILOT MAPPER TEST BILL")
    pdf.drawString(72, 720, "Units Consumed: 92,482 kWh")
    pdf.drawString(72, 690, "Maximum Demand: 417 kVA")
    pdf.drawString(72, 660, "Average Power Factor: 0.89")
    pdf.drawString(72, 630, "PF Penalty: INR 24,000")
    pdf.drawString(72, 600, "Energy Charges: INR 310,000")
    pdf.drawString(72, 570, "Demand Charges: INR 112,000")
    pdf.drawString(72, 540, "Fixed Charges: INR 10,000")
    pdf.drawString(72, 510, "Amount Payable: INR 524,381")

    pdf.save()


def test_pdf_extraction_maps_to_electricity_bill(tmp_path: Path):
    pdf_path = tmp_path / "bill.pdf"
    create_mapper_test_bill(pdf_path)

    document = read_pdf(pdf_path)
    extraction = extract_fields_from_document(document)

    bill = extraction_to_bill(
        extraction,
        bill_id="GP-PDF-001",
        facility_name="Demo Manufacturing Plant",
        country="India",
        billing_period_start=TEST_PERIOD_START,
        billing_period_end=TEST_PERIOD_END,
    )

    assert bill.bill_id == "GP-PDF-001"

    assert bill.facility.name == "Demo Manufacturing Plant"
    assert bill.facility.country == "India"

    assert bill.billing_period.start == TEST_PERIOD_START
    assert bill.billing_period.end == TEST_PERIOD_END

    assert bill.consumption.kwh == 92482.0
    assert bill.demand.maximum_kva == 417.0
    assert bill.power_factor == 0.89
    assert bill.total_cost == 524381.0


def test_pdf_charges_map_to_bill(tmp_path: Path):
    pdf_path = tmp_path / "bill.pdf"
    create_mapper_test_bill(pdf_path)

    document = read_pdf(pdf_path)
    extraction = extract_fields_from_document(document)

    bill = extraction_to_bill(
        extraction,
        bill_id="GP-PDF-002",
        facility_name="Demo Manufacturing Plant",
        country="India",
        billing_period_start=TEST_PERIOD_START,
        billing_period_end=TEST_PERIOD_END,
    )

    assert bill.charges.energy == 310000.0
    assert bill.charges.demand == 112000.0
    assert bill.charges.fixed == 10000.0
    assert bill.charges.power_factor_penalty == 24000.0


def test_mapping_preserves_evidence(tmp_path: Path):
    pdf_path = tmp_path / "bill.pdf"
    create_mapper_test_bill(pdf_path)

    document = read_pdf(pdf_path)
    extraction = extract_fields_from_document(document)

    bill = extraction_to_bill(
        extraction,
        bill_id="GP-PDF-003",
        facility_name="Demo Manufacturing Plant",
        country="India",
        billing_period_start=TEST_PERIOD_START,
        billing_period_end=TEST_PERIOD_END,
    )

    assert len(bill.evidence) > 0

    evidence_fields = {
        evidence.field
        for evidence in bill.evidence
    }

    assert "consumption_kwh" in evidence_fields
    assert "total_cost" in evidence_fields
    assert "power_factor" in evidence_fields


def test_missing_required_field_blocks_mapping(tmp_path: Path):
    pdf_path = tmp_path / "incomplete.pdf"

    pdf = canvas.Canvas(str(pdf_path))

    pdf.drawString(
        72,
        760,
        "Units Consumed: 50,000 kWh",
    )

    pdf.save()

    document = read_pdf(pdf_path)
    extraction = extract_fields_from_document(document)

    with pytest.raises(
        BillMappingError,
        match="total_cost",
    ):
        extraction_to_bill(
            extraction,
            bill_id="GP-INCOMPLETE-001",
            facility_name="Incomplete Facility",
            country="India",
            billing_period_start=TEST_PERIOD_START,
            billing_period_end=TEST_PERIOD_END,
        )


def test_missing_billing_period_blocks_mapping(tmp_path: Path):
    pdf_path = tmp_path / "bill.pdf"
    create_mapper_test_bill(pdf_path)

    document = read_pdf(pdf_path)
    extraction = extract_fields_from_document(document)

    with pytest.raises(
        BillMappingError,
        match="Billing period",
    ):
        extraction_to_bill(
            extraction,
            bill_id="GP-NO-PERIOD-001",
            facility_name="Demo Manufacturing Plant",
        )
