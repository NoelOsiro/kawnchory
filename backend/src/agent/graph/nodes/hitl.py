from __future__ import annotations
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def hitl_node(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Human-in-the-loop review step. Returns human_feedback when present."""
    # Placeholder: in production, integrate with task queue or UI for reviewers
    return {"human_feedback": None}
