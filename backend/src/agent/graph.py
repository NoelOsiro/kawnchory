"""LangGraph single-node graph template.

This file keeps the graph logic. The `State` model has been moved
to `state.py` so behavioral signals and other schema items live
in a dedicated file.
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from .state import State


async def call_model(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Process input and return output.

    Uses runtime.context when available.
    """
    return {
        "changeme": "output from call_model. "
        f"Configured with {(runtime.context or {}).get('my_configurable_param') if getattr(runtime, 'context', None) else None}"
    }


# Define the graph. Context schema is optional; the runtime may still carry context.
graph = (
    StateGraph(State)
    .add_node(call_model)
    .add_edge("__start__", "call_model")
    .compile(name="New Graph")
)
