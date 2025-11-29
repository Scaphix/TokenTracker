"""
Coordinator Agent (Root Agent)

This agent orchestrates the workflow between specialized agents
to provide complete AI cost analysis.
"""
from __future__ import annotations

from google.adk.agents import Agent
from .information_collector import InformationCollectorAgent
from .cost_calculator import CostCalculatorAgent


root_agent = Agent(
    name="TokenTrackerCoordinator",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are the TokenTracker Coordinator, orchestrating a multiple agent workflow:\n\n"

        "STEP 1 - Start InformationCollector agent as soon as the user starts the conversation\n"
        "STEP 2 - InformationCollector gets user input and returns validated_data to you\n"
        "STEP 3 - You pass validated_data to CostCalculator agent\n"
        "STEP 4 - CostCalculator returns cost_report to you\n"
        "STEP 5 - You review the cost_report and return it to the user\n"
        
        "TONE: Professional, organized, results-focused"
    ),
    sub_agents=[InformationCollectorAgent, CostCalculatorAgent],
    output_key="final_analysis",
)

