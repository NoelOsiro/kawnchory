from agent.graph.nodes.safety import safety_node
import asyncio


def test_safety_passes_on_clean_message():
    state = {
        "generated_message": "Thanks for your interest! Here are some offers.",
        "offers": [
            {"product_id": "p1", "final_price": 10.0, "discount": 0.1},
        ],
    }

    out = asyncio.run(safety_node(state, None))
    assert out["safety_passed"] is True
    assert out["safety_report"]["reasons"] == []


def test_safety_fails_on_banned_keyword_and_bad_offer():
    state = {
        "generated_message": "This is a scam offer",
        "offers": [
            {"product_id": "p2", "final_price": -5.0, "discount": 0.6},
        ],
    }

    out = asyncio.run(safety_node(state, None))
    assert out["safety_passed"] is False
    reasons = out["safety_report"]["reasons"]
    assert "banned_keywords_in_message" in reasons
    assert "offers_sanity_failed" in reasons
    assert out["routing_hint"] == "hitl"
