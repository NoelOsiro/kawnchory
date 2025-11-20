from __future__ import annotations

from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def generation_node(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Generate natural language message from offers and retrieved content.

    This simple generator is deterministic and safe for unit tests. In
    production, replace with an LLM or a controlled prompt chain.
    """
    if isinstance(state, dict):
        segment = state.get("segment")
        offers = state.get("offers") or []
    else:
        segment = getattr(state, "segment", None)
        offers = getattr(state, "offers", None) or []

    message = f"Here are the best options we found for you ({segment})."
    if not offers:
        message = f"We didn't find direct offers for your segment ({segment}) right now."

    return {"generated_message": message, "generation_metadata": {"offers_count": len(offers)}}
