# GridPilot System Architecture

## 1. Architecture Objective

GridPilot is designed as a modular energy intelligence platform that can evolve from electricity-bill analysis into asset optimisation, flexibility aggregation, and eventually Virtual Power Plant infrastructure.

The architecture must therefore support two very different requirements:

1. Deliver useful financial intelligence from simple energy data today.
2. Avoid architectural decisions that prevent future integration with meters, distributed energy resources, control systems, and electricity markets.

The system follows an evidence-first principle:

**Source → Structured Data → Deterministic Calculation → Finding → Opportunity → Recommendation**

AI reasoning is layered on top of deterministic energy calculations rather than replacing them.

---

## 2. v0.1 Architecture

GridPilot v0.1 focuses on electricity bill intelligence.

```text
Electricity Bill
       |
       v
+-------------------+
| Document Ingestion|
+---------+---------+
          |
          v
+-------------------+
| Field Extraction  |
+---------+---------+
          |
          v
+-------------------+
| Normalization     |
+---------+---------+
          |
          v
+-------------------+
| Energy Data Model |
+---------+---------+
          |
          +-------------------+
          |                   |
          v                   v
+----------------+    +----------------+
| Tariff Engine  |    | Energy Ledger  |
+-------+--------+    +-------+--------+
        |                     |
        +----------+----------+
                   |
                   v
          +----------------+
          | Analytics      |
          | Engine         |
          +-------+--------+
                  |
                  v
          +----------------+
          | Anomaly Engine |
          +-------+--------+
                  |
                  v
          +--------------------+
          | Opportunity Engine |
          +---------+----------+
                    |
                    v
          +--------------------+
          | Agentic Analyst    |
          +---------+----------+
                    |
                    v
          +--------------------+
          | Intelligence Report|
          +--------------------+

          ---

## 3. Core Architectural Layers

### 3.1 Ingestion Layer

Responsible for receiving external data.

Initial inputs:

- structured JSON
- electricity bills
- tariff information
- facility metadata

Future inputs:

- PDF bills
- CSV exports
- smart meter data
- utility APIs
- building-management systems
- solar inverter APIs
- battery-management systems
- EV charging systems
- IoT devices

The ingestion layer does not make energy recommendations.

Its job is to transform external information into data GridPilot can understand.

### 3.2 Normalization Layer

Utilities, countries and energy providers represent information differently.

GridPilot therefore requires a canonical internal representation.

For example:

```text
Utility Bill A: "Maximum Demand"
Utility Bill B: "Recorded MD"
Utility Bill C: "Billing Demand"

These may map into a standardized GridPilot field such as:

```text
maximum_demand_kw
```

Normalization isolates downstream analytics from document-specific formats.
Energy Data Model

The Energy Data Model represents the state of a facility.

Core entities will eventually include:

Organisation
    |
Facility
    |
    +--- Electricity Account
    |
    +--- Tariff
    |
    +--- Meter
    |
    +--- Energy Bill
    |
    +--- Energy Asset

    Future Energy Assets may include:

Solar PV
Battery
HVAC
EV Charger
Generator
Refrigeration
Industrial Load
Thermal Storage

5. Energy Ledger

The Energy Ledger reconstructs where electricity expenditure went.

Example:

Energy Charges           310,000
Demand Charges           112,000
Power Factor Penalty      24,000
Taxes                     48,000
Other Charges             30,381
--------------------------------
Total                    524,381

The ledger provides a financial representation of energy consumption.

This is important because GridPilot's initial optimisation objective is financial:

Where is the facility losing money and why?
6. Tariff Engine

The Tariff Engine calculates expected electricity costs from structured tariff rules.

Potential components include:

fixed charges
volumetric energy charges
time-of-use charges
demand charges
power-factor penalties
reactive-energy charges
taxes
surcharges

Tariff calculations must remain deterministic.

An LLM must never be responsible for calculating the expected electricity bill.

7. Analytics Engine

The Analytics Engine calculates facility energy KPIs.

Initial metrics may include:

effective cost per kWh
demand-cost percentage
penalty-cost percentage
fixed-cost percentage
maximum demand
power factor
month-over-month consumption change

With interval data this expands to:

load factor
baseload
peak-to-average ratio
operating-hour consumption
off-hours consumption
peak duration
load variability
load-shifting potential
8. Anomaly Engine

The Anomaly Engine identifies conditions that may require attention.

Examples:

Poor power factor
High demand-charge contribution
Unexpected consumption increase
Billing inconsistency
Tariff mismatch
Unusual miscellaneous charge
Demand spike
Abnormal effective energy cost

An anomaly is an observation.

It is not automatically an opportunity.

Example:

Finding:
Power factor = 0.82

Severity:
High

The Opportunity Engine determines whether that finding can be converted into economic value.

9. Opportunity Engine

The Opportunity Engine converts energy findings into potential interventions.

Conceptually:

Finding
   |
   v
Intervention
   |
   v
Baseline
   |
   v
Scenario
   |
   v
Estimated Savings
   |
   v
Implementation Cost
   |
   v
Payback / IRR
   |
   v
Confidence

Potential opportunities include:

power-factor correction
demand reduction
tariff optimisation
operational scheduling
energy efficiency
solar installation
battery storage
load shifting
demand response

Not every opportunity can be calculated from bill data alone.

GridPilot must explicitly identify when additional data is required.

10. Evidence & Provenance

GridPilot should preserve where important data came from.

Example:

{
  "field": "maximum_demand",
  "value": 417,
  "unit": "kVA",
  "source": "electricity_bill.pdf",
  "page": 2,
  "source_text": "Recorded Maximum Demand: 417 kVA",
  "confidence": 0.98
}

This allows a recommendation to eventually be traced backwards:

Recommendation
      |
Opportunity
      |
Finding
      |
Calculation
      |
Evidence
      |
Source
11. Agentic Layer

Agents are used only where reasoning provides value.

Initial agent roles may include:

Evidence Agent

Validates extracted information and provenance.

Energy Analyst

Interprets deterministic outputs and identifies relevant patterns.

Skeptic Agent

Challenges assumptions, recommendations and unsupported conclusions.

Research Agent

Retrieves tariff, regulatory or market information when external knowledge is required.

Report Agent

Converts structured findings into a clear Energy Intelligence Report.

Agents do not replace deterministic calculation engines.

12. Future Architecture

GridPilot evolves by adding new intelligence and control layers.

Bill Intelligence
       |
       v
Meter Intelligence
       |
       v
Scenario Engine
       |
       v
Asset Model
       |
       v
Forecasting
       |
       v
Optimisation Engine
       |
       v
Control Interface
       |
       v
Flexibility Engine
       |
       v
Aggregation
       |
       v
Market Interface
13. VPP Architecture

At sufficient scale, GridPilot may coordinate many distributed assets.

Facility A ----\
Facility B -----\
Facility C ------> GridPilot Aggregation Layer
Facility D -----/             |
Facility N ----/              v
                      Flexibility Portfolio
                              |
                              v
                        Optimisation
                              |
                              v
                      Market Participation

The VPP is therefore not a standalone feature.

It is the eventual result of progressively building:

energy intelligence + asset intelligence + control + flexibility + aggregation.

14. Safety Principle

GridPilot v0.1 is an analytical system.

Future control functionality must introduce additional safeguards including:

human authorization
asset operating constraints
fail-safe states
command validation
audit logs
permission boundaries
grid-code compliance
fallback behaviour

AI-generated reasoning must never directly control physical energy assets without deterministic safety and authorization layers.
