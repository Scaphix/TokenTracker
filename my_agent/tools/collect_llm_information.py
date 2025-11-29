"""
LLM information collection tool.

Gathers project information specifically for LLM cost estimation.
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
            "llm_cost": {
                "avg_tokens_per_call": 2000,
                "days": 30,
                "include_output": True,
                "retry_rate": 0.05
            }
        }


def collect_llm_information(
    model: str = None,
    avg_tokens_per_call: int = None,
    calls_per_day: int = None,
    days: int = None,
) -> Dict[str, Any]:
    """
    Collect information for LLM cost estimation.

    This tool gathers data needed to calculate LLM API costs.

    Args:
        model: LLM model name (e.g., gpt-4o, gemini-2.5-flash-lite)
        avg_tokens_per_call: Average tokens per API call
        calls_per_day: Number of API calls per day
        days: Number of days to calculate (default: 30)

    Returns:
        Dictionary with validated data, applied defaults, and warnings
    """
    defaults = _load_defaults()["llm_cost"]
    validated_data = {"type": "llm_cost"}
    missing_fields = []
    applied_defaults = {}
    warnings = []
    questions = []

    # Required: model
    if not model:
        return {
            "status": "need_info",
            "missing_fields": ["model"],
            "message": "To calculate LLM costs, I need to know which model you're using.",
            "prompt": "Which LLM model will you use? (e.g., gpt-4o, gemini-2.5-flash-lite, claude-3-5-sonnet)"
        }
    validated_data["model"] = model

    # Optional: avg_tokens_per_call
    if avg_tokens_per_call:
        validated_data["avg_tokens_per_call"] = avg_tokens_per_call
    else:
        default_val = defaults["avg_tokens_per_call"]
        validated_data["avg_tokens_per_call"] = default_val
        applied_defaults["avg_tokens_per_call"] = default_val
        missing_fields.append("avg_tokens_per_call")
        warnings.append(
            f"Using industry average: {default_val} tokens/call. "
            "For better accuracy, monitor your first 100 API calls."
        )

    # Optional: calls_per_day
    if calls_per_day:
        validated_data["calls_per_day"] = calls_per_day
    else:
        default_val = 50
        validated_data["calls_per_day"] = default_val
        applied_defaults["calls_per_day"] = default_val
        missing_fields.append("calls_per_day")
        questions.append("How many API calls do you expect per day?")
        warnings.append(
            f"Assuming {default_val} calls/day. Adjust based on your expected traffic."
        )

    # Optional: days
    validated_data["days"] = days or defaults["days"]
    if not days:
        applied_defaults["days"] = defaults["days"]

    # Extra fields
    validated_data["include_output"] = defaults["include_output"]
    validated_data["retry_rate"] = defaults["retry_rate"]

    # Calculate confidence
    confidence = 1.0 - min(0.5, len(missing_fields) * 0.1)

    return {
        "status": "success",
        "validated_data": validated_data,
        "missing_fields": missing_fields,
        "applied_defaults": applied_defaults,
        "warnings": warnings,
        "questions": questions,
        "confidence": confidence,
        "message": f"LLM information collected successfully! Confidence: {confidence:.0%}"
    }

