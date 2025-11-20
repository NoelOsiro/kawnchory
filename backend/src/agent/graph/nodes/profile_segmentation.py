"""Profile-based segmentation wrapper.

Simple wrapper that delegates to `segmentation_node` for now. This file
keeps the specialized node slot available for future profile-specific logic.
"""
from typing import Any, Dict, Optional


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


async def profile_seg(state: Any, runtime: Any = None) -> Any:
    """Profile-driven segmentation.

    Look for `customer_profile` fields like `vip_tier` or `loyalty_score`
    and return a suitable segment and routing hint.
    """
    if isinstance(state, dict):
        profile = state.get("customer_profile") or {}
    else:
        profile = getattr(state, "customer_profile", {}) or {}

    vip = profile.get("vip_tier") or profile.get("tier")
    loyalty = _safe_float(profile.get("loyalty_score", 0.0))
    country = profile.get("country")

    reasons = []
    routing_hint: Optional[str] = None
    if vip and str(vip).lower() in ("gold", "platinum", "diamond"):
        segment = "vip"
        reasons.append(f"vip_tier={vip}")
        routing_hint = "generation"
    elif loyalty >= 80:
        segment = "loyal_customer"
        reasons.append(f"loyalty_score={loyalty}")
        routing_hint = "generation"
    elif country and str(country).lower() in ("us", "uk", "ca"):
        segment = "regional"
        reasons.append(f"country={country}")
        routing_hint = "offers"
    else:
        segment = "profile_unknown"
        reasons.append("no_profile_match")

    segment_metadata: Dict[str, Any] = {"rule_applied": "profile_rule", "loyalty_score": loyalty}

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
