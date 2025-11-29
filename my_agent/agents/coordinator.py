"""
Coordinator Agent (Root Agent)

This agent orchestrates the workflow between specialized agents
to provide complete AI cost analysis.
"""
from __future__ import annotations

from google.adk.agents import Agent
from .information_collector import InformationCollectorAgent
from .database_checker import DatabaseCheckerAgent
from .cost_calculator import CostCalculatorAgent


root_agent = Agent(
    name="TokenTrackerCoordinator",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are the TokenTracker Coordinator, orchestrating a multiple agent workflow:\n\n"

        "- Start InformationCollector agent as soon as the user starts the conversation\n"
        "- InformationCollector gets user input and returns validated_data to you\n"
        "- You pass validated_data to DatabaseChecker agent\n"
        "- DatabaseChecker returns database_check_result to you\n"
        "- If database_check_result is found, you pass validated_data to CostCalculator agent\n"
        "- If database_check_result is not found, you return the user a message that the pricing is not found and cannot calculate the cost.\n"
        "- CostCalculator returns cost_report to you\n"
        "- You review the cost_report and return it to the user\n"
        
        "TONE: Professional, organized, results-focused"
    ),
    sub_agents=[InformationCollectorAgent, DatabaseCheckerAgent, CostCalculatorAgent],
    output_key="final_analysis",
)

