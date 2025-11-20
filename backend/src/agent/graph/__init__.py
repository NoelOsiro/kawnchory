"""Graph package for agent workflows.

Expose `graph` at package level so `from agent.graph import graph` continues
to work for existing code that imports the top-level module.
"""

from .workflow_graph import workflow as graph

__all__ = ["graph"]
