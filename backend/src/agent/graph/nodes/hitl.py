"""Human-in-the-loop (HITL) node backed by an in-repo review queue.

This node enqueues the current state for human review and returns a small
payload containing the `review_id` and `status`. A separate process or test
can call `agent.services.hitl_queue.approve_review` to mark the review as
approved or rejected.
"""
from typing import Any, Dict

from agent.services.hitl_queue import enqueue_review


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
    return {"review_id": review_id, "status": "pending"}

