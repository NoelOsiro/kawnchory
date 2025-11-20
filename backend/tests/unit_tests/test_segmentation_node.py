import asyncio

from agent.graph.nodes.segmentation import segmentation_node


def test_frequent_browser() -> None:
    state = {"behavior_summary": {"views_last_7d": 12, "purchases_last_30d": 0}}
    res = asyncio.run(segmentation_node(state, None))
    assert res["segment"] == "frequent_browser"
    assert res["routing_hint"] == "offers"
    assert res["segment_metadata"]["views_last_7d"] == 12


def test_recent_buyer() -> None:
    state = {"behavior_summary": {"views_last_7d": 2, "purchases_last_30d": 3}}
    res = asyncio.run(segmentation_node(state, None))
    assert res["segment"] == "recent_buyer"
    assert res["segment_metadata"]["purchases_last_30d"] == 3


def test_form_abandoned() -> None:
    state = {"last_event": "started_form"}
    res = asyncio.run(segmentation_node(state, None))
    assert res["segment"] == "form_abandoned"
    assert any("last_event" in str(r) for r in res["reasons"]) or any("last_event" in str(v) for v in res["segment_metadata"].values())


def test_empty_state_defaults_to_new_or_casual() -> None:
    # Empty input should be handled gracefully and return fallback segment
    res = asyncio.run(segmentation_node({}, None))
    assert res["segment"] == "new_or_casual"


def test_malformed_numeric_values() -> None:
    # Non-numeric views/purchases should be treated as 0, not raise
    state = {"behavior_summary": {"views_last_7d": "a-lot", "purchases_last_30d": "none"}}
    res = asyncio.run(segmentation_node(state, None))
    assert res["segment"] == "new_or_casual"


def test_views_threshold_boundary() -> None:
    # Exactly the threshold should classify as frequent_browser
    state = {"behavior_summary": {"views_last_7d": 10, "purchases_last_30d": 0}}
    res = asyncio.run(segmentation_node(state, None))
    assert res["segment"] == "frequent_browser"
