from __future__ import annotations

from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def delivery_node(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Final delivery step: publish or return the generated message."""
    if isinstance(state, dict):
        message = state.get("generated_message")
    else:
        message = getattr(state, "generated_message", None)

    return {"delivered_message": message}
