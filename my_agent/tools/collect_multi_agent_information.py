"""
Multi-agent workflow information collection tool.

Gathers project information specifically for multi-agent workflow cost estimation.
Collects data conversationally, building up the agent list incrementally.
"""
from __future__ import annotations

from typing import Any, Dict
import json

from my_agent.data_update import DATABASE_PATH


def _load_defaults() -> Dict[str, Any]:
    """Load default values from database."""
    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
            return db.get("defaults", {})
    except Exception:
        return {
            "multi_agent": {"days": 30},
            "llm_cost": {
                "avg_tokens_per_call": 2000,
                "days": 30,
            }
        }


def collect_multi_agent_information(
    total_agents: int = None,
    collected_agents_json: str = None,
    current_agent_name: str = None,
    current_agent_purpose: str = None,
    current_agent_model: str = None,
    current_agent_tokens: int = None,
    current_agent_calls: int = None,
    days: int = None,
) -> Dict[str, Any]:
    """
    Collect information for multi-agent workflow cost estimation.

    This tool collects agent data incrementally. Call it multiple times to add agents.
    
    WORKFLOW:
    1. First call: Provide total_agents (how many agents total)
    2. Next calls: Add one agent at a time with current_agent_* parameters
    3. Pass collected_agents_json from previous response to maintain state
    4. When all agents collected, returns status='success'

    Args:
        total_agents: Total number of agents in the workflow
        collected_agents_json: JSON string of already-collected agents (from previous calls)
        current_agent_name: Name of the agent being added now
        current_agent_purpose: Brief description of what this agent does
        current_agent_model: LLM model (e.g., gpt-4o, gemini-2.5-flash-lite)
        current_agent_tokens: Average tokens per call (optional, defaults to 2000)
        current_agent_calls: Daily API calls (optional, defaults to 50)
        days: Number of days to calculate (default: 30)

    Returns:
        Dictionary with collected agents so far, or final validated_data when complete
    """
    defaults = _load_defaults()
    
    # Parse already collected agents
    collected_agents = []
    if collected_agents_json:
        try:
            collected_agents = json.loads(collected_agents_json)
        except json.JSONDecodeError:
            collected_agents = []

    # Step 1: Ask for total number of agents
    if total_agents is None:
        return {
            "status": "need_info",
            "missing_fields": ["total_agents"],
            "message": "Let's build your multi-agent workflow step by step.",
            "prompt": "How many AI agents are in your workflow? (No limit!)"
        }

    if total_agents < 1:
        return {
            "status": "error",
            "message": "Please specify at least 1 agent in your workflow."
        }

    # Check if we're done collecting
    num_collected = len(collected_agents)
    
    if num_collected >= total_agents:
        # All agents collected! Return final data
        validated_data = {
            "type": "multi_agent",
            "agents": collected_agents,
            "days": days or defaults["multi_agent"]["days"]
        }
        
        applied_defaults = {}
        if not days:
            applied_defaults["days"] = defaults["multi_agent"]["days"]
        
        # Count how many agents used defaults
        missing_fields = []
        warnings = []
        for agent in collected_agents:
            if agent.get("used_default_tokens"):
                missing_fields.append(f"{agent['name']}_tokens")
                warnings.append(f"{agent['name']}: Using {agent['avg_tokens_per_call']} tokens/call (default)")
            if agent.get("used_default_calls"):
                missing_fields.append(f"{agent['name']}_calls")
                warnings.append(f"{agent['name']}: Assuming {agent['calls_per_day']} calls/day (default)")
        
        confidence = 1.0 - min(0.5, len(missing_fields) * 0.03)
        
        return {
            "status": "success",
            "validated_data": validated_data,
            "missing_fields": missing_fields,
            "applied_defaults": applied_defaults,
            "warnings": warnings,
            "questions": [],
            "confidence": confidence,
            "message": (
                f"Multi-agent workflow configured! "
                f"{total_agents} agents ready. Confidence: {confidence:.0%}"
            )
        }

    # We need to collect another agent
    agent_num = num_collected + 1
    
    # Step 2: Agent name
    if not current_agent_name:
        return {
            "status": "collecting",
            "progress": f"{num_collected}/{total_agents} agents",
            "collected_agents_json": json.dumps(collected_agents),
            "message": f"Configuring Agent {agent_num} of {total_agents}",
            "prompt": f"What's the name or role of Agent #{agent_num}? (e.g., 'researcher', 'coder', 'reviewer')"
        }

    # Step 3: Agent purpose
    if not current_agent_purpose:
        return {
            "status": "collecting",
            "progress": f"{num_collected}/{total_agents} agents",
            "collected_agents_json": json.dumps(collected_agents),
            "message": f"Understanding '{current_agent_name}'...",
            "prompt": f"What does '{current_agent_name}' do? (Brief description of its purpose)"
        }

    # Step 4: Agent model
    if not current_agent_model:
        return {
            "status": "collecting",
            "progress": f"{num_collected}/{total_agents} agents",
            "collected_agents_json": json.dumps(collected_agents),
            "message": f"Which model does '{current_agent_name}' use?",
            "prompt": "Which LLM model? (e.g., gpt-4o, gemini-2.5-flash-lite, claude-3-5-sonnet)"
        }

    # Step 5 & 6: Apply defaults if needed
    if not current_agent_tokens:
        current_agent_tokens = defaults["llm_cost"]["avg_tokens_per_call"]
        used_default_tokens = True
    else:
        used_default_tokens = False

    if not current_agent_calls:
        current_agent_calls = 50
        used_default_calls = True
    else:
        used_default_calls = False

    # Add the completed agent to the list
    new_agent = {
        "name": current_agent_name,
        "purpose": current_agent_purpose,
        "model": current_agent_model,
        "avg_tokens_per_call": current_agent_tokens,
        "calls_per_day": current_agent_calls,
        "used_default_tokens": used_default_tokens,
        "used_default_calls": used_default_calls,
    }
    collected_agents.append(new_agent)

    # If we just collected the last agent, we're done!
    if len(collected_agents) >= total_agents:
        # Recursively call ourselves to trigger the completion logic
        return collect_multi_agent_information(
            total_agents=total_agents,
            collected_agents_json=json.dumps(collected_agents),
            days=days
        )

    # Otherwise, ask for the next agent
    return {
        "status": "collecting",
        "progress": f"{len(collected_agents)}/{total_agents} agents",
        "collected_agents_json": json.dumps(collected_agents),
        "message": f"✓ '{current_agent_name}' configured! Moving to next agent...",
        "prompt": f"Ready to configure Agent #{len(collected_agents) + 1}. What's its name?"
    }

