"""Intent-based segmentation wrapper.

Intent segmentation may rely on NLP or explicit `intent` fields. For now we
delegate to `segmentation_node` but this file is the place to add intent
parsing and lightweight NLP in future.
"""
from typing import Any, Dict, Optional


async def intent_seg(state: Any, runtime: Any = None) -> Any:
    """Intent-driven segmentation.

    Examines `intent` or `user_query` fields to infer routing and simple
    segments. This is intentionally lightweight and deterministic.
    """
    if isinstance(state, dict):
        intent = state.get("intent")
        query = state.get("user_query")
    else:
        intent = getattr(state, "intent", None)
        query = getattr(state, "user_query", None)

    text = ""
    if intent:
        text = str(intent)
    elif query:
        text = str(query)

    text_l = text.lower()

    reasons = []
    routing_hint: Optional[str] = None

    if any(k in text_l for k in ("buy", "purchase", "price", "order")):
        segment = "purchase_intent"
        routing_hint = "offers"
        reasons.append("purchase_intent_detected")
    elif any(k in text_l for k in ("info", "details", "spec", "what is")):
        segment = "info_intent"
        routing_hint = "retrieval"
        reasons.append("info_intent_detected")
    elif any(k in text_l for k in ("support", "help", "problem", "issue", "complaint")):
        segment = "support_intent"
        routing_hint = "generation"
        reasons.append("support_intent_detected")
    else:
        segment = "unknown_intent"
        reasons.append("no_intent_match")

    segment_metadata: Dict[str, Any] = {"intent_text": text}

    result = {"segment": segment, "reasons": reasons, "segment_metadata": segment_metadata, "routing_hint": routing_hint}

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
