from pydantic import BaseModel

from gridpilot.models.bill import ElectricityBill


class EnergyLedger(BaseModel):
    """Financial reconstruction of an electricity bill."""

    energy_charges: float
    demand_charges: float
    fixed_charges: float
    power_factor_penalty: float
    reactive_energy_charges: float
    taxes: float
    other_charges: float

    calculated_total: float
    stated_total: float
    reconciliation_difference: float

    effective_cost_per_kwh: float | None

    energy_cost_percentage: float
    demand_cost_percentage: float
    penalty_cost_percentage: float
    fixed_cost_percentage: float


def _percentage(value: float, total: float) -> float:
    """Return value as a percentage of total."""

    if total == 0:
        return 0.0

    return (value / total) * 100


def build_energy_ledger(bill: ElectricityBill) -> EnergyLedger:
    """
    Reconstruct the financial composition of an electricity bill.

    The ledger is deterministic. It does not use an LLM or any
    probabilistic reasoning.
    """

    charges = bill.charges
    calculated_total = charges.subtotal

    return EnergyLedger(
        energy_charges=charges.energy,
        demand_charges=charges.demand,
        fixed_charges=charges.fixed,
        power_factor_penalty=charges.power_factor_penalty,
        reactive_energy_charges=charges.reactive_energy,
        taxes=charges.taxes,
        other_charges=charges.other,
        calculated_total=calculated_total,
        stated_total=bill.total_cost,
        reconciliation_difference=bill.charge_reconciliation_difference,
        effective_cost_per_kwh=bill.effective_cost_per_kwh,
        energy_cost_percentage=_percentage(charges.energy, bill.total_cost),
        demand_cost_percentage=_percentage(charges.demand, bill.total_cost),
        penalty_cost_percentage=_percentage(
            charges.power_factor_penalty,
            bill.total_cost,
        ),
        fixed_cost_percentage=_percentage(charges.fixed, bill.total_cost),
    )
