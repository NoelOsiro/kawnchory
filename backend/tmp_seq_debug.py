import asyncio
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.delivery import delivery_node

async def fake_generation(state):
    return {"generated_message": "This is a scam test message.", "routing_hint": "hitl"}

async def seq():
    state = {'customer_profile': {'product_id': 'p_101'}}
    out1 = await fake_generation(state)
    state = {**state, **out1}
    print('after generation state:', state)
    out2 = await safety_node(state, None)
    state = {**state, **out2}
    print('after safety state:', state)
    out3 = hitl_node(state)
    print('hitl returned:', out3)
    state = {**state, **out3}
    print('after hitl state:', state)
    out4 = await delivery_node(state, None)
    print('delivery returned:', out4)

if __name__ == '__main__':
    asyncio.run(seq())
