import pytest

pytestmark = pytest.mark.anyio

from agent.graph.nodes.behavior_segmentation import behavior_seg
from agent.graph.nodes.profile_segmentation import profile_seg
from agent.graph.nodes.rfm_segmentation import rfm_seg
from agent.graph.nodes.intent_segmentation import intent_seg


async def test_behavior_seg_recent_buyer():
    state = {"behavior_summary": {"purchases_last_30d": 2, "views_last_7d": 3}}
    res = await behavior_seg(state.copy())
    assert res.get("segment") == "recent_buyer"
    assert "purchases_last_30d=2" in res.get("reasons", [])
    # segment metadata reflects purchases
    assert res.get("segment_metadata", {}).get("purchases_last_30d") == 2


async def test_behavior_seg_frequent_browser():
    state = {"behavior_summary": {"views_last_7d": 12, "purchases_last_30d": 0}}
    res = await behavior_seg(state.copy())
    assert res.get("segment") == "frequent_browser"
    assert res.get("routing_hint") == "offers"
    assert "no_recent_purchases" in res.get("reasons", [])
    assert res.get("segment_metadata", {}).get("views_last_7d") == 12


async def test_profile_seg_vip():
    state = {"customer_profile": {"vip_tier": "Gold", "loyalty_score": 95}}
    res = await profile_seg(state.copy())
    assert res.get("segment") == "vip"
    assert res.get("routing_hint") == "generation"
    assert res.get("segment_metadata", {}).get("loyalty_score") == 95


async def test_rfm_seg_high_value_active():
    state = {"rfm_signals": {"recency_days": 30, "frequency": 10, "monetary": 2500}}
    res = await rfm_seg(state.copy())
    assert res.get("segment") == "high_value_active"
    assert res.get("routing_hint") == "generation"
    assert float(res.get("segment_metadata", {}).get("monetary", 0)) == 2500.0


async def test_intent_seg_purchase_intent():
    state = {"user_query": "I want to buy a new laptop"}
    res = await intent_seg(state.copy())
    assert res.get("segment") == "purchase_intent"
    assert res.get("routing_hint") == "offers"


async def test_intent_seg_unknown_and_empty():
    # empty state -> unknown intent
    res = await intent_seg({})
    assert res.get("segment") == "unknown_intent"
    assert res.get("routing_hint") is None


async def test_behavior_malformed_values():
    # malformed numeric strings should fall back to defaults (0)
    state = {"behavior_summary": {"views_last_7d": "notanumber", "purchases_last_30d": "x"}}
    res = await behavior_seg(state.copy())
    # no numeric signals -> new_or_casual
    assert res.get("segment") == "new_or_casual"


async def test_rfm_missing_values_defaults():
    # missing monetary/frequency should default to 0 and produce rfm_unknown
    res = await rfm_seg({})
    assert res.get("segment") in ("rfm_unknown", "win_back", "loyal")
