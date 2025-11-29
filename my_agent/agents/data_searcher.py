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
        "You will receive validated_data from the coordinator that contains:\n"
        "- model: 'gpt-4o', 'gemini-2.5-flash-lite', 'claude-3-5-sonnet', etc.\n"
        "- provider: 'openai', 'google', 'anthropic', etc.\n"
        "Example: {model: 'gpt-4o', provider: 'openai'}\n\n"
        
        "YOUR JOB:\n"
        "1. Take the validated_data provided by the coordinator\n"
        "2. Use google_search tool with this data\n"
        "3. Use save_to_database tool to save the pricing data to the database\n"
        "4. Return the success or failure of the save to the coordinator\n"
    ),
    tools=[google_search, save_to_database],
    output_key="search_result",
)