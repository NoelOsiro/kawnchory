"""Test helper utilities for HITL workflows.

Provides a small helper to auto-approve pending reviews (useful in integration
tests to progress flows that would otherwise wait for a human reviewer).
"""
from typing import Optional

from agent.services import hitl_queue


def auto_approve_pending(reviewer: str = "test_auto", notes: Optional[str] = "Auto-approved in test", limit: Optional[int] = None):
    """Approve up to `limit` pending reviews. If `limit` is None, approve all.

    Returns list of review ids approved.
    """
    pending = hitl_queue.list_pending()
    approved = []
    for idx, r in enumerate(pending):
        if limit is not None and idx >= limit:
            break
        rid = r["id"]
        hitl_queue.approve_review(rid, reviewer=reviewer, notes=notes, result={"approved": True})
        approved.append(rid)
    return approved
