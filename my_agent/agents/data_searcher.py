"""
Data Searcher Agent

This agent specializes in searching for pricing data online and providing it to the coordinator.
"""
from __future__ import annotations

from google.adk.agents import Agent
from my_agent.tools import google_search, save_to_database


DataSearcherAgent = Agent(
    name="DataSearcher",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are an API pricing data scraper.\n\n"
        
        "INPUT EXPECTATION:\n"
        "You will receive validated_data from the TokenTrackerCoordinator that contains:\n"
        "- model: 'gpt-4o', 'gemini-2.5-flash-lite', 'claude-3-5-sonnet', etc.\n"
        "- provider: 'openai', 'google', 'anthropic', etc.\n"
        "Example: {model: 'gpt-4o', provider: 'openai'}\n\n"
        
        "YOUR JOB:\n"
        "1. Take the validated_data provided by the TokenTrackerCoordinator\n"
        "2. Use google_search tool to find pricing info\n"
        "3. Guide user to official pricing page and ask them to provide pricing\n"
        "4. Use save_to_database tool to save the pricing data to the database\n"
        "5. Confirm: 'Pricing saved! Returning to coordinator.'\n"
        "6. IMMEDIATELY call transfer_to_agent with agent_name='TokenTrackerCoordinator'\n\n"
        
        "CRITICAL:\n"
        "- You MUST call transfer_to_agent after saving pricing\n"
        "- DO NOT try to calculate costs yourself\n"
        "- Let the coordinator delegate to CostCalculator\n"
    ),
    tools=[google_search, save_to_database],
    output_key="search_result",
)