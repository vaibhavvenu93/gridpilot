from pydantic import BaseModel

from gridpilot.models.bill import ElectricityBill


class EnergyKPIs(BaseModel):
    """Core energy and financial KPIs calculated from an electricity bill."""

    consumption_kwh: float

    maximum_demand_kw: float | None
    maximum_demand_kva: float | None

    power_factor: float | None

    total_cost: float
    effective_cost_per_kwh: float | None

    energy_cost_percentage: float
    demand_cost_percentage: float
    penalty_cost_percentage: float
    fixed_cost_percentage: float

    apparent_to_real_demand_ratio: float | None


def _percentage(value: float, total: float) -> float:
    """Calculate a percentage safely."""

    if total == 0:
        return 0.0

    return (value / total) * 100


def _demand_ratio(
    maximum_kw: float | None,
    maximum_kva: float | None,
) -> float | None:
    """
    Compare apparent demand (kVA) with real demand (kW).

    A larger gap may indicate poorer power factor, although
    interpretation requires appropriate facility and tariff context.
    """

    if maximum_kw is None or maximum_kva is None:
        return None

    if maximum_kw == 0:
        return None

    return maximum_kva / maximum_kw


def calculate_kpis(bill: ElectricityBill) -> EnergyKPIs:
    """
    Calculate deterministic energy and financial KPIs.

    No LLM reasoning is used in this calculation.
    """

    return EnergyKPIs(
        consumption_kwh=bill.consumption.kwh,
        maximum_demand_kw=bill.demand.maximum_kw,
        maximum_demand_kva=bill.demand.maximum_kva,
        power_factor=bill.power_factor,
        total_cost=bill.total_cost,
        effective_cost_per_kwh=bill.effective_cost_per_kwh,
        energy_cost_percentage=_percentage(
            bill.charges.energy,
            bill.total_cost,
        ),
        demand_cost_percentage=_percentage(
            bill.charges.demand,
            bill.total_cost,
        ),
        penalty_cost_percentage=_percentage(
            bill.charges.power_factor_penalty,
            bill.total_cost,
        ),
        fixed_cost_percentage=_percentage(
            bill.charges.fixed,
            bill.total_cost,
        ),
        apparent_to_real_demand_ratio=_demand_ratio(
            bill.demand.maximum_kw,
            bill.demand.maximum_kva,
        ),
    )
