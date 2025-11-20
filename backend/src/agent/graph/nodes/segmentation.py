from __future__ import annotations
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def segmentation_node(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Runs segmentation. Returns segment, segment_metadata and optional routing_hint."""
    # Placeholder logic: replace with your real segmentation call
    return {
        "segment": "frequent_browser",
        "segment_metadata": {"rule_applied": "demo_rule"},
        "routing_hint": None,
    }
