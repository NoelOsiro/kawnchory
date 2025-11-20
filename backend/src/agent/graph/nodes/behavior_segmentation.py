"""Specialized behavior-based segmentation wrapper.

This wrapper calls the existing `segmentation_node` to compute a segment
based on behavior signals and returns the augmented state for downstream nodes.
"""
from typing import Any, Dict, List

from agent.state import State


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except Exception:
        return default


async def behavior_seg(state: Any, runtime: Any = None) -> Any:
    """Behavior-driven segmentation.

    Produces `segment`, `reasons`, `segment_metadata`, and `routing_hint`.
    """
    # extract behavior signals
    if isinstance(state, dict):
        behavior = state.get("behavior_summary") or {}
        last_event = state.get("last_event") or (state.get("customer_profile") or {}).get("last_event")
    else:
        behavior = getattr(state, "behavior_summary", {}) or {}
        last_event = getattr(state, "last_event", None) or (getattr(state, "customer_profile", {}) or {}).get("last_event")

    views = _to_int(behavior.get("views_last_7d", 0))
    purchases = _to_int(behavior.get("purchases_last_30d", 0))

    reasons: List[str] = []
    routing_hint = None

    if purchases > 0:
        segment = "recent_buyer"
        reasons.append(f"purchases_last_30d={purchases}")
    elif views >= 10 and purchases == 0:
        segment = "frequent_browser"
        reasons.append(f"views_last_7d={views}")
        reasons.append("no_recent_purchases")
        routing_hint = "offers"
    elif last_event and any(k in str(last_event).lower() for k in ("form", "abandon", "abandoned", "cart")):
        segment = "abandonment"
        reasons.append(f"last_event={last_event}")
        routing_hint = "offers"
    else:
        segment = "new_or_casual"
        reasons.append("no_significant_activity")

    segment_metadata: Dict[str, Any] = {
        "views_last_7d": views,
        "purchases_last_30d": purchases,
        "rule_applied": "behavior_rule",
    }

    result = {
        "segment": segment,
        "reasons": reasons,
        "segment_metadata": segment_metadata,
        "routing_hint": routing_hint,
    }

    try:
        if isinstance(state, dict):
            state.update(result)
            return state
        else:
            for k, v in result.items():
                try:
                    setattr(state, k, v)
                except Exception:
                    pass
            return state
    except Exception:
        return result
