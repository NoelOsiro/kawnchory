from __future__ import annotations
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def delivery_node(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Final delivery step: publish or return the generated message."""
    return {"delivered_message": state.generated_message}
