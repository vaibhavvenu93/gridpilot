from typing import Literal

from pydantic import BaseModel

from gridpilot.analytics.kpis import EnergyKPIs
from gridpilot.models.bill import ElectricityBill


Severity = Literal["LOW", "MEDIUM", "HIGH"]


class EnergyFinding(BaseModel):
    """A deterministic finding produced by the GridPilot anomaly engine."""

    code: str
    title: str
    severity: Severity

    observed_value: float | None = None
    expected_value: float | None = None
    unit: str | None = None

    estimated_cost: float | None = None

    explanation: str
    evidence_fields: list[str]


def detect_anomalies(
    bill: ElectricityBill,
    kpis: EnergyKPIs,
) -> list[EnergyFinding]:
    """
    Detect energy and billing anomalies using explicit rules.

    These rules are intentionally deterministic and transparent.
    They should become configurable as GridPilot develops.
    """

    findings: list[EnergyFinding] = []

    # Rule 1: Poor power factor
    if bill.power_factor is not None and bill.power_factor < 0.95:
        severity: Severity

        if bill.power_factor < 0.85:
            severity = "HIGH"
        elif bill.power_factor < 0.90:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        findings.append(
            EnergyFinding(
                code="POOR_POWER_FACTOR",
                title="Power factor below target",
                severity=severity,
                observed_value=bill.power_factor,
                expected_value=0.95,
                estimated_cost=bill.charges.power_factor_penalty,
                explanation=(
                    "Recorded power factor is below the initial GridPilot "
                    "screening threshold of 0.95. This may increase apparent "
                    "power demand or create tariff penalties depending on the "
                    "utility tariff."
                ),
                evidence_fields=[
                    "power_factor",
                    "charges.power_factor_penalty",
                ],
            )
        )

    # Rule 2: Explicit power-factor penalty
    if bill.charges.power_factor_penalty > 0:
        findings.append(
            EnergyFinding(
                code="POWER_FACTOR_PENALTY",
                title="Explicit power-factor penalty detected",
                severity="HIGH",
                observed_value=bill.charges.power_factor_penalty,
                unit=bill.currency,
                estimated_cost=bill.charges.power_factor_penalty,
                explanation=(
                    "The electricity bill contains an explicit power-factor "
                    "penalty. This represents a directly observable cost and "
                    "should be investigated."
                ),
                evidence_fields=[
                    "charges.power_factor_penalty",
                ],
            )
        )

    # Rule 3: High demand-charge contribution
    if kpis.demand_cost_percentage >= 20:
        findings.append(
            EnergyFinding(
                code="HIGH_DEMAND_COST",
                title="Demand charges represent a material share of the bill",
                severity="MEDIUM",
                observed_value=kpis.demand_cost_percentage,
                expected_value=20,
                unit="percent",
                estimated_cost=bill.charges.demand,
                explanation=(
                    "Demand charges represent at least 20% of the total bill. "
                    "This does not prove that demand can be reduced, but it "
                    "indicates that interval meter data could reveal valuable "
                    "peak-demand optimisation opportunities."
                ),
                evidence_fields=[
                    "charges.demand",
                    "total_cost",
                    "demand.maximum_kw",
                    "demand.maximum_kva",
                ],
            )
        )

    # Rule 4: Bill reconciliation mismatch
    reconciliation_difference = bill.charge_reconciliation_difference

    if abs(reconciliation_difference) > 1:
        findings.append(
            EnergyFinding(
                code="BILL_RECONCILIATION_MISMATCH",
                title="Bill components do not reconcile with stated total",
                severity="HIGH",
                observed_value=reconciliation_difference,
                expected_value=0,
                unit=bill.currency,
                explanation=(
                    "The sum of the structured charge components differs from "
                    "the stated bill total. The bill extraction or source "
                    "document should be reviewed before downstream analysis."
                ),
                evidence_fields=[
                    "charges",
                    "total_cost",
                ],
            )
        )

    return findings
