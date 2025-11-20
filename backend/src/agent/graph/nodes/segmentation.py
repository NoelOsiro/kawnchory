"""Deterministic, explainable segmentation node for customer behavior.

This module provides a single async function `segmentation_node` which accepts
a State or plain dict and returns a segmentation label, human-readable reasons,
a compact metadata object for observability, and an optional routing_hint for
upstream workflow routing.
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import State

# Configuration: make thresholds tunable via env vars for quick tuning without code changes
VIEWS_THRESHOLD = int(os.getenv("SEGMENT_VIEWS_THRESHOLD", "10"))
PURCHASES_THRESHOLD = int(os.getenv("SEGMENT_PURCHASES_THRESHOLD", "1"))


logger = logging.getLogger(__name__)


@dataclass
class ValidatedRequest:
    """A small container for extracted, validated input used by the decision logic.

    Attributes:
        behavior: dict of behavior signals (views_last_7d, purchases_last_30d, ...)
        last_event: raw last_event value if present
    """
    behavior: Dict[str, Any]
    last_event: Any


@dataclass
class SegmentResult:
    """Result of segmentation decision.

    Attributes:
        segment: chosen segment label
        reasons: human-readable reasons for the choice
        segment_metadata: compact metadata useful for observability
        routing_hint: optional routing hint for workflow routing
    """
    segment: str
    reasons: List[str]
    segment_metadata: Dict[str, Any]
    routing_hint: str | None


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except Exception:
        logger.debug("Failed to parse int from value=%r, defaulting to %d", value, default)
        return default


# --- Caching ---------------------------------------------------------------
# In-process LRU cache for development; Redis-backed cache for production when
# `SEGMENT_CACHE_REDIS` is configured. Cache key includes a small config
# fingerprint so changing thresholds invalidates cached values.
SEGMENT_CACHE_TTL = int(os.getenv("SEGMENT_CACHE_TTL", "3600"))
SEGMENT_CACHE_REDIS = os.getenv("SEGMENT_CACHE_REDIS")

_CACHE_FINGERPRINT = json.dumps({"v": 1, "views": VIEWS_THRESHOLD, "purchases": PURCHASES_THRESHOLD}, sort_keys=True)

redis_client = None
if SEGMENT_CACHE_REDIS:
    try:
        # Import lazily; if redis is not installed this will raise ImportError and
        # we silently continue using the in-process cache only.
        import redis  # type: ignore

        redis_client = redis.from_url(SEGMENT_CACHE_REDIS)
    except Exception:  # pragma: no cover - best-effort redis integration
        logger.exception("Failed to initialize redis client for segmentation cache; continuing without redis")


def _make_cache_key(state: Any) -> str:
    # Normalize the state to include only the signals relevant to segmentation
    # so transient or irrelevant keys do not create cache fragmentation.
    try:
        norm = _normalize_state_for_cache(state)
        serial = json.dumps(norm, sort_keys=True, default=str)
    except Exception:
        # Fallback to best-effort serialization
        try:
            serial = json.dumps(state or {}, sort_keys=True, default=str)
        except Exception:
            serial = str(state)

    # include config fingerprint to avoid stale cached entries when thresholds change
    payload = _CACHE_FINGERPRINT + "|" + serial
    key = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    logger.debug("segmentation cache key computed: %s (fingerprint=%s)", key, _CACHE_FINGERPRINT)
    return key


def _normalize_state_for_cache(state: Any) -> Dict[str, Any]:
    """Return a minimal, deterministic representation of `state` used for.

    cache key generation. This reduces cache fragmentation by only including
    the signals that affect segmentation decisions.
    """
    norm: Dict[str, Any] = {}
    if state is None:
        return norm

    # Extract behavior_summary in a predictable shape
    behavior = None
    if isinstance(state, dict):
        behavior = state.get("behavior_summary") or {}
        last_event = state.get("last_event") or (state.get("customer_profile") or {}).get("last_event")
    else:
        behavior = getattr(state, "behavior_summary", {}) or {}
        last_event = getattr(state, "last_event", None) or (getattr(state, "customer_profile", {}) or {}).get("last_event")

    # Coerce important numeric signals to ints to avoid string/float mismatches
    norm_behavior: Dict[str, int] = {}
    norm_behavior["views_last_7d"] = _to_int(behavior.get("views_last_7d", 0), 0)
    norm_behavior["purchases_last_30d"] = _to_int(behavior.get("purchases_last_30d", 0), 0)

    norm["behavior_summary"] = norm_behavior
    # Normalize last_event to a short string (lowercased) to keep keys small
    if last_event is not None:
        try:
            norm["last_event"] = str(last_event).strip().lower()
        except Exception:
            norm["last_event"] = str(last_event)

    return norm


@functools.lru_cache(maxsize=1024)
def _compute_segment_cached(key: str, serialized_state: str) -> Dict[str, Any]:
    # This is the in-process cached computation. Deserialize the payload and
    # compute segmentation using existing helpers. We return a plain dict so
    # callers don't rely on internal dataclasses.
    try:
        state = json.loads(serialized_state)
    except Exception:
        state = serialized_state
    validated = _validate_and_extract(state)
    result = _decide_segment(validated)
    return {
        "segment": result.segment,
        "reasons": result.reasons,
        "segment_metadata": result.segment_metadata,
        "routing_hint": result.routing_hint,
    }


def _get_cached_or_compute(state: Any) -> Dict[str, Any]:
    key = _make_cache_key(state)
    # Serialize the normalized state rather than the raw state to keep cache
    # entries consistent across equivalent inputs.
    try:
        serialized = json.dumps(_normalize_state_for_cache(state), sort_keys=True, default=str)
    except Exception:
        serialized = json.dumps(state or {}, sort_keys=True, default=str)

    # Try Redis first if configured
    if redis_client:
        try:
            cached = redis_client.get(key)
            if cached:
                try:
                    logger.debug("segmentation redis cache hit: %s", key)
                    return json.loads(cached)
                except Exception:
                    logger.debug("Failed to parse cached redis value for key=%s, recomputing", key)
            # compute and store
            res = _compute_segment_cached(key, serialized)
            try:
                redis_client.setex(key, SEGMENT_CACHE_TTL, json.dumps(res))
                logger.debug("segmentation redis cache set: %s ttl=%s", key, SEGMENT_CACHE_TTL)
            except Exception:
                logger.debug("Failed to set redis cache for key=%s", key)
            return res
        except Exception:
            logger.exception("Redis cache access failed, falling back to in-process cache")

    # Fallback to in-process lru cache
    logger.debug("segmentation in-process cache lookup for key=%s", key)
    return _compute_segment_cached(key, serialized)



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
    # Use caching layer (in-process LRU during dev, Redis in prod when configured)
    cached = _get_cached_or_compute(state)
    result = SegmentResult(
        segment=cached["segment"],
        reasons=cached["reasons"],
        segment_metadata=cached["segment_metadata"],
        routing_hint=cached.get("routing_hint"),
    )

    # Log the decision for observability (debug/info depending on environment)
    logger.info(
        "segmentation decision: segment=%s views=%d purchases=%d rule=%s",
        result.segment,
        result.segment_metadata.get("views_last_7d", 0),
        result.segment_metadata.get("purchases_last_30d", 0),
        result.segment_metadata.get("rule_applied", "default"),
    )

    return {
        "segment": result.segment,
        "reasons": result.reasons,
        "segment_metadata": result.segment_metadata,
        "routing_hint": result.routing_hint,
    }


def _validate_and_extract(state: State | Dict[str, Any]) -> ValidatedRequest:
    if state is None:
        logger.debug("_validate_and_extract: state is None -> empty dict")
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

    return ValidatedRequest(behavior=behavior, last_event=last_event)


def _decide_segment(req: ValidatedRequest) -> SegmentResult:
    views = _to_int(req.behavior.get("views_last_7d", 0), 0)
    purchases = _to_int(req.behavior.get("purchases_last_30d", 0), 0)

    reasons: List[str] = []
    routing_hint: str | None = None

    if purchases >= PURCHASES_THRESHOLD:
        segment = "recent_buyer"
        reasons.append(f"purchases_last_30d={purchases}")
    elif views >= VIEWS_THRESHOLD and purchases < PURCHASES_THRESHOLD:
        segment = "frequent_browser"
        reasons.append(f"views_last_7d={views}")
        reasons.append("no_recent_purchases")
        routing_hint = "offers"
    elif req.last_event and any(k in str(req.last_event).lower() for k in ("form", "abandon", "abandoned", "cart")):
        if "form" in str(req.last_event).lower():
            segment = "form_abandoned"
        else:
            segment = "cart_abandoned"
        reasons.append(f"last_event={req.last_event}")
    else:
        segment = "new_or_casual"
        reasons.append("no_significant_activity")

    rule = (
        "purchases_present"
        if purchases >= PURCHASES_THRESHOLD
        else ("views_high_no_purchases" if views >= VIEWS_THRESHOLD else ("abandonment_detected" if "abandon" in " ".join(reasons) else "default"))
    )

    segment_metadata = {
        "rule_applied": rule,
        "views_last_7d": views,
        "purchases_last_30d": purchases,
        "config": {"views_threshold": VIEWS_THRESHOLD, "purchases_threshold": PURCHASES_THRESHOLD},
    }

    return SegmentResult(segment=segment, reasons=reasons, segment_metadata=segment_metadata, routing_hint=routing_hint)

