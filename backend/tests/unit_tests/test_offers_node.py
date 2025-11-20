import asyncio

from agent.graph.nodes.offers import offers_node


def test_offers_from_retrieved_docs() -> None:
    state = {"segment": "frequent_browser", "retrieved_docs": [{"id": "p_101", "title": "P101", "content": "Stuff", "source": "product_docs"}]}
    res = asyncio.run(offers_node(state, None))
    assert res["offers"]
    assert res["offers_metadata"]["source_docs_count"] == 1


def test_offers_recent_buyer_fallback() -> None:
    state = {"segment": "recent_buyer", "retrieved_docs": []}
    res = asyncio.run(offers_node(state, None))
    assert any(o["type"] == "loyalty_discount" for o in res["offers"]) 


def test_offers_empty_fallback_to_trial() -> None:
    state = {"segment": "frequent_browser", "retrieved_docs": []}
    res = asyncio.run(offers_node(state, None))
    assert any(o["type"] == "trial_offer" for o in res["offers"]) 
