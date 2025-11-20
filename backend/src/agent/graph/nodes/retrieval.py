"""Retrieval node for personalized document retrieval.

This module provides `retrieval_node`, which runs retrieval using segment and
behavior signals to personalize results and returns retrieved documents along
with a lightweight explanation for observability.
"""

from __future__ import annotations

from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.state import State


async def retrieval_node(state: State | Dict[str, Any], runtime: Runtime) -> Dict[str, Any]:
    """Run retrieval using segment and behavior signals to personalize results.

    This node calls the `backend.agents.retriever.retrieve_citations` function
    when available and stores the resulting list as `retrieved_docs` in the
    returned dict. The node also provides a lightweight `retrieval_explain`
    dict for observability.
    """
    # Extract a customer-like payload for the retriever
    customer = {}
    if isinstance(state, dict):
        customer = {
            "properties": state.get("customer_profile") or {},
            "behavior_summary": state.get("behavior_summary") or {},
        }
    else:
        customer = {
            "properties": getattr(state, "customer_profile", {}) or {},
            "behavior_summary": getattr(state, "behavior_summary", {}) or {},
        }

    try:
        # Prefer the runtime agents implementation
        from agent.agents.retriever import retrieve_citations

        docs = retrieve_citations(customer) or []
    except Exception:
        # Fall back to a services-level re-export if present (editor/legacy compatibility)
        try:
            from agent.services.retriever import (
                retrieve_citations as retrieve_citations_alt,
            )

            docs = retrieve_citations_alt(customer) or []
        except Exception:
            docs = []

    retrieval_explain = {"result_count": len(docs)}

    return {
        "retrieved_docs": docs,
        "retrieval_explain": retrieval_explain,
        "retrieval_settings": {},
    }
