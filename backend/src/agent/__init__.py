"""Agent package initializer.

Avoid importing the compiled `graph` at module import time to prevent
optional dependency failures during tests. Importers can still access
`agent.graph` directly when they need the runtime graph.
"""
try:
	# Prefer explicit import when available
	from agent.graph import graph
except Exception:
	# Fall back to None to keep imports lightweight in test environments
	graph = None

__all__ = ["graph"]
