"""Merge/normalize outputs from specialized segmentation nodes.

This node accepts the state after one of the specialized segmentation nodes
and returns a consistent shape that downstream nodes can rely on.

It ensures the final state contains:
- `segment`: canonical segment label
- `segment_reasons`: list[str]
- `segment_metadata`: dict
- `routing_hint`: optional str

This helps avoid fragmentation when different segmentation nodes return
slightly different keys.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State

logger = logging.getLogger(__name__)


async def segment_merge(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Normalize segmentation outputs into a single shape."""
    def _get(key: str, default=None):
        if isinstance(state, dict):
            return state.get(key, default)
        return getattr(state, key, default)

    # Prefer explicit keys commonly returned by segmentation nodes
    segment = _get("segment")
    reasons = _get("reasons") or _get("segment_reasons") or []
    if reasons is None:
        reasons = []
    # Ensure it's a list
    if not isinstance(reasons, list):
        reasons = [str(reasons)]

    metadata = _get("segment_metadata") or {}

    routing_hint = _get("routing_hint")

    # Log for observability
    logger.debug("segment_merge: segment=%s routing_hint=%s reasons=%s", segment, routing_hint, reasons)

    return {
        "segment": segment,
        "segment_reasons": reasons,
        "segment_metadata": metadata,
        "routing_hint": routing_hint,
    }
