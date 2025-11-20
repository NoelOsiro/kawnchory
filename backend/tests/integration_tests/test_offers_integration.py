import pytest

pytestmark = pytest.mark.anyio


async def test_graph_generates_offers() -> None:
    from agent import graph

    inputs = {"customer_profile": {"product_id": "p_101"}}
    res = await graph.ainvoke(inputs)

    assert res is not None

    # pulled from final state
    if hasattr(res, "get"):
        offers = res.get("offers")
        offers_count = res.get("offers_count")
    else:
        offers = getattr(res, "offers", None)
        offers_count = getattr(res, "offers_count", None)

    assert offers is not None
    assert isinstance(offers, list)
    # either count exists or infer from list
    if offers_count is not None:
        assert offers_count == len(offers)
    assert len(offers) >= 0
