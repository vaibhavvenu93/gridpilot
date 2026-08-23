# GridPilot

> Open-source energy intelligence infrastructure for commercial and industrial facilities.

GridPilot is an experimental energy intelligence platform designed to help commercial and industrial businesses understand, optimise, and eventually control distributed energy assets.

The starting point is deliberately simple:

**Give GridPilot an electricity bill and/or interval meter data. It identifies where money is being lost, quantifies potential savings, explains what can be done, and progressively enables optimisation and automation.**

## The Problem

Commercial and industrial businesses spend significant amounts on electricity but often lack dedicated energy teams, sophisticated optimisation software, DERMS, or access to energy-market expertise.

An electricity bill tells a business how much it owes.

It usually does not clearly answer:

- Why did we spend this much?
- Which charges are avoidable?
- Are demand peaks costing us money?
- Are we on the right tariff?
- Is our power factor creating penalties?
- Would solar or battery storage make financial sense?
- Which loads could be shifted?
- How much flexibility could this site eventually provide?

GridPilot aims to turn fragmented energy data into financial and operational intelligence.

## Product Thesis

GridPilot evolves through a series of increasingly valuable layers:

Electricity Bill Intelligence  
↓  
Meter & Load Intelligence  
↓  
Financial Optimisation  
↓  
Asset Intelligence  
↓  
Asset Optimisation  
↓  
Asset Control  
↓  
Flexibility  
↓  
Multi-site Aggregation  
↓  
Energy Market Participation  
↓  
Virtual Power Plant

The long-term thesis is to build a hardware-agnostic financial and control layer across distributed commercial and industrial energy assets.

## v0.1 — Bill Intelligence

The first version focuses on the smallest useful product.

### Input

- Electricity bill data
- Facility information
- Tariff information

### Intelligence

GridPilot will:

1. Normalize electricity bill data
2. Reconstruct energy costs
3. Calculate energy KPIs
4. Detect anomalies
5. Identify potential savings opportunities
6. Quantify opportunities where possible
7. Preserve evidence and provenance
8. Generate an explainable Energy Intelligence Report

### Output

Instead of:

> Your electricity bill is ₹524,381.

GridPilot should eventually be able to say:

> Your electricity bill was ₹524,381. Approximately 21% came from demand charges. Four demand peaks materially increased your cost. Power-factor penalties contributed an additional ₹24,000. We identified three optimisation opportunities worth an estimated ₹X annually.

## Architecture Principle

GridPilot separates deterministic computation from probabilistic AI reasoning.

### Deterministic engines

Used for:

- tariff calculations
- energy mathematics
- KPI calculation
- financial modelling
- anomaly thresholds
- battery and solar simulation
- optimisation

### AI / Agentic systems

Used where reasoning is useful:

- document interpretation
- evidence extraction
- tariff and regulatory research
- anomaly explanation
- recommendation synthesis
- scenario interpretation
- report generation

**LLMs should not be responsible for energy mathematics that can be calculated deterministically.**

## Evidence First

Every important result should eventually be traceable:

Source → Evidence → Calculation → Finding → Opportunity → Recommendation

GridPilot should be able to explain not only **what** it recommends, but **why**, **using which data**, and **with what level of confidence**.

## Long-Term Architecture

GridPilot is being designed toward five major intelligence layers:

### 1. Energy Intelligence

Understand bills, tariffs, consumption and costs.

### 2. Financial Optimisation

Identify avoidable expenditure and model interventions.

### 3. Asset Intelligence

Understand solar, batteries, HVAC, EV charging, refrigeration and other flexible assets.

### 4. Flexibility & Control

Optimise and eventually orchestrate controllable distributed assets.

### 5. Aggregation & VPP

Aggregate flexible capacity across many C&I facilities and enable participation in electricity and flexibility markets.

## Repository Status

🚧 **Active development**

Current milestone:

**v0.1 — Electricity Bill Intelligence Engine**

The current repository is an experimental open-source implementation of the GridPilot product thesis and is not intended for production energy-system control.
