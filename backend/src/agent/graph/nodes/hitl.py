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
    # Small retry loop to ensure the review record is visible (helps in
    # environments where DB writes may be briefly delayed). This keeps
    # the node deterministic while making integration tests less flaky.
    rev = None
    for _ in range(3):
        try:
            rev = get_review(review_id)
            if rev is not None:
                break
        except Exception:
            rev = None
        try:
            import time

            time.sleep(0.01)
        except Exception:
            pass

    status = rev.get("status") if rev is not None else "pending"
    human_review = _maybe_fetch_existing_review_result(review_id)

    # Prepare a minimal result dict with the review metadata. Returning a
    # dict ensures the graph runtime writes only these keys into the shared
    # state — this is more reliable than attempting to mutate state-like
    # objects in-place across different runtimes.
    result = {"review_id": review_id, "status": status}
    if human_review is not None:
        result["human_review"] = human_review

    # Also update the passed-in mapping when possible for convenience
    # (so immediate callers that inspect the same object see the values).
    try:
        if isinstance(state, dict):
            state.update(result)
    except Exception:
        pass

    return result

