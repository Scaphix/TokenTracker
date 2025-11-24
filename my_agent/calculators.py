"""Deterministic pricing calculators that consume the pricing cache."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple
from google.adk.agents import Agent
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "database.json"


def _load_database() -> Dict[str, Any]:
    with open(DATABASE_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _ensure_positive(value: float, field: str) -> float:
    if value <= 0:
        raise ValueError(f"{field} must be greater than zero (got {value})")
    return value


def _resolve_model_pricing(
    model: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    database = _load_database()
    metadata = database.get("metadata", {})
    pricing = database.get("pricing", {}).get("models", {})
    if model not in pricing:
        raise KeyError(
            f"Model `{model}` not found in pricing database."
        )
    return pricing[model], metadata


def _resolve_server_pricing(
    provider: str,
    plan: str,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    database = _load_database()
    metadata = database.get("metadata", {})
    pricing = database.get("pricing", {}).get("servers", {}).get(provider)
    if pricing is None or plan not in pricing:
        raise KeyError(
            f"Plan `{plan}` for provider `{provider}` not found."
        )
    return pricing[plan], metadata


def estimate_llm_cost(
    model: str,
    avg_tokens_per_call: float,
    calls_per_day: float,
    days: int = 30,
    include_output: bool = True,
    retry_rate: float = 0.0,
) -> Dict[str, Any]:
    """Calculate LLM API costs and expose pricing metadata."""
    pricing, metadata = _resolve_model_pricing(model)

    avg_tokens_per_call = _ensure_positive(
        avg_tokens_per_call,
        "avg_tokens_per_call",
    )
    calls_per_day = _ensure_positive(calls_per_day, "calls_per_day")
    days = int(_ensure_positive(days, "days"))
    retry_rate = max(0.0, retry_rate)

    input_price = pricing["input_per_1m"]
    output_price = pricing["output_per_1m"]

    total_input_tokens = avg_tokens_per_call * calls_per_day * days
    output_ratio = 0.25 if include_output else 0.0
    total_output_tokens = total_input_tokens * output_ratio

    total_input_tokens *= 1 + retry_rate
    total_output_tokens *= 1 + retry_rate

    input_cost = (total_input_tokens / 1_000_000) * input_price
    output_cost = (total_output_tokens / 1_000_000) * output_price
    monthly_cost = input_cost + output_cost

    return {
        "monthly_cost": monthly_cost,
        "daily_cost": monthly_cost / days,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_tokens": total_input_tokens + total_output_tokens,
        "price_per_1m": input_price,
        "currency": pricing.get(
            "currency",
            metadata.get("currency", "USD"),
        ),
        "pricing_source": pricing.get("source"),
        "retrieved_at": pricing.get("retrieved_at"),
        "metadata": metadata,
    }


def estimate_server_cost(
    provider: str,
    plan_or_type: str,
    runtime_hours: float = 720,
    storage_gb: float = 20,
    traffic_gb: float = 50,
) -> Dict[str, Any]:
    """Calculate server hosting costs with metadata."""
    pricing, metadata = _resolve_server_pricing(provider, plan_or_type)

    runtime_hours = _ensure_positive(runtime_hours, "runtime_hours")
    storage_gb = max(0.0, storage_gb)
    traffic_gb = max(0.0, traffic_gb)

    base_cost = pricing["base_monthly"]
    storage_cost = storage_gb * pricing.get("storage_gb_price", 0.0)
    traffic_cost = traffic_gb * pricing.get("traffic_gb_price", 0.0)

    runtime_ratio = runtime_hours / 720
    adjusted_base = base_cost * runtime_ratio
    monthly_cost = adjusted_base + storage_cost + traffic_cost

    return {
        "monthly_cost": monthly_cost,
        "daily_cost": monthly_cost / 30,
        "base_cost": adjusted_base,
        "storage_cost": storage_cost,
        "traffic_cost": traffic_cost,
        "currency": pricing.get(
            "currency",
            metadata.get("currency", "USD"),
        ),
        "pricing_source": pricing.get("source"),
        "retrieved_at": pricing.get("retrieved_at"),
        "metadata": metadata,
    }


def estimate_multi_agent_cost(
    agents: List[Dict[str, Any]],
    days: int = 30,
) -> Dict[str, Any]:
    """Aggregate multiple agent LLM costs."""
    if not agents:
        raise ValueError("At least one agent definition is required.")

    days = int(_ensure_positive(days, "days"))
    breakdown = []
    total = 0.0
    metadata_snapshot: Dict[str, Any] = {}

    for agent in agents:
        required = {"name", "model", "avg_tokens_per_call", "calls_per_day"}
        missing = required.difference(agent)
        if missing:
            needed = ", ".join(missing)
            raise ValueError(f"Agent entry missing fields: {needed}")

        llm_result = estimate_llm_cost(
            model=agent["model"],
            avg_tokens_per_call=agent["avg_tokens_per_call"],
            calls_per_day=agent["calls_per_day"],
            days=days,
            include_output=agent.get("include_output", True),
            retry_rate=agent.get("retry_rate", 0.0),
        )

        breakdown.append(
            {
                "name": agent["name"],
                "cost": llm_result["monthly_cost"],
            }
        )
        total += llm_result["monthly_cost"]
        metadata_snapshot.setdefault(
            agent["model"],
            {
                "retrieved_at": llm_result.get("retrieved_at"),
                "source": llm_result.get("pricing_source"),
            },
        )

    return {
        "total_monthly_cost": total,
        "daily_cost": total / days,
        "agents": breakdown,
        "metadata": metadata_snapshot,
    }


# Price Calculator Agent
price_calculator_agent = Agent(
    name="price_Calculator",
    model="gemini-2.5-flash-lite",
    instruction="""You are a cost calculation specialist.
    Using the collected information: {collected_information}
""",
    tools=[estimate_llm_cost, estimate_server_cost, estimate_multi_agent_cost],
    output_key="price_analysis"
)

print("✅ price_calculator_agent created.")
