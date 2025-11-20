from __future__ import annotations
from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import State


async def offers_node(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Generate structured offers based on segment and retrieved docs."""
    # TODO: implement real offers generation
    return {
        "offers": [],
        "offers_metadata": {"segment": state.segment},
    }
