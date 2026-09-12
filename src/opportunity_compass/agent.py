"""Strands agent assembly."""

from __future__ import annotations

import os

from strands import Agent

from .tools import inspect_public_page, score_verified_opportunity

SYSTEM_PROMPT = """You are Opportunity Compass, a conservative opportunity-verification agent.
Your job is to prevent a human from wasting time on stale, deceptive, ineligible, or
AI-prohibited earning opportunities.

Rules:
1. Treat aggregators as leads, never proof. Inspect the original source.
2. Never infer that an opportunity is open, free, AI-compatible, or payable.
3. Record unknown facts as unknown. Do not embellish rewards or odds.
4. Reject anything requiring an entry fee when the user requests zero-cost mode.
5. Do not perform security testing. You may only inspect published program rules.
6. Use score_verified_opportunity after gathering evidence.
7. Explain exactly which human-only action remains, if any.
"""


def build_agent() -> Agent:
    """Create the production Strands agent using the configured model provider."""
    provider = os.getenv("OPPORTUNITY_COMPASS_PROVIDER", "bedrock").lower()
    model_id = os.getenv("OPPORTUNITY_COMPASS_MODEL")
    kwargs: dict[str, object] = {
        "system_prompt": SYSTEM_PROMPT,
        "tools": [inspect_public_page, score_verified_opportunity],
        # The CLI prints the final result itself. Disabling the default streaming
        # callback keeps terminal output concise and avoids printing it twice.
        "callback_handler": None,
    }

    if provider == "ollama":
        from strands.models.ollama import OllamaModel

        kwargs["model"] = OllamaModel(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            model_id=model_id or "qwen3:4b",
            temperature=0.1,
        )
    elif provider == "bedrock" and model_id:
        kwargs["model"] = model_id
    elif provider != "bedrock":
        raise ValueError(f"Unsupported model provider: {provider}")
    return Agent(**kwargs)
