from pydantic import BaseModel

from gridpilot.analytics.kpis import EnergyKPIs, calculate_kpis
from gridpilot.anomalies.engine import EnergyFinding, detect_anomalies
from gridpilot.ledger.engine import EnergyLedger, build_energy_ledger
from gridpilot.models.bill import ElectricityBill
from gridpilot.opportunities.engine import (
    EnergyOpportunity,
    identify_opportunities,
)


class GridPilotAnalysis(BaseModel):
    """
    Complete structured output produced by the GridPilot
    Bill Intelligence Engine.
    """

    bill_id: str
    facility_name: str
    currency: str

    ledger: EnergyLedger
    kpis: EnergyKPIs
    findings: list[EnergyFinding]
    opportunities: list[EnergyOpportunity]

    data_gaps: list[str]
    recommended_next_data: list[str]


def _collect_data_gaps(
    opportunities: list[EnergyOpportunity],
) -> list[str]:
    """
    Collect unique data requirements across all identified opportunities.
    """

    gaps: list[str] = []

    for opportunity in opportunities:
        for requirement in opportunity.required_data:
            if requirement not in gaps:
                gaps.append(requirement)

    return gaps


def _recommend_next_data(
    findings: list[EnergyFinding],
    opportunities: list[EnergyOpportunity],
) -> list[str]:
    """
    Prioritize the next datasets that would materially improve
    GridPilot's analysis.
    """

    recommendations: list[str] = []

    finding_codes = {finding.code for finding in findings}
    opportunity_codes = {opportunity.code for opportunity in opportunities}

    if "HIGH_DEMAND_COST" in finding_codes:
        recommendations.append(
            "15-minute or 30-minute interval meter data"
        )

    if (
        "POOR_POWER_FACTOR" in finding_codes
        or "POWER_FACTOR_PENALTY" in finding_codes
    ):
        recommendations.append(
            "12 months of electricity bills and power-factor history"
        )

    if "SOLAR_SCREENING" in opportunity_codes:
        recommendations.append(
            "12 months of electricity consumption and daytime load data"
        )

    return recommendations


def analyze_bill(bill: ElectricityBill) -> GridPilotAnalysis:
    """
    Run the complete GridPilot v0.1 deterministic bill analysis pipeline.

    Pipeline:

    Electricity Bill
        -> Energy Ledger
        -> KPI Calculation
        -> Anomaly Detection
        -> Opportunity Identification
        -> Data-Gap Analysis
    """

    ledger = build_energy_ledger(bill)

    kpis = calculate_kpis(bill)

    findings = detect_anomalies(
        bill=bill,
        kpis=kpis,
    )

    opportunities = identify_opportunities(
        bill=bill,
        findings=findings,
    )

    data_gaps = _collect_data_gaps(opportunities)

    recommended_next_data = _recommend_next_data(
        findings=findings,
        opportunities=opportunities,
    )

    return GridPilotAnalysis(
        bill_id=bill.bill_id,
        facility_name=bill.facility.name,
        currency=bill.currency,
        ledger=ledger,
        kpis=kpis,
        findings=findings,
        opportunities=opportunities,
        data_gaps=data_gaps,
        recommended_next_data=recommended_next_data,
    )
