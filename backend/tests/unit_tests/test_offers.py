import pytest

from agent.graph.nodes.offers import offers_node


def test_offers_node_basic():
    state = {
        "retrieved_docs": [
            {"id": "p1", "title": "Alpha", "price": 20.0},
            {"id": "p2", "title": "Beta", "price": 15.0},
            {"id": "p3", "title": "Gamma", "price": 5.0},
        ],
        "segment": "frequent_browser",
    }

    out = offers_node(state)

    assert out["offers_count"] == 3
    assert out["routing_hint"] == "generation"
    # discounts applied for frequent_browser
    for o in out["offers"]:
        assert "discount" in o
        assert o["discount"] == pytest.approx(0.10)


def test_offers_node_empty_retrieval():
    state = {"retrieved_docs": [], "segment": "recent_buyer"}
    out = offers_node(state)
    assert out["offers_count"] == 0
    assert out["offers"] == []
