from gridpilot.ingestion.models import BillExtraction
from gridpilot.models.bill import BillCharges, ElectricityBill


class BillMappingError(ValueError):
    """
    Raised when extracted bill data cannot safely be mapped
    into GridPilot's canonical ElectricityBill model.
    """


def _normalized_values(
    extraction: BillExtraction,
) -> dict[str, float]:
    """
    Return successfully normalized fields as a lookup table.
    """

    values: dict[str, float] = {}

    for field in extraction.fields:
        if (
            field.status == "NORMALIZED"
            and field.normalized_value is not None
        ):
            values[field.field_name] = field.normalized_value

    return values


def extraction_to_bill(
    extraction: BillExtraction,
    *,
    bill_id: str,
    facility_name: str,
) -> ElectricityBill:
    """
    Convert evidence-backed extracted fields into GridPilot's
    canonical ElectricityBill model.

    Required financial and consumption fields must exist before
    analysis is allowed to continue.
    """

    values = _normalized_values(extraction)

    required = {
        "consumption_kwh",
        "total_cost",
    }

    missing = sorted(
        field_name
        for field_name in required
        if field_name not in values
    )

    if missing:
        raise BillMappingError(
            "Cannot construct ElectricityBill. "
            "Missing normalized fields: "
            + ", ".join(missing)
        )

    charges = BillCharges(
        energy_charge=values.get(
            "energy_charge",
            0.0,
        ),
        demand_charge=values.get(
            "demand_charge",
            0.0,
        ),
        fixed_charge=values.get(
            "fixed_charge",
            0.0,
        ),
        power_factor_penalty=values.get(
            "power_factor_penalty",
            0.0,
        ),
    )

    return ElectricityBill(
        bill_id=bill_id,
        facility_name=facility_name,
        consumption_kwh=values["consumption_kwh"],
        maximum_demand_kw=values.get(
            "maximum_demand_kw"
        ),
        maximum_demand_kva=values.get(
            "maximum_demand_kva"
        ),
        power_factor=values.get(
            "power_factor"
        ),
        charges=charges,
        total_cost=values["total_cost"],
    )
