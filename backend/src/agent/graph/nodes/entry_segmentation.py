"""Entry segmentation node: choose which specialized segmentation track to run.

This node inspects the incoming `state` and sets a `routing_hint` that points
to one of the specialized segmentation nodes. It does not perform deep
classification itself.

Routing preference (checked in order):
- `behavior_summary` -> `behavior_seg`
- `customer_profile` -> `profile_seg`
- `rfm_signals` -> `rfm_seg`
- `user_query` or `intent` -> `intent_seg`
"""
from typing import Any


async def entry_segmentation(state: Any, runtime: Any = None) -> Any:
    # normalize access for dict-like or State-like objects
    def has(key: str) -> bool:
        if isinstance(state, dict):
            return key in state and state.get(key) is not None
        return hasattr(state, key) and getattr(state, key) is not None

    # decide routing target
    if has("behavior_summary"):
        target = "behavior_seg"
    elif has("customer_profile"):
        target = "profile_seg"
    elif has("rfm_signals"):
        target = "rfm_seg"
    elif has("user_query") or has("intent"):
        target = "intent_seg"
    else:
        # fallback to behavior segmentation when unsure
        target = "behavior_seg"

    # attach routing hint to state so the StateGraph conditional routing can pick it
    try:
        if isinstance(state, dict):
            state["routing_hint"] = target
        else:
            setattr(state, "routing_hint", target)
    except Exception:
        # Best-effort; if mutation fails, return a minimal dict with routing
        return {"routing_hint": target}

    return state
