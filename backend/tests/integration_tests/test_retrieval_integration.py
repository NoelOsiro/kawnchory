import pytest

pytestmark = pytest.mark.anyio


async def test_graph_retrieves_docs() -> None:
    from agent import graph

    inputs = {"customer_profile": {"product_id": "p_101"}}
    res = await graph.ainvoke(inputs)
    # Ensure graph ran and retrieval node provided docs (if wired)
    assert res is not None
    # If result is mapping-like, prefer key-based check; otherwise attribute
    retrieved = None
    if hasattr(res, "get"):
        retrieved = res.get("retrieved_docs")
    else:
        retrieved = getattr(res, "retrieved_docs", None)

    assert retrieved is not None
    # Expect at least one retrieved doc for the sample product id
    assert len(retrieved) > 0
