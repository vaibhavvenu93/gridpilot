from datetime import date

from gridpilot.ingestion.models import BillExtraction
from gridpilot.models.bill import (
    BillingPeriod,
    ChargeBreakdown,
    Consumption,
    Demand,
    ElectricityBill,
    Evidence,
    Facility,
)


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


def _build_evidence(
    extraction: BillExtraction,
) -> list[Evidence]:
    """
    Preserve extraction provenance when converting into the
    canonical GridPilot bill model.
    """

    evidence: list[Evidence] = []

    for field in extraction.fields:
        if field.normalized_value is None:
            continue

        source_evidence = field.evidence

        evidence.append(
            Evidence(
                field=field.field_name,
                value=field.normalized_value,
                unit=field.unit,
                source=extraction.source_file,
                page=(
                    source_evidence.page
                    if source_evidence is not None
                    else None
                ),
                source_text=(
                    source_evidence.raw_text
                    if source_evidence is not None
                    else None
                ),
                confidence=(
                    source_evidence.confidence
                    if source_evidence is not None
                    else 1.0
                ),
            )
        )

    metadata_evidence = extraction.metadata.billing_period_evidence

    if (
        metadata_evidence is not None
        and extraction.metadata.billing_period_start is not None
        and extraction.metadata.billing_period_end is not None
    ):
        evidence.append(
            Evidence(
                field="billing_period",
                value=(
                    f"{extraction.metadata.billing_period_start.isoformat()}"
                    f" to "
                    f"{extraction.metadata.billing_period_end.isoformat()}"
                ),
                source=extraction.source_file,
                page=metadata_evidence.page,
                source_text=metadata_evidence.raw_text,
                confidence=metadata_evidence.confidence,
            )
        )

    return evidence


def extraction_to_bill(
    extraction: BillExtraction,
    *,
    bill_id: str,
    facility_name: str,
    country: str = "India",
    billing_period_start: date | None = None,
    billing_period_end: date | None = None,
    currency: str = "INR",
) -> ElectricityBill:
    """
    Convert evidence-backed extracted fields into GridPilot's
    canonical ElectricityBill model.

    Billing-period dates are taken from extraction metadata unless
    explicitly supplied as overrides.

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

    resolved_start = (
        billing_period_start
        if billing_period_start is not None
        else extraction.metadata.billing_period_start
    )

    resolved_end = (
        billing_period_end
        if billing_period_end is not None
        else extraction.metadata.billing_period_end
    )

    if resolved_start is None or resolved_end is None:
        raise BillMappingError(
            "Billing period start and end dates are required "
            "to construct ElectricityBill."
        )

    charges = ChargeBreakdown(
        energy=values.get("energy_charge", 0.0),
        demand=values.get("demand_charge", 0.0),
        fixed=values.get("fixed_charge", 0.0),
        power_factor_penalty=values.get(
            "power_factor_penalty",
            0.0,
        ),
        reactive_energy=values.get(
            "reactive_energy_charge",
            0.0,
        ),
        taxes=values.get("taxes", 0.0),
        other=values.get("other_charge", 0.0),
    )

    facility = Facility(
        name=facility_name,
        country=country,
    )

    billing_period = BillingPeriod(
        start=resolved_start,
        end=resolved_end,
    )

    consumption = Consumption(
        kwh=values["consumption_kwh"],
    )

    demand = Demand(
        maximum_kw=values.get("maximum_demand_kw"),
        maximum_kva=values.get("maximum_demand_kva"),
    )

    return ElectricityBill(
        bill_id=bill_id,
        facility=facility,
        billing_period=billing_period,
        consumption=consumption,
        demand=demand,
        power_factor=values.get("power_factor"),
        charges=charges,
        total_cost=values["total_cost"],
        currency=currency,
        evidence=_build_evidence(extraction),
    )
