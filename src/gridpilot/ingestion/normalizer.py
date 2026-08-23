import re
from typing import Any

from gridpilot.ingestion.models import ExtractedField


FIELD_ALIASES: dict[str, set[str]] = {
    "consumption_kwh": {
        "energy consumption",
        "electricity consumption",
        "units consumed",
        "units",
        "kwh consumption",
        "total kwh",
        "energy kwh",
    },
    "maximum_demand_kw": {
        "maximum demand kw",
        "max demand kw",
        "md kw",
        "billing demand kw",
        "recorded demand kw",
    },
    "maximum_demand_kva": {
        "maximum demand kva",
        "max demand kva",
        "md kva",
        "billing demand kva",
        "recorded demand kva",
    },
    "power_factor": {
        "power factor",
        "average power factor",
        "avg power factor",
        "pf",
    },
    "energy_charge": {
        "energy charge",
        "energy charges",
        "consumption charge",
        "consumption charges",
    },
    "demand_charge": {
        "demand charge",
        "demand charges",
        "maximum demand charge",
        "maximum demand charges",
        "md charge",
        "md charges",
    },
    "power_factor_penalty": {
        "power factor penalty",
        "pf penalty",
        "power factor surcharge",
        "pf surcharge",
    },
    "fixed_charge": {
        "fixed charge",
        "fixed charges",
        "customer charge",
        "customer charges",
    },
    "taxes_and_other_charges": {
        "tax",
        "taxes",
        "electricity duty",
        "other charges",
        "taxes and other charges",
    },
    "total_cost": {
        "total amount",
        "total bill amount",
        "bill amount",
        "amount payable",
        "net amount payable",
        "total electricity cost",
    },
}


def clean_label(label: str) -> str:
    """
    Normalize a source label so utility-specific formatting
    does not affect alias matching.
    """

    value = label.strip().lower()

    value = re.sub(
        r"[_:/\-]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def canonical_field_name(
    source_label: str,
) -> str | None:
    """
    Map a utility bill label to a canonical GridPilot field.
    """

    cleaned = clean_label(source_label)

    for canonical_name, aliases in FIELD_ALIASES.items():
        if cleaned in aliases:
            return canonical_name

    return None


def normalize_numeric_value(
    value: Any,
) -> float | None:
    """
    Convert common bill representations into a numeric value.

    Examples:
        "92,482" -> 92482.0
        "₹24,000.00" -> 24000.0
        "0.89" -> 0.89
        "371 kW" -> 371.0
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if not text:
        return None

    text = text.replace(",", "")

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        text,
    )

    if match is None:
        return None

    return float(match.group())


def normalize_field(
    source_label: str,
    raw_value: Any,
    unit: str | None = None,
) -> ExtractedField:
    """
    Normalize one extracted utility-bill field.
    """

    canonical_name = canonical_field_name(
        source_label
    )

    if canonical_name is None:
        return ExtractedField(
            field_name=source_label,
            raw_value=raw_value,
            unit=unit,
            status="REVIEW_REQUIRED",
        )

    normalized_value = normalize_numeric_value(
        raw_value
    )

    if normalized_value is None:
        return ExtractedField(
            field_name=canonical_name,
            raw_value=raw_value,
            unit=unit,
            status="REVIEW_REQUIRED",
        )

    return ExtractedField(
        field_name=canonical_name,
        raw_value=raw_value,
        normalized_value=normalized_value,
        unit=unit,
        status="NORMALIZED",
    )
