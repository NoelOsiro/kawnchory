from agent.graph.nodes import segmentation


def test_to_int_parsing() -> None:
    assert segmentation._to_int("5") == 5
    assert segmentation._to_int(None) == 0
    assert segmentation._to_int("bad", default=7) == 7


def test_validate_and_extract_none() -> None:
    vr = segmentation._validate_and_extract(None)
    assert vr.behavior == {}
    assert vr.last_event is None


def test_decide_recent_buyer() -> None:
    req = segmentation.ValidatedRequest(behavior={"purchases_last_30d": 3}, last_event=None)
    res = segmentation._decide_segment(req)
    assert res.segment == "recent_buyer"
    assert any("purchases_last_30d=3" in r for r in res.reasons)
    assert res.routing_hint is None


def test_decide_frequent_browser_threshold() -> None:
    req = segmentation.ValidatedRequest(
        behavior={"views_last_7d": segmentation.VIEWS_THRESHOLD, "purchases_last_30d": 0},
        last_event=None,
    )
    res = segmentation._decide_segment(req)
    assert res.segment == "frequent_browser"
    assert res.routing_hint == "offers"


def test_decide_abandonment_cart() -> None:
    req = segmentation.ValidatedRequest(behavior={}, last_event="user_abandoned_cart")
    res = segmentation._decide_segment(req)
    assert res.segment == "cart_abandoned"
    assert any("last_event" in r for r in res.reasons)
