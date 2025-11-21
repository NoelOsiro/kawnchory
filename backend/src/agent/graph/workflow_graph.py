"""Full Workflow Graph with factory helpers.

This module exposes factory functions so tests and tools can build fresh
StateGraph instances or compiled workflows on demand. The module also keeps
a backward-compatible `workflow` variable for existing importers.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

# Config-driven wiring
from agent.services import config_store

# Require jsonlogic for routing rule evaluation. Prefer the `jsonlogic`
# package API but also accept the `json_logic` package (different naming).
try:
    from jsonlogic import jsonlogic as _jsonlogic
except Exception:
    try:
        # Some environments install the package named `json-logic` which
        # exposes a `jsonLogic` function in the `json_logic` module. Wrap it
        # so callers can use `_jsonlogic(expr, data)` uniformly.
        import json_logic as _jl

        def _jsonlogic(expr, data=None):
            return _jl.jsonLogic(expr, data)

    except Exception as exc:  # pragma: no cover - startup failure if missing
        raise ImportError(
            "The 'jsonlogic' package is required for routing rule evaluation. "
            "Install it with 'pip install jsonlogic' or 'pip install json-logic', "
            "or add it to your environment (see backend/requirements.txt)."
        ) from exc

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


def create_state_graph(enabled_segments: set | None = None, configs: dict | None = None) -> StateGraph:
    """Create a fresh, uncompiled StateGraph for the Retail workflow.

    Returns a `StateGraph(State)` with all nodes and routing configured. Call
    `compile()` on the result to get a runnable workflow instance.
    """
    # If configs provided, derive enabled segments from node rows; otherwise
    # fall back to legacy `enabled_segments` or defaults.
    if configs is None:
        try:
            configs = config_store.store.get_all_configs()
        except Exception:
            configs = None

    if configs and "nodes" in configs:
        enabled_segments = {name for name, info in configs.get("nodes", {}).items() if info.get("enabled")}

    if enabled_segments is None:
        enabled_segments = {"behavior_seg", "profile_seg", "rfm_seg", "intent_seg"}

    graph = StateGraph(State)

    # Register nodes
    # Register segmentation nodes; provide `destinations` metadata so Studio
    # can render possible outgoing edges without adding static runtime edges.
    # Destinations are only used for rendering and do not affect execution.
    if "behavior_seg" in enabled_segments:
        graph.add_node("behavior_seg", behavior_seg)
    if "profile_seg" in enabled_segments:
        graph.add_node("profile_seg", profile_seg)
    if "rfm_seg" in enabled_segments:
        graph.add_node("rfm_seg", rfm_seg)
    if "intent_seg" in enabled_segments:
        graph.add_node("intent_seg", intent_seg)
    # Pre-segmentation inspection: normalize and flag incoming data
    # Provide `destinations` metadata only for the segmentors that are enabled
    inspection_destinations = tuple(p for p in ("behavior_seg", "profile_seg", "rfm_seg", "intent_seg") if p in enabled_segments)
    graph.add_node("context_inspection", context_inspection, destinations=inspection_destinations)
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

        # Prefer enabled segmentors first
        if strat == "behavior" and "behavior_seg" in enabled_segments:
            return "behavior_seg"
        if strat == "profile" and "profile_seg" in enabled_segments:
            return "profile_seg"
        if strat == "rfm" and "rfm_seg" in enabled_segments:
            return "rfm_seg"
        if strat == "intent" and "intent_seg" in enabled_segments:
            return "intent_seg"

        # Fallback to presence checks for older callers or when inspection
        # did not produce a strategy
        def has(key: str) -> bool:
            if isinstance(state, dict):
                return key in state and state.get(key) is not None
            return hasattr(state, key) and getattr(state, key) is not None

        # Fallback presence checks, prefer enabled ones
        if has("behavior_summary") and "behavior_seg" in enabled_segments:
            return "behavior_seg"
        if has("customer_profile") and "profile_seg" in enabled_segments:
            return "profile_seg"
        if has("rfm_signals") and "rfm_seg" in enabled_segments:
            return "rfm_seg"
        if (has("user_query") or has("intent")) and "intent_seg" in enabled_segments:
            return "intent_seg"
        # If none of the preferred options are available, pick the first enabled
        for fallback in ("behavior_seg", "profile_seg", "rfm_seg", "intent_seg"):
            if fallback in enabled_segments:
                return fallback
        # As a last resort, default to behavior
        return "behavior_seg"

    # Allow config-driven routing rules to override the default routing.
    # Rules are evaluated top-to-bottom; a rule matches if its `source_node`
    # matches the logical source (e.g., 'context_inspection' or 'segment_merge')
    # and all key/value pairs in `condition` equal values in the state.
    def _match_rules_for_source(source_key: str, state: State):
        """Match routing rules for a given source against the current state.

        This implementation requires the `jsonlogic` package (imported at
        module import time). Rules' `condition` fields are evaluated against a
        mapping view of the runtime state using `jsonlogic.jsonlogic(cond, data)`.
        The first truthy rule wins and its `target_node` is returned.
        """
        if configs is None:
            return None

        # Convert state to a plain mapping for jsonlogic evaluation
        if isinstance(state, dict):
            data = state
        else:
            data = {}
            for k in dir(state):
                if k.startswith("_"):
                    continue
                try:
                    v = getattr(state, k)
                except Exception:
                    continue
                if callable(v):
                    continue
                data[k] = v

        rules = configs.get("routing_rules", [])
        for r in rules:
            if not r.get("enabled", True):
                continue
            src = r.get("source_node")
            if source_key == "segment_merge" and src in ("segment_merge", "seg"):
                pass
            elif source_key == "context_inspection" and src in ("context_inspection", "inspection"):
                pass
            elif src != source_key:
                continue

            cond = r.get("condition") or {}
            try:
                if _jsonlogic(cond, data):
                    return r.get("target_node")
            except Exception:
                # If a rule's expression errors, skip it rather than crash
                continue
        return None

    # Ensure the route function has a stable name for Studio drawing
    try:
        route_from_start.__name__ = "route_from_context_inspection"
    except Exception:
        pass

    # Conditional edges originate from the inspection node so runtime writes
    # remain single-writer per LastValue key while Studio can still render
    # the possible outgoing edges.
    # Only include enabled targets in the path_map so Studio/renderers stay accurate
    graph.add_conditional_edges("context_inspection", route_from_start, path_map=[p for p in ("behavior_seg", "profile_seg", "rfm_seg", "intent_seg") if p in enabled_segments])

    graph.add_edge("retrieval", "generation")
    graph.add_edge("offers", "generation")
    graph.add_edge("generation", "safety")
    graph.add_edge("safety", "hitl")
    graph.add_edge("hitl", "delivery")
    graph.add_edge("delivery", END)

    # Connect each specialized segmentation node into the `segment_merge`
    # Only add these edges for nodes that were actually registered above
    if "behavior_seg" in enabled_segments:
        graph.add_edge("behavior_seg", "segment_merge")
    if "profile_seg" in enabled_segments:
        graph.add_edge("profile_seg", "segment_merge")
    if "rfm_seg" in enabled_segments:
        graph.add_edge("rfm_seg", "segment_merge")
    if "intent_seg" in enabled_segments:
        graph.add_edge("intent_seg", "segment_merge")

    # Post-segmentation router: choose offers/retrieval/generation based on
    # `routing_hint` or segment content. Provide a path_map so Studio renders
    # explicit possible targets.
    def _get_hint(state: State):
        if isinstance(state, dict):
            return state.get("routing_hint")
        return getattr(state, "routing_hint", None)

    def route_after_seg(state: State):
        # First consult routing rules attached to the post-segmentation
        # source (segment_merge). If a rule matches, use its target.
        matched = _match_rules_for_source("segment_merge", state)
        if matched:
            return matched

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


def create_workflow(compiled: bool = True, name: str | None = "Retail Workflow Graph", enabled_segments: set | None = None):
    """Create a workflow instance.

    If `compiled` is True (default), returns the compiled workflow (runnable)
    created by calling `compile(name=...)` on a fresh StateGraph. If False,
    returns the uncompiled `StateGraph` (useful for tests that want to modify
    nodes before compile).
    """
    graph = create_state_graph(enabled_segments=enabled_segments)
    if compiled:
        return graph.compile(name=name)
    return graph


# Backwards-compatible module-level workflow (lazy initialized).
# Creating the compiled workflow at import time can trigger heavy imports
# and circular initialization races when the application is started under
# auto-reloaders. Use lazy initialization so callers can obtain the workflow
# when the import graph is stable.
workflow = None


# Helpers to atomically replace the module-level workflow instance.
import threading

_workflow_lock = threading.Lock()


def replace_workflow(new_workflow):
    """Atomically replace the module-level `workflow` instance.

    Useful for runtime rebuilds performed by an admin API or background
    task. Uses a simple threading lock so both sync and async callers can
    safely swap the global reference.
    """
    global workflow
    with _workflow_lock:
        global workflow
        workflow = new_workflow


def get_workflow():
    """Return the current module-level workflow instance."""
    global workflow
    # Lazily create the workflow on first access if it hasn't been built yet.
    if workflow is None:
        # Defer to create_workflow which constructs the graph; keep this
        # guarded by the module-level lock in case callers race.
        with _workflow_lock:
            if workflow is None:
                workflow = create_workflow()
    return workflow


# Initialize the module-level `workflow` at import time so `from agent.graph import graph`
# returns a usable workflow instance for existing callers and tests. Use the same
# lock to avoid races when imported under test runners.
try:
    with _workflow_lock:
        if workflow is None:
            workflow = create_workflow()
except Exception:
    # Best-effort initialization: if workflow creation fails during import,
    # leave `workflow` as None and allow callers to lazily initialize via
    # `get_workflow()` to avoid crashing the test/imports.
    pass

