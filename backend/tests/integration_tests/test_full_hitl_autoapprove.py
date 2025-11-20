import pytest

pytestmark = pytest.mark.anyio


async def test_full_flow_auto_approves_hitl():
    """End-to-end integration that enqueues a HITL review and auto-approves it.

    This builds a local StateGraph (using the same nodes) so it doesn't mutate
    the package-level compiled workflow.
    """
    from langgraph.graph import StateGraph, END
    from agent.state import State
    from agent.graph.nodes.safety import safety_node
    from agent.graph.nodes.hitl import hitl_node
    from agent.graph.nodes.delivery import delivery_node
    from agent.services import hitl_queue
    from agent.services import hitl_test_helper

    # Fake generation that triggers safety failure (banned keyword)
    async def fake_generation(state, runtime=None):
        return {"generated_message": "This is a scam test message.", "routing_hint": "hitl"}

    async def delivery_wrapper(state, runtime=None):
        # Check for a review id and auto-approve if still pending
        if isinstance(state, dict):
            rid = state.get("review_id")
        else:
            rid = getattr(state, "review_id", None)

        if rid is not None:
            review = hitl_queue.get_review(rid)
            if review is None or review.get("status") != "approved":
                # auto-approve pending reviews for the integration test
                hitl_test_helper.auto_approve_pending()

        # Call the real delivery node to produce delivered_message
        return await delivery_node(state, runtime)

    builder = StateGraph(State)
    builder.add_node("generation", fake_generation)
    builder.add_node("safety", safety_node)
    builder.add_node("hitl", hitl_node)
    builder.add_node("delivery", delivery_wrapper)

    builder.add_edge("__start__", "generation")
    builder.add_edge("generation", "safety")
    builder.add_edge("safety", "hitl")
    builder.add_edge("hitl", "delivery")
    builder.add_edge("delivery", END)

    wf = builder.compile(name="Test Full HITL Workflow")

    inputs = {"customer_profile": {"product_id": "p_101"}}
    res = await wf.ainvoke(inputs)

    assert res is not None

    # Ensure a review was created and is now approved
    if hasattr(res, "get"):
        rid = res.get("review_id")
        assert rid is not None
        rev = hitl_queue.get_review(rid)
        assert rev is not None and rev.get("status") == "approved"
        assert res.get("delivered_message") is not None
    else:
        rid = getattr(res, "review_id", None)
        assert rid is not None
        rev = hitl_queue.get_review(rid)
        assert rev is not None and rev.get("status") == "approved"
        assert getattr(res, "delivered_message", None) is not None
