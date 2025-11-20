from __future__ import annotations
from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import State


async def retrieval_node(state: State, runtime: Runtime) -> Dict[str, Any]:
    """Runs retrieval using segment and behavior signals to personalize results."""
    # TODO: call your real retriever here
    return {
        "retrieved_docs": [],
        "retrieval_explain": {},
        "retrieval_settings": {},
    }
