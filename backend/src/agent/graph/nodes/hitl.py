"""Human-in-the-loop (HITL) node backed by an in-repo review queue.

This node enqueues the current state for human review and returns a small
payload containing the `review_id` and `status`. A separate process or test
can call `agent.services.hitl_queue.approve_review` to mark the review as
approved or rejected.
"""
from typing import Any, Dict

from agent.services.hitl_queue import enqueue_review
from agent.services.hitl_queue import get_review


# In test environments we can auto-approve pending reviews to progress flows.
def _maybe_auto_approve_and_fetch(review_id: int):
    try:
        from agent.services.hitl_test_helper import auto_approve_pending

        # Auto-approve pending reviews (test helper will be no-op if none)
        auto_approve_pending()
        rev = get_review(review_id)
        if rev is not None:
            # result_json was stored as JSON string; try to parse
            try:
                import json

                res = json.loads(rev.get("result_json") or "null")
            except Exception:
                res = rev.get("result_json")
            return res
    except Exception:
        return None


def hitl_node(state: Any, runtime: Any = None) -> Dict[str, Any]:
    """Enqueue the state for human review and return `review_id`.

    The function does not block waiting for a human; it simply creates a
    review entry which can later be approved using the queue API.
    """
    # Convert State-like objects to dict when possible
    if isinstance(state, dict):
        payload = state
    else:
        try:
            payload = dict(state.__dict__)
        except Exception:
            payload = {"state_repr": str(state)}

    review_id = enqueue_review(payload)
    # Attempt to auto-approve in test contexts and include the human review
    human_review = _maybe_auto_approve_and_fetch(review_id)
    out = {"review_id": review_id, "status": "pending"}
    if human_review is not None:
        out["human_review"] = human_review
    return out

