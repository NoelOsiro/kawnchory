import pytest

pytestmark = pytest.mark.anyio


async def test_segmentation_stategraph_normalization():
    """Build a small StateGraph that runs `segmentation_node` and assert
    that semantically-equivalent states (different transient keys or numeric
    types) produce the same segment output thanks to normalization.
    """
    from langgraph.graph import StateGraph, END
    from agent.state import State
    from agent.graph.nodes.segmentation import segmentation_node

    # Two generation nodes that produce equivalent semantic signals but
    # differ in transient keys and the types of numeric signals.
    async def gen_str_values(state, runtime=None):
        return {
            "behavior_summary": {"views_last_7d": "12", "purchases_last_30d": "0"},
            "last_event": None,
            "transient": "abc",
        }

    async def gen_int_values(state, runtime=None):
        return {
            "behavior_summary": {"views_last_7d": 12, "purchases_last_30d": 0},
            "last_event": None,
            "transient": {"request_id": 12345},
        }

    builder = StateGraph(State)
    builder.add_node("generation", gen_str_values)
    builder.add_node("segmentation", segmentation_node)
    builder.add_edge("__start__", "generation")
    builder.add_edge("generation", "segmentation")
    builder.add_edge("segmentation", END)

    wf = builder.compile(name="Segmentation Normalization Test")

    res1 = await wf.ainvoke({})
    assert res1 is not None
    seg1 = res1.get("segment") if hasattr(res1, "get") else getattr(res1, "segment", None)
    assert seg1 is not None

    # Now swap the generation node to produce int-typed values and different
    # transient payload; the segmentation decision should be the same.
    builder = StateGraph(State)
    builder.add_node("generation", gen_int_values)
    builder.add_node("segmentation", segmentation_node)
    builder.add_edge("__start__", "generation")
    builder.add_edge("generation", "segmentation")
    builder.add_edge("segmentation", END)

    wf2 = builder.compile(name="Segmentation Normalization Test 2")
    res2 = await wf2.ainvoke({})
    seg2 = res2.get("segment") if hasattr(res2, "get") else getattr(res2, "segment", None)

    assert seg2 == seg1
import pytest

pytestmark = pytest.mark.anyio


@pytest.mark.langsmith
async def test_graph_runs_with_behavior() -> None:
    inputs = {"behavior_summary": {"views_last_7d": 12, "purchases_last_30d": 0}}
    from agent import graph

    res = await graph.ainvoke(inputs)
    assert res is not None
