"""
Agents module for TokenTracker system.

This module exports all agents for AI cost estimation workflow.
"""
from __future__ import annotations

from .information_collector import InformationCollectorAgent
from .database_checker import DatabaseCheckerAgent
from .cost_calculator import CostCalculatorAgent
from .coordinator import root_agent

__all__ = [
    "InformationCollectorAgent",
    "DatabaseCheckerAgent",
    "CostCalculatorAgent",
    "root_agent",
]

# Print confirmation when agents are loaded
print("✅ InformationCollectorAgent loaded.")
print("✅ DatabaseCheckerAgent loaded.")
print("✅ CostCalculatorAgent loaded.")
print("✅ TokenTrackerCoordinator (root_agent) loaded.")

