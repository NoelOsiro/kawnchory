import pytest

pytestmark = pytest.mark.anyio


from agent.graph.workflow_graph import create_state_graph


async def _run_graph_with_state(state):
    graph = create_state_graph()
    wf = graph.compile(name="Test Entry Routing")
    return await wf.ainvoke(state)


async def test_entry_routes_to_behavior():
    state = {"behavior_summary": {"views_last_7d": 5}}
    res = await _run_graph_with_state(state)
    # behavior_seg should annotate the state with a `segment`
    assert res.get("segment") is not None


async def test_entry_routes_to_profile():
    state = {"customer_profile": {"vip_tier": "Gold"}}
    res = await _run_graph_with_state(state)
    assert res.get("segment") in ("vip", "loyal_customer", "profile_unknown")


async def test_entry_routes_to_rfm():
    state = {"rfm_signals": {"recency_days": 300}}
    res = await _run_graph_with_state(state)
    assert res.get("segment") is not None


async def test_entry_routes_to_intent():
    state = {"user_query": "I need help with my order"}
    res = await _run_graph_with_state(state)
    assert res.get("segment") is not None
