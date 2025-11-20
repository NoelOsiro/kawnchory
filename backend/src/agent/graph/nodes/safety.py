from __future__ import annotations
from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import State
from agent.services.hitl_queue import enqueue_review


def _extract(state: Any, key: str, default=None):
    if isinstance(state, dict):
        return state.get(key, default)
    return getattr(state, key, default)


async def safety_node(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Deterministic safety checks for local/dev testing.

    Checks performed:
    - simple banned-keyword scan on generated text
    - offers sanity checks (discount bounds, final_price non-negative)

    Outputs:
    - `safety_passed`: bool
    - `safety_report`: dict with `reasons` list and optional `offending` details
    - `routing_hint`: when failed, recommend `hitl` for human review
    """
    reasons: List[str] = []
    offending: Dict[str, Any] = {}

    generated = _extract(state, "generated_message", "") or ""
    offers = _extract(state, "offers", []) or []

    # simple banned-keyword list (deterministic)
    banned = ["scam", "fraud", "illegal"]
    lowered = generated.lower()
    found = [w for w in banned if w in lowered]
    if found:
        reasons.append("banned_keywords_in_message")
        offending["message_keywords"] = found

    # offers sanity checks
    bad_offers = []
    for o in offers:
        try:
            discount = float(o.get("discount", 0.0))
        except Exception:
            discount = 0.0
        final_price = o.get("final_price")
        try:
            final_price_val = float(final_price) if final_price is not None else None
        except Exception:
            final_price_val = None

        if discount < 0 or discount > 0.5:
            bad_offers.append({"reason": "discount_out_of_bounds", "offer": o})
        if final_price_val is not None and final_price_val < 0:
            bad_offers.append({"reason": "negative_final_price", "offer": o})

    if bad_offers:
        reasons.append("offers_sanity_failed")
        offending["offers"] = bad_offers

    passed = len(reasons) == 0
    report = {"reasons": reasons, "offending": offending}
    routing_hint = "hitl" if not passed else None

    out = {"safety_passed": passed, "safety_report": report, "routing_hint": routing_hint}

    # If safety failed, create a HITL review immediately so downstream
    # nodes (or tests) can observe the `review_id` even if the workflow
    # routing doesn't execute the dedicated `hitl` node.
    if not passed:
        # Convert state into a JSON-serializable payload when possible
        try:
            if isinstance(state, dict):
                payload = state
            else:
                payload = dict(state.__dict__)
        except Exception:
            payload = {"state_repr": str(state)}
        try:
            rid = enqueue_review(payload)
            out["review_id"] = rid
        except Exception:
            # If enqueue fails, don't block safety processing — tests may
            # fall back to other mechanisms.
            pass

    return out


# Stub hook for integrating an external safety/policy service or ML classifier.
# Replace the body with a call to your policy engine when integrating.
def external_safety_policy_check(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder for external safety/policy service integration.

    Expected to return a dict with keys like `safety_passed` and `safety_report`.

    NOTE: Using an external service requires adding SDK dependencies, configuration
    (secrets, endpoints), and gating tests so they don't call external APIs in CI.
    """
    # No-op placeholder — production integration should implement this.
    return {"safety_passed": True, "safety_report": {}}
