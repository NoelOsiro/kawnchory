"""Static visualization-only workflow for LangGraph Studio.

This module builds a simple, statically-edged StateGraph that mirrors the
intended runtime routing. It's compiled and exposed as `visual_workflow` so
LangGraph Studio / LangSmith can show explicit edges (including START
connections). This graph is intended for visualization only — do not run
it for production workloads because static broadcast edges can execute
multiple nodes in a single step and may trigger runtime conflicts.

Use `visual_workflow` in Studio to inspect the topology.
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

# Import the real node implementations so Studio shows node names; we don't
# call them here — the compiled graph is for visualization.
from agent.graph.nodes.behavior_segmentation import behavior_seg
from agent.graph.nodes.delivery import delivery_node
from agent.graph.nodes.generation import generation_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.intent_segmentation import intent_seg
from agent.graph.nodes.offers import _offers_node_async
from agent.graph.nodes.profile_segmentation import profile_seg
from agent.graph.nodes.retrieval import retrieval_node
from agent.graph.nodes.rfm_segmentation import rfm_seg
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.segmentation import segmentation_node
from agent.state import State


def create_visual_state_graph() -> StateGraph:
    """Build a static graph for Studio visualization only.

    This graph uses explicit/static edges so LangGraph Studio shows them
    clearly. Do NOT execute this graph in production — it's only for
    topology inspection.
    """
    g = StateGraph(State)

    # Register nodes (use real node callables for naming clarity)
    g.add_node("segmentation", segmentation_node)
    g.add_node("behavior_seg", behavior_seg)
    g.add_node("profile_seg", profile_seg)
    g.add_node("rfm_seg", rfm_seg)
    g.add_node("intent_seg", intent_seg)
    g.add_node("retrieval", retrieval_node)
    g.add_node("offers", _offers_node_async)
    g.add_node("generation", generation_node)
    g.add_node("safety", safety_node)
    g.add_node("hitl", hitl_node)
    g.add_node("delivery", delivery_node)

    # START connections (visual only)
    g.add_edge("__start__", "behavior_seg")
    g.add_edge("__start__", "profile_seg")
    g.add_edge("__start__", "rfm_seg")
    g.add_edge("__start__", "intent_seg")

    # Core flow
    g.add_edge("retrieval", "offers")
    g.add_edge("offers", "generation")
    g.add_edge("generation", "safety")
    g.add_edge("safety", "hitl")
    g.add_edge("safety", "delivery")
    g.add_edge("hitl", "delivery")
    g.add_edge("delivery", END)

    return g


# Compiled visual workflow for Studio. Import this module in Studio or set
# LANGGRAPH to pick up `visual_workflow` for display.
visual_workflow = create_visual_state_graph().compile(name="Retail Visual Workflow")
