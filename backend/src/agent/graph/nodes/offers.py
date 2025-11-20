from __future__ import annotations

from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import State


async def offers_node(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Generate simple, deterministic offers based on segment and retrieved docs.

    This implementation is intentionally simple and deterministic for tests.
    Production should replace this with a business-driven offers engine.
    """

    # Extract segment and retrieved docs from either State or dict
    if isinstance(state, dict):
        segment = state.get("segment")
        retrieved = state.get("retrieved_docs") or []
    else:
        segment = getattr(state, "segment", None)
        retrieved = getattr(state, "retrieved_docs", None) or []

    offers: List[Dict[str, Any]] = []

    # Generate document recommendation offers from retrieved docs
    for doc in retrieved:
        offers.append(
            {
                "id": f"offer_doc_{doc.get('id')}",
                "type": "doc_recommendation",
                "title": doc.get("title") or "Recommended",
                "summary": (doc.get("content") or "").strip()[:200],
                "source": doc.get("source"),
            }
        )

    # Segment-specific offers
    if not offers:
        if segment == "recent_buyer":
            offers.append(
                {
                    "id": "offer_loyalty_1",
                    "type": "loyalty_discount",
                    "title": "Thank you — enjoy 10% off",
                    "summary": "Loyalty discount for recent buyers",
                    "source": "promotions",
                }
            )
        elif segment == "frequent_browser":
            offers.append(
                {
                    "id": "offer_trial_1",
                    "type": "trial_offer",
                    "title": "Try premium features",
                    "summary": "Special trial for frequent browsers",
                    "source": "promotions",
                }
            )

    offers_metadata = {"segment": segment, "offers_count": len(offers), "source_docs_count": len(retrieved)}

    return {"offers": offers, "offers_metadata": offers_metadata}
