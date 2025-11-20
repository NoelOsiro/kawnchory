"""Full Workflow Graph.

Defines the multi-node retail workflow and routing logic.
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from agent.graph.nodes.delivery import delivery_node
from agent.graph.nodes.generation import generation_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.offers import offers_node
from agent.graph.nodes.retrieval import retrieval_node
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.segmentation import segmentation_node
from agent.state import State

# Build graph
graph = StateGraph(State)

# Register nodes
graph.add_node("segmentation", segmentation_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("offers", offers_node)
graph.add_node("generation", generation_node)
graph.add_node("safety", safety_node)
graph.add_node("hitl", hitl_node)
graph.add_node("delivery", delivery_node)


# Routing
graph.add_edge("__start__", "segmentation")
# Add explicit static edges for visualization in the Studio.
# Keep the conditional routing handler below for runtime decision-making.
graph.add_edge("segmentation", "offers")
graph.add_edge("segmentation", "retrieval")

def route_after_segmentation(state: State):
    """Determine the next workflow node after segmentation.

    Parameters
    ----------
    state : State
        The current workflow state which provides a `routing_hint` attribute.

    Returns:
    -------
    str
        The id of the next node: "offers" when state's routing_hint equals "offers",
        otherwise "retrieval".
    """
    if isinstance(state, dict):
        routing_hint = state.get("routing_hint")
    else:
        routing_hint = getattr(state, "routing_hint", None)

    return "offers" if routing_hint == "offers" else "retrieval"

graph.add_conditional_edges("segmentation", route_after_segmentation)

graph.add_edge("retrieval", "offers")
graph.add_edge("offers", "generation")
graph.add_edge("generation", "safety")
graph.add_edge("safety", "hitl")
graph.add_edge("hitl", "delivery")
graph.add_edge("delivery", END)


workflow = graph.compile(name="Retail Workflow Graph")
