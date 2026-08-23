from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from gridpilot.ingestion.pdf import read_pdf


def create_test_bill(
    path: Path,
) -> None:
    """
    Create a small synthetic digital electricity bill
    for testing GridPilot's PDF ingestion layer.
    """

    pdf = canvas.Canvas(str(path))

    pdf.drawString(
        72,
        760,
        "GRIDPILOT TEST ELECTRICITY BILL",
    )

    pdf.drawString(
        72,
        730,
        "Facility: Demo Manufacturing Plant",
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
        "PF Penalty: INR 24,000",
    )

    pdf.drawString(
        72,
        580,
        "Amount Payable: INR 524,381",
    )

    pdf.showPage()

    pdf.drawString(
        72,
        760,
        "GRIDPILOT TEST BILL - PAGE 2",
    )

    pdf.drawString(
        72,
        730,
        "Demand Charges: INR 112,000",
    )

    pdf.save()


def test_read_pdf_extracts_pages(
    tmp_path: Path,
):
    pdf_path = tmp_path / "test_bill.pdf"

    create_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    assert document.source_file == "test_bill.pdf"
    assert document.page_count == 2
    assert len(document.pages) == 2


def test_pdf_preserves_page_numbers(
    tmp_path: Path,
):
    pdf_path = tmp_path / "test_bill.pdf"

    create_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    assert document.pages[0].page_number == 1
    assert document.pages[1].page_number == 2


def test_pdf_extracts_bill_text(
    tmp_path: Path,
):
    pdf_path = tmp_path / "test_bill.pdf"

    create_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    assert "Units Consumed: 92,482 kWh" in document.pages[0].text
    assert "Average Power Factor: 0.89" in document.pages[0].text
    assert "Demand Charges: INR 112,000" in document.pages[1].text


def test_full_text_combines_pages(
    tmp_path: Path,
):
    pdf_path = tmp_path / "test_bill.pdf"

    create_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    assert "Amount Payable: INR 524,381" in document.full_text
    assert "Demand Charges: INR 112,000" in document.full_text


def test_character_count_is_recorded(
    tmp_path: Path,
):
    pdf_path = tmp_path / "test_bill.pdf"

    create_test_bill(pdf_path)

    document = read_pdf(pdf_path)

    assert document.pages[0].character_count > 0
    assert document.pages[1].character_count > 0


def test_non_pdf_is_rejected(
    tmp_path: Path,
):
    file_path = tmp_path / "bill.txt"

    file_path.write_text(
        "Not a PDF",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Expected a PDF file",
    ):
        read_pdf(file_path)


def test_missing_pdf_is_rejected(
    tmp_path: Path,
):
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(
        FileNotFoundError,
        match="PDF does not exist",
    ):
        read_pdf(missing_path)
