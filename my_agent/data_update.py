"""Shared configuration for TokenTracker's Google ADK agents."""
from __future__ import annotations

from pathlib import Path

# Centralized model selection so every agent stays in sync.
ADK_MODEL = "gemini-2.5-flash-lite"

# Where pricing data is cached locally after each refresh pass.
DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "database.json"

# Targets that the pricing updater should attempt to refresh.
PRICING_TARGETS = {
    "llm": [
        {"provider": "openai", "models": ["gpt-4o", "gpt-4o-mini"]},
        {"provider": "google", "models": ["gemini-2.5-flash-lite"]},
        {"provider": "anthropic", "models": ["claude-3-5-sonnet"]},
    ],
    "server": [
        {"provider": "aws", "plans": ["t2.micro", "t2.small"]},
        {"provider": "digitalocean", "plans": ["basic_1", "basic_2"]},
    ],
    "currency": "USD",
    "sources": [
        "official provider pricing pages",
        "public API references",
        "recent blog announcements",
    ],
}

# Refresh pricing data at least once per day.
PRICING_REFRESH_TTL_HOURS = 24
