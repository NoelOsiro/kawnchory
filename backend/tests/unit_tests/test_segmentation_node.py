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
