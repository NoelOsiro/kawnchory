from __future__ import annotations

from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def segmentation_node(state: State, runtime: Runtime) -> Dict[str, Any]:

    # state could be a dict or a State instance
    behavior = (
        state.behavior_summary
        if hasattr(state, "behavior_summary")
        else state.get("behavior_summary")
    ) or {}

    views = behavior.get("views_last_7d", 0)
    purchases = behavior.get("purchases_last_30d", 0)

    routing_hint = None
    if views >= 10 and purchases == 0:
        routing_hint = "offers"

    return {
        "segment": "frequent_browser",
        "segment_metadata": {
            "rule_applied": "views_high_no_purchases",
            "views_last_7d": views,
            "purchases_last_30d": purchases,
        },
        "routing_hint": routing_hint,
    }

