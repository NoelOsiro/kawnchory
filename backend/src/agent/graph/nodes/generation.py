from __future__ import annotations
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def generation_node(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Generate natural language message from offers and retrieved content."""
    # TODO: integrate LLM or chain/agent call
    return {
        "generated_message": f"Here are the best options we found for you ({state.segment}).",
        "generation_metadata": {},
    }
