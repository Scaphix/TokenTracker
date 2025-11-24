"""
TokenTracker: Professional Multi-Agent AI Cost Calculator

A production-ready cost estimation system powered by Google ADK that helps
developers predict and optimize AI infrastructure costs before deployment.

Features:
- Real-time pricing data fetching from providers
- Multi-agent workflow cost calculation
- Intelligent optimization recommendations
- Complete transparency with confidence levels
- Support for LLM, server, and multi-agent scenarios

Example:
    from my_agent import TokenTrackerCoordinator

    coordinator = TokenTrackerCoordinator()
    result = coordinator.run({
        "type": "llm_cost",
        "model": "gemini-2.5-flash-lite",
        "avg_tokens_per_call": 2000,
        "calls_per_day": 50
    })

    print(f"Monthly cost: ${result.monthly_cost:.2f}")
    print(f"Optimizations: {result.optimizations}")
"""
from __future__ import annotations

from .calculators import (
    estimate_llm_cost,
    estimate_multi_agent_cost,
    estimate_server_cost,
)
from .pricing_updater import update_pricing_database
from .tokentracker import CostEstimateResult, TokenTrackerCoordinator


__all__ = [
    "TokenTrackerCoordinator",
    "CostEstimateResult",
    "update_pricing_database",
    "estimate_llm_cost",
    "estimate_server_cost",
    "estimate_multi_agent_cost",
]
