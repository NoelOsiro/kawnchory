import pytest

pytestmark = pytest.mark.anyio


@pytest.mark.langsmith
async def test_graph_runs_with_behavior() -> None:
    inputs = {"behavior_summary": {"views_last_7d": 12, "purchases_last_30d": 0}}
    from agent import graph

    res = await graph.ainvoke(inputs)
    assert res is not None
