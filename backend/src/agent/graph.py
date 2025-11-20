"""Top-level graph shim.

LangGraph's graph loader expects to import `graph` from
`src/agent/graph.py`. This file exposes the compiled workflow
from `agent.graph.workflow_graph` as `graph` so the loader can
continue to point at the same path while we keep the full
workflow split into multiple node files.
"""

from __future__ import annotations

from agent.graph.workflow_graph import workflow as graph  # noqa: F401

