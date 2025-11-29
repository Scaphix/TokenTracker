"""
TokenTracker: Professional AI Cost Calculator

A production-ready cost estimation system powered by Google ADK that helps
developers predict and optimize AI infrastructure costs before deployment.

Features:
- Real-time pricing data fetching from providers
- Multi-agent workflow cost calculation
- Intelligent optimization recommendations
- Complete transparency with confidence levels
- Support for LLM, server, and multi-agent scenarios

Example:
    from my_agent import root_agent
    from google.adk.runners import InMemoryRunner

    # Use with ADK CLI (recommended):
    # $ adk run my_agent

    # Or programmatically:
    runner = InMemoryRunner(agent=root_agent)
    # Then use ADK's session API
"""
from __future__ import annotations

# Import agents from new structure
from .agents import (
    root_agent,
    InformationCollectorAgent,
    DatabaseCheckerAgent,
    CostCalculatorAgent,
)

# Import tools
from .tools import (
    collect_llm_information,
    collect_server_information,
    collect_multi_agent_information,
    check_pricing_in_database,
    calculate_cost_estimate,
)

# Import calculators
from .calculators import (
    estimate_llm_cost,
    estimate_server_cost,
    estimate_multi_agent_cost,
)

# Import utilities
from .pricing_updater import update_pricing_database

__all__ = [
    # Main agent
    "root_agent",
    # Sub-agents
    "InformationCollectorAgent",
    "DatabaseCheckerAgent",
    "CostCalculatorAgent",
    # Tools
    "collect_llm_information",
    "collect_server_information",
    "collect_multi_agent_information",
    "check_pricing_in_database",
    "calculate_cost_estimate",
    # Calculators
    "estimate_llm_cost",
    "estimate_server_cost",
    "estimate_multi_agent_cost",
    # Utilities
    "update_pricing_database",
]
