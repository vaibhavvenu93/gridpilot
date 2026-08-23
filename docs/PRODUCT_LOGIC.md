# GridPilot Product Logic

## 1. Core Product Question

GridPilot exists to answer:

> Where is this facility spending money on electricity, what appears inefficient or unusual, what can be changed, and what is the potential financial value of changing it?

The system progresses through six logical stages:

**Observe → Structure → Calculate → Diagnose → Model → Recommend**

---

## 2. Observe

GridPilot receives evidence about a facility.

v0.1 inputs may include:

- electricity bill
- facility metadata
- tariff information

Future inputs include:

- interval meter data
- asset telemetry
- weather
- occupancy
- operating schedules
- market prices

Every important input should retain provenance.

---

## 3. Structure

Raw information is converted into the GridPilot canonical data model.

Example:

```json
{
  "facility": {
    "country": "IN",
    "state": "Karnataka",
    "type": "manufacturing"
  },
  "billing_period": {
    "start": "2026-07-01",
    "end": "2026-07-31"
  },
  "consumption_kwh": 92482,
  "maximum_demand_kva": 417,
  "power_factor": 0.89,
  "total_cost": 524381,
  "currency": "INR"
}
```

No analysis should depend directly on the layout of a particular utility bill.

---

## 4. Calculate

GridPilot calculates objective energy and financial metrics.

Examples:

```text
Effective energy cost
= total bill / electricity consumption

Demand cost %
= demand charges / total bill

Penalty cost %
= penalties / total bill
```

All deterministic calculations should be reproducible.

---

## 5. Diagnose

GridPilot evaluates calculated metrics against:

- tariff rules
- historical performance
- engineering thresholds
- facility characteristics
- comparable operating patterns
- explicit business rules

Example:

```text
Observed power factor: 0.82
Preferred threshold: >= 0.95

Finding:
Poor power factor

Severity:
High
```

GridPilot should distinguish:

**fact**

from:

**inference**

from:

**recommendation**

---

## 6. Model Opportunities

A finding does not automatically mean money can be saved.

GridPilot therefore creates an intervention hypothesis.

Example:

```text
Finding:
High demand-charge contribution

Hypothesis:
Reducing maximum demand may lower electricity expenditure.

Required information:
- tariff demand rate
- interval consumption
- timing of demand peaks

Status:
Additional data required
```

Where sufficient information exists:

```text
Baseline annual demand cost
            |
            v
Proposed demand reduction
            |
            v
Recalculated tariff cost
            |
            v
Annual savings
            |
            v
Implementation cost
            |
            v
Payback / IRR
```

---

## 7. Rank Opportunities

Opportunities should eventually be ranked using more than estimated savings.

Potential scoring dimensions:

```text
Financial impact
Confidence
Implementation difficulty
Capital requirement
Operational disruption
Data quality
Payback period
Strategic value
```

An opportunity with slightly lower savings but near-zero implementation cost may be preferable to a large capital project.

---

## 8. Recommend

The final recommendation combines:

```text
Evidence
+
Deterministic calculations
+
Opportunity models
+
Confidence
+
Constraints
```

AI may help explain and prioritize the result.

AI should not invent missing measurements or financial assumptions.

---

## 9. Ask for More Data

An important GridPilot behaviour is:

**I don't have enough information yet.**

Example:

```text
Potential battery opportunity detected.

Confidence: LOW

Why:
Monthly bill data shows high demand charges, but battery sizing requires interval consumption data.

Next data requested:
12 months of 15-minute meter readings.
```

Requesting the next highest-value dataset is itself part of the product.

---

## 10. Progressive Intelligence

GridPilot becomes more useful as additional data becomes available.

```text
LEVEL 1

One electricity bill
→ Basic financial intelligence

LEVEL 2

12 months of bills
→ Trends and seasonality

LEVEL 3

Interval meter data
→ Load intelligence

LEVEL 4

Asset data
→ Asset modelling

LEVEL 5

Real-time telemetry
→ Operational optimisation

LEVEL 6

Controllable assets
→ Automated optimisation

LEVEL 7

Many facilities
→ Aggregated flexibility

LEVEL 8

Market connectivity
→ VPP
```

---

## 11. v0.1 Output Contract

The first working GridPilot engine should return something conceptually similar to:

```json
{
  "facility": {},
  "bill_summary": {},
  "energy_ledger": {},
  "kpis": {},
  "findings": [],
  "opportunities": [],
  "data_gaps": [],
  "recommended_next_data": [],
  "confidence": {}
}
```

Future interfaces — dashboards, APIs, agents and reports — should consume this structured intelligence rather than independently analysing raw bills.

---

## 12. Product Feedback Loop

The long-term system should learn from outcomes.

```text
Recommendation
      |
      v
Action Taken
      |
      v
Observed Result
      |
      v
Expected vs Actual
      |
      v
Model Improvement
```

This allows GridPilot to move from theoretical savings estimates toward measured optimisation intelligence.

---

## 13. Long-Term Product Logic

The ultimate GridPilot loop is:

```text
OBSERVE
   |
   v
UNDERSTAND
   |
   v
PREDICT
   |
   v
OPTIMISE
   |
   v
ACT
   |
   v
MEASURE
   |
   +------> repeat
```

At a single facility this becomes an Energy Optimisation System.

Across thousands of distributed flexible assets it becomes the foundation for a Virtual Power Plant.
