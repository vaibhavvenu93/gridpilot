from gridpilot.ingestion.normalizer import (
    canonical_field_name,
    clean_label,
    normalize_field,
    normalize_numeric_value,
)


def test_clean_label():
    assert clean_label(" Maximum_Demand-KVA ") == "maximum demand kva"
    assert clean_label("PF / Penalty") == "pf penalty"


def test_consumption_alias():
    assert canonical_field_name("Units Consumed") == "consumption_kwh"


def test_maximum_demand_kw_alias():
    assert canonical_field_name("MD KW") == "maximum_demand_kw"


def test_maximum_demand_kva_alias():
    assert canonical_field_name("MD KVA") == "maximum_demand_kva"


def test_power_factor_alias():
    assert canonical_field_name("Average Power Factor") == "power_factor"


def test_power_factor_penalty_alias():
    assert canonical_field_name("PF Penalty") == "power_factor_penalty"


def test_total_bill_alias():
    assert canonical_field_name("Amount Payable") == "total_cost"


def test_numeric_consumption_normalization():
    assert normalize_numeric_value("92,482") == 92482.0


def test_currency_normalization():
    assert normalize_numeric_value("₹24,000.00") == 24000.0


def test_demand_unit_normalization():
    assert normalize_numeric_value("417 kVA") == 417.0


def test_power_factor_normalization():
    assert normalize_numeric_value("0.89") == 0.89


def test_known_field_is_normalized():
    field = normalize_field(
        source_label="MD KVA",
        raw_value="417 kVA",
        unit="kVA",
    )

    assert field.field_name == "maximum_demand_kva"
    assert field.normalized_value == 417.0
    assert field.status == "NORMALIZED"


def test_unknown_field_requires_review():
    field = normalize_field(
        source_label="Mysterious Adjustment",
        raw_value="₹8,500",
    )

    assert field.field_name == "Mysterious Adjustment"
    assert field.normalized_value is None
    assert field.status == "REVIEW_REQUIRED"


def test_unreadable_value_requires_review():
    field = normalize_field(
        source_label="Power Factor",
        raw_value="not readable",
    )

    assert field.field_name == "power_factor"
    assert field.normalized_value is None
    assert field.status == "REVIEW_REQUIRED"
