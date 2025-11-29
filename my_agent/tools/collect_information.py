"""
Information collection tool for AI cost estimation.

This module provides a schema-driven validation tool that gathers
project information from users through conversational interaction.
"""
from __future__ import annotations

from typing import Any, Dict
import json

from my_agent.data_update import DATABASE_PATH


# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

VALIDATION_SCHEMAS = {
    "llm_cost": {
        "required": [
            {
                "field": "model",
                "prompt": "Which LLM model will you use? (e.g., gpt-4o, gemini-2.5-flash-lite, claude-3-5-sonnet)",
                "message": "To calculate LLM costs, I need to know which model you're using."
            }
        ],
        "optional": [
            {
                "field": "avg_tokens_per_call",
                "default_key": "avg_tokens_per_call",
                "warning": "Using industry average: {value} tokens/call. For better accuracy, monitor your first 100 API calls."
            },
            {
                "field": "calls_per_day",
                "default_value": 50,
                "question": "How many API calls do you expect per day? (This helps estimate your usage pattern)",
                "warning": "Assuming {value} calls/day. Adjust based on your expected traffic."
            },
            {
                "field": "days",
                "default_key": "days"
            }
        ],
        "extra_fields": {
            "include_output": "include_output",
            "retry_rate": "retry_rate"
        }
    },
    "server_cost": {
        "required": [
            {
                "field": "provider",
                "prompt": "Which hosting provider? (e.g., aws, digitalocean, gcp)",
                "message": "Which cloud provider will host your AI agent?"
            },
            {
                "field": "plan_or_type",
                "prompt_template": "Which {provider} plan/instance type? (e.g., t2.micro for AWS, basic_1 for DigitalOcean)",
                "message_template": "Which {provider} plan will you use?",
                "depends_on": "provider"
            }
        ],
        "optional": [
            {
                "field": "runtime_hours",
                "default_key": "runtime_hours",
                "warning": "Assuming 24/7 operation (720 hours/month). Specify runtime_hours if different."
            },
            {
                "field": "storage_gb",
                "default_key": "storage_gb"
            },
            {
                "field": "traffic_gb",
                "default_key": "traffic_gb"
            }
        ]
    }
}


# ============================================================================
# INFORMATION COLLECTION TOOL
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

    # Special case: Multi-agent workflow
    if request_type == "multi_agent":
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

    # Get validation schema
    schema = VALIDATION_SCHEMAS.get(request_type)
    if not schema:
        return {
            "status": "error",
            "message": (
                f"Unknown request type: {request_type}. "
                "Supported types: llm_cost, server_cost, multi_agent"
            )
        }

    # Prepare tracking variables
    validated_data = {"type": request_type}
    missing_fields = []
    applied_defaults = {}
    warnings = []
    questions = []
    
    # Map all provided arguments
    provided_values = {
        "model": model,
        "avg_tokens_per_call": avg_tokens_per_call,
        "calls_per_day": calls_per_day,
        "days": days,
        "provider": provider,
        "plan_or_type": plan_or_type,
        "runtime_hours": runtime_hours,
        "storage_gb": storage_gb,
        "traffic_gb": traffic_gb
    }

    # ========================================================================
    # REQUIRED FIELDS VALIDATION (ask one at a time for better UX)
    # ========================================================================
    for field_def in schema.get("required", []):
        field_name = field_def["field"]
        field_value = provided_values.get(field_name)
        
        if not field_value:
            # Handle template-based prompts (e.g., provider-dependent questions)
            if "prompt_template" in field_def:
                prompt = field_def["prompt_template"].format(**validated_data)
                message = field_def["message_template"].format(**validated_data)
            else:
                prompt = field_def["prompt"]
                message = field_def["message"]
            
            questions.append(prompt)
            return {
                "status": "need_info",
                "missing_fields": [field_name],
                "questions": questions,
                "message": message
            }
        
        validated_data[field_name] = field_value

    # ========================================================================
    # OPTIONAL FIELDS WITH DEFAULTS
    # ========================================================================
    for field_def in schema.get("optional", []):
        field_name = field_def["field"]
        field_value = provided_values.get(field_name)
        
        if field_value:
            validated_data[field_name] = field_value
        else:
            # Apply default
            if "default_key" in field_def:
                default_val = defaults[request_type][field_def["default_key"]]
            else:
                default_val = field_def["default_value"]
            
            validated_data[field_name] = default_val
            applied_defaults[field_name] = default_val
            missing_fields.append(field_name)
            
            # Add warning if specified
            if "warning" in field_def:
                warnings.append(field_def["warning"].format(value=default_val))
            
            # Add question if specified
            if "question" in field_def:
                questions.append(field_def["question"])

    # ========================================================================
    # EXTRA FIELDS (copy from defaults)
    # ========================================================================
    for field_name, default_key in schema.get("extra_fields", {}).items():
        validated_data[field_name] = defaults[request_type][default_key]

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

