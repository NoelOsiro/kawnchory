"""Human-in-the-loop (HITL) node backed by an in-repo review queue.

This node enqueues the current state for human review and returns a small
payload containing the `review_id` and `status`. A separate process or test
can call `agent.services.hitl_queue.approve_review` to mark the review as
approved or rejected.
"""
from typing import Any, Dict

from agent.services.hitl_queue import enqueue_review, get_review


def _maybe_fetch_existing_review_result(review_id: int):
    """Fetch an existing review result if present without triggering.

    any auto-approval side-effects. Tests or other helpers may approve
    reviews separately; this function only reads the stored result.
    """
    try:
        rev = get_review(review_id)
        if rev is not None and rev.get("result_json"):
            try:
                import json

                return json.loads(rev.get("result_json"))
            except Exception:
                return rev.get("result_json")
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
    # Do not auto-approve here; tests are responsible for invoking the
    # test-helper auto-approve when needed. We will, however, include an
    # existing human review result if one is already present.
    human_review = _maybe_fetch_existing_review_result(review_id)
    rev = get_review(review_id)
    status = rev.get("status") if rev is not None else "pending"

    # Mutate the received state in-place when possible so the runtime's
    # state object seen by downstream nodes includes the review metadata.
    try:
        if isinstance(state, dict):
            state["review_id"] = review_id
            state["status"] = status
            if human_review is not None:
                state["human_review"] = human_review
            return state
        else:
            # Try to set attributes on a state-like object
            try:
                setattr(state, "review_id", review_id)
                setattr(state, "status", status)
                if human_review is not None:
                    setattr(state, "human_review", human_review)
                return state
            except Exception:
                # Fall back to returning a dict copy if we cannot mutate
                out_state = dict(getattr(state, "__dict__", {}))
                out_state["review_id"] = review_id
                out_state["status"] = status
                if human_review is not None:
                    out_state["human_review"] = human_review
                return out_state
    except Exception:
        # As a last resort, return a minimal dict with review info
        out = {"review_id": review_id, "status": status}
        if human_review is not None:
            out["human_review"] = human_review
        return out

