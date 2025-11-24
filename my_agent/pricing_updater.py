from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from google.adk.agents import Agent, ParallelAgent
from google.adk.tools import google_search

from my_agent.data_update import (
    DATABASE_PATH,
    PRICING_REFRESH_TTL_HOURS,
    PRICING_TARGETS,
)
# --------------------- Database Helpers ---------------------


def _load_database() -> Dict[str, Any]:
    with open(DATABASE_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_database(payload: Dict[str, Any]) -> None:
    with open(DATABASE_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def should_refresh(metadata: Dict[str, Any]) -> bool:
    last = metadata.get("last_successful_update")
    if not last:
        return True

    try:
        last_dt = datetime.fromisoformat(last)
    except ValueError:
        return True

    window = timedelta(hours=PRICING_REFRESH_TTL_HOURS)
    return datetime.now(timezone.utc) - last_dt >= window
# --------------------- Agents ---------------------


LLMPricingAgent = Agent(
    name="LLMPricingAgent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "You gather token pricing for LLM APIs. "
        "Use google_search to find official pricing pages. "
        "Return JSON with `models`, each containing: "
        "{name, provider, input_per_1m, output_per_1m, "
        "currency, source, retrieved_at}. Always use USD per 1M tokens."
    ),
    tools=[google_search],
    output_key="llm_pricing",
)

ServerPricingAgent = Agent(
    name="ServerPricingAgent",
    model="gemini-2.5-flash-lite",
    instruction=(
        "Collect current monthly hosting prices for cloud providers. "
        "Use google_search. Respond with JSON containing `servers`, "
        "each with: {provider, plan, base_monthly, storage_gb_price, "
        "traffic_gb_price, currency, source, retrieved_at}."
    ),
    tools=[google_search],
    output_key="server_pricing",
)

PricingUpdater = ParallelAgent(
    name="PricingUpdater",
    model="gemini-2.5-flash-lite",
    instruction=(
        "Call LLMPricingAgent & ServerPricingAgent. "
        "Merge outputs into one JSON with keys `models` and `servers`."
    ),
    sub_agents=[LLMPricingAgent, ServerPricingAgent],
    output_key="pricing_payload",
)

# --------------------- Normalization ---------------------


def _normalize_model_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    required = ["name", "input_per_1m", "output_per_1m"]
    for field in required:
        if field not in entry:
            msg = f"Missing `{field}` in LLM pricing entry: {entry}"
            raise ValueError(msg)

    return {
        "name": entry["name"],
        "input_per_1m": float(entry["input_per_1m"]),
        "output_per_1m": float(entry["output_per_1m"]),
        "currency": entry.get("currency", PRICING_TARGETS["currency"]),
        "source": entry.get("source", "google_search"),
        "retrieved_at": entry.get(
            "retrieved_at",
            datetime.now(timezone.utc).isoformat()
        ),
        "notes": entry.get("notes", ""),
    }


def _normalize_server_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    required = ["provider", "plan", "base_monthly"]
    for field in required:
        if field not in entry:
            msg = f"Missing `{field}` in server pricing entry: {entry}"
            raise ValueError(msg)

    return {
        "provider": entry["provider"],
        "plan": entry["plan"],
        "base_monthly": float(entry["base_monthly"]),
        "storage_gb_price": float(entry.get("storage_gb_price", 0.0)),
        "traffic_gb_price": float(entry.get("traffic_gb_price", 0.0)),
        "currency": entry.get("currency", PRICING_TARGETS["currency"]),
        "source": entry.get("source", "google_search"),
        "retrieved_at": entry.get(
            "retrieved_at",
            datetime.now(timezone.utc).isoformat()
        ),
    }


def update_pricing_database(force: bool = False) -> Dict[str, Any]:
    database = _load_database()
    metadata = database.get("metadata", {})

    if not force and not should_refresh(metadata):
        return database

    payload = PricingUpdater.run(metadata=metadata)
    database["metadata"] = {
        **metadata,
        "last_successful_update": datetime.now(timezone.utc).isoformat()
    }
    database["pricing"] = payload
    _write_database(database)
    return database


update_pricing_database = Agent(
    name="update_pricing_database",
    model="gemini-2.5-flash-lite",
    instruction=(
        "Refresh pricing data if stale and persist the new snapshot."
    ),
    tools=[
        PricingUpdater,
        _normalize_model_entry,
        _normalize_server_entry,
        update_pricing_database,
        _load_database,
        _write_database,
        should_refresh,
    ],
    output_key="pricing_database",
)
