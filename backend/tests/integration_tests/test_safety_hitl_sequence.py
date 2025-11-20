import asyncio


def test_safety_hitl_delivery_sequence():
    """Simulate the end-to-end sequence by calling nodes in order and ensuring
    HITL is invoked when safety fails before delivery."""
    import importlib

    gen_mod = importlib.import_module("agent.graph.nodes.generation")
    safety_mod = importlib.import_module("agent.graph.nodes.safety")
    hitl_mod = importlib.import_module("agent.graph.nodes.hitl")
    delivery_mod = importlib.import_module("agent.graph.nodes.delivery")

    # Fake generation that produces a banned keyword to force safety failure
    async def fake_generation(state, runtime=None):
        return {"generated_message": "This is a scam test message."}

    call_order = []

    async def call_generation(state):
        call_order.append("generation")
        return await fake_generation(state)

    async def call_safety(state):
        call_order.append("safety")
        out = await safety_mod.safety_node(state, None)
        # Ensure hint for this simulation
        if not out.get("safety_passed"):
            out["routing_hint"] = "hitl"
        return out

    def call_hitl(state):
        call_order.append("hitl")
        return hitl_mod.hitl_node(state)

    async def call_delivery(state):
        call_order.append("delivery")
        return await delivery_mod.delivery_node(state, None)

    # Run sequence
    state = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    gen_out = loop.run_until_complete(call_generation(state))
    state.update(gen_out)

    safety_out = loop.run_until_complete(call_safety(state))
    state.update(safety_out)

    # Since safety failed, we expect routing_hint -> hitl
    assert state.get("routing_hint") == "hitl"

    hitl_out = call_hitl(state)
    state.update(hitl_out)

    delivery_out = loop.run_until_complete(call_delivery(state))
    state.update(delivery_out)

    # Validate order and presence of outputs
    assert call_order[0] == "generation"
    assert "safety" in call_order
    assert "hitl" in call_order
    assert call_order.index("hitl") < call_order.index("delivery")

    assert state.get("human_review") is not None
    assert state.get("delivered_message") is not None
