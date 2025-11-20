"""Runtime retriever implementation for the agent package.

Provides `retrieve_citations(customer)` using a small in-memory index for
development and tests. Replace with a vector DB call in production.
"""
from __future__ import annotations

from typing import Any, Dict, List

# Small sample index used for deterministic tests
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


def _lookup_by_product_id(product_id: str) -> List[Dict[str, Any]]:
    if not product_id:
        return []
    item = _SAMPLE_INDEX.get(product_id)
    return [item] if item else []


def retrieve_citations(customer: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Retrieve citation documents for a customer's product.

    Parameters
    ----------
    customer : Dict[str, Any]
        Customer object expected to contain an optional "properties" mapping
        with a "product_id" key used to look up citations.

    Returns:
    -------
    List[Dict[str, Any]]
        A list of citation documents (possibly empty) matching the customer's
        product_id. The function first attempts to use an optional vector DB
        hook (agent.services.vector_db.query_by_product_id) and falls back to
        a small in-memory index used for tests and development.

    Notes:
    -----
    Any exceptions raised while attempting to import or call the optional
    vector DB hook are suppressed and the in-memory lookup is used as a
    fallback.
    """
    if not customer:
        return []

    props = customer.get("properties") or {}
    product_id = props.get("product_id") if isinstance(props, dict) else None

    # Optional hook to agent.services.vector_db if present
    try:
        from agent.services.vector_db import query_by_product_id

        if callable(query_by_product_id):
            results = query_by_product_id(product_id)
            if results:
                return results
    except Exception:
        pass

    return _lookup_by_product_id(product_id)
