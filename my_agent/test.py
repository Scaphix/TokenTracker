"""
TokenTracker Demo - Professional AI Cost Estimation

Run this script to see TokenTracker in action with example scenarios.
"""
from my_agent.agent import TokenTrackerCoordinator


def main():
    """Run TokenTracker demo with multiple cost estimation scenarios."""

    coordinator = TokenTrackerCoordinator()

    # Example 1: Gemini Flash Lite - Complete data
    print("\n" + "=" * 70)
    print("SCENARIO 1: Gemini Flash Lite Production Workload")
    print("=" * 70)
    result1 = coordinator.run({
        "type": "llm_cost",
        "model": "gemini-2.5-flash-lite",
        "avg_tokens_per_call": 1800,
        "calls_per_day": 80
    })

    print("\n📊 COST SUMMARY")
    print(f"   Monthly: ${result1.monthly_cost:.2f} {result1.currency}")
    print(f"   Daily: ${result1.daily_cost:.2f} {result1.currency}")
    print(f"   Confidence: {result1.confidence_level:.0%}")

    if result1.optimizations:
        print(f"\n🔧 OPTIMIZATIONS ({len(result1.optimizations)} found):")
        for opt in result1.optimizations[:3]:
            print(f"   • {opt}")

    if result1.alternatives:
        print("\n💡 ALTERNATIVES:")
        for alt in result1.alternatives[:2]:
            savings_pct = alt['savings_percent']
            print(f"   • {alt['model']}: Save ${alt['savings']:.2f}/mo "
                  f"({savings_pct:.0f}% cheaper)")

    print("\n📝 EXECUTIVE SUMMARY:")
    print(f"{result1.summary}\n")

    # Example 2: GPT-4o with missing data
    print("\n" + "=" * 70)
    print("SCENARIO 2: GPT-4o with Incomplete Data")
    print("=" * 70)
    result2 = coordinator.run({
        "type": "llm_cost",
        "model": "gpt-4o",
        "calls_per_day": 60
        # Missing: avg_tokens_per_call - will use defaults
    })

    print("\n📊 COST SUMMARY")
    print(f"   Monthly: ${result2.monthly_cost:.2f} {result2.currency}")
    print(f"   Confidence: {result2.confidence_level:.0%}")

    if result2.applied_defaults:
        print("\n⚙️ DEFAULTS APPLIED:")
        for field, value in result2.applied_defaults.items():
            print(f"   • {field}: {value}")

    if result2.warnings:
        print("\n⚠️ WARNINGS:")
        for warning in result2.warnings:
            print(f"   • {warning}")

    # Example 3: Multi-agent workflow
    print("\n" + "=" * 70)
    print("SCENARIO 3: Multi-Agent Production System")
    print("=" * 70)
    result3 = coordinator.run({
        "type": "multi_agent",
        "agents": [
            {
                "name": "research",
                "model": "gemini-2.5-flash-lite",
                "avg_tokens_per_call": 2000,
                "calls_per_day": 40
            },
            {
                "name": "coder",
                "model": "gpt-4o-mini",
                "avg_tokens_per_call": 3000,
                "calls_per_day": 20
            },
            {
                "name": "memory",
                "model": "gpt-3.5-turbo",
                "avg_tokens_per_call": 800,
                "calls_per_day": 100
            }
        ]
    })

    print("\n📊 TOTAL COST")
    print(f"   Monthly: ${result3.monthly_cost:.2f} {result3.currency}")
    print(f"   Daily: ${result3.daily_cost:.2f} {result3.currency}")

    print("\n📊 COST BREAKDOWN BY AGENT:")
    for agent_name, cost in result3.cost_breakdown.items():
        pct = (cost / result3.monthly_cost) * 100
        print(f"   • {agent_name}: ${cost:.2f} ({pct:.1f}%)")

    if result3.optimizations:
        print("\n🔧 OPTIMIZATION OPPORTUNITIES:")
        for opt in result3.optimizations:
            print(f"   • {opt}")

    print("\n📝 PRICING DATA:")
    print(f"   Last Updated: {result3.pricing_last_updated}")
    print(f"   Sources: {', '.join(result3.data_sources)}")

    print("\n" + "=" * 70)
    print("✅ All scenarios completed successfully!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
