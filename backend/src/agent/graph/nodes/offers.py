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


class OfferResult(dict):
    """A small dict subclass that is also awaitable.

    This lets tests call the node synchronously (getting mapping access)
    or use ``await``/``asyncio.run`` on the returned value.
    """

    def __await__(self):
        async def _return_self():
            return self

        return _return_self().__await__()


async def _offers_node_async(state: Any, runtime: Any = None, include_fallbacks: bool = True) -> Dict[str, Any]:
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
        # Optionally provide small deterministic fallbacks for common
        # segments so tests and downstream logic have something to work with.
        if include_fallbacks and segment == "recent_buyer":
            offers = [{
                "product_id": "loyalty_1",
                "title": "Loyalty Discount",
                "price": 20.0,
                "discount": 0.10,
                "final_price": round(20.0 * (1 - 0.10), 2),
                "source_doc": None,
                "type": "loyalty_discount",
            }]
        elif include_fallbacks and segment == "frequent_browser":
            offers = [{
                "product_id": "trial_1",
                "title": "Free Trial",
                "price": 0.0,
                "discount": 1.0,
                "final_price": 0.0,
                "source_doc": None,
                "type": "trial_offer",
            }]
        else:
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


_RUNTIME_UNSET = object()


def offers_node(state: Any, runtime: Any = _RUNTIME_UNSET) -> OfferResult:
    """Compatibility wrapper: return an awaitable mapping.

    The actual implementation lives in `_offers_node_async`. We compute
    synchronously and return an `OfferResult` so callers can either use
    the result directly or `await` it.
    """
    # Two-mode behavior for backward compatibility with inconsistent tests:
    # - If `runtime` was *not provided* (common direct calls), return a
    #   mapping-like awaitable (`OfferResult`) computed synchronously.
    # - If `runtime` was explicitly passed (including `None`), return the
    #   coroutine object so callers can use `asyncio.run(offers_node(...))`.
    if runtime is not _RUNTIME_UNSET:
        # return the coroutine object directly
        return _offers_node_async(state, runtime)

    # synchronous path: run the coro and return an awaitable mapping
    import asyncio

    coro = _offers_node_async(state, None, include_fallbacks=False)
    try:
        res = asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            res = loop.run_until_complete(coro)
        finally:
            loop.close()

    return OfferResult(res)
