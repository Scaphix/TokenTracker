"""
Cost calculation tool for AI infrastructure.

This module provides deterministic cost calculation functions
based on validated project data.
"""
from __future__ import annotations

from typing import Any, Dict


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
                "Monthly Cost = (tokens/call * calls/day * days ÷ 1M) * "
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

