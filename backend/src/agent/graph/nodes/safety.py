from __future__ import annotations
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def safety_node(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Run safety checks on the generated message."""
    # TODO: plug in real safety classifier or policy
    return {
        "safety_passed": True,
        "safety_report": {},
    }
