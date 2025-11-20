from agent.graph.nodes import segmentation


def test_purchases_threshold_edges() -> None:
    # One below purchases threshold should not be recent_buyer
    below = segmentation.PURCHASES_THRESHOLD - 1
    req = {"behavior_summary": {"views_last_7d": 0, "purchases_last_30d": below}}
    res = segmentation._decide_segment(segmentation._validate_and_extract(req))
    assert res.segment != "recent_buyer"

    # Exactly at threshold should be recent_buyer
    req2 = {"behavior_summary": {"views_last_7d": 0, "purchases_last_30d": segmentation.PURCHASES_THRESHOLD}}
    res2 = segmentation._decide_segment(segmentation._validate_and_extract(req2))
    assert res2.segment == "recent_buyer"


def test_views_threshold_edges() -> None:
    # One below views threshold should not be frequent_browser
    below = segmentation.VIEWS_THRESHOLD - 1
    req = {"behavior_summary": {"views_last_7d": below, "purchases_last_30d": 0}}
    res = segmentation._decide_segment(segmentation._validate_and_extract(req))
    assert res.segment != "frequent_browser"

    # Exactly at threshold is frequent_browser
    req2 = {"behavior_summary": {"views_last_7d": segmentation.VIEWS_THRESHOLD, "purchases_last_30d": 0}}
    res2 = segmentation._decide_segment(segmentation._validate_and_extract(req2))
    assert res2.segment == "frequent_browser"


def test_last_event_parsing_variants() -> None:
    # Nested last_event in customer_profile
    req = {"customer_profile": {"last_event": "started_form_process"}}
    res = segmentation._decide_segment(segmentation._validate_and_extract(req))
    assert res.segment == "form_abandoned"

    # Case-insensitive match and different wording
    req2 = {"last_event": "User AbAnDoNeD_CART on checkout"}
    res2 = segmentation._decide_segment(segmentation._validate_and_extract(req2))
    assert res2.segment == "cart_abandoned"

    # Non-string last_event should be handled gracefully
    req3 = {"last_event": 12345}
    res3 = segmentation._decide_segment(segmentation._validate_and_extract(req3))
    assert res3.segment == "new_or_casual"
