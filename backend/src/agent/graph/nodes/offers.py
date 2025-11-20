"""Offers node: build structured offers from retrieval results and segmentation."""
from typing import Any, Dict, List


def _as_dict(state: Any) -> Dict:
    if isinstance(state, dict):
        return state
    # minimal State-compatible adapter: try mapping-like access
    try:
        return dict(state.__dict__)
    except Exception:
        return {}


def offers_node(state: Any, runtime: Any = None) -> Dict[str, Any]:
    """Create simple deterministic offers from `retrieved_docs` and `segment`.

    Input (state or dict) keys used:
    - `retrieved_docs`: list of dicts with keys like `id`, `title`, `price`
    - `segment`: segmentation label (string)

    Output:
    - `offers`: list of offer dicts
    - `offers_count`: int
    - `routing_hint`: next node hint (defaults to `generation`)
    - `offers_metadata`: small summary
    """
    s = _as_dict(state)
    retrieved: List[Dict] = s.get("retrieved_docs") or []
    segment: str = s.get("segment") or getattr(state, "segment", "new_or_casual")

    # choose top N deterministic (first N)
    max_offers = 3
    chosen = retrieved[:max_offers]

    offers: List[Dict] = []
    for doc in chosen:
        pid = doc.get("id") or doc.get("product_id") or "unknown"
        title = doc.get("title") or doc.get("name") or "Product"
        price = doc.get("price") if doc.get("price") is not None else 9.99

        # simple personalization rules
        discount = 0.0
        if segment == "recent_buyer":
            discount = 0.05
        elif segment == "frequent_browser":
            discount = 0.10
        elif segment == "cart_abandoned":
            discount = 0.15

        final_price = round(max(0.0, price * (1 - discount)), 2)

        offers.append({
            "product_id": pid,
            "title": title,
            "price": price,
            "discount": discount,
            "final_price": final_price,
            "source_doc": doc,
            "type": "retrieval_offer",
        })

    # If no retrieved docs, return an empty offers list (tests expect this)
    if not offers:
        offers = []

    result = {
        "offers": offers,
        "offers_count": len(offers),
        "routing_hint": "generation",
        "offers_metadata": {
            "selected_from_retrieval": len(retrieved),
            "max_offers": max_offers,
            "source_docs_count": len(retrieved),
        },
    }

    return result
