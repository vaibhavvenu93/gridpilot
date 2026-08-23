import json
from pathlib import Path

import pytest

from gridpilot.analysis import analyze_bill
from gridpilot.models.bill import ElectricityBill


SAMPLE_BILL = (
    Path(__file__).parent.parent
    / "data"
    / "sample"
    / "manufacturing_bill.json"
)


def load_sample_bill() -> ElectricityBill:
    """Load and validate the synthetic manufacturing electricity bill."""

    with SAMPLE_BILL.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return ElectricityBill.model_validate(data)


def test_sample_bill_loads():
    bill = load_sample_bill()

    assert bill.bill_id == "GP-DEMO-001"
    assert bill.facility.name == "GridPilot Demo Manufacturing Plant"
    assert bill.consumption.kwh == 92482
    assert bill.demand.maximum_kw == 371
    assert bill.demand.maximum_kva == 417
    assert bill.power_factor == 0.89
    assert bill.total_cost == 524381


def test_bill_reconciles():
    bill = load_sample_bill()

    assert bill.charges.subtotal == 524381
    assert bill.charge_reconciliation_difference == 0


def test_effective_cost_per_kwh():
    bill = load_sample_bill()

    assert bill.effective_cost_per_kwh == pytest.approx(
        524381 / 92482,
        rel=1e-6,
    )


def test_complete_analysis_pipeline():
    bill = load_sample_bill()

    analysis = analyze_bill(bill)

    assert analysis.bill_id == "GP-DEMO-001"
    assert analysis.facility_name == "GridPilot Demo Manufacturing Plant"

    assert analysis.ledger.calculated_total == 524381
    assert analysis.ledger.reconciliation_difference == 0

    assert analysis.kpis.effective_cost_per_kwh == pytest.approx(
        5.67,
        rel=0.01,
    )


def test_expected_findings_are_detected():
    bill = load_sample_bill()

    analysis = analyze_bill(bill)

    finding_codes = {
        finding.code
        for finding in analysis.findings
    }

    assert "POOR_POWER_FACTOR" in finding_codes
    assert "POWER_FACTOR_PENALTY" in finding_codes
    assert "HIGH_DEMAND_COST" in finding_codes


def test_expected_opportunities_are_identified():
    bill = load_sample_bill()

    analysis = analyze_bill(bill)

    opportunity_codes = {
        opportunity.code
        for opportunity in analysis.opportunities
    }

    assert "POWER_FACTOR_CORRECTION" in opportunity_codes
    assert "PEAK_DEMAND_OPTIMISATION" in opportunity_codes
    assert "BATTERY_SCREENING" in opportunity_codes
    assert "SOLAR_SCREENING" in opportunity_codes


def test_power_factor_savings_are_screening_only():
    bill = load_sample_bill()

    analysis = analyze_bill(bill)

    opportunity = next(
        opportunity
        for opportunity in analysis.opportunities
        if opportunity.code == "POWER_FACTOR_CORRECTION"
    )

    assert opportunity.status == "SCREENING"
    assert opportunity.estimated_monthly_savings == 24000
    assert opportunity.estimated_annual_savings == 288000
    assert opportunity.confidence == 0.75


def test_battery_is_not_prematurely_recommended():
    bill = load_sample_bill()

    analysis = analyze_bill(bill)

    opportunity = next(
        opportunity
        for opportunity in analysis.opportunities
        if opportunity.code == "BATTERY_SCREENING"
    )

    assert opportunity.status == "MORE_DATA_REQUIRED"
    assert opportunity.estimated_annual_savings is None
    assert opportunity.confidence == 0.35

    assert (
        "15-minute or finer interval meter data"
        in opportunity.required_data
    )


def test_gridpilot_requests_interval_data():
    bill = load_sample_bill()

    analysis = analyze_bill(bill)

    assert (
        "15-minute or 30-minute interval meter data"
        in analysis.recommended_next_data
    )
