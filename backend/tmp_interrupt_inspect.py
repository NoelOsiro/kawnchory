from langgraph.graph import StateGraph, END
from agent.state import State
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.delivery import delivery_node

builder = StateGraph(State)
builder.add_node('generation', lambda s, r=None: {'generated_message':'x','routing_hint':'hitl'})
builder.add_node('safety', safety_node)
builder.add_node('hitl', hitl_node)
builder.add_node('delivery', delivery_node)

builder.add_edge('__start__','generation')
builder.add_edge('generation','safety')
builder.add_edge('safety','hitl')
builder.add_edge('hitl','delivery')
builder.add_edge('delivery',END)

wf = builder.compile('dbg')
print('interrupt_before_nodes type:', type(wf.interrupt_before_nodes))
print('interrupt_before_nodes value:', wf.interrupt_before_nodes)
print('interrupt_after_nodes type:', type(wf.interrupt_after_nodes))
print('interrupt_after_nodes value:', wf.interrupt_after_nodes)
