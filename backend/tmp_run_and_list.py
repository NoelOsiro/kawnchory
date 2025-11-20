import asyncio
from langgraph.graph import StateGraph, END
from agent.state import State
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.delivery import delivery_node
from agent.services import hitl_queue

async def fake_generation(state, runtime=None):
    return {"generated_message": "This is a scam test message.", "routing_hint": "hitl"}

async def delivery_wrapper(state, runtime=None):
    return await delivery_node(state, runtime)

async def main():
    builder = StateGraph(State)
    builder.add_node('generation', fake_generation)
    builder.add_node('safety', safety_node)
    builder.add_node('hitl', hitl_node)
    builder.add_node('delivery', delivery_wrapper)
    builder.add_edge('__start__', 'generation')
    builder.add_edge('generation', 'safety')
    builder.add_edge('safety', 'hitl')
    builder.add_edge('hitl', 'delivery')
    builder.add_edge('delivery', END)
    wf = builder.compile('Test')
    res = await wf.ainvoke({'customer_profile': {'product_id': 'p_101'}})
    print('workflow result:', res)
    print('pending reviews after run:', hitl_queue.list_pending())

if __name__ == '__main__':
    asyncio.run(main())
