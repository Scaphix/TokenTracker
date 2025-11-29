"""
Server information collection tool.

Gathers project information specifically for server/hosting cost estimation.
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
            "server_cost": {
                "runtime_hours": 720,
                "storage_gb": 20,
                "traffic_gb": 50
            }
        }


def collect_server_information(
    provider: str = None,
    plan_or_type: str = None,
    runtime_hours: int = None,
    storage_gb: int = None,
    traffic_gb: int = None,
) -> Dict[str, Any]:
    """
    Collect information for server/hosting cost estimation.

    This tool gathers data needed to calculate server hosting costs.

    Args:
        provider: Server provider (aws, digitalocean, gcp, etc.)
        plan_or_type: Server plan/instance type
        runtime_hours: Monthly server runtime hours (default: 720 for 24/7)
        storage_gb: Storage in GB
        traffic_gb: Network traffic in GB

    Returns:
        Dictionary with validated data, applied defaults, and warnings
    """
    defaults = _load_defaults()["server_cost"]
    validated_data = {"type": "server_cost"}
    missing_fields = []
    applied_defaults = {}
    warnings = []

    # Required: provider
    if not provider:
        return {
            "status": "need_info",
            "missing_fields": ["provider"],
            "message": "Which cloud provider will host your AI agent?",
            "prompt": "Which hosting provider? (e.g., aws, digitalocean, gcp)"
        }
    validated_data["provider"] = provider

    # Required: plan_or_type (depends on provider)
    if not plan_or_type:
        return {
            "status": "need_info",
            "missing_fields": ["plan_or_type"],
            "message": f"Which {provider} plan will you use?",
            "prompt": f"Which {provider} plan/instance type? (e.g., t2.micro for AWS, basic_1 for DigitalOcean)"
        }
    validated_data["plan_or_type"] = plan_or_type

    # Optional: runtime_hours
    if runtime_hours:
        validated_data["runtime_hours"] = runtime_hours
    else:
        default_val = defaults["runtime_hours"]
        validated_data["runtime_hours"] = default_val
        applied_defaults["runtime_hours"] = default_val
        missing_fields.append("runtime_hours")
        warnings.append("Assuming 24/7 operation (720 hours/month). Specify runtime_hours if different.")

    # Optional: storage_gb
    if storage_gb:
        validated_data["storage_gb"] = storage_gb
    else:
        default_val = defaults["storage_gb"]
        validated_data["storage_gb"] = default_val
        applied_defaults["storage_gb"] = default_val
        missing_fields.append("storage_gb")

    # Optional: traffic_gb
    if traffic_gb:
        validated_data["traffic_gb"] = traffic_gb
    else:
        default_val = defaults["traffic_gb"]
        validated_data["traffic_gb"] = default_val
        applied_defaults["traffic_gb"] = default_val
        missing_fields.append("traffic_gb")

    # Calculate confidence
    confidence = 1.0 - min(0.5, len(missing_fields) * 0.1)

    return {
        "status": "success",
        "validated_data": validated_data,
        "missing_fields": missing_fields,
        "applied_defaults": applied_defaults,
        "warnings": warnings,
        "questions": [],
        "confidence": confidence,
        "message": f"Server information collected successfully! Confidence: {confidence:.0%}"
    }

