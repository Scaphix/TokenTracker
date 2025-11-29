"""
Coordinator Agent (Root Agent)

This agent orchestrates the workflow between specialized agents
to provide complete AI cost analysis.
"""
from __future__ import annotations

from google.adk.agents import Agent
from .information_collector import InformationCollectorAgent
from .database_checker import DatabaseCheckerAgent
from .data_searcher import DataSearcherAgent
from .cost_calculator import CostCalculatorAgent


root_agent = Agent(
    name="TokenTrackerCoordinator",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are the TokenTracker Coordinator, orchestrating a multiple agent workflow:\n\n"

        "1) Start InformationCollector agent as soon as the user starts the conversation\n"
        "2) InformationCollector gets user input and returns validated_data to you\n"
        "3) You pass validated_data to DatabaseChecker agent\n"
        "4) DatabaseChecker returns database_check_result to you\n"
        "5) If database_check_result is not found, you pass validated_data to DataSearcher agent and wait for the result. \n"
        "6) CostCalculator returns cost_report to you\n"
        "7) You review the cost_report and return it to the user\n"
        
        "TONE: Professional, organized, results-focused"
    ),
    sub_agents=[InformationCollectorAgent, DatabaseCheckerAgent, DataSearcherAgent, CostCalculatorAgent],
    output_key="final_analysis",
)

