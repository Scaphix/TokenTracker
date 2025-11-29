"""
Database checking tool.

Checks if pricing data exists in database.json for a given model or provider.
"""
from __future__ import annotations

from typing import Any, Dict
import json

from my_agent.data_update import DATABASE_PATH


def check_pricing_in_database(
    identifier: str,
    data_type: str = "llm_model",
) -> Dict[str, Any]:
    """
    Check if pricing data exists in the database for a model or provider.

    Args:
        identifier: Model name (e.g., "gpt-4o") or provider (e.g., "aws")
        data_type: Type of data to check ("llm_model" or "cloud_provider")

    Returns:
        Dictionary indicating if pricing exists and showing the data if found
    """
    try:
        # Load database
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)

        # Check LLM models
        if data_type == "llm_model":
            llm_models = db.get("llm_models", {})
            
            if identifier in llm_models:
                pricing = llm_models[identifier]
                return {
                    "status": "found",
                    "exists": True,
                    "identifier": identifier,
                    "data_type": data_type,
                    "pricing_data": pricing,
                    "message": f"✓ Pricing found for {identifier}",
                    "details": {
                        "price_input": pricing.get("price_input"),
                        "price_output": pricing.get("price_output"),
                        "currency": pricing.get("currency", "USD"),
                        "unit": pricing.get("unit", "per_1m_tokens"),
                        "last_updated": pricing.get("last_updated", "unknown"),
                    }
                }
            else:
                return {
                    "status": "not_found",
                    "exists": False,
                    "identifier": identifier,
                    "data_type": data_type,
                    "message": f"✗ Pricing NOT found for {identifier}",
                    "available_models": list(llm_models.keys())[:10],  # Show first 10
                    "suggestion": "Pricing data needs to be added to database"
                }

        # Check cloud providers
        elif data_type == "cloud_provider":
            cloud_providers = db.get("cloud_providers", {})
            
            if identifier in cloud_providers:
                pricing = cloud_providers[identifier]
                return {
                    "status": "found",
                    "exists": True,
                    "identifier": identifier,
                    "data_type": data_type,
                    "pricing_data": pricing,
                    "message": f"✓ Pricing found for {identifier}",
                    "plans": list(pricing.keys()) if isinstance(pricing, dict) else []
                }
            else:
                return {
                    "status": "not_found",
                    "exists": False,
                    "identifier": identifier,
                    "data_type": data_type,
                    "message": f"✗ Pricing NOT found for {identifier}",
                    "available_providers": list(cloud_providers.keys()),
                    "suggestion": "Pricing data needs to be added to database"
                }

        else:
            return {
                "status": "error",
                "message": f"Unknown data_type: {data_type}. Use 'llm_model' or 'cloud_provider'"
            }

    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"Database file not found at {DATABASE_PATH}"
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Database file is corrupted or invalid JSON"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking database: {str(e)}"
        }

