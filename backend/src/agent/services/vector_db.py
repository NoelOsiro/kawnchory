"""Simple vector DB stub used for development and tests.

Provides `query_by_product_id(product_id)` which returns deterministic
fixtures for test inputs. Replace with real vector search in production.
"""
from __future__ import annotations

from typing import Any, Dict, List

_SAMPLE_INDEX = {
    "p_101": {
        "id": "p_101",
        "title": "Product 101 Specs",
        "content": "Details about product 101...",
        "source": "product_docs",
    },
    "p_202": {
        "id": "p_202",
        "title": "Product 202 Guide",
        "content": "Usage guidance for product 202...",
        "source": "product_docs",
    },
}


def query_by_product_id(product_id: str) -> List[Dict[str, Any]]:
    """Return a list of citation dicts matching `product_id` from sample index."""
    if not product_id:
        return []
    item = _SAMPLE_INDEX.get(product_id)
    return [item] if item else []
