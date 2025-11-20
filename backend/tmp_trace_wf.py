import asyncio
from langgraph.graph import StateGraph, END
from agent.state import State
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.delivery import delivery_node

async def fake_generation(state, runtime=None):
    return {"generated_message": "This is a scam test message.", "routing_hint": "hitl"}

async def main():
    builder = StateGraph(State)
    builder.add_node('generation', fake_generation)
    builder.add_node('safety', safety_node)
    builder.add_node('hitl', hitl_node)
    builder.add_node('delivery', delivery_node)
    builder.add_edge('__start__', 'generation')
    builder.add_edge('generation', 'safety')
    builder.add_edge('safety', 'hitl')
    builder.add_edge('hitl', 'delivery')
    builder.add_edge('delivery', END)

    wf = builder.compile(name='TraceWF')

    # Register interrupts to trace node execution
    def before(node_name, state):
        print('BEFORE NODE:', node_name, 'state snapshot keys:', list(state.keys()) if isinstance(state, dict) else dir(state))

    def after(node_name, state):
        print('AFTER NODE:', node_name, 'state snapshot keys:', list(state.keys()) if isinstance(state, dict) else dir(state))

    # Register interrupts by appending to the lists provided by the runtime
    try:
        wf.interrupt_before_nodes.append(before)
        wf.interrupt_after_nodes.append(after)
    except Exception as e:
        print('Failed to attach interrupts:', e)

    res = await wf.ainvoke({'customer_profile': {'product_id': 'p_101'}})
    print('final result:', res)

if __name__ == '__main__':
    asyncio.run(main())
