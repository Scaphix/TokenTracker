"""
Google search tool for finding pricing information.

Searches the web for current pricing data for AI models and cloud providers.
"""
from __future__ import annotations

from typing import Any, Dict


def google_search(
    query: str,
    model_name: str = None,
    provider: str = None,
) -> Dict[str, Any]:
    """
    Search Google for pricing information about AI models or cloud providers.

    This tool searches for current pricing data and provides guidance on
    where to find official pricing information.

    Args:
        query: The search query (e.g., "GPT-4o pricing 2024")
        model_name: The model name to search for (e.g., "gpt-4o", "gemini-3")
        provider: The provider name (e.g., "openai", "google", "anthropic")

    Returns:
        Dictionary with search guidance, suggested sources, and pricing hints
    """
    # Build intelligent search guidance based on provider/model
    search_guidance = _generate_search_guidance(model_name, provider)
    
    # Generate the optimal search query
    if not query and model_name:
        query = f"{model_name} API pricing per million tokens 2024"
    
    return {
        "status": "search_guidance",
        "query": query,
        "model_name": model_name,
        "provider": provider,
        "message": (
            f"To find pricing for '{model_name or query}':\n\n"
            f"{search_guidance}\n\n"
            "NOTE: Automated web search is not yet implemented.\n"
            "Please visit the suggested source and provide the pricing information.\n\n"
            "Expected format:\n"
            "- Input token price (per 1M tokens): $X.XX\n"
            "- Output token price (per 1M tokens): $Y.YY"
        ),
        "search_guidance": search_guidance,
        "next_step": "User provides pricing → use save_to_database tool"
    }


def _generate_search_guidance(model_name: str = None, provider: str = None) -> str:
    """Generate intelligent search guidance based on model/provider."""
    if not model_name and not provider:
        return "🔍 Please specify a model name or provider to search for."
    
    identifier = (model_name or "").lower()
    prov = (provider or "").lower()
    
    # OpenAI / GPT models
    if "gpt" in identifier or "openai" in prov:
        return (
            "📍 Official Source: https://openai.com/api/pricing/\n"
            "Look for your specific GPT model in the pricing table.\n"
            "Models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo"
        )
    
    # Google / Gemini models
    elif "gemini" in identifier or "google" in prov:
        return (
            "📍 Official Source: https://ai.google.dev/pricing\n"
            "⚠️ Note: 'Gemini 3' doesn't exist yet!\n"
            "Available Gemini models:\n"
            "- gemini-2.0-flash-exp (newest)\n"
            "- gemini-1.5-pro\n"
            "- gemini-1.5-flash\n"
            "- gemini-2.5-flash-lite"
        )
    
    # Anthropic / Claude models
    elif "claude" in identifier or "anthropic" in prov:
        return (
            "📍 Official Source: https://www.anthropic.com/pricing\n"
            "Look for Claude models (3.5 Sonnet, 3.5 Haiku, etc.)"
        )
    
    # AWS
    elif "aws" in identifier or "aws" in prov:
        return (
            "📍 Official Source: https://aws.amazon.com/ec2/pricing/\n"
            "Search for your instance type (e.g., t2.micro, t3.medium)"
        )
    
    # DigitalOcean
    elif "digitalocean" in identifier or "digitalocean" in prov:
        return (
            "📍 Official Source: https://www.digitalocean.com/pricing\n"
            "Check Droplet pricing for your plan"
        )
    
    # Generic
    else:
        return (
            f"🔍 Search Google for: '{model_name or provider} API pricing 2024'\n"
            "Look for official provider documentation or pricing pages."
        )

