import pytest

pytestmark = pytest.mark.anyio


from agent.graph.nodes.behavior_segmentation import behavior_seg
from agent.graph.nodes.profile_segmentation import profile_seg
from agent.graph.nodes.rfm_segmentation import rfm_seg
from agent.graph.nodes.intent_segmentation import intent_seg


async def test_behavior_segmentation_routes_offers_for_frequent_browser():
    state = {"behavior_summary": {"views_last_7d": 12, "purchases_last_30d": 0}}
    out = await behavior_seg(state)
    assert out.get("segment") == "frequent_browser"
    assert out.get("routing_hint") == "offers"


async def test_profile_segmentation_vip_to_generation():
    state = {"customer_profile": {"vip_tier": "Gold", "loyalty_score": 90}}
    out = await profile_seg(state)
    assert out.get("segment") in ("vip", "loyal_customer")
    assert out.get("routing_hint") == "generation"


async def test_rfm_segmentation_win_back_and_loyal():
    state1 = {"rfm_signals": {"recency_days": 200, "frequency": 1, "monetary": 50}}
    out1 = await rfm_seg(state1)
    assert out1.get("segment") == "win_back"

    state2 = {"rfm_signals": {"recency_days": 10, "frequency": 6, "monetary": 20}}
    out2 = await rfm_seg(state2)
    assert out2.get("segment") == "loyal"


async def test_intent_segmentation_purchase_vs_info():
    s1 = {"user_query": "I want to buy the new phone"}
    o1 = await intent_seg(s1)
    assert o1.get("segment") == "purchase_intent"
    assert o1.get("routing_hint") == "offers"

    s2 = {"user_query": "What is the battery life of model X?"}
    o2 = await intent_seg(s2)
    assert o2.get("segment") == "info_intent"
    assert o2.get("routing_hint") == "retrieval"
