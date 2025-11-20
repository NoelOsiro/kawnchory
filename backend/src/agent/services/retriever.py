"""Compatibility re-export for retriever.

Some parts of the codebase (or editors) may import `agent.services.retriever`.
This module re-exports `retrieve_citations` from `agent.agents.retriever` so both
import paths resolve to the same implementation.
"""
from __future__ import annotations

from typing import Any, Dict, List

try:
    # Import from the runtime agents package
    from agent.agents.retriever import retrieve_citations  # type: ignore
except Exception:  # pragma: no cover - best-effort fallback for editors/tests
    # Fallback stub: return empty list when called
    def retrieve_citations(customer: Dict[str, Any]) -> List[Dict[str, Any]]:  # type: ignore
        return []
