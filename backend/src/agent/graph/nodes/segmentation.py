"""Deterministic, explainable segmentation node for customer behavior.

This module provides a single async function `segmentation_node` which accepts
a State or plain dict and returns a segmentation label, human-readable reasons,
a compact metadata object for observability, and an optional routing_hint for
upstream workflow routing.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import State


# Configuration: make thresholds tunable via env vars for quick tuning without code changes
VIEWS_THRESHOLD = int(os.getenv("SEGMENT_VIEWS_THRESHOLD", "10"))
PURCHASES_THRESHOLD = int(os.getenv("SEGMENT_PURCHASES_THRESHOLD", "1"))


logger = logging.getLogger(__name__)


async def segmentation_node(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Deterministic, explainable segmentation logic.

    The node accepts either a `State` instance or a plain dict. It examines
    behavioral signals and simple rules to return a segment label, a list of
    human-readable reasons, and optional routing_hint used by the workflow.

    Rules (ordered):
    - recent_buyer: purchases_last_30d > 0
    - frequent_browser: views_last_7d >= 10 and purchases_last_30d == 0
    - form_abandoned / cart_abandoned: last_event indicates abandonment
    - new_or_casual: fallback
    """
    # Support both State objects and plain dicts for easy testing. Validate early.
    if state is None:
        logger.debug("segmentation_node called with state=None, treating as empty dict")
        state = {}

    behavior = (
        getattr(state, "behavior_summary", None)
        if hasattr(state, "behavior_summary")
        else (state.get("behavior_summary") if isinstance(state, dict) else None)
    ) or {}

    # Try to find a last_event from behavior or customer_profile
    last_event = None
    if isinstance(state, dict):
        last_event = state.get("last_event") or (state.get("customer_profile") or {}).get("last_event")
    else:
        last_event = getattr(state, "last_event", None) or (getattr(state, "customer_profile", {}) or {}).get("last_event")

    # Normalize numeric values defensively: malformed values treated as 0
    def _to_int(value: Any, default: int = 0) -> int:
        try:
            return int(value or 0)
        except Exception:
            logger.debug("Failed to parse int from value=%r, defaulting to %d", value, default)
            return default

    views = _to_int(behavior.get("views_last_7d", 0), 0)
    purchases = _to_int(behavior.get("purchases_last_30d", 0), 0)

    reasons: List[str] = []
    routing_hint = None

    if purchases >= PURCHASES_THRESHOLD:
        segment = "recent_buyer"
        reasons.append(f"purchases_last_30d={purchases}")
    elif views >= VIEWS_THRESHOLD and purchases < PURCHASES_THRESHOLD:
        segment = "frequent_browser"
        reasons.append(f"views_last_7d={views}")
        reasons.append("no_recent_purchases")
        routing_hint = "offers"
    elif last_event and any(k in str(last_event).lower() for k in ("form", "abandon", "abandoned", "cart")):
        if "form" in str(last_event).lower():
            segment = "form_abandoned"
        else:
            segment = "cart_abandoned"
        reasons.append(f"last_event={last_event}")
    else:
        segment = "new_or_casual"
        reasons.append("no_significant_activity")

    # Log the decision for observability (debug/info depending on environment)
    logger.info(
        "segmentation decision: segment=%s views=%d purchases=%d rule=%s",
        segment,
        views,
        purchases,
        "recent_buyer" if purchases >= PURCHASES_THRESHOLD else ("views_high_no_purchases" if views >= VIEWS_THRESHOLD else ("abandonment_detected" if "abandon" in " ".join(reasons) else "default")),
    )

    segment_metadata = {
        "rule_applied": (
            "purchases_present"
            if purchases >= PURCHASES_THRESHOLD
            else ("views_high_no_purchases" if views >= VIEWS_THRESHOLD else ("abandonment_detected" if "abandon" in " ".join(reasons) else "default"))
        ),
        "views_last_7d": views,
        "purchases_last_30d": purchases,
        "config": {"views_threshold": VIEWS_THRESHOLD, "purchases_threshold": PURCHASES_THRESHOLD},
    }

    return {
        "segment": segment,
        "reasons": reasons,
        "segment_metadata": segment_metadata,
        "routing_hint": routing_hint,
    }

