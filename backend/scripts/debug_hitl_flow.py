import asyncio

from langgraph.graph import END, StateGraph

from agent.graph.nodes.delivery import delivery_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.safety import safety_node
from agent.services import hitl_queue, hitl_test_helper
from agent.state import State


async def fake_generation(state, runtime=None):
    print('generation input:', state)
    out = {"generated_message": "This is a scam test message.", "routing_hint": "hitl"}
    print('generation output:', out)
    return out

async def delivery_wrapper(state, runtime=None):
    print('delivery_wrapper received state:', state)
    if isinstance(state, dict):
        rid = state.get("review_id")
    else:
        rid = getattr(state, "review_id", None)

    print('delivery_wrapper found review_id:', rid)

    if rid is not None:
        review = hitl_queue.get_review(rid)
        print('delivery_wrapper looked up review:', review)
        if review is None or review.get("status") != "approved":
            print('delivery_wrapper auto-approving pending...')
            hitl_test_helper.auto_approve_pending()

    res = await delivery_node(state, runtime)
    print('delivery_node output:', res)
    return res

async def main():
    builder = StateGraph(State)
    builder.add_node('generation', fake_generation)
    builder.add_node('safety', safety_node)

    # wrap hitl_node to observe what it returns inside the workflow
    async def hitl_wrapper(state, runtime=None):
        print('hitl_wrapper received state:', state)
        out = hitl_node(state, runtime)
        print('hitl_wrapper returned:', out)
        return out

    builder.add_node('hitl', hitl_wrapper)
    builder.add_node('delivery', delivery_wrapper)
    builder.add_edge('__start__', 'generation')
    builder.add_edge('generation', 'safety')
    builder.add_edge('safety', 'hitl')
    builder.add_edge('hitl', 'delivery')
    builder.add_edge('delivery', END)

    wf = builder.compile(name='Debug HITL Workflow')
    inputs = {"customer_profile": {"product_id": "p_101"}}
    res = await wf.ainvoke(inputs)
    print('final result:', res)

if __name__ == '__main__':
    asyncio.run(main())
