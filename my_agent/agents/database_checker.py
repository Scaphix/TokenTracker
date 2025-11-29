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
        "2. Get the result (status='found' or status='not_found')\n"
        "3. Say one sentence about the result:\n"
        "   - 'Pricing found for [identifier]!' OR 'Pricing not found for [identifier].'\n"
        "4. IMMEDIATELY call transfer_to_agent with agent_name='TokenTrackerCoordinator'\n\n"
        
        "CRITICAL:\n"
        "- You MUST call transfer_to_agent after reporting the result\n"
        "- DO NOT ask follow-up questions\n"
        "- DO NOT wait for user input\n"
        "- DO NOT try to solve the problem yourself\n"
        
        "TONE: Factual, brief, one sentence then transfer"
    ),
    tools=[check_pricing_in_database],
    output_key="database_check_result",
)

