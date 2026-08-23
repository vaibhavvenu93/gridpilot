import argparse
import json
from pathlib import Path

from gridpilot.analysis import GridPilotAnalysis, analyze_bill
from gridpilot.models.bill import ElectricityBill


def load_bill(path: Path) -> ElectricityBill:
    """Load and validate an electricity bill from JSON."""

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return ElectricityBill.model_validate(data)


def format_currency(value: float, currency: str) -> str:
    """Format a monetary value."""

    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = symbols.get(currency, f"{currency} ")

    return f"{symbol}{value:,.2f}"


def print_analysis(analysis: GridPilotAnalysis) -> None:
    """Print a human-readable GridPilot Energy Intelligence Report."""

    print()
    print("=" * 72)
    print("GRIDPILOT ENERGY INTELLIGENCE")
    print("=" * 72)

    print()
    print(f"Facility: {analysis.facility_name}")
    print(f"Bill ID:  {analysis.bill_id}")

    print()
    print("ENERGY SUMMARY")
    print("-" * 72)

    print(
        "Total electricity cost: "
        f"{format_currency(analysis.kpis.total_cost, analysis.currency)}"
    )

    print(
        "Consumption: "
        f"{analysis.kpis.consumption_kwh:,.0f} kWh"
    )

    if analysis.kpis.effective_cost_per_kwh is not None:
        print(
            "Effective cost: "
            f"{format_currency(analysis.kpis.effective_cost_per_kwh, analysis.currency)}"
            "/kWh"
        )

    if analysis.kpis.maximum_demand_kw is not None:
        print(
            "Maximum demand: "
            f"{analysis.kpis.maximum_demand_kw:,.0f} kW"
        )

    if analysis.kpis.maximum_demand_kva is not None:
        print(
            "Maximum apparent demand: "
            f"{analysis.kpis.maximum_demand_kva:,.0f} kVA"
        )

    if analysis.kpis.power_factor is not None:
        print(
            "Power factor: "
            f"{analysis.kpis.power_factor:.2f}"
        )

    print()
    print("COST STRUCTURE")
    print("-" * 72)

    print(
        f"Energy charges: {analysis.kpis.energy_cost_percentage:.2f}%"
    )
    print(
        f"Demand charges: {analysis.kpis.demand_cost_percentage:.2f}%"
    )
    print(
        f"Penalty charges: {analysis.kpis.penalty_cost_percentage:.2f}%"
    )
    print(
        f"Fixed charges: {analysis.kpis.fixed_cost_percentage:.2f}%"
    )

    print()
    print("FINDINGS")
    print("-" * 72)

    if not analysis.findings:
        print("No material findings detected.")
    else:
        for number, finding in enumerate(analysis.findings, start=1):
            print(
                f"{number}. [{finding.severity}] "
                f"{finding.title}"
            )
            print(f"   {finding.explanation}")

            if finding.estimated_cost is not None:
                print(
                    "   Observed cost: "
                    f"{format_currency(finding.estimated_cost, analysis.currency)}"
                )

            print()

    print("OPPORTUNITIES")
    print("-" * 72)

    if not analysis.opportunities:
        print("No opportunities identified.")
    else:
        for number, opportunity in enumerate(
            analysis.opportunities,
            start=1,
        ):
            print(
                f"{number}. {opportunity.title}"
                f" [{opportunity.status}]"
            )

            print(
                f"   Confidence: "
                f"{opportunity.confidence:.0%}"
            )

            if opportunity.estimated_monthly_savings is not None:
                print(
                    "   Monthly savings screen: "
                    f"{format_currency(
                        opportunity.estimated_monthly_savings,
                        analysis.currency,
                    )}"
                )

            if opportunity.estimated_annual_savings is not None:
                print(
                    "   Annual savings screen: "
                    f"{format_currency(
                        opportunity.estimated_annual_savings,
                        analysis.currency,
                    )}"
                )

            print(f"   Action: {opportunity.recommended_action}")
            print()

    print("RECOMMENDED NEXT DATA")
    print("-" * 72)

    if not analysis.recommended_next_data:
        print("No additional data requested.")
    else:
        for item in analysis.recommended_next_data:
            print(f"- {item}")

    print()
    print("=" * 72)
    print(
        "GridPilot screening output. "
        "Recommendations require appropriate engineering validation."
    )
    print("=" * 72)
    print()


def main() -> None:
    """GridPilot command-line interface."""

    parser = argparse.ArgumentParser(
        prog="gridpilot",
        description=(
            "Energy intelligence for commercial and industrial facilities."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a structured electricity bill.",
    )

    analyze_parser.add_argument(
        "bill",
        type=Path,
        help="Path to an electricity bill JSON file.",
    )

    args = parser.parse_args()

    if args.command == "analyze":
        bill = load_bill(args.bill)
        analysis = analyze_bill(bill)
        print_analysis(analysis)


if __name__ == "__main__":
    main()
