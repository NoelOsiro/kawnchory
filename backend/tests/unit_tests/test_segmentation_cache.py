from agent.graph.nodes import segmentation


def test_inprocess_lru_cache_hits_on_repeated_calls() -> None:
    # Ensure LRU cache is clear before test
    segmentation._compute_segment_cached.cache_clear()
    info_before = segmentation._compute_segment_cached.cache_info()
    assert info_before.hits == 0

    state = {"behavior_summary": {"views_last_7d": 2, "purchases_last_30d": 0}}

    # First call will populate cache (miss)
    res1 = segmentation._get_cached_or_compute(state)
    assert isinstance(res1, dict)

    # Second call should hit the in-process cache
    res2 = segmentation._get_cached_or_compute(state)
    assert res1 == res2

    info_after = segmentation._compute_segment_cached.cache_info()
    # Expect one miss (first call) and one hit (second call)
    assert info_after.misses >= 1
    assert info_after.hits >= 1
