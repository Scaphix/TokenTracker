"""
Database saving tool.

Saves pricing data to database.json for LLM models and cloud providers.
"""
from __future__ import annotations

from typing import Any, Dict
import json
from datetime import datetime

from my_agent.data_update import DATABASE_PATH


def save_to_database(
    identifier: str,
    data_type: str,
    price_input: float = None,
    price_output: float = None,
    price_base: float = None,
    price_storage: float = None,
    price_traffic: float = None,
    currency: str = "USD",
    source: str = None,
) -> Dict[str, Any]:
    """
    Save pricing data to database.json.

    This tool stores pricing information for LLM models or cloud providers.

    Args:
        identifier: Model name (e.g., "gpt-4o") or provider name (e.g., "aws")
        data_type: Type of data ("llm_model" or "cloud_provider")
        price_input: Input token price for LLM (per 1M tokens)
        price_output: Output token price for LLM (per 1M tokens)
        price_base: Base price for cloud provider (per hour or per month)
        price_storage: Storage price for cloud (per GB)
        price_traffic: Traffic price for cloud (per GB)
        currency: Currency code (default: USD)
        source: Source URL where pricing was found

    Returns:
        Dictionary with save status and confirmation
    """
    try:
        # Load existing database
        try:
            with open(DATABASE_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        except FileNotFoundError:
            # Create new database structure
            db = {
                "llm_models": {},
                "cloud_providers": {},
                "defaults": {
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
            }

        # Prepare pricing entry with timestamp
        timestamp = datetime.now().isoformat()
        
        # Save LLM model pricing
        if data_type == "llm_model":
            if price_input is None or price_output is None:
                return {
                    "status": "error",
                    "message": "For LLM models, both price_input and price_output are required"
                }
            
            pricing_entry = {
                "price_input": price_input,
                "price_output": price_output,
                "currency": currency,
                "unit": "per_1m_tokens",
                "last_updated": timestamp,
                "source": source or "manual_entry"
            }
            
            if "llm_models" not in db:
                db["llm_models"] = {}
            
            db["llm_models"][identifier] = pricing_entry
            
            # Save to file
            with open(DATABASE_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            return {
                "status": "success",
                "message": f"✓ Successfully saved pricing for {identifier}",
                "identifier": identifier,
                "data_type": data_type,
                "saved_data": pricing_entry,
                "details": f"Input: ${price_input}, Output: ${price_output} per 1M tokens"
            }

        # Save cloud provider pricing
        elif data_type == "cloud_provider":
            if price_base is None:
                return {
                    "status": "error",
                    "message": "For cloud providers, price_base is required"
                }
            
            pricing_entry = {
                "price_base": price_base,
                "price_storage": price_storage or 0.0,
                "price_traffic": price_traffic or 0.0,
                "currency": currency,
                "unit": "per_month",
                "last_updated": timestamp,
                "source": source or "manual_entry"
            }
            
            if "cloud_providers" not in db:
                db["cloud_providers"] = {}
            
            if identifier not in db["cloud_providers"]:
                db["cloud_providers"][identifier] = {}
            
            db["cloud_providers"][identifier]["default"] = pricing_entry
            
            # Save to file
            with open(DATABASE_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            return {
                "status": "success",
                "message": f"✓ Successfully saved pricing for {identifier}",
                "identifier": identifier,
                "data_type": data_type,
                "saved_data": pricing_entry,
                "details": f"Base: ${price_base}/month"
            }

        else:
            return {
                "status": "error",
                "message": f"Invalid data_type: {data_type}. Use 'llm_model' or 'cloud_provider'"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save to database: {str(e)}",
            "details": str(e)
        }

