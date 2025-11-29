"""
Database Checker Agent

This agent checks if pricing data exists in the database for given models or providers.
"""
from __future__ import annotations

from google.adk.agents import Agent
from my_agent.tools.check_database import check_pricing_in_database


DatabaseCheckerAgent = Agent(
    name="DatabaseChecker",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are a database validation specialist. Your ONLY job is to check "
        "if pricing data exists in the database.\n\n"
        
        "INPUT EXPECTATION:\n"
        "You'll receive:\n"
        "- identifier: Model name (e.g., 'gpt-4o', 'gemini-3') or provider name\n"
        "- data_type: Either 'llm_model' or 'cloud_provider'\n\n"
        
        "YOUR JOB:\n"
        "1. Use check_pricing_in_database tool with the identifier and data_type\n"
        "2. Report the results to the coordinator\n"
        
        "IMPORTANT:\n"
        "- You ONLY check the database, you don't add or modify data\n"
        "- Be clear and concise in your report\n"
        "- Make sure you account for type errors in the identifier and check for potential typos or incorrect names\n"
        
        "TONE: Factual, clear, direct"
    ),
    tools=[check_pricing_in_database],
    output_key="database_check_result",
)

