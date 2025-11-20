"""Full Workflow Graph with factory helpers.

This module exposes factory functions so tests and tools can build fresh
StateGraph instances or compiled workflows on demand. The module also keeps
a backward-compatible `workflow` variable for existing importers.
"""
from __future__ import annotations

from typing import Optional

from langgraph.graph import END, StateGraph

from agent.graph.nodes.delivery import delivery_node
from agent.graph.nodes.generation import generation_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.offers import offers_node
from agent.graph.nodes.retrieval import retrieval_node
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.segmentation import segmentation_node
from agent.state import State


def create_state_graph() -> StateGraph:
    """Create a fresh, uncompiled StateGraph for the Retail workflow.

    Returns a `StateGraph(State)` with all nodes and routing configured. Call
    `compile()` on the result to get a runnable workflow instance.
    """
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
    # Static edges for visualization in the Studio; runtime decision happens via
    # conditional edges (see route_after_segmentation) but static edges help the
    # Studio render a full graph.
    graph.add_edge("segmentation", "offers")
    graph.add_edge("segmentation", "retrieval")

    def route_after_segmentation(state: State):
        if isinstance(state, dict):
            routing_hint = state.get("routing_hint")
        else:
            routing_hint = getattr(state, "routing_hint", None)

        return "offers" if routing_hint == "offers" else "retrieval"

    graph.add_conditional_edges("segmentation", route_after_segmentation)

    graph.add_edge("retrieval", "offers")
    graph.add_edge("offers", "generation")
    graph.add_edge("generation", "safety")

    # Static visualization edges and conditional routing after safety
    graph.add_edge("safety", "hitl")
    graph.add_edge("safety", "delivery")

    def route_after_safety(state: State):
        if isinstance(state, dict):
            routing_hint = state.get("routing_hint")
        else:
            routing_hint = getattr(state, "routing_hint", None)

        return "hitl" if routing_hint == "hitl" else "delivery"

    graph.add_conditional_edges("safety", route_after_safety)

    graph.add_edge("hitl", "delivery")
    graph.add_edge("delivery", END)

    return graph


def create_workflow(compiled: bool = True, name: Optional[str] = "Retail Workflow Graph"):
    """Create a workflow instance.

    If `compiled` is True (default), returns the compiled workflow (runnable)
    created by calling `compile(name=...)` on a fresh StateGraph. If False,
    returns the uncompiled `StateGraph` (useful for tests that want to modify
    nodes before compile).
    """
    graph = create_state_graph()
    if compiled:
        return graph.compile(name=name)
    return graph


# Backwards-compatible module-level workflows
workflow = create_workflow()

