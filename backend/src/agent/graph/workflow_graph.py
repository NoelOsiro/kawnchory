"""Full Workflow Graph with factory helpers.

This module exposes factory functions so tests and tools can build fresh
StateGraph instances or compiled workflows on demand. The module also keeps
a backward-compatible `workflow` variable for existing importers.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agent.graph.nodes.behavior_segmentation import behavior_seg
from agent.graph.nodes.context_inspection import context_inspection
from agent.graph.nodes.delivery import delivery_node
from agent.graph.nodes.generation import generation_node
from agent.graph.nodes.hitl import hitl_node
from agent.graph.nodes.intent_segmentation import intent_seg
from agent.graph.nodes.offers import _offers_node_async
from agent.graph.nodes.profile_segmentation import profile_seg
from agent.graph.nodes.retrieval import retrieval_node
from agent.graph.nodes.rfm_segmentation import rfm_seg
from agent.graph.nodes.safety import safety_node
from agent.graph.nodes.segment_merge import segment_merge
from agent.state import State


def create_state_graph() -> StateGraph:
    """Create a fresh, uncompiled StateGraph for the Retail workflow.

    Returns a `StateGraph(State)` with all nodes and routing configured. Call
    `compile()` on the result to get a runnable workflow instance.
    """
    graph = StateGraph(State)

    # Register nodes
    # Register segmentation nodes; provide `destinations` metadata so Studio
    # can render possible outgoing edges without adding static runtime edges.
    # Destinations are only used for rendering and do not affect execution.
    graph.add_node("behavior_seg", behavior_seg)
    graph.add_node("profile_seg", profile_seg)
    graph.add_node("rfm_seg", rfm_seg)
    graph.add_node("intent_seg", intent_seg)
    # Pre-segmentation inspection: normalize and flag incoming data
    graph.add_node("context_inspection", context_inspection, destinations=("behavior_seg","profile_seg","rfm_seg","intent_seg"))
    graph.add_node("retrieval", retrieval_node)
    # segment_merge: unify outputs from specialized segmentation nodes
    graph.add_node("segment_merge", segment_merge, destinations=("offers", "retrieval", "generation"))
    # Register the async implementation of the offers node so the graph
    # scheduler awaits it and receives a plain dict update. The compatibility
    # `offers_node` wrapper remains available for direct/legacy calls.
    graph.add_node("offers", _offers_node_async)
    graph.add_node("generation", generation_node)
    graph.add_node("safety", safety_node)
    graph.add_node("hitl", hitl_node)
    graph.add_node("delivery", delivery_node)

    # Route: START -> context_inspection -> conditional segmentation
    # Connect START to the inspection node; the inspection node will
    # normalize inputs and set `segmentation_strategy` / flags used below.
    graph.add_edge(START, "context_inspection")

    def route_from_start(state: State):
        # Prefer an explicit `segmentation_strategy` set by the
        # `context_inspection` node. Fall back to presence-based heuristics.
        if isinstance(state, dict):
            strat = state.get("segmentation_strategy")
        else:
            strat = getattr(state, "segmentation_strategy", None)

        if strat == "behavior":
            return "behavior_seg"
        if strat == "profile":
            return "profile_seg"
        if strat == "rfm":
            return "rfm_seg"
        if strat == "intent":
            return "intent_seg"

        # Fallback to presence checks for older callers or when inspection
        # did not produce a strategy
        def has(key: str) -> bool:
            if isinstance(state, dict):
                return key in state and state.get(key) is not None
            return hasattr(state, key) and getattr(state, key) is not None

        if has("behavior_summary"):
            return "behavior_seg"
        if has("customer_profile"):
            return "profile_seg"
        if has("rfm_signals"):
            return "rfm_seg"
        if has("user_query") or has("intent"):
            return "intent_seg"
        return "behavior_seg"

    # Ensure the route function has a stable name for Studio drawing
    try:
        route_from_start.__name__ = "route_from_context_inspection"
    except Exception:
        pass

    # Conditional edges originate from the inspection node so runtime writes
    # remain single-writer per LastValue key while Studio can still render
    # the possible outgoing edges.
    graph.add_conditional_edges("context_inspection", route_from_start, path_map=["behavior_seg", "profile_seg", "rfm_seg", "intent_seg"])

    graph.add_edge("retrieval", "generation")
    graph.add_edge("offers", "generation")
    graph.add_edge("generation", "safety")
    graph.add_edge("safety", "hitl")
    graph.add_edge("hitl", "delivery")
    graph.add_edge("delivery", END)

    # Connect each specialized segmentation node into the `segment_merge`
    graph.add_edge("behavior_seg", "segment_merge")
    graph.add_edge("profile_seg", "segment_merge")
    graph.add_edge("rfm_seg", "segment_merge")
    graph.add_edge("intent_seg", "segment_merge")

    # Post-segmentation router: choose offers/retrieval/generation based on
    # `routing_hint` or segment content. Provide a path_map so Studio renders
    # explicit possible targets.
    def _get_hint(state: State):
        if isinstance(state, dict):
            return state.get("routing_hint")
        return getattr(state, "routing_hint", None)

    def route_after_seg(state: State):
        hint = _get_hint(state)
        if hint in ("retrieval", "offers", "generation"):
            return hint
        # Fallback to simple segment-based defaults
        if isinstance(state, dict):
            seg = state.get("segment")
            has_query = bool(state.get("user_query") or state.get("intent"))
        else:
            seg = getattr(state, "segment", None)
            has_query = bool(getattr(state, "user_query", None) or getattr(state, "intent", None))

        if has_query or (isinstance(seg, str) and "intent" in seg):
            return "retrieval"
        # Commerce-oriented defaults
        return "offers"

    try:
        route_after_seg.__name__ = "route_after_seg"
    except Exception:
        pass

    graph.add_conditional_edges("segment_merge", route_after_seg, path_map=["offers", "retrieval", "generation"])

    return graph


def create_workflow(compiled: bool = True, name: str | None = "Retail Workflow Graph"):
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

