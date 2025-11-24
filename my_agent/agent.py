"""
TokenTracker: Professional Multi-Agent Cost Calculator
Orchestrates information collection → cost calculation → optimization
"""
from __future__ import annotations

from typing import Any, Dict

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search

from my_agent.data_update import DATABASE_PATH
import json


# ============================================================================
# TOOL 1: Information Collection Helper
# ============================================================================

def collect_project_information(
    request_type: str = None,
    model: str = None,
    avg_tokens_per_call: int = None,
    calls_per_day: int = None,
    days: int = None,
    provider: str = None,
    plan_or_type: str = None,
    runtime_hours: int = None,
    storage_gb: int = None,
    traffic_gb: int = None,
) -> Dict[str, Any]:
    """
    Interactive information collection tool for AI cost estimation.

    This tool helps gather all necessary data about the user's AI project
    to calculate accurate costs. It validates inputs and applies industry
    defaults when data is missing.

    Args:
        request_type: Type of cost calculation (llm_cost, server_cost,
                     multi_agent)
        model: LLM model name (e.g., gpt-4o, gemini-2.5-flash-lite)
        avg_tokens_per_call: Average tokens per API call
        calls_per_day: Number of API calls per day
        days: Number of days to calculate (default: 30)
        provider: Server provider (aws, digitalocean, etc.)
        plan_or_type: Server plan/instance type
        runtime_hours: Monthly server runtime hours (default: 720 for 24/7)
        storage_gb: Storage in GB
        traffic_gb: Network traffic in GB

    Returns:
        Dictionary with validated data, applied defaults, and warnings
    """
    # Load defaults from database
    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
            defaults = db.get("defaults", {})
    except Exception:
        defaults = {
            "llm_cost": {
                "avg_tokens_per_call": 2000,
                "days": 30,
                "include_output": True,
                "retry_rate": 0.05
            },
            "server_cost": {
                "runtime_hours": 720,
                "storage_gb": 20,
                "traffic_gb": 50
            },
            "multi_agent": {"days": 30}
        }

    validated_data = {}
    missing_fields = []
    applied_defaults = {}
    warnings = []
    questions = []

    # Validate request type
    if not request_type:
        return {
            "status": "error",
            "message": (
                "I need to know what type of cost you want to calculate. "
                "Please specify:\n"
                "- 'llm_cost' for LLM API costs\n"
                "- 'server_cost' for hosting costs\n"
                "- 'multi_agent' for multi-agent workflow costs"
            ),
            "required_field": "request_type"
        }

    validated_data["type"] = request_type

    # ========================================================================
    # LLM Cost Calculation
    # ========================================================================
    if request_type == "llm_cost":
        # Required: model
        if not model:
            questions.append(
                "Which LLM model will you use? "
                "(e.g., gpt-4o, gemini-2.5-flash-lite, claude-3-5-sonnet)"
            )
            return {
                "status": "need_info",
                "missing_fields": ["model"],
                "questions": questions,
                "message": (
                    "To calculate LLM costs, I need to know which model "
                    "you're using."
                )
            }

        validated_data["model"] = model

        # Optional but important: avg_tokens_per_call
        if avg_tokens_per_call:
            validated_data["avg_tokens_per_call"] = avg_tokens_per_call
        else:
            default_tokens = defaults["llm_cost"]["avg_tokens_per_call"]
            validated_data["avg_tokens_per_call"] = default_tokens
            applied_defaults["avg_tokens_per_call"] = default_tokens
            missing_fields.append("avg_tokens_per_call")
            warnings.append(
                f"Using industry average: {default_tokens} tokens/call. "
                "For better accuracy, monitor your first 100 API calls."
            )

        # Optional: calls_per_day
        if calls_per_day:
            validated_data["calls_per_day"] = calls_per_day
        else:
            questions.append(
                "How many API calls do you expect per day? "
                "(This helps estimate your usage pattern)"
            )
            # For now, use a reasonable default
            default_calls = 50
            validated_data["calls_per_day"] = default_calls
            applied_defaults["calls_per_day"] = default_calls
            missing_fields.append("calls_per_day")
            warnings.append(
                f"Assuming {default_calls} calls/day. Adjust based on "
                "your expected traffic."
            )

        # Optional: days
        validated_data["days"] = days or defaults["llm_cost"]["days"]
        if not days:
            applied_defaults["days"] = defaults["llm_cost"]["days"]

        # Apply other defaults
        validated_data["include_output"] = defaults["llm_cost"][
            "include_output"
        ]
        validated_data["retry_rate"] = defaults["llm_cost"]["retry_rate"]

    # ========================================================================
    # Server Cost Calculation
    # ========================================================================
    elif request_type == "server_cost":
        # Required: provider
        if not provider:
            questions.append(
                "Which hosting provider? (e.g., aws, digitalocean, gcp)"
            )
            return {
                "status": "need_info",
                "missing_fields": ["provider"],
                "questions": questions,
                "message": "Which cloud provider will host your AI agent?"
            }

        validated_data["provider"] = provider

        # Required: plan_or_type
        if not plan_or_type:
            questions.append(
                f"Which {provider} plan/instance type? "
                "(e.g., t2.micro for AWS, basic_1 for DigitalOcean)"
            )
            return {
                "status": "need_info",
                "missing_fields": ["plan_or_type"],
                "questions": questions,
                "message": f"Which {provider} plan will you use?"
            }

        validated_data["plan_or_type"] = plan_or_type

        # Optional parameters with defaults
        validated_data["runtime_hours"] = (
            runtime_hours or defaults["server_cost"]["runtime_hours"]
        )
        if not runtime_hours:
            applied_defaults["runtime_hours"] = defaults["server_cost"][
                "runtime_hours"
            ]
            warnings.append(
                "Assuming 24/7 operation (720 hours/month). "
                "Specify runtime_hours if different."
            )

        validated_data["storage_gb"] = (
            storage_gb or defaults["server_cost"]["storage_gb"]
        )
        if not storage_gb:
            applied_defaults["storage_gb"] = defaults["server_cost"][
                "storage_gb"
            ]

        validated_data["traffic_gb"] = (
            traffic_gb or defaults["server_cost"]["traffic_gb"]
        )
        if not traffic_gb:
            applied_defaults["traffic_gb"] = defaults["server_cost"][
                "traffic_gb"
            ]

    # ========================================================================
    # Multi-Agent Workflow (handled differently - needs agent list)
    # ========================================================================
    elif request_type == "multi_agent":
        return {
            "status": "need_info",
            "message": (
                "For multi-agent workflows, please provide a list of agents "
                "with their configurations. Each agent needs:\n"
                "- name: Agent identifier\n"
                "- model: LLM model used\n"
                "- avg_tokens_per_call: Token usage\n"
                "- calls_per_day: Call frequency"
            ),
            "required_field": "agents",
            "example": {
                "type": "multi_agent",
                "agents": [
                    {
                        "name": "research",
                        "model": "gemini-2.5-flash-lite",
                        "avg_tokens_per_call": 2000,
                        "calls_per_day": 40
                    },
                    {
                        "name": "coder",
                        "model": "gpt-4o-mini",
                        "avg_tokens_per_call": 3000,
                        "calls_per_day": 20
                    }
                ]
            }
        }

    else:
        return {
            "status": "error",
            "message": (
                f"Unknown request type: {request_type}. "
                "Supported types: llm_cost, server_cost, multi_agent"
            )
        }

    # Calculate confidence based on missing fields
    confidence = 1.0 - min(0.5, len(missing_fields) * 0.1)

    return {
        "status": "success",
        "validated_data": validated_data,
        "missing_fields": missing_fields,
        "applied_defaults": applied_defaults,
        "warnings": warnings,
        "questions": questions,
        "confidence": confidence,
        "message": (
            f"Information collected successfully! "
            f"Confidence: {confidence:.0%}"
        )
    }


# ============================================================================
# TOOL 2: Cost Calculation Helper
# ============================================================================

def calculate_cost_estimate(
    validated_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate cost estimates using deterministic pricing functions.

    Args:
        validated_data: Validated project data from collect_project_information

    Returns:
        Dictionary with cost breakdown, formula, and recommendations
    """
    from my_agent.calculators import (
        estimate_llm_cost,
        estimate_server_cost,
        estimate_multi_agent_cost,
    )

    request_type = validated_data.get("type")

    try:
        # LLM cost calculation
        if request_type == "llm_cost":
            result = estimate_llm_cost(
                model=validated_data["model"],
                avg_tokens_per_call=validated_data["avg_tokens_per_call"],
                calls_per_day=validated_data["calls_per_day"],
                days=validated_data.get("days", 30),
                include_output=validated_data.get("include_output", True),
                retry_rate=validated_data.get("retry_rate", 0.0),
            )
            formula = (
                "Monthly Cost = (tokens/call × calls/day × days ÷ 1M) × "
                "price_per_1M"
            )
            breakdown = {"llm_cost": result["monthly_cost"]}

        # Server cost calculation
        elif request_type == "server_cost":
            result = estimate_server_cost(
                provider=validated_data["provider"],
                plan_or_type=validated_data["plan_or_type"],
                runtime_hours=validated_data.get("runtime_hours", 720),
                storage_gb=validated_data.get("storage_gb", 20),
                traffic_gb=validated_data.get("traffic_gb", 50),
            )
            formula = "Monthly Cost = base_plan + storage + traffic"
            breakdown = {
                "base_plan": result["base_cost"],
                "storage": result["storage_cost"],
                "traffic": result["traffic_cost"],
            }

        # Multi-agent workflow calculation
        elif request_type == "multi_agent":
            result = estimate_multi_agent_cost(
                validated_data["agents"],
                days=validated_data.get("days", 30)
            )
            formula = "Workflow Cost = Σ(all agent costs)"
            breakdown = {
                agent["name"]: agent["cost"]
                for agent in result.get("agents", [])
            }

        else:
            return {
                "status": "error",
                "message": f"Unknown request type: {request_type}"
            }

        return {
            "status": "success",
            "monthly_cost": result.get(
                "monthly_cost",
                result.get("total_monthly_cost", 0.0)
            ),
            "daily_cost": result.get("daily_cost", 0.0),
            "currency": result.get("currency", "USD"),
            "breakdown": breakdown,
            "formula": formula,
            "raw_result": result,
            "message": "Cost calculation completed successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Cost calculation failed: {str(e)}",
            "details": str(e)
        }


# ============================================================================
# AGENT 1: Information Collector
# ============================================================================

InformationCollectorAgent = Agent(
    name="InformationCollector",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are an AI cost estimation specialist. Your job is to gather "
        "complete information about the user's AI project.\n\n"
        "WORKFLOW:\n"
        "1. Greet the user and ask what type of cost they want to calculate\n"
        "2. Use collect_project_information tool to gather required data\n"
        "3. If information is missing, ask specific follow-up questions\n"
        "4. When you have complete data, confirm with the user\n"
        "5. Return the validated data for cost calculation\n\n"
        "BE CONVERSATIONAL:\n"
        "- Ask clear, specific questions\n"
        "- Explain why you need each piece of information\n"
        "- Offer examples when helpful\n"
        "- Summarize what you've collected\n\n"
        "KEY QUESTIONS TO ASK:\n"
        "For LLM costs:\n"
        "- Which model? (gpt-4o, gemini-2.5-flash-lite, claude, etc.)\n"
        "- How many API calls per day?\n"
        "- Average tokens per call? (or typical prompt/response size)\n\n"
        "For server costs:\n"
        "- Which cloud provider? (AWS, DigitalOcean, GCP)\n"
        "- Which plan/instance type?\n"
        "- How many hours per month will it run?\n"
        "- Storage and bandwidth needs?\n\n"
        "Use google_search if you need current pricing info or typical "
        "usage patterns."
    ),
    tools=[collect_project_information, google_search],
    output_key="collection_report",
)


# ============================================================================
# AGENT 2: Cost Calculator
# ============================================================================

CostCalculatorAgent = Agent(
    name="CostCalculator",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are a cost calculation specialist. Given validated project data, "
        "calculate accurate cost estimates.\n\n"
        "WORKFLOW:\n"
        "1. Receive validated_data from the InformationCollector\n"
        "2. Use calculate_cost_estimate tool to compute costs\n"
        "3. Analyze the results and identify optimization opportunities\n"
        "4. Present clear, actionable cost breakdown\n\n"
        "YOUR ANALYSIS SHOULD INCLUDE:\n"
        "- Total monthly and daily costs\n"
        "- Cost breakdown by component\n"
        "- Formula used for transparency\n"
        "- Confidence level based on data quality\n"
        "- 2-3 optimization recommendations\n"
        "- Alternative cheaper options if available\n\n"
        "OPTIMIZATION TIPS:\n"
        "- Suggest cheaper models with similar performance\n"
        "- Recommend caching for high-volume usage\n"
        "- Identify cost drivers (e.g., high token usage)\n"
        "- Suggest reserved instances for 24/7 workloads\n\n"
        "Use google_search to find:\n"
        "- Alternative models/services\n"
        "- Current pricing updates\n"
        "- Cost-saving strategies"
    ),
    tools=[calculate_cost_estimate, google_search],
    output_key="calculation_summary",
)


# ============================================================================
# ROOT COORDINATOR: TokenTracker
# ============================================================================

TokenTrackerCoordinator = SequentialAgent(
    name="TokenTrackerCoordinator",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You are TokenTracker, a professional AI cost estimation system.\n\n"
        "YOUR MISSION:\n"
        "Help users understand and optimize their AI infrastructure costs "
        "BEFORE deployment.\n\n"
        "WORKFLOW:\n"
        "1. Delegate to InformationCollector to gather project details\n"
        "2. Delegate to CostCalculator to compute accurate costs\n"
        "3. Synthesize findings into an executive summary\n\n"
        "YOUR EXECUTIVE SUMMARY MUST INCLUDE:\n"
        "- Clear cost breakdown (monthly/daily)\n"
        "- Confidence level and assumptions made\n"
        "- Data freshness (when pricing was last updated)\n"
        "- Top 3 actionable optimization opportunities\n"
        "- Next steps for the user\n\n"
        "TONE:\n"
        "- Professional but approachable\n"
        "- Transparent about limitations\n"
        "- Action-oriented\n"
        "- Data-driven\n\n"
        "Remember: Your goal is to help users make informed decisions and "
        "avoid budget surprises in production."
    ),
    sub_agents=[InformationCollectorAgent, CostCalculatorAgent],
    output_key="coordinator_summary",
)
