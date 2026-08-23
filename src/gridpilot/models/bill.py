from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Facility(BaseModel):
    """Basic information about the facility being analysed."""

    name: str
    country: str
    state: str | None = None
    facility_type: str | None = None


class BillingPeriod(BaseModel):
    """Start and end dates covered by an electricity bill."""

    start: date
    end: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end < self.start:
            raise ValueError("Billing period end date cannot be before start date.")
        return self


class Consumption(BaseModel):
    """Electricity consumption recorded during the billing period."""

    kwh: float = Field(ge=0)


class Demand(BaseModel):
    """Maximum electrical demand recorded during the billing period."""

    maximum_kw: float | None = Field(default=None, ge=0)
    maximum_kva: float | None = Field(default=None, ge=0)


class ChargeBreakdown(BaseModel):
    """Financial components of an electricity bill."""

    energy: float = Field(default=0, ge=0)
    demand: float = Field(default=0, ge=0)
    fixed: float = Field(default=0, ge=0)
    power_factor_penalty: float = Field(default=0, ge=0)
    reactive_energy: float = Field(default=0, ge=0)
    taxes: float = Field(default=0, ge=0)
    other: float = Field(default=0, ge=0)

    @property
    def subtotal(self) -> float:
        return (
            self.energy
            + self.demand
            + self.fixed
            + self.power_factor_penalty
            + self.reactive_energy
            + self.taxes
            + self.other
        )


class Evidence(BaseModel):
    """Provenance for a value extracted from an external source."""

    field: str
    value: str | float | int
    unit: str | None = None
    source: str
    page: int | None = Field(default=None, ge=1)
    source_text: str | None = None
    confidence: float = Field(default=1.0, ge=0, le=1)


class ElectricityBill(BaseModel):
    """Canonical GridPilot representation of an electricity bill."""

    bill_id: str
    facility: Facility
    billing_period: BillingPeriod

    consumption: Consumption
    demand: Demand = Field(default_factory=Demand)

    power_factor: float | None = Field(default=None, ge=0, le=1)

    charges: ChargeBreakdown

    total_cost: float = Field(ge=0)
    currency: Literal["INR", "USD", "EUR", "GBP"] = "INR"

    evidence: list[Evidence] = Field(default_factory=list)

    @property
    def effective_cost_per_kwh(self) -> float | None:
        if self.consumption.kwh == 0:
            return None

        return self.total_cost / self.consumption.kwh

    @property
    def charge_reconciliation_difference(self) -> float:
        """
        Difference between the stated bill total and the sum of
        individual charge components.
        """

        return self.total_cost - self.charges.subtotal
