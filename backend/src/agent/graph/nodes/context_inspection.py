"""Inspect and normalize incoming state before segmentation.

This node ensures downstream segmentation nodes receive a predictable
shape and sets flags useful for routing decisions.

Outputs (merges into state):
- `has_behavior`: bool
- `has_profile`: bool
- `has_rfm`: bool
- `has_intent`: bool
- `normalized_user_query`: str | None
- `segmentation_strategy`: one of 'behavior'|'profile'|'rfm'|'intent'|None

The node is intentionally simple and deterministic.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State

logger = logging.getLogger(__name__)


async def context_inspection(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Inspect and normalize incoming state before segmentation.

    Parameters
    ----------
    state : State | Dict[str, Any]
        Incoming state object or mapping containing keys like 'behavior_summary',
        'customer_profile', 'rfm_signals', 'user_query', or 'intent'.
    runtime : Runtime
        Execution runtime provided by langgraph (kept for node signature compatibility).

    Returns:
    -------
    Dict[str, Any]
        A dictionary of flags and normalized fields to merge into state, including:
        - has_behavior: bool
        - has_profile: bool
        - has_rfm: bool
        - has_intent: bool
        - normalized_user_query: Optional[str]
        - segmentation_strategy: Optional[str]

    Notes:
    -----
    The node is intentionally simple and deterministic; it should not raise under
    normal conditions and is safe for use in routing/segmentation pipelines.
    """
    out: Dict[str, Any] = {}

    def _get(key: str):
        if isinstance(state, dict):
            return state.get(key)
        return getattr(state, key, None)

    behavior = _get("behavior_summary") or {}
    profile = _get("customer_profile") or {}
    rfm = _get("rfm_signals") or {}
    user_query = _get("user_query") or _get("intent")

    has_behavior = bool(behavior and any(v is not None for v in behavior.values()))
    has_profile = bool(profile and any(v is not None for v in profile.values()))
    has_rfm = bool(rfm and any(v is not None for v in rfm.values()))
    has_intent = bool(user_query)

    # normalize simple query text
    normalized_user_query = None
    if has_intent:
        try:
            normalized_user_query = str(user_query).strip()
            if normalized_user_query == "":
                normalized_user_query = None
        except Exception:
            normalized_user_query = None

    out["has_behavior"] = has_behavior
    out["has_profile"] = has_profile
    out["has_rfm"] = has_rfm
    out["has_intent"] = has_intent
    out["normalized_user_query"] = normalized_user_query

    # Heuristic strategy: prefer profile when product_id present; intent when query present;
    # rfm when strong recency/frequency signals; fallback to behavior.
    strategy = None
    try:
        if profile and profile.get("product_id"):
            strategy = "profile"
        elif normalized_user_query:
            strategy = "intent"
        elif rfm and (rfm.get("recency_days") is not None or rfm.get("frequency") is not None):
            strategy = "rfm"
        elif has_behavior:
            strategy = "behavior"
    except Exception:
        strategy = None

    out["segmentation_strategy"] = strategy

    logger.debug("context_inspection: strategy=%s flags=%s", strategy, {k: out[k] for k in ("has_behavior","has_profile","has_rfm","has_intent")})

    return out
