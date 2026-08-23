from typing import Literal

from pydantic import BaseModel

from gridpilot.anomalies.engine import EnergyFinding
from gridpilot.models.bill import ElectricityBill


OpportunityStatus = Literal[
    "QUANTIFIED",
    "SCREENING",
    "MORE_DATA_REQUIRED",
]


class EnergyOpportunity(BaseModel):
    """A potential energy optimisation opportunity."""

    code: str
    title: str
    status: OpportunityStatus

    source_findings: list[str]

    estimated_monthly_savings: float | None = None
    estimated_annual_savings: float | None = None
    currency: str | None = None

    confidence: float

    rationale: str

    required_data: list[str] = []
    recommended_action: str


def identify_opportunities(
    bill: ElectricityBill,
    findings: list[EnergyFinding],
) -> list[EnergyOpportunity]:
    """
    Convert deterministic findings into potential interventions.

    The engine must not claim savings that cannot be supported
    by available evidence.
    """

    opportunities: list[EnergyOpportunity] = []

    finding_codes = {finding.code for finding in findings}

    # Opportunity 1: Investigate power-factor correction
    if (
        "POOR_POWER_FACTOR" in finding_codes
        or "POWER_FACTOR_PENALTY" in finding_codes
    ):
        penalty = bill.charges.power_factor_penalty

        if penalty > 0:
            opportunities.append(
                EnergyOpportunity(
                    code="POWER_FACTOR_CORRECTION",
                    title="Investigate power-factor correction",
                    status="SCREENING",
                    source_findings=[
                        code
                        for code in [
                            "POOR_POWER_FACTOR",
                            "POWER_FACTOR_PENALTY",
                        ]
                        if code in finding_codes
                    ],
                    estimated_monthly_savings=penalty,
                    estimated_annual_savings=penalty * 12,
                    currency=bill.currency,
                    confidence=0.75,
                    rationale=(
                        "The bill contains an explicit power-factor penalty. "
                        "If corrective measures eliminate the full penalty and "
                        "similar conditions persist, the current penalty "
                        "provides an initial upper-bound savings screen. "
                        "Engineering validation is required before treating "
                        "this as an achievable savings forecast."
                    ),
                    required_data=[
                        "12 months of electricity bills",
                        "power-factor history",
                        "reactive power measurements",
                        "facility electrical load information",
                    ],
                    recommended_action=(
                        "Review historical power-factor penalties and assess "
                        "whether power-factor correction equipment or changes "
                        "to existing compensation equipment are appropriate."
                    ),
                )
            )

    # Opportunity 2: Peak-demand optimisation
    if "HIGH_DEMAND_COST" in finding_codes:
        opportunities.append(
            EnergyOpportunity(
                code="PEAK_DEMAND_OPTIMISATION",
                title="Investigate peak-demand optimisation",
                status="MORE_DATA_REQUIRED",
                source_findings=["HIGH_DEMAND_COST"],
                currency=bill.currency,
                confidence=0.60,
                rationale=(
                    "Demand charges represent a material portion of the bill. "
                    "Monthly bill data alone cannot determine whether peaks are "
                    "short, persistent, operationally necessary, or flexible."
                ),
                required_data=[
                    "12 months of electricity bills",
                    "15-minute or 30-minute interval meter data",
                    "operating schedule",
                    "major load inventory",
                ],
                recommended_action=(
                    "Collect interval meter data and identify the timing, "
                    "duration, frequency, and operational causes of demand peaks."
                ),
            )
        )

    # Opportunity 3: Battery screening
    if "HIGH_DEMAND_COST" in finding_codes:
        opportunities.append(
            EnergyOpportunity(
                code="BATTERY_SCREENING",
                title="Screen battery storage for demand management",
                status="MORE_DATA_REQUIRED",
                source_findings=["HIGH_DEMAND_COST"],
                currency=bill.currency,
                confidence=0.35,
                rationale=(
                    "Material demand charges can make battery storage worth "
                    "investigating, but a monthly bill is insufficient for "
                    "battery sizing or financial modelling."
                ),
                required_data=[
                    "15-minute or finer interval meter data",
                    "applicable tariff",
                    "battery capital-cost assumptions",
                    "battery efficiency",
                    "battery degradation assumptions",
                    "site operating constraints",
                ],
                recommended_action=(
                    "Do not recommend a battery yet. First reconstruct the "
                    "facility load profile and model peak-shaving scenarios."
                ),
            )
        )

    # Opportunity 4: Solar screening
    if bill.consumption.kwh > 0:
        opportunities.append(
            EnergyOpportunity(
                code="SOLAR_SCREENING",
                title="Evaluate on-site solar economics",
                status="MORE_DATA_REQUIRED",
                source_findings=[],
                currency=bill.currency,
                confidence=0.30,
                rationale=(
                    "The facility has measurable electricity consumption, but "
                    "a single monthly bill is not sufficient to determine an "
                    "appropriate solar system size or financial return."
                ),
                required_data=[
                    "12 months of electricity consumption",
                    "daytime load profile",
                    "facility location",
                    "available roof or land area",
                    "solar generation assumptions",
                    "applicable import/export tariff",
                    "project cost assumptions",
                ],
                recommended_action=(
                    "Collect annual consumption and daytime load information "
                    "before modelling solar capacity and economics."
                ),
            )
        )

    return opportunities
